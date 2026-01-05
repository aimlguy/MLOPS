# Progressive Model Deployment Pipeline

This system implements a **progressive model training and deployment pipeline** where models are trained incrementally and deployed only if they improve performance.

## Architecture

### Pipeline Stages
1. **Baseline** (worst model) - Logistic Regression + Random Forest
2. **Improved** - Enhanced feature engineering
3. **Best** - XGBoost with hyperparameter tuning

### Workflow

```
START → Deploy Baseline (worst)
   ↓
   → Click "Trigger Pipeline"
   ↓
   → Train Improved
   ↓
   → If AUC > Current? 
      ├─ YES → Build Docker → Deploy → Update State
      └─ NO → Skip deployment
   ↓
   → Click "Trigger Pipeline"
   ↓
   → Train Best
   ↓
   → If AUC > Current?
      ├─ YES → Build Docker → Deploy → Update State
      └─ NO → Skip deployment
   ↓
   → Click "Reset Pipeline" → Back to Baseline
```

## Components

### Backend (`server/routes.ts`)
- `GET /api/pipeline/state` - Get current pipeline state
- `POST /api/pipeline/trigger` - Trigger next model training
- `POST /api/pipeline/reset` - Reset to baseline

### State Management (`src/pipeline_state.py`)
- Tracks current deployed model stage
- Records deployment history
- Determines next model to train
- Validates if new model should deploy

### Training Script (`src/train_progressive.py`)
- Trains specific model stage on demand
- Returns metrics in JSON format
- Supports auto-promotion

### GitHub Actions (`.github/workflows/progressive-training.yml`)
- Trains specified model stage
- Builds Docker image if better
- Deploys container locally
- Updates pipeline state

## Usage

### 1. Start with Baseline
```bash
# Initial deployment (baseline model)
python src/train_progressive.py --stage baseline
docker build -f Dockerfile.api -t noshow-api:baseline .
docker run -d --name noshow-api -p 8080:8080 noshow-api:baseline
```

### 2. Trigger Progressive Training
**Frontend:** Click "Trigger Pipeline" button

**Backend Process:**
1. Check current stage (baseline)
2. Determine next stage (improved)
3. Trigger GitHub Actions with stage=improved
4. GitHub Actions trains improved model
5. If AUC > baseline_AUC:
   - Build Docker image
   - Deploy container
   - Update state
6. Otherwise: Skip deployment

### 3. Continue Training
Click "Trigger Pipeline" again to train best model

### 4. Reset Pipeline
Click "Reset Pipeline" to go back to baseline

## State File (`pipeline_state.json`)
```json
{
  "current_stage": "improved",
  "current_model_auc": 0.7088,
  "deployment_history": [
    {"stage": "baseline", "auc": 0.6554, "timestamp": "..."},
    {"stage": "improved", "auc": 0.7088, "timestamp": "..."}
  ],
  "last_updated": "2026-01-05T..."
}
```

## Docker Deployment

### Local Docker
```bash
# Build
docker build -f Dockerfile.api -t noshow-api:latest .

# Run
docker run -d \
  --name noshow-api \
  -p 8080:8080 \
  -v $(pwd)/mlruns:/app/mlruns \
  noshow-api:latest

# Check logs
docker logs noshow-api

# Stop
docker stop noshow-api && docker rm noshow-api
```

### Model Versioning
Each stage creates a tagged Docker image:
- `noshow-api:baseline`
- `noshow-api:improved`
- `noshow-api:best`

## Key Features

✅ **Progressive Training** - One model at a time  
✅ **Automatic Comparison** - Only deploys if better  
✅ **Docker Containerization** - Each model in container  
✅ **State Persistence** - Tracks deployment history  
✅ **Reset Capability** - Return to baseline anytime  
✅ **GitHub Actions Integration** - Automated workflow  

## API Responses

### Trigger Pipeline
```json
{
  "message": "Training improved model via GitHub Actions",
  "runId": "run-1767636136463",
  "workflow": "progressive-training.yml",
  "stage": "improved",
  "current_stage": "baseline"
}
```

### Pipeline State
```json
{
  "current_stage": "baseline",
  "current_model_auc": 0.6554,
  "next_stage": "improved",
  "can_progress": true,
  "deployment_history": [...],
  "last_updated": "2026-01-05T..."
}
```

### Reset
```json
{
  "message": "Pipeline reset to baseline model",
  "current_stage": "baseline",
  "next_stage": "improved"
}
```

## Testing

```bash
# Get state
curl http://localhost:5000/api/pipeline/state

# Trigger
curl -X POST http://localhost:5000/api/pipeline/trigger

# Reset
curl -X POST http://localhost:5000/api/pipeline/reset

# Check Docker
docker ps
docker logs noshow-api
```
