from pydantic import BaseModel
from typing import List, Optional

class EarningsReport(BaseModel):
    company_ticker: str
    report_date: str
    report_type: str
    raw_data: str

class TrainingRequest(BaseModel):
    period: str
    metric: str

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    timestamp: str

class InflectionInsight(BaseModel):
    company_ticker: str
    latest_filing_date: str | None = None
    price: float
    sales_multiple: float | None = None
    peg: float | None = None
    narrative_shift: bool
    cheap_on_sales: bool
    multi_theme_exposure: bool
    ecosystem_halo: bool
    peg_value: bool
    technical_confirmed: bool
    score: int
    theme_tags: list[str]
    highlights: list[str]
    latest_filings: list[str]
    summary: str
