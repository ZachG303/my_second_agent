from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import analysis, scrape, train, report, predict

app = FastAPI(title="Earnings Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["root"])
async def root():
    return {"status": "ok", "message": "Earnings Agent API is running"}

app.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
app.include_router(train.router, prefix="/train", tags=["train"])
app.include_router(report.router, prefix="/reports", tags=["reports"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
