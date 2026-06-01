from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.database import Base

# ==========================================
# SQLAlchemy Models
# ==========================================

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="My Portfolio")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tickers = relationship("PortfolioTicker", back_populates="portfolio", cascade="all, delete-orphan", lazy="selectin")
    jobs = relationship("AnalysisJob", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioTicker(Base):
    __tablename__ = "portfolio_tickers"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker = Column(String, nullable=False)
    weight = Column(Float, nullable=False)  # Normalized weight (e.g. 0.25 for 25%)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="tickers")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)  # job_id (UUID or custom string)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    risk_score = Column(Float, nullable=True)
    report_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="jobs", lazy="selectin")


# ==========================================
# Pydantic Schemas
# ==========================================

class TickerInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    weight: float = Field(..., description="Portfolio weight (0.0 to 1.0 or 0 to 100)")

    @field_validator("ticker")
    @classmethod
    def clean_ticker(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Weight cannot be negative.")
        # If weights are given as percentages (e.g. 25.0 instead of 0.25), we normalize them during service logic
        return v


class PortfolioCreate(BaseModel):
    name: Optional[str] = Field("My Portfolio", description="Optional portfolio name")
    tickers: List[TickerInput] = Field(..., description="List of tickers and weights")

    @field_validator("tickers")
    @classmethod
    def check_weights(cls, tickers: List[TickerInput]) -> List[TickerInput]:
        if not tickers:
            raise ValueError("Portfolio must contain at least one ticker.")
        
        # We validate total sum of weights. We support both 0-1 range and 0-100 range.
        total_weight = sum(t.weight for t in tickers)
        
        # If they are mostly 0-1, we check if sum is ~1.0
        # If they are mostly >1, we check if sum is ~100.0
        # To make it hackathon-friendly and simple, we'll normalize them in the service.
        # But we do want to verify they are not all 0.
        if total_weight <= 0:
            raise ValueError("Total weight must be greater than zero.")
        return tickers


class TickerResponse(BaseModel):
    id: int
    ticker: str
    weight: float

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    tickers: List[TickerResponse]

    class Config:
        from_attributes = True


class AnalysisJobResponse(BaseModel):
    id: str
    portfolio_id: int
    status: str
    risk_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    report_markdown: Optional[str] = None
    portfolio: Optional[PortfolioResponse] = None

    class Config:
        from_attributes = True
