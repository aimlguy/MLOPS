import xgboost as xgb
import pandas as pd
import joblib
import mlflow
import mlflow.xgboost
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from sklearn.preprocessing import LabelEncoder
from src.feature_engineering import load_data, preprocess, build_features, engineer_patient_history

def train_model(data_path: str, model_path: str = "models/xgboost_model.json"):
    mlflow.set_experiment("noshow-prediction")
    
    with mlflow.start_run():
        # Load & Process
        print("Loading data...")
        df = load_data(data_path)
        df = preprocess(df)
        df = build_features(df)
        df = engineer_patient_history(df)
        
        # Encoders
        le_gender = LabelEncoder()
        df['gender_encoded'] = le_gender.fit_transform(df['gender'])
        
        # Feature Selection
        features = [
            'hour_block', 'day_of_week', 'is_holiday_or_weekend', 'lead_time_days', 
            'same_day_appointment', 'appointment_month',
            'age', 'gender_encoded', 'scholarship', 'hypertension', 'diabetes', 
            'alcoholism', 'handicap', 'sms_received',
            'rolling_no_show_rate', 'prev_appointments'
        ]
        
        X = df[features].fillna(0)
        y = df['no_show']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train
        ratio = (y_train == 0).sum() / (y_train == 1).sum()
        params = {
            "n_estimators": 300,
            "max_depth": 6,
            "learning_rate": 0.1,
            "scale_pos_weight": ratio,
            "eval_metric": "auc"
        }
        
        mlflow.log_params(params)
        
        print("Training XGBoost...")
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)
        
        # Evaluate
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, probs)
        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        
        print(f"Metrics: AUC={auc:.4f}, Accuracy={acc:.4f}, F1={f1:.4f}")
        
        mlflow.log_metrics({"auc": auc, "accuracy": acc, "f1": f1})
        mlflow.xgboost.log_model(model, "model")
        
        # Save local artifact
        model.save_model(model_path)
        print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model("data/raw/noshow.csv")
