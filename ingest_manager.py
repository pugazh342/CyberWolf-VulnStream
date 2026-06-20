import os
import requests
import csv
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from embeddings.embedder import get_local_embedder

load_dotenv()
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./vectordb/chroma_storage")
COLLECTION_NAME = "cyberwolf_cti"

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"
MITRE_ATTACK_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class ProductionIngestionEngine:
    def __init__(self):
        print("[+] Initializing Production Ingestion Engine Core...")
        self.embeddings = get_local_embedder()
        self.db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self) -> set:
        """Fetches all existing document IDs from ChromaDB for deduplication."""
        print("[*] Analyzing existing vector database for deduplication...")
        existing_records = self.db.get(include=['metadatas'])
        existing_set = set()
        if existing_records and existing_records['metadatas']:
            for meta in existing_records['metadatas']:
                if meta and 'id' in meta:
                    existing_set.add(meta['id'])
        print(f"[*] Found {len(existing_set)} existing threat records in database.")
        return existing_set

    def _batch_ingest(self, normalized_docs: list, doc_ids: list):
        """Helper function to ingest documents in manageable chunks."""
        batch_size = 100
        for i in range(0, len(normalized_docs), batch_size):
            chunk = normalized_docs[i:i + batch_size]
            chunk_ids = doc_ids[i:i + batch_size]
            self.db.add_documents(documents=chunk, ids=chunk_ids)
            print(f"    [-->] Embedded and saved records {i} to {min(i + batch_size, len(normalized_docs))}...")

    # ---------------------------------------------------------
    # 1. CISA KEV INGESTION
    # ---------------------------------------------------------
    def fetch_and_ingest_cisa_kev(self):
        print(f"\n[*] Fetching live CISA KEV catalog...")
        try:
            response = requests.get(CISA_KEV_URL, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"[-] Failed to fetch live CISA feed: {str(e)}")
            return

        reader = list(csv.DictReader(response.content.decode('utf-8').splitlines()))
        new_records = [r for r in reader if r.get('cveID') not in self.existing_ids]
        
        if not new_records:
            print("✅ CISA KEV is up to date.")
            return
            
        print(f"[+] Found {len(new_records)} NEW CISA vulnerabilities to process.")
        
        docs, ids = [], []
        for row in new_records:
            cve_id = row.get('cveID', 'N/A')
            content = (
                f"Vulnerability ID: {cve_id}\nVendor: {row.get('vendorProject', 'N/A')}\n"
                f"Product: {row.get('product', 'N/A')}\nName: {row.get('vulnerabilityName', 'N/A')}\n"
                f"Description: {row.get('shortDescription', 'N/A')}\nRemediation: {row.get('requiredAction', 'N/A')}"
            )
            metadata = {"source": "CISA_KEV", "document_type": "vulnerability", "id": cve_id, "is_exploited": True}
            docs.append(Document(page_content=content, metadata=metadata))
            ids.append(cve_id) 

        self._batch_ingest(docs, ids)
        self.existing_ids.update(ids)

    # ---------------------------------------------------------
    # 2. MITRE ATT&CK INGESTION
    # ---------------------------------------------------------
    def fetch_and_ingest_mitre(self):
        print(f"\n[*] Fetching live MITRE ATT&CK Enterprise matrix...")
        try:
            response = requests.get(MITRE_ATTACK_URL, timeout=20)
            response.raise_for_status()
            stix_data = response.json()
        except Exception as e:
            print(f"[-] Failed to fetch MITRE ATT&CK feed: {str(e)}")
            return

        objects = stix_data.get("objects", [])
        # Filter for attack patterns (techniques)
        techniques = [obj for obj in objects if obj.get("type") == "attack-pattern"]
        
        docs, ids = [], []
        for tech in techniques:
            # Extract MITRE ID (e.g., T1059)
            ext_refs = tech.get("external_references", [])
            mitre_id = next((ref.get("external_id") for ref in ext_refs if ref.get("source_name") == "mitre-attack"), None)
            
            if not mitre_id or mitre_id in self.existing_ids:
                continue

            name = tech.get("name", "Unknown")
            description = tech.get("description", "No description provided.")
            
            content = f"MITRE Technique ID: {mitre_id}\nTechnique Name: {name}\nDescription: {description}"
            metadata = {"source": "MITRE_ATTACK", "document_type": "technique", "id": mitre_id, "title": name}
            
            docs.append(Document(page_content=content, metadata=metadata))
            ids.append(mitre_id)

        if not docs:
            print("✅ MITRE ATT&CK matrix is up to date.")
            return

        print(f"[+] Found {len(docs)} NEW MITRE techniques to process.")
        self._batch_ingest(docs, ids)
        self.existing_ids.update(ids)

    # ---------------------------------------------------------
    # 3. NVD RECENT INGESTION (Past 7 Days)
    # ---------------------------------------------------------
    def fetch_and_ingest_nvd_recent(self):
        print(f"\n[*] Fetching recent NVD vulnerabilities (last 7 days)...")
        
        # Calculate date range for the API
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        pub_start_date = seven_days_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        pub_end_date = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        params = {
            "pubStartDate": pub_start_date,
            "pubEndDate": pub_end_date,
            "resultsPerPage": 500  # Pull up to 500 recent CVEs
        }
        
        # If you register for an NVD API key, add it here to avoid strict rate limiting
        headers = {}
        nvd_api_key = os.getenv("NVD_API_KEY")
        if nvd_api_key:
            headers["apiKey"] = nvd_api_key

        try:
            response = requests.get(NVD_API_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            nvd_data = response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 403:
                print("[-] NVD API rate limit hit. Consider getting a free API key at https://nvd.nist.gov/developers/request-an-api-key")
            else:
                print(f"[-] NVD Fetch Error: {err}")
            return
        except Exception as e:
            print(f"[-] Failed to fetch NVD feed: {str(e)}")
            return

        vulnerabilities = nvd_data.get("vulnerabilities", [])
        docs, ids = [], []
        
        for item in vulnerabilities:
            cve = item.get("cve", {})
            cve_id = cve.get("id")
            
            if not cve_id or cve_id in self.existing_ids:
                continue

            # Extract English description
            descriptions = cve.get("descriptions", [])
            desc_text = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "No description.")
            
            # Extract CVSS Score (Try v3.1 first, then v3.0, then v2)
            cvss_score = "N/A"
            metrics = cve.get("metrics", {})
            if "cvssMetricV31" in metrics:
                cvss_score = metrics["cvssMetricV31"][0]["cvssData"]["baseScore"]
            elif "cvssMetricV30" in metrics:
                cvss_score = metrics["cvssMetricV30"][0]["cvssData"]["baseScore"]

            content = f"Vulnerability ID: {cve_id}\nCVSS Score: {cvss_score}\nDescription: {desc_text}"
            metadata = {"source": "NVD", "document_type": "vulnerability", "id": cve_id, "cvss": cvss_score}
            
            docs.append(Document(page_content=content, metadata=metadata))
            ids.append(cve_id)

        if not docs:
            print("✅ NVD Recent is up to date.")
            return

        print(f"[+] Found {len(docs)} NEW NVD vulnerabilities to process.")
        self._batch_ingest(docs, ids)
        self.existing_ids.update(ids)

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🛡️  CYBERWOLF VULNSTREAM: LIVE PRODUCTION INGESTION ENGINE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    engine = ProductionIngestionEngine()
    
    # Execute the triad of ingestion sources
    engine.fetch_and_ingest_cisa_kev()
    engine.fetch_and_ingest_mitre()
    engine.fetch_and_ingest_nvd_recent()