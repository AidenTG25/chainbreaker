import numpy as np

from backend.ml.rf_detector import RFDetector
from backend.ml.xgb_detector import XGBDetector
from backend.ml.anomaly_detector import AnomalyDetector
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("ensemble")


class Ensemble:
    def __init__(self):
        self.rf = RFDetector()
        self.xgb = XGBDetector()
        self.if_detector = AnomalyDetector()
        self.vote_threshold = config.get("detection.ensemble_vote_threshold", 0.65)
        self.rf.load()
        self.xgb.load()
        self.if_detector.load()

    def predict(self, flow: dict) -> tuple[str | None, float, dict]:
        rf_label, rf_conf = self.rf.predict(flow)
        xgb_label, xgb_conf = self.xgb.predict(flow)
        is_anomaly, anomaly_score = self.if_detector.predict(flow)

        votes: dict[str, float] = {}
        if rf_label:
            votes[rf_label] = votes.get(rf_label, 0.0) + rf_conf * 0.4
        if xgb_label:
            votes[xgb_label] = votes.get(xgb_label, 0.0) + xgb_conf * 0.4
        if is_anomaly:
            inferred_stage = self._infer_stage_from_anomaly(flow)
            votes[inferred_stage] = votes.get(inferred_stage, 0.0) + anomaly_score * 0.2

        if not votes:
            return None, 0.0, {"rf": None, "xgb": None, "anomaly": False}

        best_label = max(votes, key=votes.get)
        combined_confidence = votes[best_label]

        if combined_confidence < self.vote_threshold:
            return None, combined_confidence, {"rf": rf_label, "xgb": xgb_label, "anomaly": is_anomaly}

        return best_label, combined_confidence, {"rf": rf_label, "xgb": xgb_label, "anomaly": is_anomaly}

    def predict_batch(self, flows: list[dict]) -> list[tuple[str | None, float, dict]]:
        rf_results = self.rf.predict_batch(flows)
        xgb_results = self.xgb.predict_batch(flows)
        if_results = self.if_detector.predict_batch(flows)

        results = []
        for rf, xgb_r, if_r in zip(rf_results, xgb_results, if_results):
            rf_label, rf_conf = rf
            xgb_label, xgb_conf = xgb_r
            is_anomaly, anomaly_score = if_r

            votes = {}
            if rf_label:
                votes[rf_label] = votes.get(rf_label, 0.0) + rf_conf * 0.4
            if xgb_label:
                votes[xgb_label] = votes.get(xgb_label, 0.0) + xgb_conf * 0.4
            if is_anomaly:
                inferred = self._infer_stage_from_anomaly({})
                votes[inferred] = votes.get(inferred, 0.0) + anomaly_score * 0.2

            if not votes:
                results.append((None, 0.0, {"rf": None, "xgb": None, "anomaly": False}))
                continue

            best_label = max(votes, key=votes.get)
            combined_confidence = votes[best_label]

            if combined_confidence < self.vote_threshold:
                results.append((None, combined_confidence, {"rf": rf_label, "xgb": xgb_label, "anomaly": is_anomaly}))
            else:
                results.append((best_label, combined_confidence, {"rf": rf_label, "xgb": xgb_label, "anomaly": is_anomaly}))

        return results

    def _infer_stage_from_anomaly(self, flow: dict) -> str:
        dst_port = flow.get("dst_port", 0)
        src_port = flow.get("src_port", 0)
        if src_port in [4444, 5555, 6666, 8080, 31337]:
            return "Command_and_Control"
        if dst_port in [22, 23, 3389]:
            return "Initial_Access"
        if dst_port == 445 or dst_port == 139:
            return "Lateral_Movement"
        return "Initial_Access"
