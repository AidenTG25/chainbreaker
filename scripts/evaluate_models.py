#!/usr/bin/env python3
import argparse
import asyncio
import csv
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, precision_recall_fscore_support, roc_auc_score

from backend.ml.model_manager import ModelManager
from backend.utils.logger import setup_logger

logger = setup_logger("evaluate_models")


async def load_test_data(csv_path: str):
    from backend.ml.feature_extractor import flow_to_vector
    flows = []
    labels = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                flow = {}
                for key, val in row.items():
                    flow[key.lower().replace(".", "_")] = val
                vector = flow_to_vector(flow)
                flows.append(vector)
                labels.append(row.get("Label", "BENIGN").strip())
            except Exception:
                continue
    return np.array(flows, dtype=np.float32), labels


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--model", type=str, default="ensemble", choices=["ensemble", "rf", "xgb", "anomaly"])
    args = parser.parse_args()

    manager = ModelManager()
    manager.load_all()
    manager.set_model(args.model)

    X, y_true = await load_test_data(args.dataset)
    logger.info("test_data_loaded", samples=len(X), classes=len(set(y_true)))

    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_true)

    predictions = []
    for i in range(0, len(X), 1000):
        batch = X[i:i+1000]
        batch_flows = [{"features": row} for row in batch]
        results = manager.predict_batch(batch_flows)
        for r in results:
            predictions.append(r[0] if r[0] else "BENIGN")

    y_pred = le.transform(predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(y_encoded, y_pred, average="weighted")
    logger.info("evaluation_results", precision=precision, recall=recall, f1=f1)
    report = classification_report(y_true, predictions, output_dict=True)
    for cls, metrics in report.items():
        if isinstance(metrics, dict):
            logger.info("class_report", cls=cls, **metrics)


if __name__ == "__main__":
    asyncio.run(main())
