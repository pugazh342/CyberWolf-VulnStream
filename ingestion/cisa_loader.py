import csv
from typing import List
from langchain_core.documents import Document
from ingestion.normalizer import create_threat_document

def load_cisa_kev_csv(file_path: str) -> List[Document]:
    documents = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cve_id = row.get("cveID", "")
            vendor = row.get("vendorProject", "")
            product = row.get("product", "")
            description = row.get("shortDescription", "")
            date_added = row.get("dateAdded", "")
            
            doc = create_threat_document(
                source="CISA_KEV",
                document_type="kev",
                page_content=description,
                id=cve_id,
                title=cve_id,
                vendor=vendor,
                product=product,
                published=date_added,
                is_exploited=True  # Inherently True for this dataset
            )
            documents.append(doc)
            
    return documents