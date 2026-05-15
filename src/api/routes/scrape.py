import json
from typing import List
from fastapi import APIRouter, HTTPException
from src.api.schemas import EarningsReport
from src.scraper import scrape_earnings_reports

router = APIRouter()

@router.post("/reports", response_model=List[EarningsReport])
async def get_recent_reports(limit: int = 10):
    try:
        reports = scrape_earnings_reports(limit=limit)
        return [
            EarningsReport(
                company_ticker=report["ticker"],
                report_date=report["date"],
                report_type=report["period"],
                raw_data=json.dumps(report["data"])
            ) for report in reports
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
