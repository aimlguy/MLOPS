# 🔧 Setup Guide: Trigger Pipeline & Cloud Backend

## Issues to Fix:

### 1. ❌ Trigger Pipeline Button Not Working
**Problem:** Button doesn't trigger GitHub Actions  
**Root Cause:** Missing GITHUB_TOKEN environment variable

### 2. ❌ Cloud Backend Using Fallback Model  
**Problem:** Cloud Run API returns 0.5 probability (fallback)  
**Root Cause:** MLflow models (mlruns/) not included in Docker image

### 3. ❌ Frontend Not Connected to Cloud  
**Problem:** Frontend calls localhost, not Cloud Run  
**Solution:** Need to configure backend URL

---

## 🚀 Quick Fixes

### Fix 1: Enable GitHub Actions Trigger

#### Step 1: Create GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `MLOps Pipeline Trigger`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

#### Step 2: Set Environment Variable
```powershell
# Windows PowerShell (temporary - current session only)
$env:GITHUB_TOKEN="your_token_here"

# OR add to .env file for persistence
```

#### Step 3: Create .env File
```bash
# Create .env in project root
GITHUB_TOKEN=ghp_your_token_here_xxxxxxxxxxxxx
GITHUB_REPOSITORY=aimlguy/MLOPS
PORT=5000
```

#### Step 4: Restart Server
```powershell
# Stop current server (Ctrl+C)
# Restart with:
npm run dev
```

#### Step 5: Test Trigger Button
1. Open http://localhost:5000
2. Click "Trigger Pipeline"
3. Check GitHub Actions: https://github.com/aimlguy/MLOPS/actions
4. Should see workflow running!

---

### Fix 2: Deploy Cloud Backend with MLflow Models

#### Updated Dockerfile.api
```dockerfile
# ✅ NOW INCLUDES mlruns/
COPY mlruns/ ./mlruns/
```

#### Deploy Command
```powershell
# From D:\MLops directory
gcloud run deploy noshow-prediction-api `
  --source . `
  --platform managed `
  --region asia-south1 `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 4 `
  --timeout 300 `
  --max-instances 10
```

**Expected:** 
- Build time: 3-5 minutes
- Model will load from mlruns/
- /health will show `"model_loaded": true`
- Predictions will use XGBoost (AUC 0.9347)

---

### Fix 3: Connect Frontend to Cloud Backend

#### Option A: Environment Variable (Recommended)
```bash
# Create .env in project root
VITE_API_URL=https://noshow-prediction-api-865778656829.asia-south1.run.app
```

#### Option B: Update vite.config.ts
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://noshow-prediction-api-865778656829.asia-south1.run.app',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

#### Option C: Direct API Calls (Quick Test)
Update `client/src/hooks/use-predictions.ts`:
```typescript
const API_URL = 'https://noshow-prediction-api-865778656829.asia-south1.run.app';

export function usePredict() {
  return useMutation({
    mutationFn: async (data: PredictionInput) => {
      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      // ...
    }
  });
}
```

---

## 🧪 Testing Everything

### Test 1: Cloud Backend Health
```powershell
curl https://noshow-prediction-api-865778656829.asia-south1.run.app/health
```

**Expected:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_info": {
    "name": "noshow-prediction-model",
    "version": "8",
    "stage": "Production"
  }
}
```

### Test 2: Cloud Backend Prediction
```powershell
$body = @{
  patient_id = 12345
  gender = "F"
  age = 35
  scheduled_day = "2024-04-15T10:30:00"
  appointment_day = "2024-04-20T14:00:00"
  neighbourhood = "JARDIM CAMBURI"
  scholarship = $false
  hypertension = $false
  diabetes = $false
  alcoholism = $false
  handicap = 0
  sms_received = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://noshow-prediction-api-865778656829.asia-south1.run.app/predict" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

**Expected:**
```json
{
  "probability": 0.23,
  "is_no_show": false,
  "model_name": "noshow-prediction-model",
  "model_version": "8"
}
```

### Test 3: GitHub Actions Trigger
```powershell
# With GITHUB_TOKEN set
curl -X POST http://localhost:5000/api/pipeline/trigger
```

**Expected Response:**
```json
{
  "message": "Pipeline triggered successfully via GitHub Actions",
  "runId": "run-1736105234567",
  "workflow": "model-training.yml"
}
```

**Check GitHub:**
https://github.com/aimlguy/MLOPS/actions

---

## 📋 Complete Setup Checklist

### Backend (Cloud Run)
- [ ] Update Dockerfile.api to include mlruns/
- [ ] Deploy to Cloud Run (5 min)
- [ ] Test /health endpoint (model_loaded: true)
- [ ] Test /predict endpoint (real predictions)

### Frontend Connection
- [ ] Choose connection method (env var recommended)
- [ ] Update configuration
- [ ] Restart dev server
- [ ] Test prediction from UI

### GitHub Actions
- [ ] Create GitHub Personal Access Token
- [ ] Add to .env file or environment
- [ ] Restart local server
- [ ] Test trigger button
- [ ] Verify workflow runs on GitHub

---

## 🎯 Expected Final State

### Local Development
```
Browser → http://localhost:5000
   ↓
React Frontend
   ↓
Cloud Run API (https://...asia-south1.run.app)
   ↓
Production XGBoost Model (AUC 0.9347)
```

### Trigger Pipeline Flow
```
Dashboard Button → Local Express → GitHub API
   ↓
GitHub Actions Workflow Triggered
   ↓
model-training.yml runs:
   - Train baseline
   - Train improved
   - Train best
   - Auto-promote
   ↓
See execution: github.com/aimlguy/MLOPS/actions
```

---

## 🚨 Troubleshooting

### Issue: Deployment taking too long
**Solution:** mlruns/ is large (50+ MB). Cloud Build might timeout.
```powershell
# Check Cloud Build logs
gcloud builds list --limit=5
```

### Issue: Model still not loading
**Check Dockerfile includes:**
```dockerfile
COPY mlruns/ ./mlruns/
```

**Check logs:**
```powershell
gcloud run logs read noshow-prediction-api --region asia-south1 --limit 50
```

### Issue: GitHub Actions not triggering
**Check:**
1. GITHUB_TOKEN set: `echo $env:GITHUB_TOKEN`
2. Token has workflow permission
3. Repository name correct: aimlguy/MLOPS

### Issue: Frontend can't reach Cloud Run
**Check CORS:**
Cloud Run should allow all origins (currently configured)

**Test directly:**
```powershell
curl https://noshow-prediction-api-865778656829.asia-south1.run.app/health
```

---

## 📞 Quick Commands Reference

```powershell
# Deploy Cloud Run
gcloud run deploy noshow-prediction-api --source . --region asia-south1

# Check deployment
gcloud run services describe noshow-prediction-api --region asia-south1

# View logs
gcloud run logs read noshow-prediction-api --region asia-south1 --limit 50

# Test health
curl https://noshow-prediction-api-865778656829.asia-south1.run.app/health

# Start local dev
npm run dev

# Check GitHub token
echo $env:GITHUB_TOKEN

# Trigger pipeline
curl -X POST http://localhost:5000/api/pipeline/trigger
```

---

**Next Steps:**
1. Set up GITHUB_TOKEN first (5 min)
2. Deploy Cloud Run with mlruns/ (5 min build)
3. Connect frontend to cloud backend (2 min)
4. Test everything (5 min)

**Total Time:** ~20 minutes for complete setup
