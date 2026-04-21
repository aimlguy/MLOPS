"""Test local prediction with MLflow model"""
import mlflow
import pandas as pd
from datetime import datetime

print("\n" + "="*60)
print("TESTING LOCAL PREDICTION WITH PRODUCTION MODEL")
print("="*60 + "\n")

# Load production model
model_uri = "models:/noshow-prediction-model/Production"
print(f"Loading model: {model_uri}")
model = mlflow.pyfunc.load_model(model_uri)
print("✓ Model loaded successfully\n")

# Create sample prediction data
sample_data = pd.DataFrame([{
    "patient_id": 12345,
    "gender": "F",
    "age": 35,
    "scheduled_day": "2024-04-15T10:30:00",
    "appointment_day": "2024-04-20T14:00:00",
    "neighbourhood": "JARDIM CAMBURI",
    "scholarship": False,
    "hypertension": False,
    "diabetes": False,
    "alcoholism": False,
    "handicap": 0,
    "sms_received": True
}])

print("Sample input:")
print(sample_data.T)
print()

# Make prediction
try:
    prediction = model.predict(sample_data)
    print(f"Prediction: {prediction}")
    print(f"Probability: {prediction[0]:.4f}")
    print(f"Classification: {'No-Show' if prediction[0] > 0.5 else 'Will Attend'}")
    print("\n✓ Local prediction successful!")
except Exception as e:
    print(f"✗ Prediction failed: {e}")

print("="*60 + "\n")
