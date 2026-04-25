"""
train_ml.py — Entry point for training the NIDS ML models.

Run from project root:
    python scripts/train_ml.py

Optional flags (passed through to backend.ml.train):
    --phase1  PATH          Path to phase1 CSV  [default: data/raw/phase1_NetworkData.csv]
    --phase2  PATH          Path to phase2 CSV  [default: data/raw/phase2_NetworkData.csv]
    --outdir  DIR           Model output dir    [default: models/]
    --chunksize N           Rows per chunk      [default: 200000]
    --max-rows N            Dev mode row cap    [default: 0 = all]
    --test-size FLOAT       Test split fraction [default: 0.2]
    --contamination FLOAT   IsoForest param     [default: 0.05]

Example (dev / smoke-test on 500k rows):
    python scripts/train_ml.py --max-rows 500000 --chunksize 100000
"""

import sys
import os

# Ensure project root is on the path so 'backend' is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.train import _parse_args, train_pipeline  # noqa: E402

if __name__ == "__main__":
    args = _parse_args()
    train_pipeline(
        csv_paths=[args.phase1, args.phase2],
        outdir=args.outdir,
        chunksize=args.chunksize,
        max_rows=args.max_rows,
        test_size=args.test_size,
        contamination=args.contamination,
    )
