# No-Show Prediction MLOps Pipeline

This repository contains a production-grade MLOps pipeline for predicting medical appointment no-shows.

## Architecture
- **Data Versioning**: DVC (S3 remote)
- **Validation**: Great Expectations
- **Modeling**: XGBoost
- **Tracking**: MLflow
- **Orchestration**: Apache Airflow
- **Serving**: FastAPI + Docker

## Structure
- `src/`: Python source code for data processing and modeling.
- `airflow/`: Airflow DAGs.
- `docker/`: Dockerfiles for serving.
- `client/`: React Dashboard for monitoring.
- `server/`: Node.js Control Plane.

## Usage

### Training
```bash
python src/train.py
```

### Serving
```bash
uvicorn src.predict:app --host 0.0.0.0 --port 8000
```

### Airflow
Ensure Airflow is running and drop the DAGs in the dags folder.
