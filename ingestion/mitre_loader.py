import json
from typing import List
from langchain_core.documents import Document
from ingestion.normalizer import create_threat_document

def load_mitre_attack(file_path: str) -> List[Document]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    documents = []
    
    for obj in data.get("objects", []):
        if obj.get("type") == "attack-pattern":
            name = obj.get("name", "")
            description = obj.get("description", "")
            
            # Extract the T-Code (e.g., T1059)
            technique_id = None
            for ext_ref in obj.get("external_references", []):
                if ext_ref.get("source_name") == "mitre-attack":
                    technique_id = ext_ref.get("external_id")
                    break
            
            # Extract the overarching Tactic (e.g., Execution, Persistence)
            tactics = [kc.get("phase_name") for kc in obj.get("kill_chain_phases", [])]
            tactic = tactics[0].title().replace("-", " ") if tactics else None
            
            doc = create_threat_document(
                source="MITRE_ATTACK",
                document_type="attack",
                page_content=description,
                id=technique_id,
                title=name,
                technique_id=technique_id,
                tactic=tactic
            )
            documents.append(doc)
            
    return documents