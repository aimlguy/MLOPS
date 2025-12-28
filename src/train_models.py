"""
Production Model Training Pipeline
Trains multiple models and selects the best one based on AUC score
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, classification_report
import xgboost as xgb
import pickle
import json
from pathlib import Path
from datetime import datetime


class NoShowModelTrainer:
    def __init__(self, data_path='data/raw/noshow.csv'):
        self.data_path = data_path
        self.models_dir = Path('models')
        self.models_dir.mkdir(exist_ok=True)
        self.best_model = None
        self.best_model_name = None
        self.best_score = 0
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_and_preprocess_data(self):
        """Load and preprocess the dataset"""
        print("Loading data...")
        df = pd.read_csv(self.data_path)
        
        # Drop unnecessary columns
        if 'PatientId' in df.columns:
            df = df.drop(['PatientId'], axis=1)
        if 'AppointmentID' in df.columns:
            df = df.drop(['AppointmentID'], axis=1)
            
        # Convert dates
        if 'ScheduledDay' in df.columns:
            df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
        if 'AppointmentDay' in df.columns:
            df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])
            
        # Feature engineering
        if 'ScheduledDay' in df.columns and 'AppointmentDay' in df.columns:
            df['LeadTimeDays'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days
            df['ScheduledHour'] = df['ScheduledDay'].dt.hour
            df['ScheduledDayOfWeek'] = df['ScheduledDay'].dt.dayofweek
            df['AppointmentDayOfWeek'] = df['AppointmentDay'].dt.dayofweek
            df = df.drop(['ScheduledDay', 'AppointmentDay'], axis=1)
            
        # Encode target variable
        if 'No-show' in df.columns:
            df['NoShow'] = df['No-show'].map({'No': 0, 'Yes': 1})
            df = df.drop(['No-show'], axis=1)
            
        # Encode categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col not in ['NoShow']:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
                
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        
        # Separate features and target
        X = df.drop(['NoShow'], axis=1)
        y = df['NoShow']
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X = pd.DataFrame(X_scaled, columns=X.columns)
        
        print(f"Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
        print(f"Class distribution: {y.value_counts().to_dict()}")
        
        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    def train_logistic_regression(self, X_train, y_train):
        """Train Logistic Regression model"""
        print("\n--- Training Logistic Regression ---")
        model = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
        model.fit(X_train, y_train)
        return model
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        print("\n--- Training Random Forest ---")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def train_gradient_boosting(self, X_train, y_train):
        """Train Gradient Boosting model"""
        print("\n--- Training Gradient Boosting ---")
        model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost model"""
        print("\n--- Training XGBoost ---")
        
        # Calculate scale_pos_weight for imbalanced dataset
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
        
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric='auc',
            use_label_encoder=False
        )
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_name):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, y_pred_proba)
        f1 = f1_score(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n{model_name} Results:")
        print(f"AUC: {auc:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"Accuracy: {accuracy:.4f}")
        
        metrics = {
            'auc': float(auc),
            'f1': float(f1),
            'accuracy': float(accuracy),
            'model_name': model_name,
            'timestamp': datetime.now().isoformat()
        }
        
        return metrics
    
    def save_model(self, model, model_name, metrics):
        """Save model and metadata"""
        model_path = self.models_dir / f'{model_name}.pkl'
        metadata_path = self.models_dir / f'{model_name}_metadata.json'
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"Model saved to {model_path}")
        
        # Save metadata
        metadata = {
            'model_name': model_name,
            'metrics': metrics,
            'feature_names': self.feature_names,
            'training_date': datetime.now().isoformat()
        }
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to {metadata_path}")
        
    def save_preprocessors(self):
        """Save scaler and label encoders"""
        scaler_path = self.models_dir / 'scaler.pkl'
        encoders_path = self.models_dir / 'label_encoders.pkl'
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(encoders_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
            
        print(f"Preprocessors saved")
        
    def train_all_models(self):
        """Train all models and select the best one"""
        print("="*60)
        print("Starting Model Training Pipeline")
        print("="*60)
        
        # Load data
        X_train, X_test, y_train, y_test = self.load_and_preprocess_data()
        
        # Train models
        models = {
            'logistic_regression': self.train_logistic_regression(X_train, y_train),
            'random_forest': self.train_random_forest(X_train, y_train),
            'gradient_boosting': self.train_gradient_boosting(X_train, y_train),
            'xgboost': self.train_xgboost(X_train, y_train)
        }
        
        # Evaluate all models
        all_metrics = {}
        for model_name, model in models.items():
            metrics = self.evaluate_model(model, X_test, y_test, model_name)
            all_metrics[model_name] = metrics
            self.save_model(model, model_name, metrics)
            
            # Track best model
            if metrics['auc'] > self.best_score:
                self.best_score = metrics['auc']
                self.best_model = model
                self.best_model_name = model_name
        
        # Save preprocessors
        self.save_preprocessors()
        
        # Save best model info
        best_model_info = {
            'best_model': self.best_model_name,
            'best_score': self.best_score,
            'all_metrics': all_metrics,
            'selection_date': datetime.now().isoformat()
        }
        
        with open(self.models_dir / 'best_model_info.json', 'w') as f:
            json.dump(best_model_info, f, indent=2)
            
        print("\n" + "="*60)
        print(f"Best Model: {self.best_model_name}")
        print(f"Best AUC Score: {self.best_score:.4f}")
        print("="*60)
        
        return self.best_model_name, self.best_score, all_metrics


if __name__ == "__main__":
    trainer = NoShowModelTrainer()
    best_model, best_score, metrics = trainer.train_all_models()
    
    print("\n✅ Training completed successfully!")
    print(f"\nBest model '{best_model}' with AUC={best_score:.4f} is ready for production.")
