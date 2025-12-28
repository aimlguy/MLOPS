# Deployment Verification Commands

## Check Deployment Status

Run these commands to verify your Cloud Run deployment:

### 1. Check if service exists
```powershell
gcloud run services list --region us-central1
```

### 2. Get service URL
```powershell
$serviceUrl = (gcloud run services describe noshow-prediction-api --region us-central1 --format="value(status.url)")
Write-Host "Service URL: $serviceUrl"
```

### 3. Test health endpoint
```powershell
$serviceUrl = (gcloud run services describe noshow-prediction-api --region us-central1 --format="value(status.url)")
Invoke-RestMethod -Uri "$serviceUrl/health" | ConvertTo-Json
```

### 4. View service logs
```powershell
gcloud run services logs read noshow-prediction-api --region us-central1 --limit 50
```

### 5. Check GitHub Actions workflow status
```powershell
Start-Process "https://github.com/discount-Pieter-Levels/MLops/actions"
```

## Expected Results

### Successful Deployment
- Service URL available (https://noshow-prediction-api-*.a.run.app)
- Health endpoint returns 200 OK
- Response includes model_info

### Example Health Response
```json
{
  "status": "healthy",
  "model_loaded": false,
  "model_info": {
    "name": "noshow-prediction-model",
    "version": "0",
    "stage": "None"
  },
  "mlflow_uri": "file:///app/mlruns"
}
```

## Troubleshooting

### If deployment fails:
1. Check GitHub Actions logs for errors
2. Verify all 3 GitHub secrets are configured correctly
3. Check Cloud Run logs: `gcloud run services logs read noshow-prediction-api --region us-central1`

### If service is slow to respond:
- First requests can take 10-30 seconds (cold start)
- Subsequent requests will be faster

## After Successful Deployment

Once verified, proceed to train models:
```powershell
# This will be done in the next step
python src/train_baseline.py --auto-promote
```
