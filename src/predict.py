from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

app = FastAPI(title="No-Show Predictor API", version="1.0.0")

class PredictionRequest(BaseModel):
    patient_id: int
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
    model_name: str
    model_version: str
    prediction_timestamp: str

# Global model state
model = None
model_info = {"name": "unknown", "version": "unknown"}

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:///app/mlruns")
MODEL_NAME = os.getenv("MODEL_NAME", "noshow-prediction-model")

def load_production_model():
    """
    Dynamically load the model currently in Production stage from MLflow Registry.
    This ensures zero-downtime model replacement - when a new model is promoted,
    the next prediction will automatically use it.
    """
    global model, model_info
    
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.MlflowClient()
        
        # Get the model version in Production stage
        prod_models = client.get_latest_versions(MODEL_NAME, stages=["Production"])
        
        if not prod_models:
            print(f"⚠️ No Production model found for '{MODEL_NAME}'. Attempting 'None' stage fallback...")
            # Fallback: get latest version regardless of stage
            all_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
            if all_versions:
                latest = max(all_versions, key=lambda x: int(x.version))
                model_uri = f"models:/{MODEL_NAME}/{latest.version}"
                model = mlflow.pyfunc.load_model(model_uri)
                model_info = {"name": MODEL_NAME, "version": latest.version, "stage": "None"}
                print(f"✅ Loaded fallback model: {MODEL_NAME} v{latest.version}")
                return
            else:
                print(f"❌ No models found for '{MODEL_NAME}'")
                model_info = {"name": "none", "version": "0", "stage": "none"}
                return
        
        # Load the Production model
        prod_model = prod_models[0]
        model_uri = f"models:/{MODEL_NAME}/Production"
        
        print(f"🔄 Loading Production model: {MODEL_NAME} v{prod_model.version}")
        model = mlflow.pyfunc.load_model(model_uri)
        model_info = {
            "name": MODEL_NAME,
            "version": prod_model.version,
            "stage": "Production"
        }
        print(f"✅ Successfully loaded: {MODEL_NAME} v{prod_model.version}")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        print("🔧 Falling back to safe mode (random predictions)")
        model = None
        model_info = {"name": "fallback", "version": "0.0.0", "stage": "error"}

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting No-Show Prediction API...")
    print(f"📍 MLflow URI: {MLFLOW_TRACKING_URI}")
    print(f"🎯 Model Name: {MODEL_NAME}")
    load_production_model()

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predict no-show probability for a medical appointment.
    Automatically uses the latest Production model from MLflow.
    """
    # Reload model on each prediction to ensure latest Production model is used
    # (In high-traffic production, use a scheduled reload or cache with TTL)
    load_production_model()
    
    if not model:
        # Fallback for demo if no model is available
        return PredictionResponse(
            probability=0.5,
            is_no_show=False,
            model_name=model_info["name"],
            model_version=model_info["version"],
            prediction_timestamp=datetime.utcnow().isoformat()
        )
    
    try:
        # Feature engineering (simplified - in production, use feature store)
        from src.feature_engineering import build_features, preprocess
        
        # Create DataFrame from request
        df = pd.DataFrame([{
            'patient_id': request.patient_id,
            'gender': request.gender,
            'age': request.age,
            'scheduled_day': request.scheduled_day,
            'appointment_day': request.appointment_day,
            'neighbourhood': request.neighbourhood,
            'scholarship': int(request.scholarship),
            'hypertension': int(request.hypertension),
            'diabetes': int(request.diabetes),
            'alcoholism': int(request.alcoholism),
            'handicap': request.handicap,
            'sms_received': int(request.sms_received),
            'no_show': 0  # placeholder
        }])
        
        # Apply feature engineering
        df = preprocess(df)
        df = build_features(df)
        
        # Add missing patient history features (use defaults for new patients)
        df['rolling_no_show_rate'] = 0.2  # population average
        df['prev_appointments'] = 0
        df['gender_encoded'] = 1 if request.gender == 'M' else 0
        
        # Feature selection (must match training features)
        features = [
            'hour_block', 'day_of_week', 'is_holiday_or_weekend', 'lead_time_days',
            'same_day_appointment', 'appointment_month',
            'age', 'gender_encoded', 'scholarship', 'hypertension', 'diabetes',
            'alcoholism', 'handicap', 'sms_received',
            'rolling_no_show_rate', 'prev_appointments'
        ]
        
        X = df[features].fillna(0)
        
        # Predict using MLflow model
        prediction = model.predict(X)
        
        # Get probability if model supports it
        try:
            proba = model.predict_proba(X)[:, 1][0]
        except:
            proba = float(prediction[0])
        
        return PredictionResponse(
            probability=float(proba),
            is_no_show=bool(proba > 0.5),
            model_name=model_info["name"],
            model_version=model_info["version"],
            prediction_timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/health")
def health():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_info": model_info,
        "mlflow_uri": MLFLOW_TRACKING_URI
    }

@app.post("/reload-model")
def reload_model():
    """
    Manually trigger model reload.
    Useful after promoting a new model to Production.
    """
    try:
        load_production_model()
        return {
            "status": "success",
            "message": "Model reloaded successfully",
            "model_info": model_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")
