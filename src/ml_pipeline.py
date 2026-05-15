import os
from typing import Dict, Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

MODEL_PATH = os.getenv("MODEL_PATH", "./models/earnings_model.pkl")


def train_and_save_model(period: str, metric: str) -> Dict[str, Any]:
    df = _load_historical_data()
    if "period" in df.columns:
        df = df[df["period"] == period]

    if metric not in df.columns:
        raise ValueError(f"Metric '{metric}' not found in historical data")

    df = _engineer_features(df)
    if df.empty:
        raise ValueError("No data available after feature engineering")

    feature_cols = [col for col in df.columns if col not in [metric, "target"]]
    X = df[feature_cols]
    y = df[metric]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return {
        "status": "success",
        "mse": float(mse),
        "r2": float(r2),
        "model_path": MODEL_PATH,
        "features_used": feature_cols,
    }


def _load_historical_data() -> pd.DataFrame:
    if os.path.exists("data/earnings_history.csv"):
        return pd.read_csv("data/earnings_history.csv")

    raise FileNotFoundError("Historical data not found. Add data/earnings_history.csv for model training.")


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    if "price" in df.columns and "earnings_per_share" in df.columns:
        df["pe_ratio"] = df["price"] / df["earnings_per_share"].replace(0, pd.NA)
        df["eps_growth_yoy"] = df["earnings_per_share"] / df["earnings_per_share"].shift(4) - 1
        df["price_volatility"] = df["price"].rolling(5).std()
        df["eps_lag_1"] = df["earnings_per_share"].shift(1)
        df["eps_lag_2"] = df["earnings_per_share"].shift(2)
        df["target"] = df["earnings_per_share"].shift(-4)
        df = df.dropna()
    return df


def load_model() -> Any:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def predict_earnings(model: Any, features: Dict[str, float]) -> float:
    import pandas as pd
    x = pd.DataFrame([features])
    return float(model.predict(x)[0])
