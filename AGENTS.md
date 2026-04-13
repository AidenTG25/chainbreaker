# Agent Commands

## Development

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run tests
```bash
pytest tests/ -v
```

### Start backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### Start frontend
```bash
cd frontend && npm install && npm run dev
```

### Initialize Neo4j (auto-detects phase1_NetworkData.csv and phase2_NetworkData.csv)
```bash
python scripts/init_neo4j.py
```

### Train ML models (processes both phase1 and phase2 datasets automatically)
```bash
python scripts/train_ml.py
```

### Run offline processor (processes both phase1 and phase2 datasets)
```bash
python scripts/offline_processor.py
```

### Train RL agent (Major phase)
```bash
python scripts/train_rl.py --mode train
```

### Docker
```bash
docker compose -f docker/docker-compose.yml up -d
```

## Environment Variables
Copy `.env.example` to `.env` and configure.