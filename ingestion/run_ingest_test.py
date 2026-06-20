import os
import json
from ingestion.cve_loader import load_cve_json
from ingestion.cisa_loader import load_cisa_kev_csv
from ingestion.mitre_loader import load_mitre_attack

def run_phase1_validation():
    print("━" * 50)
    print("🛡️ CYBERWOLF VULNSTREAM: PHASE 1 VALIDATION RUNNER")
    print("━" * 50)

    # 1. Test CVE Ingestion
    cve_path = "data/cve_samples.json"
    if os.path.exists(cve_path):
        print(f"[+] Loading sample CVEs from: {cve_path}")
        cve_docs = load_cve_json(cve_path)
        print(f"    👉 Successfully processed {len(cve_docs)} CVE documents.")
        if cve_docs:
            print(f"    👉 Sample Metadata: {json.dumps(cve_docs[0].metadata, indent=2)}")
    else:
        print(f"[-] Warning: {cve_path} not found. Skipping CVE parsing test.")

    print("─" * 50)

    # 2. Test CISA KEV Ingestion
    cisa_path = "data/cisa_kev.csv"
    if os.path.exists(cisa_path):
        print(f"[+] Loading CISA KEV entries from: {cisa_path}")
        cisa_docs = load_cisa_kev_csv(cisa_path)
        print(f"    👉 Successfully processed {len(cisa_docs)} KEV documents.")
        if cisa_docs:
            print(f"    👉 Sample Metadata: {json.dumps(cisa_docs[0].metadata, indent=2)}")
    else:
        print(f"[-] Warning: {cisa_path} not found. Skipping CISA KEV parsing test.")

    print("─" * 50)

    # 3. Test MITRE ATT&CK Ingestion
    mitre_path = "data/enterprise_attack.json"
    if os.path.exists(mitre_path):
        print(f"[+] Loading MITRE ATT&CK techniques from: {mitre_path}")
        mitre_docs = load_mitre_attack(mitre_path)
        print(f"    👉 Successfully processed {len(mitre_docs)} ATT&CK documents.")
        if mitre_docs:
            print(f"    👉 Sample Metadata: {json.dumps(mitre_docs[0].metadata, indent=2)}")
    else:
        print(f"[-] Warning: {mitre_path} not found. Skipping MITRE ATT&CK parsing test.")

    print("━" * 50)
    print("✅ Phase 1 Verification Process Complete.")
    print("━" * 50)

if __name__ == "__main__":
    run_phase1_validation()