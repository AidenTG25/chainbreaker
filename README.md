# ChainBreaker 🛡️

Graph-driven Cyber Incident Detection and Automated Kill Chain Interruption Platform.

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/ChainBreaker.git
cd ChainBreaker

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Infrastructure
Ensure Docker is running, then start the stack (Kafka, Neo4j):
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. Initialize & Run
```bash
# Initialize Neo4j schema
python scripts/init_neo4j.py

# Start Backend (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Start Frontend (React)
cd frontend && npm install && npm run dev
```

## 📂 Project Structure

- `backend/`: FastAPI application, ML models, and Neo4j logic.
- `frontend/`: React-based security dashboard.
- `docker/`: Container configurations (Kafka, Neo4j, Nginx).
- `data/`: Data storage.
  - `data/raw/`: Large datasets (ignored by Git).
  - `data/sample/`: Test-sized datasets (included).
- `scripts/`: Data ingestion, training, and utility scripts.
- `dev/`: Workspace for experimentation and research.

## 🤝 Contributing

1. **Feature Branches**: Create a new branch for each feature or bugfix.
2. **Environment**: Copy `.env.example` to `.env` and configure your credentials.
3. **Data**: Use `data/sample/` for local development and testing.

## 🛠️ Tech Stack
- **Engine**: Python 3.10+
- **Graph**: Neo4j
- **Streaming**: Apache Kafka
- **API**: FastAPI
- **Frontend**: Vite / React
