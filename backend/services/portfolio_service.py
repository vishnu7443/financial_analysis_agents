import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.portfolio import Portfolio, PortfolioTicker, AnalysisJob, PortfolioCreate

logger = logging.getLogger(__name__)

async def save_portfolio(db: AsyncSession, portfolio_in: PortfolioCreate) -> Portfolio:
    """
    Saves a portfolio to the database and normalizes ticker weights.
    If weights sum up to ~100, we divide each by 100 to save as decimals (0.0 to 1.0).
    """
    # Calculate sum of weights to determine normalization method
    total_weight = sum(t.weight for t in portfolio_in.tickers)
    
    should_divide_100 = total_weight > 1.5  # If sum is e.g. 100.0 rather than 1.0
    
    db_portfolio = Portfolio(name=portfolio_in.name or "My Portfolio")
    db.add(db_portfolio)
    await db.flush()  # Populates db_portfolio.id
    
    for ticker_item in portfolio_in.tickers:
        normalized_weight = ticker_item.weight
        if should_divide_100:
            normalized_weight = ticker_item.weight / 100.0
            
        # Bound between 0 and 1
        normalized_weight = max(0.0, min(1.0, normalized_weight))
        
        db_ticker = PortfolioTicker(
            portfolio_id=db_portfolio.id,
            ticker=ticker_item.ticker.upper().strip(),
            weight=normalized_weight
        )
        db.add(db_ticker)
        
    await db.commit()
    # Refresh to load relationships
    query = select(Portfolio).where(Portfolio.id == db_portfolio.id)
    result = await db.execute(query)
    portfolio_loaded = result.scalar_one()
    return portfolio_loaded

async def get_portfolio_by_id(db: AsyncSession, portfolio_id: int) -> Optional[Portfolio]:
    query = select(Portfolio).where(Portfolio.id == portfolio_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_new_job(db: AsyncSession, portfolio_id: int) -> AnalysisJob:
    job_id = str(uuid.uuid4())
    db_job = AnalysisJob(
        id=job_id,
        portfolio_id=portfolio_id,
        status="PENDING",
        created_at=datetime.utcnow()
    )
    db.add(db_job)
    await db.commit()
    
    # Reload with relationships
    query = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(query)
    return result.scalar_one()

async def update_job(
    db: AsyncSession,
    job_id: str,
    status: str,
    risk_score: Optional[float] = None,
    report_markdown: Optional[str] = None
) -> Optional[AnalysisJob]:
    query = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        logger.warning(f"Portfolio Service: AnalysisJob with ID {job_id} not found to update.")
        return None
        
    job.status = status
    if risk_score is not None:
        job.risk_score = risk_score
    if report_markdown is not None:
        job.report_markdown = report_markdown
        
    if status in ["COMPLETED", "FAILED"]:
        job.completed_at = datetime.utcnow()
        
    await db.commit()
    return job

async def get_job_by_id(db: AsyncSession, job_id: str) -> Optional[AnalysisJob]:
    query = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
