import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from embeddings.embedder import get_local_embedder

load_dotenv()
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./vectordb/chroma_storage")
COLLECTION_NAME = "cyberwolf_cti"

class CyberWolfCTIRetriever:
    def __init__(self):
        self.embeddings = get_local_embedder()
        self.db = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )

    def search_threat_intel(self, query: str, metadata_filter: dict = None, k: int = 3):
        """
        Queries ChromaDB using semantic similarity, optionally restricted by strict metadata filters.
        """
        print(f"[*] Querying vector store for: '{query}' | Filters: {metadata_filter}")
        
        # Using LangChain's native search with Chroma metadata filtering constraints
        docs = self.db.similarity_search(
            query,
            k=k,
            filter=metadata_filter
        )
        return docs