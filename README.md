# Earnings Agent AI Web App

## Project Overview
This repository contains a full-stack prototype for scraping earnings data, training an ML model, and exposing results through a FastAPI backend and React frontend.

## Features
- Scrapes earnings-related metrics for US public companies using `yfinance`
- Trains a `RandomForestRegressor` on historical earnings data
- Persists ML models with `joblib`
- Provides REST endpoints via `FastAPI`
- Includes a React + TypeScript frontend dashboard
- Uses SQLite for development and PostgreSQL-ready SQLAlchemy support

## Quick Start
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```
2. Initialize the local SQLite database:
```bash
python -c "from db.init_db import init_db; init_db()"
```
3. Run the backend API:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
4. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Backend Endpoints
- `POST /scrape/reports?limit=10` — scrape recent earnings data
- `POST /train/model` — train the ML model
- `POST /train/agent-train` — invoke the LangGraph agent workflow
- `GET /reports/{ticker}/{date}` — fetch a saved report detail
- `GET /analysis/inflection?tickers=AMKR,PLAB,ENS` — analyze filings/transcripts for inflection potential

## Project Layout
```bash
.
├── app.py
├── codespace.json
├── db/
│   └── init_db.py
├── models/
│   └── .gitkeep
├── requirements.txt
├── src/
│   ├── api/
│   ├── agents/
│   ├── ml_pipeline.py
│   ├── scraper.py
│   └── utils/
└── frontend/
    ├── package.json
    ├── tsconfig.json
    └── src/
```

## Notes
- Use `.env.example` as a reference for environment configuration.
- `frontend/` is a Vite-powered React + TypeScript app.
- Add a `data/earnings_history.csv` file to train the model successfully.
