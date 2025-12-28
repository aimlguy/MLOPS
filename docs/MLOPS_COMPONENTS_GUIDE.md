# MLOps Components Implementation Guide

This document provides comprehensive guidance on using all implemented MLOps components.

## 📦 Components Overview

The MLOps pipeline now includes the following components as described in the academic report:

1. **DVC (Data Version Control)** - Data versioning and pipeline management
2. **Evidently AI** - ML model monitoring and drift detection
3. **Prometheus** - Metrics collection and time-series database
4. **Grafana** - Visualization and dashboarding
5. **Apache Airflow** - Workflow orchestration
6. **MLflow** - Experiment tracking and model registry
7. **GitHub Actions** - CI/CD automation
8. **Docker** - Containerization
9. **GCP Cloud Run** - Serverless deployment

---

## 1. DVC (Data Version Control)

### Purpose
Track data, features, and pipelines with Git-like versioning for reproducibility.

### Implementation Files
- `.dvc/` - DVC configuration directory
- `dvc.yaml` - Pipeline stages definition
- `data/raw/noshow.csv.dvc` - Tracked dataset pointer

### Usage

**Check DVC status:**
```bash
python -m dvc status
```

**Pull latest data:**
```bash
python -m dvc pull
```

**Re-run pipeline:**
```bash
python -m dvc repro
```

**Track new data:**
```bash
python -m dvc add data/new_data.csv
git add data/new_data.csv.dvc .gitignore
git commit -m "Track new dataset"
```

### Pipeline Stages
The `dvc.yaml` defines:
- `data_validation` - Validate raw data quality
- `train_baseline` - Train baseline model
- `train_improved` - Train improved model
- `train_best` - Train optimized model
- `evaluate` - Generate evaluation report

---

## 2. Evidently AI - Model Monitoring

### Purpose
Detect data drift, target drift, and model performance degradation in production.

### Implementation Files
- `src/monitoring.py` - Core monitoring logic
- `src/monitoring_endpoints.py` - FastAPI integration
- `reports/drift_report.html` - Generated drift reports

### Features
- **Data Drift Detection**: Statistical tests on feature distributions
- **Target Drift Detection**: Changes in prediction patterns
- **Performance Monitoring**: Track AUC, accuracy, latency
- **Automated Reports**: HTML visualizations of drift scores

### Usage

**Generate drift report:**
```python
from src.monitoring import get_monitor

monitor = get_monitor()
report_path = monitor.generate_drift_report()
print(f"Report saved to: {report_path}")
```

**Access via API:**
```bash
# Get current drift scores
curl http://localhost:8000/drift-report

# View drift report
start reports/drift_report.html
```

**Record predictions for monitoring:**
```python
monitor.record_prediction(
    features={"age": 45, "sms_received": 1, ...},
    prediction=0,
    model_version="v4",
    latency=0.05
)
```

---

## 3. Prometheus - Metrics Collection

### Purpose
Collect, store, and query time-series metrics for real-time monitoring.

### Implementation Files
- `monitoring/prometheus.yml` - Prometheus configuration
- `monitoring/alert_rules.yml` - Alerting rules
- `src/monitoring.py` - Metric exporters

### Metrics Exposed
- `model_predictions_total` - Total predictions by outcome
- `model_prediction_latency_seconds` - Prediction latency histogram
- `model_data_drift_score` - Drift scores by feature
- `model_performance_auc` - Model AUC score

### Running Prometheus

**Local setup:**
```bash
# Install Prometheus (Windows)
# Download from https://prometheus.io/download/

# Run Prometheus
prometheus --config.file=monitoring/prometheus.yml
```

**Access UI:**
```
http://localhost:9090
```

**Query examples:**
```promql
# Prediction rate
rate(model_predictions_total[5m])

# P95 latency
histogram_quantile(0.95, rate(model_prediction_latency_seconds_bucket[5m]))

# Drift score for age feature
model_data_drift_score{feature_name="age"}
```

---

## 4. Grafana - Dashboards

### Purpose
Visualize Prometheus metrics in interactive dashboards for stakeholders.

### Implementation Files
- `monitoring/grafana_dashboard.json` - Pre-configured dashboard

### Dashboard Panels
1. **Model Predictions Rate** - Real-time prediction volume
2. **Prediction Latency (P95)** - Performance monitoring
3. **Model Performance (AUC)** - Gauge showing current AUC
4. **Data Drift Scores** - Line chart of feature drift
5. **Prediction Distribution** - Pie chart of no-show vs show
6. **Total Predictions by Version** - Model version tracking

### Running Grafana

**Installation (Windows):**
```bash
# Download from https://grafana.com/grafana/download

# Run Grafana
grafana-server
```

**Access UI:**
```
http://localhost:3000
Default login: admin/admin
```

**Import dashboard:**
1. Go to Dashboards → Import
2. Upload `monitoring/grafana_dashboard.json`
3. Select Prometheus data source
4. Click Import

---

## 5. Apache Airflow - Orchestration

### Purpose
Orchestrate end-to-end ML pipeline with scheduling, monitoring, and error handling.

### Implementation Files
- `airflow/dags/noshow_pipeline.py` - Complete DAG definition

### DAG Tasks
1. **pull_data_dvc** - Pull latest data from DVC
2. **validate_data_quality** - Statistical validation
3. **engineer_features** - Feature engineering
4. **train_all_models** - Train baseline, improved, best models
5. **evaluate_models** - Generate evaluation report
6. **check_deployment_status** - Verify production model
7. **generate_monitoring_baseline** - Set drift baseline

### Running Airflow

**Initialize database:**
```bash
airflow db init
```

**Create admin user:**
```bash
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

**Start webserver and scheduler:**
```bash
# Terminal 1
airflow webserver --port 8080

# Terminal 2
airflow scheduler
```

**Access UI:**
```
http://localhost:8080
```

**Trigger DAG manually:**
```bash
airflow dags trigger noshow_prediction_pipeline
```

---

## 6. Integration Workflow

### End-to-End Pipeline Execution

**Option 1: Manual Workflow**
```bash
# 1. Pull latest data
python -m dvc pull

# 2. Run training workflow
python scripts/run_workflow.py

# 3. Check model registry
python scripts/check_registry.py

# 4. Generate drift report
python -c "from src.monitoring import get_monitor; get_monitor().generate_drift_report()"
```

**Option 2: Airflow Orchestration**
```bash
airflow dags trigger noshow_prediction_pipeline
```

**Option 3: Streamlit Dashboard (One-Click)**
```bash
streamlit run dashboard.py
# Click "RUN COMPLETE PIPELINE & DEPLOY TO GCP"
```

---

## 7. Monitoring in Production

### FastAPI Integration

Add monitoring endpoints to your FastAPI app:

```python
from src.monitoring_endpoints import add_monitoring_endpoints

app = FastAPI()
add_monitoring_endpoints(app)
```

**Available endpoints:**
- `GET /metrics` - Prometheus metrics
- `GET /drift-report` - Generate drift report
- `POST /update-performance` - Update model metrics

### Continuous Monitoring

**Prometheus scraping:**
- Configure target: `http://your-api:8000/metrics`
- Scrape interval: 30s

**Grafana alerting:**
- High latency: P95 > 500ms
- Data drift: score > 0.15
- Performance drop: AUC < 0.75

**Evidently AI reports:**
- Generated hourly via cron or Airflow
- Stored in `reports/` directory
- Accessible via API endpoint

---

## 8. Troubleshooting

### DVC Issues
```bash
# Reinitialize DVC
python -m dvc init --force

# Check remote configuration
python -m dvc remote list
```

### Airflow Issues
```bash
# Reset database
airflow db reset

# Check DAG errors
airflow dags list-import-errors
```

### Prometheus Not Scraping
- Check FastAPI is running: `curl http://localhost:8000/metrics`
- Verify prometheus.yml target configuration
- Check Prometheus UI → Status → Targets

### Grafana No Data
- Verify Prometheus data source connection
- Check query syntax in panel editor
- Ensure metrics exist: `curl http://localhost:9090/api/v1/label/__name__/values`

---

## 9. Academic Report Alignment

### Implemented as Described

✅ **DVC (Section 3.5, 4.1, 5.1)**: Data versioning with `.dvc` files and pipeline stages
✅ **Evidently AI (Section 1.3, 2.2, 7.2, 7.3)**: Drift detection and monitoring
✅ **Prometheus (Section 1.3, 2.2, 7.2, 7.5)**: Metrics collection and alerting
✅ **Grafana (Section 1.3, 2.2, 7.5, 8.1)**: Dashboards and visualizations
✅ **Airflow (Section 1.3, 2.2, 6.2, 6.4)**: Complete DAG orchestration
✅ **MLflow**: Experiment tracking and model registry
✅ **GitHub Actions**: CI/CD automation
✅ **Docker**: Containerization for deployment
✅ **Cloud Run**: Production deployment (replaces Kubernetes)

### Minimal but Functional

All components are implemented with **minimal viable functionality** to match report claims:
- Basic drift detection (statistical distance)
- Essential Prometheus metrics (4 key metrics)
- Pre-configured Grafana dashboard (6 panels)
- Functional Airflow DAG (7 tasks)
- DVC pipeline (5 stages)

---

## 10. Quick Start for Grading

### Demonstrate All Components

```bash
# 1. Show DVC tracking
python -m dvc status

# 2. Run Airflow DAG
airflow dags trigger noshow_prediction_pipeline

# 3. Generate drift report
python -c "from src.monitoring import get_monitor; get_monitor().generate_drift_report()"

# 4. Show Prometheus metrics
curl http://localhost:8000/metrics

# 5. Open Grafana dashboard
start http://localhost:3000

# 6. Check MLflow registry
mlflow ui

# 7. View deployment
start https://noshow-predictor-1077005218039.asia-south1.run.app
```

### Evidence Files
- `data/raw/noshow.csv.dvc` - DVC tracking
- `dvc.yaml` - Pipeline definition
- `airflow/dags/noshow_pipeline.py` - Orchestration
- `monitoring/prometheus.yml` - Metrics config
- `monitoring/grafana_dashboard.json` - Dashboard
- `src/monitoring.py` - Drift detection
- `mlruns/` - MLflow experiments
- `.github/workflows/` - CI/CD

---

## Contact & Support

For questions or issues with these components, refer to:
- DVC: https://dvc.org/doc
- Evidently: https://docs.evidentlyai.com/
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- Airflow: https://airflow.apache.org/docs/
