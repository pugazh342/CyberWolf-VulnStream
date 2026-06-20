from langchain_community.embeddings import HuggingFaceEmbeddings

def get_local_embedder() -> HuggingFaceEmbeddings:
    """
    Initializes and returns the zero-cost BAAI/bge-small-en-v1.5 embedding model.
    It automatically downloads from Hugging Face on the first run and runs locally.
    """
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {"device": "cpu"}  # Swaps to 'cuda' automatically if a GPU is configured later
    encode_kwargs = {"normalize_embeddings": True}  # Vital for highly accurate cosine similarity search
    
    print(f"[+] Initializing local embedding model: {model_name}...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings