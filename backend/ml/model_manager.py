import joblib
from pathlib import Path
from typing import Literal

from backend.ml.ensemble import Ensemble
from backend.ml.rf_detector import RFDetector
from backend.ml.xgb_detector import XGBDetector
from backend.ml.anomaly_detector import AnomalyDetector
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("model_manager")


class ModelManager:
    def __init__(self):
        self.ensemble = Ensemble()
        self.active_model: Literal["ensemble", "rf", "xgb", "anomaly"] = "ensemble"
        self.rf = RFDetector()
        self.xgb = XGBDetector()
        self.anomaly = AnomalyDetector()

    def set_model(self, model_name: Literal["ensemble", "rf", "xgb", "anomaly"]) -> None:
        self.active_model = model_name
        logger.info("active_model_changed", model=model_name)

    def predict(self, flow: dict):
        if self.active_model == "rf":
            return self.rf.predict(flow)
        elif self.active_model == "xgb":
            return self.xgb.predict(flow)
        elif self.active_model == "anomaly":
            label, score = self.anomaly.predict(flow)
            return (label, score) if label else (None, score)
        else:
            return self.ensemble.predict(flow)

    def predict_batch(self, flows: list[dict]):
        if self.active_model == "rf":
            return self.rf.predict_batch(flows)
        elif self.active_model == "xgb":
            return self.xgb.predict_batch(flows)
        elif self.active_model == "anomaly":
            results = self.anomaly.predict_batch(flows)
            return [(l, s) if l else (None, s) for l, s in results]
        else:
            return self.ensemble.predict_batch(flows)

    def load_all(self) -> dict[str, bool]:
        status = {}
        status["rf"] = self.rf.load()
        status["xgb"] = self.xgb.load()
        status["anomaly"] = self.anomaly.load()
        logger.info("all_models_loaded", status=status)
        return status

    def save_all(self, rf_model, xgb_model, if_model) -> None:
        self.rf.save(rf_model)
        self.xgb.save(xgb_model)
        self.anomaly.save(if_model)
        logger.info("all_models_saved")
