"""
Improved Model Training Script - XGBoost with Downsampling

This uses the BAD XGBoost pattern with more features but downsampling.
Dataset: Kaggle No-Show Appointments (KaggleV2-May-2016.csv)
Purpose: Show improvement over baseline but not optimal.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from src.model_registry import ModelRegistry
import warnings
warnings.filterwarnings('ignore')


def train_improved_model(data_path: str, auto_promote: bool = False):
    """
    Train improved XGBoost model with downsampling.
    Uses MORE features but with downsampling (not optimal).
    """
    print("\n" + "="*60)
    print("TRAINING IMPROVED MODEL (XGBoost + Downsampling)")
    print("="*60 + "\n")
    
    mlflow.set_experiment("noshow-prediction")
    
    with mlflow.start_run(run_name="improved_xgboost_downsampled") as run:
        print(">> Loading and preprocessing data...")
        
        df = pd.read_csv(data_path)
        
        df.rename(columns={
            'PatientId': 'patient_id', 'AppointmentID': 'appointment_id',
            'Gender': 'gender', 'ScheduledDay': 'scheduled_day',
            'AppointmentDay': 'appointment_day', 'Age': 'age',
            'Neighbourhood': 'neighbourhood', 'Scholarship': 'scholarship',
            'Hipertension': 'hypertension', 'Diabetes': 'diabetes',
            'Alcoholism': 'alcoholism', 'Handcap': 'handicap',
            'SMS_received': 'sms_received', 'No-show': 'no_show'
        }, inplace=True)
        
        df['scheduled_day'] = pd.to_datetime(df['scheduled_day']).dt.tz_localize(None)
        df['appointment_day'] = pd.to_datetime(df['appointment_day']).dt.tz_localize(None)
        df['no_show'] = df['no_show'].map({'No': 0, 'Yes': 1})
        
        df = df[(df['age'] >= 0) & (df['age'] <= 120)]
        df = df[df['appointment_day'] >= df['scheduled_day']]
        df = df.drop_duplicates(subset='appointment_id')
        df = df.sort_values(['scheduled_day', 'appointment_day']).reset_index(drop=True)
        
        print(">> Building INTERMEDIATE features...")
        
        # Time features
        df['lead_time_days'] = (df['appointment_day'] - df['scheduled_day']).dt.days
        df['same_day_appointment'] = (df['lead_time_days'] == 0).astype(int)
        df['appointment_hour'] = df['appointment_day'].dt.hour
        df['hour_block'] = pd.cut(df['appointment_hour'], bins=[0,8,12,16,24],
                                  labels=[0,1,2,3], include_lowest=True).astype(int)
        df['day_of_week'] = df['appointment_day'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5,6]).astype(int)
        df['appointment_month'] = df['appointment_day'].dt.month
        
        # Patient history
        df = df.sort_values(['patient_id', 'appointment_day']).reset_index(drop=True)
        df['prev_no_shows'] = df.groupby('patient_id')['no_show'].cumsum() - df['no_show']
        df['prev_appointments'] = df.groupby('patient_id').cumcount()
        global_rate = df['no_show'].mean()
        df['patient_no_show_rate'] = np.where(
            df['prev_appointments'] > 0,
            df['prev_no_shows'] / df['prev_appointments'],
            global_rate
        )
        
        # Categorical features
        df['age_group'] = pd.cut(df['age'], bins=[-1,18,35,50,65,120],
                                 labels=[0,1,2,3,4], include_lowest=True).astype('float')
        df['age_group'] = df['age_group'].fillna(4).astype(int)
        
        df['lead_time_category'] = pd.cut(df['lead_time_days'], bins=[-1,0,3,7,30,365],
                                          labels=[0,1,2,3,4], include_lowest=True).astype('float')
        df['lead_time_category'] = df['lead_time_category'].fillna(4).astype(int)
        
        df['total_conditions'] = df[['hypertension','diabetes','alcoholism','handicap']].sum(axis=1)
        
        # Interactions
        df['age_x_lead_time'] = df['age'] * df['lead_time_days']
        df['sms_x_lead_time'] = df['sms_received'] * df['lead_time_days']
        df['no_show_rate_x_lead_time'] = df['patient_no_show_rate'] * df['lead_time_days']
        df['same_day_x_no_sms'] = df['same_day_appointment'] * (1 - df['sms_received'])
        df['high_risk'] = ((df['patient_no_show_rate'] > 0.3) & (df['lead_time_days'] < 7)).astype(int)
        df['low_risk'] = ((df['patient_no_show_rate'] < 0.1) & (df['sms_received'] == 1)).astype(int)
        
        # Encoding
        df['gender_encoded'] = LabelEncoder().fit_transform(df['gender'])
        df['neighbourhood_encoded'] = LabelEncoder().fit_transform(df['neighbourhood'])
        
        # Target encoding
        df['neighbourhood_no_show_rate'] = df['neighbourhood'].map(df.groupby('neighbourhood')['no_show'].mean())
        df['hour_no_show_rate'] = df['hour_block'].map(df.groupby('hour_block')['no_show'].mean())
        df['dow_no_show_rate'] = df['day_of_week'].map(df.groupby('day_of_week')['no_show'].mean())
        
        features = [
            'lead_time_days','same_day_appointment','hour_block','day_of_week','is_weekend',
            'appointment_month','lead_time_category','age','age_group','gender_encoded',
            'scholarship','hypertension','diabetes','alcoholism','handicap','total_conditions',
            'sms_received','patient_no_show_rate','prev_appointments','prev_no_shows',
            'neighbourhood_encoded','neighbourhood_no_show_rate','hour_no_show_rate','dow_no_show_rate',
            'age_x_lead_time','sms_x_lead_time','no_show_rate_x_lead_time','same_day_x_no_sms',
            'high_risk','low_risk'
        ]
        
        X = df[features].fillna(0)
        y = df['no_show']
        
        # Time-based split
        split = int(0.8 * len(df))
        X_train_full, X_test = X.iloc[:split], X.iloc[split:]
        y_train_full, y_test = y.iloc[:split], y.iloc[split:]
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
        )
        
        print(f"   Features: {len(features)} (intermediate)")
        
        # DOWNSAMPLING (Not optimal - loses data!)
        print("\n>> Applying downsampling (not optimal)...")
        train_df = pd.concat([X_train, y_train], axis=1)
        no_show = train_df[train_df['no_show'] == 1]
        show = train_df[train_df['no_show'] == 0]
        
        show_down = show.sample(n=len(no_show), random_state=42)
        balanced = pd.concat([show_down, no_show]).sample(frac=1, random_state=42)
        
        X_train_bal = balanced[features]
        y_train_bal = balanced['no_show']
        
        print(f"   Downsampled: {X_train_bal.shape}, No-show rate: {y_train_bal.mean():.1%}")
        
        print("\n>> Training XGBoost with downsampled data...")
        
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=800,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            scale_pos_weight=1.0,
            random_state=42,
            eval_metric='logloss',
            tree_method='hist',
            n_jobs=-1
        )
        
        model.fit(X_train_bal, y_train_bal,
                  eval_set=[(X_val, y_val)],
                  verbose=False)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, y_proba)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        print(f"\n   >> IMPROVED METRICS (Better than baseline):")
        print(f"   ROC-AUC:  {auc:.4f}")
        print(f"   Accuracy: {acc:.4f}")
        print(f"   F1 Score: {f1:.4f}")
        
        mlflow.log_params({
            'model_type': 'improved',
            'num_features': len(features),
            'feature_engineering': 'intermediate',
            'downsampling': True
        })
        mlflow.log_metrics({'auc': auc, 'accuracy': acc, 'f1': f1})
        mlflow.sklearn.log_model(model, 'model')
        
        run_id = run.info.run_id
        print(f"\n   MLflow Run ID: {run_id}")
        
        if auto_promote:
            print("\n>> Attempting auto-promotion...")
            registry = ModelRegistry()
            promoted_version = registry.auto_promote_if_better(
                run_id=run_id,
                metric_name='auc',
                higher_is_better=True
            )
            
            if promoted_version:
                print(f"\n>> IMPROVED MODEL PROMOTED!")
                print(f"   Production version: v{promoted_version}")
            else:
                print("\n>> Model not promoted")
        
        print("\n" + "="*60)
        print("IMPROVED TRAINING COMPLETE")
        print("="*60 + "\n")
        
        return run_id, {'auc': auc, 'accuracy': acc, 'f1': f1}


if __name__ == '__main__':
    import sys
    auto_promote = '--auto-promote' in sys.argv
    
    print("\n>> Training Improved Model")
    print("   Purpose: Show improvement with more features")
    print("   Model: XGBoost with downsampling")
    print("   Features: Intermediate (30 features)\n")
    
    train_improved_model('data/raw/noshow.csv', auto_promote=auto_promote)
    
    print("\n>> Next: python src/train_best.py --auto-promote\n")
