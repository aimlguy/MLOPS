# MLOps Pipeline - Academic Guide

## 🎯 Project Overview

This project demonstrates a **complete end-to-end MLOps pipeline** that automatically improves model performance through continuous training and metrics-based deployment decisions.

### Core Concept

The pipeline trains three progressively better models:
1. **Baseline** (poor) → Logistic Regression with 6 features
2. **Improved** (better) → Random Forest with 16 features
3. **Best** (optimal) → Tuned XGBoost with 16 features

Each new model **automatically replaces** the previous one in production if it achieves better ROC-AUC scores.

## 🏆 Learning Objectives

By completing this project, you will demonstrate:

### 1. Machine Learning Fundamentals
- ✅ Feature engineering impact on model performance
- ✅ Algorithm selection (Linear → Ensemble → Gradient Boosting)
- ✅ Hyperparameter tuning techniques
- ✅ Model evaluation metrics (ROC-AUC, Accuracy, F1)

### 2. MLOps Practices
- ✅ Model versioning and registry (MLflow)
- ✅ Automated model promotion based on metrics
- ✅ Experiment tracking and comparison
- ✅ Model serving (FastAPI)

### 3. Software Engineering
- ✅ Containerization (Docker)
- ✅ CI/CD pipelines (GitHub Actions)
- ✅ Cloud deployment (GCP Cloud Run)
- ✅ API design and testing

### 4. Production Deployment
- ✅ Zero-downtime model updates
- ✅ Health checks and monitoring
- ✅ Rollback capabilities
- ✅ Serverless architecture

## 📚 Step-by-Step Guide

### Phase 1: Local Development (1-2 hours)

#### Step 1: Environment Setup

```bash
# Clone repository
git clone <your-repo>
cd MLops

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Train Models Locally

```bash
# Train all three models in sequence
python scripts/run_workflow.py

# This will:
# 1. Train baseline (Logistic Regression)
# 2. Train improved (Random Forest)
# 3. Train best (XGBoost)
# 4. Generate evaluation report
```

**Expected Output:**
```
STEP 1: Training Baseline Model
   ROC-AUC:  0.6234
   Promoted to Production ✅

STEP 2: Training Improved Model
   ROC-AUC:  0.7156
   Auto-replaced baseline ✅

STEP 3: Training Best Model
   ROC-AUC:  0.7891
   Auto-replaced improved ✅

STEP 4: Evaluating All Models
   Reports generated in reports/ ✅
```

#### Step 3: Review Results

```bash
# Start MLflow UI
mlflow ui --port 5000

# Open browser to http://localhost:5000
# Navigate to:
# - Experiments → "noshow-prediction"
# - Compare the 3 runs
# - Check "Models" tab for Production model
```

```bash
# View evaluation report
start reports/evaluation_report.md  # Windows
open reports/evaluation_report.md   # Mac
xdg-open reports/evaluation_report.md  # Linux

# View visualizations
start reports/model_comparison.png
start reports/auc_progression.png
start reports/features_vs_auc.png
```

### Phase 2: API Testing (30 mins)

#### Step 4: Test API Locally

```bash
# Start FastAPI server
uvicorn src.predict:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, test endpoints
```

**Test Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "model_version": "v1"}
```

**Test Prediction:**
```bash
curl -X POST http://localhost:8000/predict \
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

# Expected: {"prediction": 0, "probability": 0.23, "model_version": "v3"}
```

**Test Model Reload:**
```bash
curl http://localhost:8000/reload-model
# Expected: {"message": "Model reloaded", "version": "v3"}
```

### Phase 3: Cloud Deployment (1-2 hours)

#### Step 5: Setup GCP Project

```bash
# Install gcloud CLI (if not already)
# https://cloud.google.com/sdk/docs/install

# Login to GCP
gcloud auth login

# Set project
gcloud config set project ethika-rag-model

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### Step 6: Create Artifact Registry

```bash
# Create repository for Docker images
gcloud artifacts repositories create noshow-models \
  --repository-format=docker \
  --location=asia-south1 \
  --description="No-show prediction models"

# Configure Docker authentication
gcloud auth configure-docker asia-south1-docker.pkg.dev
```

#### Step 7: Setup GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

1. **GCP_PROJECT_ID**
   ```
   ethika-rag-model
   ```

2. **GCP_SA_KEY**
   ```bash
   # Create service account
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions"

   # Grant permissions
   gcloud projects add-iam-policy-binding ethika-rag-model \
     --member="serviceAccount:github-actions@ethika-rag-model.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding ethika-rag-model \
     --member="serviceAccount:github-actions@ethika-rag-model.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"

   # Create key
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@ethika-rag-model.iam.gserviceaccount.com

   # Copy contents of key.json and paste as GCP_SA_KEY secret
   cat key.json
   ```

3. **GCP_SERVICE_ACCOUNT_EMAIL**
   ```
   github-actions@ethika-rag-model.iam.gserviceaccount.com
   ```

#### Step 8: Deploy to Cloud Run

```bash
# Commit and push to trigger deployment
git add .
git commit -m "Deploy to Cloud Run"
git push origin main

# GitHub Actions will:
# 1. Run tests (ci.yml)
# 2. Build Docker image
# 3. Push to Artifact Registry
# 4. Deploy to Cloud Run in Mumbai (asia-south1)
```

Monitor deployment:
- Go to GitHub → Actions tab
- Watch "Deploy to GCP Cloud Run" workflow
- Should complete in ~5 minutes

#### Step 9: Test Production API

```bash
# Get Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe noshow-prediction \
  --region=asia-south1 --format='value(status.url)')

echo $CLOUD_RUN_URL

# Test production endpoint
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
```

### Phase 4: Demonstrate Auto-Promotion (30 mins)

#### Step 10: Train New Model

```bash
# Make a small change to improve model
# Edit src/train_best.py - increase n_estimators to 300

# Train new version
python src/train_best.py --auto-promote

# Check if it auto-promotes
# Expected: "✅ BEST MODEL PROMOTED! New Production version: v4"
```

#### Step 11: Reload Production Model

```bash
# Trigger model reload on Cloud Run
curl $CLOUD_RUN_URL/reload-model

# Expected: {"message": "Model reloaded", "version": "v4"}

# Verify new model is serving
curl -X POST $CLOUD_RUN_URL/predict \
  -H "Content-Type: application/json" \
  -d '{ ... }'

# Check model version in response
```

## 📊 Evaluation Criteria

When presenting this project, highlight:

### 1. Technical Implementation (40%)
- ✅ Three working models with progressive improvement
- ✅ Automated promotion logic based on metrics
- ✅ Proper MLflow integration
- ✅ Production-ready API
- ✅ Docker containerization

### 2. Cloud Deployment (25%)
- ✅ Successful Cloud Run deployment
- ✅ GitHub Actions CI/CD
- ✅ Mumbai region deployment
- ✅ Working production endpoints

### 3. Documentation (20%)
- ✅ Clear README with instructions
- ✅ Evaluation report with visualizations
- ✅ Code comments and docstrings
- ✅ Academic guide (this document)

### 4. Demonstration (15%)
- ✅ Show model training workflow
- ✅ Demonstrate auto-promotion
- ✅ Test API endpoints
- ✅ Explain architecture decisions

## 🎤 Presentation Tips

### Opening (2 mins)
"This project demonstrates an end-to-end MLOps pipeline that automatically improves model performance. I trained three models with progressively better algorithms and feature engineering. The system automatically promotes the best model to production based on ROC-AUC metrics."

### Demo Flow (5-7 mins)

1. **Show Repository Structure**
   - Point out `src/train_*.py` files
   - Explain `src/model_registry.py` auto-promotion logic
   - Show GitHub Actions workflows

2. **Run Training Workflow**
   ```bash
   python scripts/run_workflow.py
   ```
   - Show real-time output
   - Highlight auto-promotion messages
   - Point out metric improvements

3. **Show MLflow UI**
   - Open http://localhost:5000
   - Compare the three runs
   - Show Production model in registry
   - Explain metrics progression

4. **Show Evaluation Report**
   - Open `reports/evaluation_report.md`
   - Walk through visualizations
   - Highlight performance improvements

5. **Test Production API**
   - Show Cloud Run service in GCP console
   - Test `/predict` endpoint
   - Demonstrate `/reload-model` capability

### Key Points to Emphasize

✅ **Automation**: "No manual intervention needed - models auto-promote"  
✅ **Metrics-Driven**: "Decisions based on quantitative comparison"  
✅ **Production-Ready**: "Deployed on GCP Cloud Run with zero downtime"  
✅ **Reproducible**: "Complete workflow in one command"  
✅ **Industry-Standard**: "MLflow, Docker, CI/CD - real-world tools"  

### Q&A Preparation

**Q: Why did you choose these three models?**
A: "I wanted to demonstrate progression: simple linear model → ensemble method → gradient boosting. This shows how algorithm sophistication impacts performance while keeping feature sets comparable."

**Q: How does auto-promotion work?**
A: "The `ModelRegistry` class compares new model's AUC against current Production. If higher, it archives the old version and promotes the new one. This ensures only improvements reach production."

**Q: What if a new model performs worse?**
A: "It won't be promoted. The old model stays in Production. We can also manually rollback to any previous version through MLflow."

**Q: How does the API update without downtime?**
A: "Cloud Run's serverless architecture handles this. The `/reload-model` endpoint fetches the latest Production model from MLflow. Old requests complete before switching."

**Q: Why Mumbai region?**
A: "Academic requirement specified asia-south1. Also demonstrates region selection in deployment configuration."

## 🐛 Common Issues & Solutions

### Issue 1: MLflow Tracking URI Error

**Error:**
```
No such file or directory: './mlruns'
```

**Solution:**
```bash
# Create mlruns directory
mkdir mlruns

# Or set tracking URI explicitly
export MLFLOW_TRACKING_URI=./mlruns
```

### Issue 2: Model Not Found in Registry

**Error:**
```
Model 'noshow_predictor' not found
```

**Solution:**
```bash
# Ensure at least one model is trained
python src/train_baseline.py --auto-promote

# Check MLflow UI
mlflow ui --port 5000
# Verify model appears in "Models" tab
```

### Issue 3: Docker Build Fails

**Error:**
```
COPY models/ models/ ERROR: not found
```

**Solution:**
Already fixed in current Dockerfile. Models loaded from MLflow at runtime, not copied during build.

### Issue 4: Cloud Run Deployment Fails

**Error:**
```
Permission denied: Cloud Run Admin
```

**Solution:**
```bash
# Grant service account Cloud Run Admin role
gcloud projects add-iam-policy-binding ethika-rag-model \
  --member="serviceAccount:github-actions@ethika-rag-model.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

### Issue 5: API Returns 500 Error

**Error:**
```
{"detail": "Model not loaded"}
```

**Solution:**
```bash
# Ensure MLflow tracking URI is set in Cloud Run
gcloud run services update noshow-prediction \
  --region=asia-south1 \
  --update-env-vars MLFLOW_TRACKING_URI=./mlruns

# Or check logs
gcloud run services logs read noshow-prediction --region=asia-south1
```

## 📈 Extension Ideas

Want to go beyond the basic implementation?

### Advanced Features
1. **A/B Testing**: Deploy multiple models and split traffic
2. **Model Monitoring**: Track prediction distribution drift
3. **Automated Retraining**: Trigger training on schedule or data drift
4. **Feature Store**: Centralize feature engineering
5. **Model Explainability**: Add SHAP values to predictions

### Infrastructure Improvements
1. **Kubernetes Deployment**: Use GKE instead of Cloud Run
2. **Load Testing**: Add locust tests for performance
3. **Cost Optimization**: Implement request batching
4. **Multi-Region**: Deploy to multiple regions for HA
5. **Secrets Management**: Use Google Secret Manager

### ML Enhancements
1. **Ensemble Models**: Combine all three models
2. **Online Learning**: Update model with new data
3. **Bayesian Optimization**: Advanced hyperparameter tuning
4. **AutoML**: Automate model selection
5. **Deep Learning**: Try neural networks

## 🎓 Academic Submission Checklist

Before submitting:

- [ ] All three models train successfully
- [ ] Auto-promotion works (test with `--auto-promote`)
- [ ] Evaluation report generated
- [ ] MLflow UI accessible
- [ ] API works locally (`uvicorn src.predict:app`)
- [ ] Docker builds successfully
- [ ] Cloud Run deployment successful
- [ ] Production API responds to requests
- [ ] README.md complete with clear instructions
- [ ] Code commented and clean
- [ ] GitHub repository organized
- [ ] All secrets configured in GitHub
- [ ] Demo rehearsed (5-7 minutes)

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review error messages in terminal
3. Check GitHub Actions logs
4. Review Cloud Run logs: `gcloud run services logs read noshow-prediction --region=asia-south1`
5. Open an issue in the repository

## 🎉 Conclusion

You've built a complete MLOps pipeline! This project demonstrates:

- ✅ End-to-end ML development
- ✅ Automated model improvement
- ✅ Production deployment
- ✅ CI/CD integration
- ✅ Cloud-native architecture

**Time Investment:**
- Setup: 1 hour
- Development: 4-6 hours
- Deployment: 1-2 hours
- Testing: 1 hour
- Documentation: 2 hours
- **Total: ~10-12 hours**

**Skills Gained:**
- Python ML development
- MLflow experiment tracking
- Docker containerization
- GCP Cloud Run
- GitHub Actions CI/CD
- API development with FastAPI
- Model versioning and promotion
- Production deployment strategies

Good luck with your presentation! 🚀

---

*Last Updated: 2024-12-25*  
*Repository: MLops - No-Show Prediction Pipeline*
