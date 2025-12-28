# Quick GCP Deployment Commands

## Deploy Your Best Model to Production Cloud Run

### Current Status
- Local: v1 in Production (after reset)
- Cloud Run: Old/no model

### Deploy Now

```bash
# Add all changes including mlruns directory
git add .
git commit -m "feat: deploy automatic model promotion demo"
git push origin main
```

**GitHub Actions will:**
1. Build Docker image with mlruns/
2. Push to Google Artifact Registry
3. Deploy to Cloud Run (asia-south1)
4. Your model will be live in ~5-10 minutes

### Verify Deployment

```bash
# Check model version in production
curl https://ethika-rag-model-583756314894.asia-south1.run.app/model-info
```

Expected after workflow + deployment:
```json
{
  "name": "noshow-prediction-model",
  "version": "4",
  "stage": "Production",
  "loaded": true
}
```

### Alternative: Manual Deploy (Faster)

```powershell
# If GitHub Actions doesn't work
gcloud builds submit --tag asia-south1-docker.pkg.dev/ethika-rag-model/noshow/predictor:latest .

gcloud run deploy ethika-rag-model `
  --image asia-south1-docker.pkg.dev/ethika-rag-model/noshow/predictor:latest `
  --platform managed `
  --region asia-south1 `
  --allow-unauthenticated
```

---

## Important Note

After you run the workflow and v4 gets promoted locally, you need to **push to deploy to cloud**:

```bash
# 1. Run workflow locally (promotes v4)
python scripts/run_workflow.py

# 2. Deploy to GCP
git add mlruns/
git commit -m "deploy: best model v4 (AUC 93.47%)"
git push origin main
```

Then your production API will serve the best model automatically!
