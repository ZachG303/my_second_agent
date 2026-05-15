import json
from fastapi import APIRouter, HTTPException
from src.api.schemas import EarningsReport
from src.scraper import get_report_details
from src.utils.clear_output import clear_output

router = APIRouter()

@router.get("/{ticker}/{date}", response_model=EarningsReport)
async def get_report(ticker: str, date: str):
    try:
        report = get_report_details(ticker, date)
        return EarningsReport(
            company_ticker=ticker,
            report_date=date,
            report_type=report.get("period", "unknown"),
            raw_data=json.dumps(clear_output(report.get("data", {})))
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
