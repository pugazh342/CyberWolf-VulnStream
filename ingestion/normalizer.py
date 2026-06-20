from langchain_core.documents import Document
from typing import List, Optional

def create_threat_document(
    source: str,
    document_type: str,
    page_content: str,
    id: Optional[str] = None,
    title: Optional[str] = None,
    severity: Optional[str] = None,
    cvss: Optional[float] = None,
    published: Optional[str] = None,
    vendor: Optional[str] = None,
    product: Optional[str] = None,
    tags: Optional[List[str]] = None,
    references: Optional[List[str]] = None,
    is_exploited: Optional[bool] = None,
    technique_id: Optional[str] = None,
    tactic: Optional[str] = None,
) -> Document:
    
    # Core mandatory metadata
    metadata = {
        "source": source,
        "document_type": document_type,
    }
    
    # Map optional fields dynamically
    optional_fields = {
        "id": id,
        "title": title,
        "severity": severity,
        "cvss": cvss,
        "published": published,
        "vendor": vendor,
        "product": product,
        "is_exploited": is_exploited,
        "technique_id": technique_id,
        "tactic": tactic,
    }
    
    for key, value in optional_fields.items():
        if value is not None:
            metadata[key] = value
            
    # Flatten lists for ChromaDB metadata compatibility
    if tags:
        metadata["tags"] = ", ".join(tags)
    if references:
        metadata["references"] = ", ".join(references)

    return Document(page_content=page_content, metadata=metadata)