from fastapi import APIRouter, HTTPException
from src.api.schemas import TrainingRequest
from src.agents.agent import agent_graph
from src.ml_pipeline import train_and_save_model

router = APIRouter()

@router.post("/model")
async def train_model(request: TrainingRequest):
    try:
        result = train_and_save_model(
            period=request.period,
            metric=request.metric
        )
        return {
            "status": "success",
            "message": "Model trained and saved",
            "model_path": result.get("model_path", "models/earnings_model.pkl"),
            "metrics": {
                "mse": result.get("mse"),
                "r2": result.get("r2")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-train")
async def run_agent_training():
    try:
        result = agent_graph.invoke({}, {"configurable": {}})
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
