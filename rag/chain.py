import os
from langchain_community.llms import Ollama
from retrieval.retriever import CyberWolfCTIRetriever
from rag.prompts import CTI_SYSTEM_PROMPT

class CyberWolfRAGPipeline:
    def __init__(self):
        self.retriever = CyberWolfCTIRetriever()
        print("[+] Initializing Local Ollama Engine...")
        
        # Connects to your local Ollama instance running on port 11434
        # Change 'deepseek-r1:8b' to whichever model you have pulled locally
        self.model = Ollama(model="llama3.2:latest") 

    def execute_analysis(self, query: str, metadata_filter: dict = None) -> str:
        # 1. Fetch matching context documents from local storage
        matched_docs = self.retriever.search_threat_intel(query, metadata_filter=metadata_filter)
        
        if not matched_docs:
            return "❌ No relevant context items matched your query/metadata filters in the vector store."

        # 2. Format the context blocks into clean readable string formats for the LLM
        context_str = ""
        for i, doc in enumerate(matched_docs, 1):
            context_str += f"\n--- Document [{i}] ---\n"
            context_str += f"Source: {doc.metadata.get('source')}\n"
            context_str += f"Doc Type: {doc.metadata.get('document_type')}\n"
            context_str += f"ID/Title: {doc.metadata.get('title', doc.metadata.get('id', 'N/A'))}\n"
            
            if 'cvss' in doc.metadata: context_str += f"CVSS Score: {doc.metadata['cvss']} ({doc.metadata.get('severity')})\n"
            if 'is_exploited' in doc.metadata: context_str += f"Actively Exploited: {doc.metadata['is_exploited']}\n"
            if 'tactic' in doc.metadata: context_str += f"ATT&CK Tactic: {doc.metadata['tactic']}\n"
            
            context_str += f"Content: {doc.page_content}\n"

        # 3. Compile the system prompt
        formatted_prompt = CTI_SYSTEM_PROMPT.format(context=context_str)

        # 4. Invoke the generation API completely locally
        print(f"[+] Context assembled. Querying Local Model...")
        response = self.model.invoke(f"{formatted_prompt}\n\nUser Query: {query}")
        return response