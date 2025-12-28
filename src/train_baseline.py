"""
Baseline Model Training Script - Logistic Regression + Random Forest

This uses the WORST model pattern with minimal features.
Dataset: Kaggle No-Show Appointments (KaggleV2-May-2016.csv)
Purpose: Establish a weak baseline to demonstrate improvement.
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
from src.model_registry import ModelRegistry
import warnings
warnings.filterwarnings('ignore')


def train_baseline_model(data_path: str, auto_promote: bool = False):
    """
    Train baseline Logistic Regression and Random Forest models.
    Uses MINIMAL feature engineering - just basic features.
    """
    print("\n" + "="*60)
    print("TRAINING BASELINE MODELS (Logistic Regression + RF)")
    print("="*60 + "\n")
    
    mlflow.set_experiment("noshow-prediction")
    
    with mlflow.start_run(run_name="baseline_logistic_rf") as run:
        print(">> Loading and preprocessing data...")
        
        # Load Kaggle dataset
        df = pd.read_csv(data_path)
        df = df.rename(columns={'Hipertension': 'Hypertension', 'Handcap': 'Handicap'})
        df['NoShow'] = (df['No-show'] == 'Yes').astype(int)
        
        df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay']).dt.tz_localize(None)
        df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay']).dt.tz_localize(None)
        
        # Basic cleaning
        df = df[(df['Age'] >= 0) & (df['Age'] <= 100)]
        df = df.sort_values('AppointmentDay').reset_index(drop=True)
        
        print(">> Building BASIC features (minimal engineering)...")
        
        # Basic time features
        df['WaitDays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
        df['SameDay'] = (df['WaitDays'] == 0).astype(int)
        df['LongWait'] = (df['WaitDays'] > 14).astype(int)
        df['AppointmentHour'] = df['AppointmentDay'].dt.hour
        df['IsMorning'] = (df['AppointmentHour'] < 12).astype(int)
        df['DayOfWeek'] = df['AppointmentDay'].dt.dayofweek
        df['IsWeekend'] = df['DayOfWeek'].isin([5,6]).astype(int)
        
        # Patient history
        df['PastNoShows'] = df.groupby('PatientId')['NoShow'].cumsum() - df['NoShow']
        df['TotalAppts'] = df.groupby('PatientId').cumcount()
        df['PastNoShowRate'] = np.where(
            df['TotalAppts'] > 0,
            df['PastNoShows'] / df['TotalAppts'],
            df['NoShow'].mean()
        )
        
        # Neighborhood risk
        neigh_risk = df.groupby('Neighbourhood')['NoShow'].mean()
        df['NeighRisk'] = df['Neighbourhood'].map(neigh_risk)
        
        # Age groups
        df['AgeGroup'] = pd.cut(df['Age'], bins=[-1,18,35,55,200], labels=[0,1,2,3]).astype(int)
        
        # Simple interactions
        df['SMS_x_LongWait'] = df['SMS_received'] * df['LongWait']
        df['NoScholarship_x_LongWait'] = (1 - df['Scholarship']) * df['LongWait']
        df['Age_x_Wait'] = df['AgeGroup'] * df['WaitDays']
        
        df['Gender'] = df['Gender'].map({'M': 0, 'F': 1})
        
        # MINIMAL FEATURE SET
        features = [
            'AgeGroup', 'Scholarship', 'Hypertension', 'Diabetes', 'Alcoholism', 'Handicap',
            'SMS_received', 'WaitDays', 'SameDay', 'LongWait', 'IsMorning', 'IsWeekend',
            'PastNoShowRate', 'TotalAppts', 'NeighRisk',
            'SMS_x_LongWait', 'NoScholarship_x_LongWait', 'Age_x_Wait', 'Gender'
        ]
        
        X = df[features].fillna(0).values
        y = df['NoShow'].values
        
        # Time-based split (more realistic)
        train_idx = df['AppointmentDay'] < '2016-05-01'
        test_idx = ~train_idx
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        print(f"   Training samples: {X_train.shape[0]}")
        print(f"   Test samples: {X_test.shape[0]}")
        print(f"   Train no-show rate: {y_train.mean():.2%}")
        print(f"   Test no-show rate: {y_test.mean():.2%}")
        print(f"   Features: {len(features)} (minimal)")
        
        # Scale for Logistic Regression
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print("\n>> Training Logistic Regression...")
        lr_model = LogisticRegression(max_iter=1000, class_weight='balanced', C=0.5)
        lr_model.fit(X_train_scaled, y_train)
        lr_pred_proba = lr_model.predict_proba(X_test_scaled)[:, 1]
        lr_pred = lr_model.predict(X_test_scaled)
        lr_auc = roc_auc_score(y_test, lr_pred_proba)
        lr_acc = accuracy_score(y_test, lr_pred)
        lr_f1 = f1_score(y_test, lr_pred)
        
        print(f"   Logistic Regression - AUC: {lr_auc:.4f}, Acc: {lr_acc:.4f}, F1: {lr_f1:.4f}")
        
        print("\n>> Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=600, max_depth=15, min_samples_leaf=3,
            class_weight='balanced_subsample', random_state=42, n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_pred_proba = rf_model.predict_proba(X_test)[:, 1]
        rf_pred = rf_model.predict(X_test)
        rf_auc = roc_auc_score(y_test, rf_pred_proba)
        rf_acc = accuracy_score(y_test, rf_pred)
        rf_f1 = f1_score(y_test, rf_pred)
        
        print(f"   Random Forest - AUC: {rf_auc:.4f}, Acc: {rf_acc:.4f}, F1: {rf_f1:.4f}")
        
        # Use best model (RF typically better)
        auc = rf_auc
        accuracy = rf_acc
        f1 = rf_f1
        
        print(f"\n   >> BASELINE METRICS (Expected to be moderate):")
        print(f"   Best ROC-AUC:  {auc:.4f}")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1 Score: {f1:.4f}")
        
        # Log metrics
        mlflow.log_params({
            'model_type': 'baseline',
            'num_features': len(features),
            'feature_engineering': 'basic',
            'algorithm': 'random_forest'
        })
        mlflow.log_metrics({'auc': auc, 'accuracy': accuracy, 'f1': f1})
        
        # Log best model (RF)
        mlflow.sklearn.log_model(rf_model, 'model')
        
        run_id = run.info.run_id
        print(f"\n   MLflow Run ID: {run_id}")
        
        # Auto-promote if requested
        if auto_promote:
            print("\n>> Attempting auto-promotion...")
            registry = ModelRegistry()
            promoted_version = registry.auto_promote_if_better(
                run_id=run_id,
                metric_name='auc',
                higher_is_better=True
            )
            
            if promoted_version:
                print(f"\n>> BASELINE MODEL PROMOTED!")
                print(f"   Production version: v{promoted_version}")
            else:
                print("\n>> Promotion failed")
        
        print("\n" + "="*60)
        print("BASELINE TRAINING COMPLETE")
        print("="*60 + "\n")
        
        return run_id, {'auc': auc, 'accuracy': accuracy, 'f1': f1}


if __name__ == '__main__':
    import sys
    auto_promote = '--auto-promote' in sys.argv
    
    print("\n>> Training Baseline Model")
    print("   Purpose: Establish weak baseline")
    print("   Models: Logistic Regression + Random Forest")
    print("   Features: Basic (19 features)\n")
    
    train_baseline_model('data/raw/noshow.csv', auto_promote=auto_promote)
    
    print("\n>> Next: python src/train_improved.py --auto-promote\n")
