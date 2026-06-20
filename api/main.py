from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler

from rag.chain import CyberWolfRAGPipeline
from ingest_manager import ProductionIngestionEngine

# 1. Define the automated task
# Update this function inside api/main.py
def run_daily_ingestion():
    print("\n[*] CRON TRIGGER: Starting 24-hour automated multi-source threat ingestion...")
    engine = ProductionIngestionEngine()
    
    # 1. Update CISA KEV
    engine.fetch_and_ingest_cisa_kev()
    
    # 2. Update MITRE ATT&CK Matrix
    engine.fetch_and_ingest_mitre()
    
    # 3. Update Recent NVD Vulnerabilities
    engine.fetch_and_ingest_nvd_recent()
    
    # FIX HERE: Ensure the line ends exactly after the closing parenthesis
    print("[*] CRON TRIGGER: Automated multi-source ingestion complete. Sleeping for 24 hours.\n")
# 2. Configure the lifespan events to manage the background timer
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[+] Booting CyberWolf RAG Engine & Scheduler...")
    
    # Optional: Run once immediately on startup to verify it fires perfectly
    run_daily_ingestion()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_ingestion, 'interval', hours=24)
    scheduler.start()
    
    yield
    scheduler.shutdown()

# Initialize the FastAPI app with the lifespan hook
app = FastAPI(
    title="CyberWolf VulnStream API",
    description="Real-Time Threat Intelligence RAG Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

rag_pipeline = CyberWolfRAGPipeline()

class ThreatQuery(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None

@app.get("/")
def health_check():
    return {"status": "online", "system": "CyberWolf VulnStream API"}

@app.post("/api/analyze")
def analyze_threat(payload: ThreatQuery):
    try:
        print(f"\n[API] Received Query: {payload.query}")
        print(f"[API] Applied Filters: {payload.filters}")
        
        response_text = rag_pipeline.execute_analysis(
            query=payload.query, 
            metadata_filter=payload.filters
        )
        
        return {
            "status": "success",
            "query": payload.query,
            "response": response_text
        }
    except Exception as e:
        print(f"[-] API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal RAG Processing Error")