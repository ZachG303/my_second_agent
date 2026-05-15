from typing import List

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import InflectionInsight
from src.analysis import get_recent_inflection_insights

router = APIRouter()

@router.get("/inflection", response_model=List[InflectionInsight])
async def get_inflection_insights(
    tickers: str = Query(
        "AMKR,PLAB,ENS,PLPC,VIAV,MITK,SYNA,OSS,VPG,FIVN",
        description="Comma-separated ticker symbols to analyze",
    ),
    limit: int = Query(4, description="How many recent filers to include in the analysis"),
):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",") if ticker.strip()]
    if not ticker_list:
        raise HTTPException(status_code=400, detail="Provide at least one ticker symbol")

    insights = []
    for ticker in ticker_list:
        try:
            insights.append(get_recent_inflection_insights(ticker, limit=limit))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"{ticker}: {exc}")

    return insights
