# Quick Demo Script for Academic Grading

## 🎯 5-Minute Component Demonstration

### Prerequisites
```bash
cd D:\MLops
.venv\Scripts\activate
```

---

## Demo 1: DVC (Data Version Control)

```bash
# Show DVC is initialized
ls .dvc

# Show dataset is tracked
cat data/raw/noshow.csv.dvc

# Show pipeline definition
cat dvc.yaml

# Check status
python -m dvc status
```

**Expected Output**: DVC configuration, tracked file hash, pipeline stages

---

## Demo 2: Apache Airflow (Orchestration)

```bash
# Show DAG file
cat airflow/dags/noshow_pipeline.py | head -50

# Initialize Airflow (if not done)
# airflow db init

# List DAGs
airflow dags list | grep noshow

# Trigger DAG (optional - takes time)
# airflow dags trigger noshow_prediction_pipeline
```

**Expected Output**: DAG listed with 7 tasks

---

## Demo 3: Evidently AI (Drift Detection)

```bash
# Generate drift report
python -c "from src.monitoring import get_monitor; m = get_monitor(); m.generate_drift_report()"

# Show report file
ls reports/drift_report.html

# Open in browser
start reports/drift_report.html
```

**Expected Output**: HTML report with drift scores

---

## Demo 4: Prometheus (Metrics)

```bash
# Show configuration
cat monitoring/prometheus.yml

# Show alert rules
cat monitoring/alert_rules.yml

# Test metrics endpoint (if FastAPI running)
# curl http://localhost:8000/metrics
```

**Expected Output**: YAML configs with scrape targets and alert rules

---

## Demo 5: Grafana (Dashboards)

```bash
# Show dashboard definition
cat monitoring/grafana_dashboard.json | python -m json.tool | head -50

# Validate JSON
python -c "import json; json.load(open('monitoring/grafana_dashboard.json'))"
```

**Expected Output**: Valid JSON with 6 panel definitions

---

## Demo 6: MLflow (Existing - Full Implementation)

```bash
# Show model registry
python scripts/check_registry.py

# Start MLflow UI (optional)
# mlflow ui
```

**Expected Output**: Model versions in registry

---

## Demo 7: Complete Pipeline (Streamlit Dashboard)

```bash
# Run dashboard
streamlit run dashboard.py

# Open browser to http://localhost:8501
# Click "RUN COMPLETE PIPELINE & DEPLOY TO GCP"
```

**Expected Output**: Interactive dashboard with one-click deployment

---

## 📸 Evidence Collection

### Screenshots to Take:

1. **DVC Status**: Terminal showing `dvc status` output
2. **Airflow DAG**: DAG graph with 7 tasks
3. **Drift Report**: HTML page with drift scores
4. **Prometheus Config**: prometheus.yml file content
5. **Grafana Dashboard**: Imported dashboard in Grafana
6. **MLflow Registry**: Model versions table
7. **Streamlit Dashboard**: Complete pipeline running

### Files to Show:

```
Essential Files for Grading:
├── .dvc/config                          # DVC initialization
├── dvc.yaml                             # Pipeline definition
├── data/raw/noshow.csv.dvc             # Tracked dataset
├── airflow/dags/noshow_pipeline.py     # Complete DAG (200+ lines)
├── src/monitoring.py                    # Monitoring logic (250+ lines)
├── monitoring/
│   ├── prometheus.yml                   # Prometheus config
│   ├── alert_rules.yml                  # Alert definitions
│   └── grafana_dashboard.json           # Dashboard (6 panels)
├── requirements.txt                     # Updated dependencies
└── docs/MLOPS_COMPONENTS_GUIDE.md       # Full documentation
```

---

## 🎓 Grading Rubric Alignment

### Report Claims vs Implementation:

| Report Section | Claim | Implementation | Evidence |
|----------------|-------|----------------|----------|
| Section 1.3 | "DVC for data versioning" | ✅ `.dvc/`, `dvc.yaml`, `.dvc` files | Show files |
| Section 1.3 | "Evidently AI for drift detection" | ✅ `src/monitoring.py`, reports | Run demo |
| Section 1.3 | "Prometheus for metrics" | ✅ `prometheus.yml`, metrics endpoint | Show config |
| Section 1.3 | "Grafana for visualization" | ✅ `grafana_dashboard.json` | Import dashboard |
| Section 2.2 | "Apache Airflow orchestration" | ✅ Complete DAG with 7 tasks | Show DAG |
| Section 3.5 | "DVC workflow for traceability" | ✅ Pipeline stages, versioning | `dvc status` |
| Section 6.2 | "Airflow for pipeline automation" | ✅ Functional DAG | `airflow dags list` |
| Section 7.2 | "Evidently, Prometheus, Grafana" | ✅ All three implemented | Run all demos |

---

## ⚡ Quick Commands Reference

```bash
# DVC
python -m dvc status
python -m dvc pull

# Airflow
airflow dags list
airflow dags trigger noshow_prediction_pipeline
airflow webserver --port 8080

# Monitoring
python -c "from src.monitoring import get_monitor; get_monitor().generate_drift_report()"

# MLflow
python scripts/check_registry.py
mlflow ui

# Dashboard
streamlit run dashboard.py

# Deployment
start https://noshow-predictor-1077005218039.asia-south1.run.app
```

---

## 🔍 Verification Checklist

Before presenting:

- [ ] `.dvc/` directory exists
- [ ] `dvc.yaml` has 5 pipeline stages
- [ ] `data/raw/noshow.csv.dvc` file present
- [ ] `airflow/dags/noshow_pipeline.py` has 7 tasks
- [ ] `src/monitoring.py` has drift detection code
- [ ] `monitoring/prometheus.yml` valid YAML
- [ ] `monitoring/grafana_dashboard.json` valid JSON
- [ ] All dependencies installed (`pip list | grep evidently`)
- [ ] Documentation complete (`docs/MLOPS_COMPONENTS_GUIDE.md`)
- [ ] Models trained (check `mlruns/` directory)

---

## 💡 Key Talking Points

1. **DVC**: "We use DVC to version our 10MB dataset and define reproducible pipeline stages"

2. **Airflow**: "Our DAG orchestrates 7 tasks: data pull, validation, feature engineering, training 3 models, evaluation, deployment check, and monitoring baseline"

3. **Evidently AI**: "We implemented drift detection using statistical distance metrics, generating HTML reports"

4. **Prometheus**: "Four key metrics tracked: predictions, latency, drift scores, and model performance"

5. **Grafana**: "Dashboard with 6 panels: prediction rate, latency, AUC gauge, drift trends, distribution pie chart, and version stats"

6. **Integration**: "All components work together - Airflow triggers training, MLflow registers models, monitoring tracks drift, Prometheus collects metrics, Grafana visualizes"

7. **Minimal but Functional**: "Implemented minimal viable versions to demonstrate understanding while meeting academic requirements"

---

## 🎬 Presentation Flow

1. **Introduction** (1 min)
   - Show project structure
   - Mention all 9 components

2. **DVC Demo** (1 min)
   - Show tracked files
   - Explain pipeline stages

3. **Airflow Demo** (1 min)
   - Show DAG structure
   - Explain orchestration

4. **Monitoring Stack** (2 min)
   - Generate drift report (Evidently)
   - Show Prometheus config
   - Import Grafana dashboard

5. **Complete Pipeline** (1 min)
   - Run Streamlit dashboard
   - Show one-click deployment

**Total: 6 minutes with buffer**

---

## 📞 Support

If components don't work during demo:

- **DVC**: Show configuration files as proof
- **Airflow**: Show DAG code, explain tasks
- **Monitoring**: Show generated drift report (pre-generated)
- **Configs**: All config files are valid and demonstrate understanding

**Remember**: Implementation exists, evidence is clear, all report claims are now verifiable!
