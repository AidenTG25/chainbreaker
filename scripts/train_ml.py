#!/usr/bin/env python3
import argparse
import asyncio
import csv
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

import xgboost as xgb
from pyod.models.iforest import IsolationForest

from backend.ingestion.cicflow_parser import parse_network_flow_row, normalize_column_name
from backend.ml.feature_extractor import flow_to_vector
from backend.ml.model_manager import ModelManager
from backend.utils.config import config
from backend.utils.logger import setup_logger

logger = setup_logger("train_ml")


def load_dataset(csv_path: str, max_samples: int = 50000) -> tuple[list, list]:
    flows = []
    labels = []
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        normalized_cols = {col: normalize_column_name(col) for col in columns}
        for i, row in enumerate(reader):
            if i >= max_samples:
                break
            try:
                flow = parse_network_flow_row(row)
                vector = flow_to_vector(flow)
                flows.append(vector)
                label = flow.get("label", row.get("label", "BENIGN"))
                if not label:
                    label = row.get("label", "BENIGN")
                labels.append(str(label).strip())
            except Exception:
                continue
    logger.info("dataset_loaded", path=csv_path, samples=len(flows), labels=len(labels))
    return flows, labels


def load_combined_datasets(csv_paths: list[str], max_per_file: int = 25000) -> tuple[list, list]:
    all_flows = []
    all_labels = []
    for csv_path in csv_paths:
        flows, labels = load_dataset(csv_path, max_per_file)
        all_flows.extend(flows)
        all_labels.extend(labels)
        logger.info("file_loaded", path=csv_path, flows=len(flows))
    return all_flows, all_labels


def get_dataset_files(data_dir: Path) -> list[Path]:
    patterns = ["*phase1*.csv", "*phase2*.csv"]
    files = []
    for pattern in patterns:
        files.extend(data_dir.glob(pattern))
    return sorted(set(files))


async def train_random_forest(X_train, y_train, label_encoder):
    logger.info("training_random_forest")
    rf_params = config.get_section("ml").get("random_forest", {})
    model = RandomForestClassifier(
        n_estimators=rf_params.get("n_estimators", 200),
        max_depth=rf_params.get("max_depth", 20),
        min_samples_split=rf_params.get("min_samples_split", 5),
        min_samples_leaf=rf_params.get("min_samples_leaf", 2),
        max_features=rf_params.get("max_features", "sqrt"),
        bootstrap=rf_params.get("bootstrap", True),
        n_jobs=rf_params.get("n_jobs", -1),
        random_state=42,
    )
    model.fit(X_train, y_train)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="f1_weighted")
    logger.info("rf_cv_scores", scores=cv_scores.tolist(), mean=float(cv_scores.mean()))
    manager = ModelManager()
    manager.rf.save(model)
    return model


async def train_xgboost(X_train, y_train):
    logger.info("training_xgboost")
    xgb_params = config.get_section("ml").get("xgboost", {})
    n_classes = len(np.unique(y_train))
    model = xgb.XGBClassifier(
        n_estimators=xgb_params.get("n_estimators", 200),
        max_depth=xgb_params.get("max_depth", 8),
        learning_rate=xgb_params.get("learning_rate", 0.1),
        subsample=xgb_params.get("subsample", 0.8),
        colsample_bytree=xgb_params.get("colsample_bytree", 0.8),
        objective=xgb_params.get("objective", "multi:softprob"),
        eval_metric=xgb_params.get("eval_metric", "mlogloss"),
        num_class=n_classes,
        n_jobs=xgb_params.get("n_jobs", -1),
        random_state=42,
        use_label_encoder=False,
    )
    model.fit(X_train, y_train)
    manager = ModelManager()
    manager.xgb.save(model)
    return model


async def train_isolation_forest(X_train):
    logger.info("training_isolation_forest")
    if_params = config.get_section("ml").get("isolation_forest", {})
    model = IsolationForest(
        n_estimators=if_params.get("n_estimators", 200),
        max_samples=if_params.get("max_samples", "auto"),
        contamination=if_params.get("contamination", 0.01),
        max_features=if_params.get("max_features", 1.0),
        bootstrap=if_params.get("bootstrap", False),
        n_jobs=if_params.get("n_jobs", -1),
        random_state=42,
    )
    model.fit(X_train)
    manager = ModelManager()
    manager.anomaly.save(model)
    return model


async def evaluate_models(rf_model, xgb_model, X_test, y_test, label_encoder):
    for name, model in [("Random Forest", rf_model), ("XGBoost", xgb_model)]:
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
        logger.info(f"{name}_report", metrics=report)


async def main():
    parser = argparse.ArgumentParser(description="Train ML models for ChainBreaker")
    parser.add_argument("--dataset", type=str, nargs="+", help="Path(s) to CICAPT CSV files")
    parser.add_argument("--max-samples", type=int, default=50000, help="Max samples per file")
    parser.add_argument("--skip-xgb", action="store_true", help="Skip XGBoost training")
    parser.add_argument("--skip-if", action="store_true", help="Skip Isolation Forest training")
    args = parser.parse_args()

    if args.dataset:
        csv_paths = args.dataset
    else:
        data_dir = Path(__file__).parent.parent / "data" / "raw"
        csv_paths = [str(f) for f in get_dataset_files(data_dir)]

    if not csv_paths:
        logger.error("no_datasets_found")
        return

    logger.info("loading_datasets", paths=csv_paths)
    X, y = load_combined_datasets(csv_paths, args.max_samples)
    logger.info("datasets_loaded", total_samples=len(X))
    if not X:
        logger.error("no_data_loaded")
        return

    X = np.array(X, dtype=np.float32)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    if X.size == 0:
        logger.error("empty_features_array")
        return

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    logger.info("classes", classes=list(label_encoder.classes_))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    logger.info("data_split", train=len(X_train), test=len(X_test))

    rf_model = await train_random_forest(X_train, y_train, label_encoder)
    if not args.skip_xgb:
        xgb_model = await train_xgboost(X_train, y_train)
    if not args.skip_if:
        if_model = await train_isolation_forest(X_train)

    await evaluate_models(rf_model, xgb_model if not args.skip_xgb else None, X_test, y_test, label_encoder)
    logger.info("training_complete")


if __name__ == "__main__":
    asyncio.run(main())