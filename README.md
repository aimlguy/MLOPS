# No-Show Prediction MLOps Pipeline

> **Production MLOps System**: End-to-end ML pipeline deployed on GCP Cloud Run

[![Deployed on Cloud Run](https://img.shields.io/badge/Deployed-Cloud%20Run-blue?logo=google-cloud)](https://noshow-prediction-api-865778656829.asia-south1.run.app)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-green.svg)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.1+-orange.svg)](https://xgboost.readthedocs.io/)

**Live API**: https://noshow-prediction-api-865778656829.asia-south1.run.app

A complete MLOps pipeline that predicts medical appointment no-shows using machine learning. The system demonstrates progressive model improvement (Baseline → Improved → Best) with automatic training, versioning, and cloud deployment.

## 🚀 Quick Start

### Test the Live API

```bash
# Health check
curl https://noshow-prediction-api-865778656829.asia-south1.run.app/health

# Make a prediction
curl -X POST https://noshow-prediction-api-865778656829.asia-south1.run.app/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 12345,
    "gender": "F",
    "age": 35,
    "scheduled_day": "2024-04-15T10:30:00",
    "appointment_day": "2024-04-20T14:00:00",
    "neighbourhood": "JARDIM CAMBURI",
    "scholarship": false,
    "hypertension": false,
    "diabetes": false,
    "alcoholism": false,
    "handicap": 0,
    "sms_received": true
  }'
```

### Run Locally

```bash
# Clone repository
git clone <repository-url>
cd MLops

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run training pipeline
dvc repro

# Start local server
npm run dev  # Full stack (Frontend + Backend)
# OR
python -m uvicorn src.predict:app --reload  # API only
```

## 🎯 Key Features

- **Automatic Model Promotion**: Models automatically replace inferior versions based on ROC-AUC
- **Progressive Improvement**: Demonstrates baseline → improved → best model progression
- **Zero-Downtime Deployment**: Models update without service interruption
- **Cloud-Native**: Deployed on GCP Cloud Run (Mumbai region)
- **CI/CD Integration**: GitHub Actions for automated testing and deployment

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Pipeline  │
│  (Airflow DAG)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Model Training  │─────▶│   MLflow     │
│  (3 versions)   │      │   Registry   │
└────────┬────────┘      └──────┬───────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────┐      ┌──────────────┐
│ Auto-Promotion  │─────▶│  Production  │
│  (Metrics-Based)│      │    Model     │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Cloud Run   │
                         │   (Mumbai)   │
                         └──────────────┘
```

## 📊 Model Progression

| Model | Algorithm | Features | Expected AUC | Purpose |
|-------|-----------|----------|--------------|---------|
| **Baseline** | Logistic Regression | 6 basic | ~0.60-0.65 | Simple starting point |
| **Improved** | Random Forest | 16 engineered | ~0.70-0.75 | Show improvement |
| **Best** | XGBoost (tuned) | 16 comprehensive | ~0.78-0.82 | Optimal performance |

## 🚀 Quick Start

### 1. Download Dataset

Download the Kaggle No-Show Appointments dataset:
- Dataset: [No Show Appointments](https://www.kaggle.com/datasets/joniarroba/noshowappointments)
- File: `KaggleV2-May-2016.csv`
- Place in: `data/raw/noshow.csv`

```bash
# Using Kaggle CLI (recommended)
kaggle datasets download -d joniarroba/noshowappointments
unzip noshowappointments.zip
mv KaggleV2-May-2016.csv data/raw/noshow.csv

# Or download manually from Kaggle website
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Complete Workflow

```bash
# Train all 3 models and generate evaluation report
python scripts/run_workflow.py
```

This will:
- Train baseline model (Logistic Regression) → Promote to Production
- Train improved model (Random Forest) → Auto-replace baseline
- Train best model (XGBoost) → Auto-replace improved
- Generate comprehensive evaluation report with visualizations

### 3. Individual Model Training

```bash
# Train models individually
python src/train_baseline.py --auto-promote
python src/train_improved.py --auto-promote
python src/train_best.py --auto-promote

# Evaluate and compare
python src/evaluate.py
```

### 4. View Results

```bash
# Start MLflow UI
mlflow ui --port 5000

# Open browser to http://localhost:5000
# Check reports/ directory for visualizations
```

## 📁 Project Structure

```
.
├── src/
│   ├── train_baseline.py      # Baseline model (Logistic Regression)
│   ├── train_improved.py      # Improved model (Random Forest)
│   ├── train_best.py          # Best model (XGBoost)
│   ├── evaluate.py            # Model comparison & reporting
│   ├── predict.py             # FastAPI inference service
│   ├── model_registry.py      # Auto-promotion logic
│   └── feature_engineering.py # Feature pipeline
├── scripts/
│   └── run_workflow.py        # Complete workflow runner
├── docker/
│   └── Dockerfile             # Production container
├── .github/workflows/
│   ├── ci.yml                 # Testing pipeline
│   ├── deploy-gcp.yml         # Cloud Run deployment
│   └── model-promotion.yml    # Model promotion workflow
├── reports/                   # Generated evaluation reports
├── data/raw/                  # Training data
└── airflow/dags/             # Orchestration workflows
```

## 🌐 Cloud Deployment

### Prerequisites

```bash
# Set GCP project
gcloud config set project ethika-rag-model

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Deploy to Cloud Run (Mumbai)

```bash
# Push to main branch triggers deployment
git add .
git commit -m "Deploy new model"
git push origin main

# GitHub Actions will:
# 1. Run tests
# 2. Build Docker image
# 3. Push to Artifact Registry
# 4. Deploy to Cloud Run in asia-south1 (Mumbai)
```

### Test Production API

```bash
# Get Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe noshow-prediction \
  --region=asia-south1 --format='value(status.url)')

# Test prediction
curl -X POST $CLOUD_RUN_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "gender": "F",
    "scholarship": 0,
    "hypertension": 0,
    "diabetes": 0,
    "alcoholism": 0,
    "handicap": 0,
    "sms_received": 1,
    "scheduled_day": "2024-01-15T10:00:00",
    "appointment_day": "2024-01-20T14:30:00"
  }'

# Reload model (fetch latest from MLflow)
curl $CLOUD_RUN_URL/reload-model

# Health check
curl $CLOUD_RUN_URL/health
```

## 📈 Monitoring & Evaluation

### View Model Metrics

```bash
# Start MLflow UI
mlflow ui --port 5000

# Navigate to:
# - Experiments → "noshow-prediction"
# - Compare runs
# - Check "Models" tab for Production model
```

### Generated Reports

After running `python src/evaluate.py`, check `reports/` directory:
- `evaluation_report.md` - Comprehensive comparison
- `model_comparison.png` - Metrics bar chart
- `auc_progression.png` - Performance improvement over time
- `features_vs_auc.png` - Feature engineering impact

## 🎓 Academic Value

This project demonstrates:

1. **End-to-End ML Pipeline**: From data to production
2. **Automated Model Selection**: Metrics-driven promotion
3. **CI/CD for ML**: GitHub Actions integration
4. **Cloud Deployment**: Serverless architecture
5. **MLOps Best Practices**: Versioning, monitoring, rollback

### Key Learning Outcomes

- ✅ Feature engineering impact on performance
- ✅ Algorithm selection and hyperparameter tuning
- ✅ Automated promotion workflows
- ✅ Model registry and versioning
- ✅ Production deployment strategies

## 🛠️ Technologies

- **ML/DS**: Python 3.11, scikit-learn, XGBoost, pandas
- **Tracking**: MLflow
- **Serving**: FastAPI, uvicorn
- **Containerization**: Docker
- **Cloud**: GCP Cloud Run, Artifact Registry
- **CI/CD**: GitHub Actions
- **Orchestration**: Apache Airflow
- **Frontend**: React, TypeScript, Vite

## 📝 Usage Examples

### Training Individual Models

```python
# Train baseline
from src.train_baseline import train_baseline_model
run_id, metrics = train_baseline_model("data/raw/noshow.csv", auto_promote=True)
print(f"Baseline AUC: {metrics['auc']:.4f}")

# Train improved
from src.train_improved import train_improved_model
run_id, metrics = train_improved_model("data/raw/noshow.csv", auto_promote=True)
print(f"Improved AUC: {metrics['auc']:.4f}")

# Train best
from src.train_best import train_best_model
run_id, metrics = train_best_model("data/raw/noshow.csv", auto_promote=True)
print(f"Best AUC: {metrics['auc']:.4f}")
```

### Manual Model Promotion

```python
from src.model_registry import ModelRegistry

registry = ModelRegistry()

# Promote specific run to production
registry.promote_to_production(run_id="abc123", model_name="noshow_predictor")

# Auto-promote if better
promoted_version = registry.auto_promote_if_better(
    run_id="def456",
    metric_name="auc",
    higher_is_better=True
)
```

## 🐛 Troubleshooting

### MLflow Errors

```bash
# Reset MLflow tracking
rm -rf mlruns/
mlflow server --backend-store-uri ./mlruns --default-artifact-root ./mlruns
```

### Cloud Run Issues

```bash
# Check logs
gcloud run services logs read noshow-prediction-api \
  --region=asia-south1 --limit=50

# View service details
gcloud run services describe noshow-prediction-api --region=asia-south1

# Redeploy
gcloud run deploy noshow-prediction-api \
  --source . \
  --platform managed \
  --region asia-south1
```

## 🌐 Production Deployment

**Live Service**: https://noshow-prediction-api-865778656829.asia-south1.run.app

- **Platform**: Google Cloud Run (asia-south1 - Mumbai)
- **Memory**: 4GB
- **CPU**: 4 cores
- **Timeout**: 300 seconds
- **Max Instances**: 10 (auto-scaling)
- **Authentication**: Public (unauthenticated)

### Endpoints

- `GET /health` - Health check
- `POST /api/predict` - Prediction endpoint
- `GET /api/monitoring/status` - System status
- `GET /api/metrics` - Prometheus metrics

## 📚 Additional Resources

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions Guide](https://docs.github.com/actions)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [DVC Documentation](https://dvc.org/doc)

## 🤝 Contributing

This is a production MLOps system. For questions or suggestions:
1. Open an issue
2. Submit a pull request
3. Contact the maintainers

## 📄 License

MIT License - See LICENSE file for details

---

**Deployed on GCP Cloud Run**  
*Production-ready MLOps pipeline with automatic model training and versioning*

**Live API**: https://noshow-prediction-api-865778656829.asia-south1.run.app
