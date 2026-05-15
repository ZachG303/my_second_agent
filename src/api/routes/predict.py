from datetime import datetime
from typing import Any, Dict

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import PredictionResponse
from src.ml_pipeline import load_model, predict_earnings

router = APIRouter()


def _build_default_features(ticker: str) -> Dict[str, float]:
    features = {
        "price": 0.0,
        "earnings_per_share": 0.0,
        "pe_ratio": 0.0,
        "revenue": 0.0,
    }

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if not hist.empty:
            features["price"] = float(hist["Close"].iloc[-1])

        info = getattr(stock, "info", {}) or {}
        features["earnings_per_share"] = float(info.get("trailingEps", 0.0) or 0.0)
        features["pe_ratio"] = float(info.get("trailingPE", 0.0) or 0.0)
        features["revenue"] = float(info.get("totalRevenue", 0.0) or 0.0)
    except Exception as exc:
        print(f"Prediction feature build failed for {ticker}: {exc}")

    return features


@router.get("", response_model=PredictionResponse)
async def get_prediction(
    ticker: str,
    date: str,
    metric: str = Query("eps", description="Metric to predict")
):
    features = _build_default_features(ticker)
    prediction = features.get("earnings_per_share", 0.0)

    try:
        model = load_model()
        prediction = predict_earnings(model, features)
    except FileNotFoundError:
        print("No trained model found, using EPS baseline for prediction.")
    except Exception as exc:
        print(f"Prediction model load/predict failed: {exc}")

    return PredictionResponse(
        prediction=float(prediction),
        confidence=0.65,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
