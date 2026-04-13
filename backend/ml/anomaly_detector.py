import joblib
from pathlib import Path

from backend.ml.feature_extractor import flow_to_vector
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("anomaly_detector")


class AnomalyDetector:
    def __init__(self):
        self.model = None
        self.model_path = Path(__file__).parent.parent.parent / config.get("ml.model_paths.isolation_forest", "models/if_kill_chain.pkl")
        self.score_threshold = config.get("detection.if_score_threshold", 0.15)
        self.contamination = config.get("detection.if_contamination", 0.01)

    def load(self) -> bool:
        if not self.model_path.exists():
            logger.warning("if_model_not_found", path=str(self.model_path))
            return False
        self.model = joblib.load(self.model_path)
        logger.info("if_model_loaded", path=str(self.model_path))
        return True

    def save(self, model) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)
        logger.info("if_model_saved", path=str(self.model_path))

    def predict(self, flow: dict) -> tuple[bool, float]:
        if self.model is None:
            if not self.load():
                return False, 0.0
        vector = flow_to_vector(flow)
        if vector.shape[0] != self.model.n_features_in_:
            vector = self._pad_or_trim(vector, self.model.n_features_in_)
        score = float(self.model.score_samples(vector.reshape(1, -1))[0])
        is_anomaly = score < -self.score_threshold
        return is_anomaly, abs(score)

    def predict_batch(self, flows: list[dict]) -> list[tuple[bool, float]]:
        if not flows:
            return []
        if self.model is None:
            if not self.load():
                return [(False, 0.0)] * len(flows)
        vectors = [flow_to_vector(f) for f in flows]
        n_features = self.model.n_features_in_
        import numpy as np
        X = self._pad_or_trim_batch(vectors, n_features)
        scores = self.model.score_samples(X)
        results = []
        for score in scores:
            is_anomaly = score < -self.score_threshold
            results.append((is_anomaly, abs(float(score))))
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
