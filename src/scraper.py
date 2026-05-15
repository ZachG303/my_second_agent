import time
import json
from datetime import datetime
from typing import Any, Dict, List

import yfinance as yf
from bs4 import BeautifulSoup


def scrape_earnings_reports(limit: int = 10) -> List[Dict[str, Any]]:
    """Scrape recent earnings reports from Yahoo Finance."""
    tickers = _get_us_stock_tickers(limit)
    reports = []

    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            earnings_dates = stock.earnings_dates
            if earnings_dates is None or earnings_dates.empty:
                continue

            latest_date = max(earnings_dates.index)
            report_data = _parse_earnings_report(ticker, latest_date)

            reports.append({
                "ticker": ticker,
                "date": latest_date.strftime("%Y-%m-%d"),
                "period": report_data["period"],
                "data": report_data["data"],
                "scraped_at": datetime.utcnow().isoformat() + "Z"
            })
            time.sleep(1.0)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    return reports


def get_report_details(ticker: str, date: str) -> Dict[str, Any]:
    """Retrieve a single report detail for a given ticker and date."""
    stock = yf.Ticker(ticker)
    earnings_dates = stock.earnings_dates
    if earnings_dates is None or earnings_dates.empty:
        raise ValueError(f"No earnings data for {ticker}")

    parsed = _parse_earnings_report(ticker, date)
    return parsed


def _get_us_stock_tickers(limit: int = 10) -> List[str]:
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "NVDA", "META", "BRK-B", "V", "JPM",
    ][:limit]


def _parse_earnings_report(ticker: str, date: Any) -> Dict[str, Any]:
    stock = yf.Ticker(ticker)
    page_content = stock.page_content
    soup = BeautifulSoup(page_content or "", "html.parser")

    metrics = {
        "eps": None,
        "revenue": None,
        "price": None,
        "pe_ratio": None,
        "beat_rate": None,
    }

    hist = stock.history(period="1mo")
    if not hist.empty:
        metrics["price"] = float(hist["Close"].iloc[-1])

    try:
        eps_value = stock.info.get("trailingEps")
        if eps_value is not None:
            metrics["eps"] = float(eps_value)
    except Exception:
        pass

    try:
        metrics["pe_ratio"] = float(stock.info.get("trailingPE", 0) or 0)
    except Exception:
        metrics["pe_ratio"] = None

    metrics["revenue"] = float(stock.info.get("totalRevenue", 0) or 0)
    metrics["beat_rate"] = 0.0

    return {
        "period": "Q1",
        "date": date if isinstance(date, str) else date.strftime("%Y-%m-%d"),
        "ticker": ticker,
        "data": metrics
    }
