import json
from pathlib import Path

from backend.ml.feature_extractor import flow_to_vector
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("xgb_detector")


class XGBDetector:
    def __init__(self):
        self.model = None
        self.model_path = Path(__file__).parent.parent.parent / config.get("ml.model_paths.xgboost", "models/xgb_kill_chain.json")
        self.confidence_threshold = config.get("detection.xgb_confidence_threshold", 0.7)

    def load(self) -> bool:
        if not self.model_path.exists():
            logger.warning("xgb_model_not_found", path=str(self.model_path))
            return False
        try:
            import xgboost as xgb
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(self.model_path))
            logger.info("xgb_model_loaded", path=str(self.model_path))
            return True
        except Exception as e:
            logger.error("xgb_load_failed", error=str(e))
            return False

    def save(self, model) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        model.save_model(str(self.model_path))
        logger.info("xgb_model_saved", path=str(self.model_path))

    def predict(self, flow: dict) -> tuple[str | None, float]:
        if self.model is None:
            if not self.load():
                return None, 0.0
        vector = flow_to_vector(flow)
        if hasattr(self.model, "n_features_in_") and vector.shape[0] != self.model.n_features_in_:
            vector = self._pad_or_trim(vector, self.model.n_features_in_)
        proba = self.model.predict_proba(vector.reshape(1, -1))[0]
        confidence = float(proba.max())
        if confidence < self.confidence_threshold:
            return None, confidence
        label_idx = int(proba.argmax())
        class_labels = config.get_section("ml").get("class_labels", {})
        label = class_labels.get(str(label_idx), str(label_idx))
        if label == "BENIGN":
            return None, confidence
        return label, confidence

    def predict_batch(self, flows: list[dict]) -> list[tuple[str | None, float]]:
        if not flows:
            return []
        vectors = [flow_to_vector(f) for f in flows]
        if self.model is None:
            if not self.load():
                return [(None, 0.0)] * len(flows)
        n_features = getattr(self.model, "n_features_in_", vectors[0].shape[0])
        import numpy as np
        X = self._pad_or_trim_batch(vectors, n_features)
        probas = self.model.predict_proba(X)
        results = []
        class_labels = config.get_section("ml").get("class_labels", {})
        for proba in probas:
            confidence = float(proba.max())
            if confidence < self.confidence_threshold:
                results.append((None, confidence))
                continue
            label_idx = int(proba.argmax())
            label = class_labels.get(str(label_idx), str(label_idx))
            if label == "BENIGN":
                results.append((None, confidence))
            else:
                results.append((label, confidence))
        return results

    def _pad_or_trim(self, vector, target_size: int):
        if len(vector) < target_size:
            import numpy as np
            return np.concatenate([vector, np.zeros(target_size - len(vector))])
        return vector[:target_size]

    def _pad_or_trim_batch(self, vectors, target_size: int):
        import numpy as np
        result = []
        for v in vectors:
            result.append(self._pad_or_trim(v, target_size))
        return np.array(result, dtype=np.float32)
