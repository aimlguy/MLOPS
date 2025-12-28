"""
Best Model Training Script - Optimized XGBoost with Grid Search

This uses the BEST XGBoost pattern with comprehensive features and tuning.
Dataset: Kaggle No-Show Appointments (KaggleV2-May-2016.csv)
Purpose: Achieve optimal performance through extensive optimization.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import mlflow
import mlflow.xgboost
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from src.model_registry import ModelRegistry
import warnings
warnings.filterwarnings('ignore')


def train_best_model(data_path: str, auto_promote: bool = False):
    """
    Train the best XGBoost model with comprehensive feature engineering and grid search.
    This should be the best performing model.
    """
    print("\n" + "="*60)
    print("TRAINING BEST MODEL (XGBoost + Grid Search)")
    print("="*60 + "\n")
    
    mlflow.set_experiment("noshow-prediction")
    
    with mlflow.start_run(run_name="best_xgboost_tuned") as run:
        print(">> Loading and preprocessing data...")
        
        df = pd.read_csv(data_path)
        
        # Rename columns
        df.rename(columns={
            'PatientId': 'patient_id',
            'AppointmentID': 'appointment_id',
            'Gender': 'gender',
            'ScheduledDay': 'scheduled_day',
            'AppointmentDay': 'appointment_day',
            'Age': 'age',
            'Neighbourhood': 'neighbourhood',
            'Scholarship': 'scholarship',
            'Hipertension': 'hypertension',
            'Diabetes': 'diabetes',
            'Alcoholism': 'alcoholism',
            'Handcap': 'handicap',
            'SMS_received': 'sms_received',
            'No-show': 'no_show'
        }, inplace=True)
        
        # Convert datetime
        df['scheduled_day'] = pd.to_datetime(df['scheduled_day'])
        df['appointment_day'] = pd.to_datetime(df['appointment_day'])
        
        # Clean target
        df['no_show'] = df['no_show'].map({'No': 0, 'Yes': 1})
        
        # Data cleaning
        df = df[(df['age'] >= 0) & (df['age'] <= 120)]
        df = df[df['appointment_day'] >= df['scheduled_day']]
        df = df.drop_duplicates(subset=['appointment_id'])
        df = df.sort_values(['scheduled_day', 'appointment_day']).reset_index(drop=True)
        
        print(">> Building COMPREHENSIVE features...")
        
        # Time-based features
        df['scheduled_date'] = df['scheduled_day'].dt.date
        df['appointment_date'] = df['appointment_day'].dt.date
        df['scheduled_hour'] = df['scheduled_day'].dt.hour
        df['appointment_hour'] = df['appointment_day'].dt.hour
        
        def get_hour_block(hour):
            if hour < 8: return 0
            elif hour < 12: return 1
            elif hour < 16: return 2
            else: return 3
        
        df['hour_block'] = df['appointment_hour'].apply(get_hour_block)
        df['day_of_week'] = df['appointment_day'].dt.dayofweek
        df['is_holiday_or_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Lead time features
        df['lead_time_days'] = (df['appointment_day'] - df['scheduled_day']).dt.days
        df['lead_time_hours'] = (df['appointment_day'] - df['scheduled_day']).dt.total_seconds() / 3600
        df['same_day_appointment'] = (df['lead_time_days'] == 0).astype(int)
        df['appointment_month'] = df['appointment_day'].dt.month
        df['appointment_week'] = df['appointment_day'].dt.isocalendar().week
        
        # Patient history features
        df = df.sort_values(['patient_id', 'appointment_day']).reset_index(drop=True)
        
        patient_history = df.groupby('patient_id').agg({
            'no_show': ['sum', 'count', 'mean'],
            'age': 'first',
            'gender': 'first'
        }).reset_index()
        
        patient_history.columns = ['patient_id', 'total_no_shows', 'total_appointments', 
                                   'historical_no_show_rate', 'age', 'gender']
        
        df = df.merge(patient_history[['patient_id', 'total_no_shows', 'total_appointments', 
                                        'historical_no_show_rate']], 
                      on='patient_id', how='left')
        
        df['prev_no_shows'] = df.groupby('patient_id')['no_show'].cumsum() - df['no_show']
        df['prev_appointments'] = df.groupby('patient_id').cumcount()
        df['rolling_no_show_rate'] = np.where(
            df['prev_appointments'] > 0,
            df['prev_no_shows'] / df['prev_appointments'],
            df['historical_no_show_rate']
        )
        
        overall_no_show_rate = df['no_show'].mean()
        df['rolling_no_show_rate'] = df['rolling_no_show_rate'].fillna(overall_no_show_rate)
        
        # Aggregated historical patterns
        hourly_no_show = df.groupby('hour_block')['no_show'].mean().reset_index()
        hourly_no_show.columns = ['hour_block', 'avg_historical_no_show_rate_by_hour']
        df = df.merge(hourly_no_show, on='hour_block', how='left')
        
        dow_no_show = df.groupby('day_of_week')['no_show'].mean().reset_index()
        dow_no_show.columns = ['day_of_week', 'avg_no_show_rate_by_dow']
        df = df.merge(dow_no_show, on='day_of_week', how='left')
        
        neighbourhood_no_show = df.groupby('neighbourhood')['no_show'].mean().reset_index()
        neighbourhood_no_show.columns = ['neighbourhood', 'avg_no_show_rate_by_neighbourhood']
        df = df.merge(neighbourhood_no_show, on='neighbourhood', how='left')
        
        df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 120], labels=['0-18', '19-35', '36-50', '51-65', '65+'])
        age_no_show = df.groupby('age_group')['no_show'].mean().reset_index()
        age_no_show.columns = ['age_group', 'avg_no_show_rate_by_age']
        df = df.merge(age_no_show, on='age_group', how='left')
        
        # Encoding
        le_gender = LabelEncoder()
        df['gender_encoded'] = le_gender.fit_transform(df['gender'])
        le_neighbourhood = LabelEncoder()
        df['neighbourhood_encoded'] = le_neighbourhood.fit_transform(df['neighbourhood'])
        
        # Comprehensive feature set
        feature_columns = [
            'hour_block', 'day_of_week', 'is_holiday_or_weekend', 'lead_time_days', 
            'same_day_appointment', 'appointment_month',
            'age', 'gender_encoded', 'scholarship', 'hypertension', 'diabetes', 
            'alcoholism', 'handicap', 'sms_received',
            'rolling_no_show_rate', 'prev_appointments',
            'avg_historical_no_show_rate_by_hour', 'avg_no_show_rate_by_dow',
            'avg_no_show_rate_by_neighbourhood', 'avg_no_show_rate_by_age'
        ]
        
        X = df[feature_columns].copy()
        y = df['no_show'].copy()
        X = X.fillna(X.mean())
        
        print(f"   Features: {len(feature_columns)} (comprehensive)")
        
        # Time-based split
        split_index = int(len(df) * 0.8)
        X_train = X.iloc[:split_index]
        X_test = X.iloc[split_index:]
        y_train = y.iloc[:split_index]
        y_test = y.iloc[split_index:]
        
        X_train_final, X_val, y_train_final, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        print(f"   Training set: {X_train_final.shape}, No-show rate: {y_train_final.mean():.2%}")
        print(f"   Validation set: {X_val.shape}, No-show rate: {y_val.mean():.2%}")
        print(f"   Test set: {X_test.shape}, No-show rate: {y_test.mean():.2%}")
        
        # Calculate class imbalance
        no_show_ratio = (y_train_final == 0).sum() / (y_train_final == 1).sum()
        print(f"\n   Class imbalance ratio: {no_show_ratio:.2f}")
        
        print("\n>> Training initial XGBoost model...")
        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=300,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=no_show_ratio,
            random_state=42,
            eval_metric='auc',
            tree_method='hist',
            n_jobs=-1
        )
        
        xgb_model.fit(
            X_train_final, y_train_final,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        print("\n>> Starting hyperparameter tuning (Grid Search)...")
        param_grid = {
            'max_depth': [4, 6, 8],
            'learning_rate': [0.01, 0.05, 0.1],
            'n_estimators': [200, 300, 400],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9],
            'min_child_weight': [1, 3, 5]
        }
        
        grid_search = GridSearchCV(
            estimator=xgb.XGBClassifier(
                objective='binary:logistic',
                scale_pos_weight=no_show_ratio,
                random_state=42,
                eval_metric='auc',
                tree_method='hist',
                n_jobs=-1
            ),
            param_grid=param_grid,
            scoring='roc_auc',
            cv=3,
            verbose=1,
            n_jobs=-1
        )
        
        grid_search.fit(X_train_final, y_train_final)
        
        print(f"\n   Best parameters: {grid_search.best_params_}")
        print(f"   Best CV AUC: {grid_search.best_score_:.4f}")
        
        best_xgb_model = grid_search.best_estimator_
        
        # Final evaluation
        print("\n>> Evaluating best model...")
        
        y_test_pred = best_xgb_model.predict(X_test)
        y_test_pred_proba = best_xgb_model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, y_test_pred_proba)
        accuracy = accuracy_score(y_test, y_test_pred)
        f1 = f1_score(y_test, y_test_pred)
        
        print(f"\n   >> BEST METRICS (Highest performance):")
        print(f"   ROC-AUC:  {auc:.4f}")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   F1 Score: {f1:.4f}")
        
        # Log to MLflow
        mlflow.log_params({
            'model_type': 'best',
            'num_features': len(feature_columns),
            'feature_engineering': 'comprehensive',
            'grid_search': True,
            **grid_search.best_params_
        })
        mlflow.log_metrics({'auc': auc, 'accuracy': accuracy, 'f1': f1})
        mlflow.sklearn.log_model(best_xgb_model, 'model')
        
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
                print(f"\n>> BEST MODEL PROMOTED!")
                print(f"   New Production version: v{promoted_version}")
                print(f"   >> Complete progression: Baseline -> Improved -> Best")
            else:
                print("\n>> Model not promoted")
        
        print("\n" + "="*60)
        print("BEST MODEL TRAINING COMPLETE")
        print("="*60 + "\n")
        
        return run_id, {'auc': auc, 'accuracy': accuracy, 'f1': f1}


if __name__ == '__main__':
    import sys
    auto_promote = '--auto-promote' in sys.argv
    
    print("\n>> Training Best Model")
    print("   Purpose: Achieve optimal performance")
    print("   Model: XGBoost with Grid Search")
    print("   Features: Comprehensive (20 features)\n")
    
    train_best_model('data/raw/noshow.csv', auto_promote=auto_promote)
    
    print("\n>> Next: python src/evaluate.py\n")
