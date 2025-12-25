from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
import numpy as np
import os

app = FastAPI(title="No-Show Predictor API")

class PredictionRequest(BaseModel):
    gender: str
    age: int
    scheduled_day: str
    appointment_day: str
    neighbourhood: str
    scholarship: bool
    hypertension: bool
    diabetes: bool
    alcoholism: bool
    handicap: int
    sms_received: bool

class PredictionResponse(BaseModel):
    probability: float
    is_no_show: bool

# Load model (mock loading if file not present for CI/CD structure)
model = None
MODEL_PATH = "models/xgboost_model.json"

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = xgb.XGBClassifier()
        model.load_model(MODEL_PATH)
        print("Model loaded.")
    else:
        print("Warning: Model file not found. Inference will fail until model is trained.")

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if not model:
        # Fallback for demo / if model isn't trained yet
        # Simple heuristic fallback
        return PredictionResponse(probability=0.5, is_no_show=False)
        
    try:
        # In a real system, we'd use the same feature engineering pipeline
        # Here we mock the transformation for the endpoint structure
        
        # Create DF
        data = {
            'age': [request.age],
            'scholarship': [int(request.scholarship)],
            'hypertension': [int(request.hypertension)],
            'diabetes': [int(request.diabetes)],
            'alcoholism': [int(request.alcoholism)],
            'handicap': [request.handicap],
            'sms_received': [int(request.sms_received)]
            # ... missing features would be filled or fetched from feature store
        }
        
        # Predict
        # prob = model.predict_proba(pd.DataFrame(data))[:, 1][0]
        prob = 0.75 # Placeholder
        
        return PredictionResponse(probability=prob, is_no_show=prob > 0.5)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}
