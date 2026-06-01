import os
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

# Import database, models, schemas, and services
from backend.db.database import get_db, init_db
from backend.models.portfolio import PortfolioCreate, PortfolioResponse, AnalysisJobResponse
from backend.services.portfolio_service import save_portfolio, create_new_job, update_job, get_job_by_id
from backend.services.sse_service import sse_service
from backend.services.pdf_service import generate_pdf_report
from backend.agents.orchestrator import build_and_run_analysis_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Agentic AI Ops Manager - Financial Analyst Crew",
    description="Deterministic multi-agent financial and portfolio analysis system.",
    version="1.0.0"
)

# CORS Configuration
# Allow wildcard for easy developer access, or specific headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    """Initializes tables on startup (perfect for zero-config SQLite fallbacks)"""
    logger.info("FastAPI: Initializing database engine and tables...")
    await init_db()
    logger.info("FastAPI: Database initialization successfully completed.")

# ==========================================
# Background Analysis Executor
# ==========================================

async def run_analysis_job_in_background(
    job_id: str,
    tickers: List[str],
    weights: Dict[str, float]
):
    """
    Background worker that runs the LangGraph orchestrator crew.
    Publishes real-time status and report events to sse_service.
    """
    logger.info(f"Worker: Starting Analysis execution for Job {job_id}...")
    
    # Establish async DB session local lifecycle
    from backend.db.database import SessionLocal
    if not SessionLocal:
        logger.error("SessionLocal database connector is not initialized.")
        return
        
    async with SessionLocal() as db:
        try:
            # 1. Update job status to RUNNING in database
            await update_job(db, job_id=job_id, status="RUNNING")
            
            # Define emitter callback to publish agent logs to the SSE stream
            def publish_agent_log(event: Dict[str, Any]):
                # Call async publish in a threadsafe/async fashion
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(sse_service.publish_event(job_id, event))
            
            # 2. Trigger Orchestrator LangGraph execution
            logger.info(f"Worker: Running LangGraph for Job {job_id}...")
            final_state = await build_and_run_analysis_graph(
                job_id=job_id,
                tickers=tickers,
                weights=weights,
                emitter_callback=publish_agent_log
            )
            
            # 3. Update database job status to COMPLETED
            logger.info(f"Worker: Graph finished. Saving output for Job {job_id}...")
            await update_job(
                db,
                job_id=job_id,
                status="COMPLETED",
                risk_score=final_state.risk_score,
                report_markdown=final_state.report_markdown
            )
            
            # Publish final completion event to let the frontend dashboard close its loading bar
            await sse_service.publish_event(job_id, {
                "agent": "Orchestrator",
                "phase": "COMPLETE",
                "message": "Global multi-agent process successfully completed. Data saved.",
                "timestamp": ""
            })
            
        except Exception as e:
            logger.error(f"Worker: Analysis failed for Job {job_id}: {e}", exc_info=True)
            try:
                await update_job(db, job_id=job_id, status="FAILED")
                await sse_service.publish_event(job_id, {
                    "agent": "Orchestrator",
                    "phase": "FAILED",
                    "message": f"Global failure occurred during execution: {str(e)}",
                    "timestamp": ""
                })
            except Exception as ex:
                logger.error(f"Worker: Critical failure during DB error recovery ({ex})")

# ==========================================
# REST Endpoints
# ==========================================

@app.post("/api/portfolio", status_code=201)
async def analyze_portfolio(
    portfolio_in: PortfolioCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a portfolio, validates weights, saves in DB,
    and spins up a background LangGraph analysis job.
    """
    logger.info(f"API: Received portfolio analysis request: {portfolio_in.name}")
    
    try:
        # 1. Parse and save portfolio (normalizes weights to 0.0 - 1.0)
        portfolio = await save_portfolio(db, portfolio_in)
        
        # Prepare tickers and weight mappings for LangGraph
        tickers = [t.ticker for t in portfolio.tickers]
        weights = {t.ticker: t.weight for t in portfolio.tickers}
        
        # 2. Create database row for Analysis Job
        job = await create_new_job(db, portfolio.id)
        
        # 3. Dispatch LangGraph Orchestration graph in background thread
        background_tasks.add_task(
            run_analysis_job_in_background,
            job_id=job.id,
            tickers=tickers,
            weights=weights
        )
        
        logger.info(f"API: Portfolio saved. Dispatched Job {job.id} for Portfolio {portfolio.id}.")
        return {
            "job_id": job.id,
            "portfolio_id": portfolio.id,
            "status": "PENDING"
        }
        
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"API: Failed to submit portfolio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database insertion error: {str(e)}"
        )

@app.get("/api/stream/{job_id}")
async def stream_job_events(job_id: str):
    """
    Exposes a Server-Sent Events (SSE) stream for a running Analysis Job.
    Emits agent status logs and report tokens in real-time.
    """
    logger.info(f"API: Stream client connected for Job {job_id}.")
    
    return StreamingResponse(
        sse_service.listen_events(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/report/{job_id}", response_model=AnalysisJobResponse)
async def get_analysis_report(job_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full metadata, status, and compiled markdown report for a job"""
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis Job with ID '{job_id}' not found."
        )
    return job

@app.get("/api/report/{job_id}/pdf")
async def download_analysis_pdf(job_id: str, db: AsyncSession = Depends(get_db)):
    """Compiles and exports the analysis report into a premium corporate PDF"""
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis Job with ID '{job_id}' not found."
        )
        
    if job.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot export PDF. Job status is '{job.status}'. Report must be COMPLETED."
        )
        
    # Compile PDF to temporary scratch file inside workspace
    pdf_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filename = f"Financial_Report_{job_id}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    try:
        generate_pdf_report(job, pdf_path)
        
        p_name = job.portfolio.name if job.portfolio else "Portfolio"
        download_name = f"{p_name.replace(' ', '_')}_Analysis_Report.pdf"
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=download_name
        )
    except Exception as e:
        logger.error(f"API: PDF compilation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF Report: {str(e)}"
        )

# ==========================================
# Diagnostic / Health Checks
# ==========================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": os.getenv("CURRENT_TIME", "2026-06-01T20:07:44+05:30")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
