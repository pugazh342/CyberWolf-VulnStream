import json
from typing import List
from langchain_core.documents import Document
from ingestion.normalizer import create_threat_document

def load_cve_json(file_path: str) -> List[Document]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    documents = []
    
    # Adjust iteration based on the exact structure of your NVD/MITRE download
    for item in data:  
        cve_id = item.get("cve_id", "")
        description = item.get("description", "")
        cvss = item.get("cvss")
        
        # Simple severity mapping based on standard CVSS v3 brackets
        severity = "Unknown"
        if cvss:
            if cvss >= 9.0: severity = "Critical"
            elif cvss >= 7.0: severity = "High"
            elif cvss >= 4.0: severity = "Medium"
            else: severity = "Low"
        
        doc = create_threat_document(
            source="NVD",
            document_type="cve",
            page_content=description,
            id=cve_id,
            title=cve_id,
            cvss=cvss,
            severity=severity
        )
        documents.append(doc)
        
    return documents