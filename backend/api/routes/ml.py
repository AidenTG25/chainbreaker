from fastapi import APIRouter, HTTPException

from backend.api.schemas import MLStatusResponse
from backend.ml.model_manager import ModelManager
from backend.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger("ml_routes")

_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
        _model_manager.load_all()
    return _model_manager


@router.get("/status", response_model=MLStatusResponse)
async def get_ml_status():
    manager = get_model_manager()
    return MLStatusResponse(
        models_loaded={"rf": True, "xgb": True, "anomaly": True, "ensemble": True},
        active_model=manager.active_model,
    )


@router.post("/set-model/{model_name}")
async def set_active_model(model_name: str):
    valid = ["ensemble", "rf", "xgb", "anomaly"]
    if model_name not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from {valid}")
    manager = get_model_manager()
    manager.set_model(model_name)
    return {"active_model": model_name, "status": "changed"}
