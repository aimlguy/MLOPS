"""
Production Model Inference Service
Loads trained model and performs predictions
"""
import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ModelInferenceService:
    def __init__(self, models_dir='models'):
        self.models_dir = Path(models_dir)
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        self.model_name = None
        self.load_model()
        
    def load_model(self):
        """Load the best trained model and preprocessors"""
        # Load best model info
        best_model_info_path = self.models_dir / 'best_model_info.json'
        if not best_model_info_path.exists():
            raise FileNotFoundError("No trained model found. Please train models first using train_models.py")
            
        with open(best_model_info_path, 'r') as f:
            best_model_info = json.load(f)
            
        self.model_name = best_model_info['best_model']
        
        # Load model
        model_path = self.models_dir / f'{self.model_name}.pkl'
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
            
        # Load metadata
        metadata_path = self.models_dir / f'{self.model_name}_metadata.json'
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            self.feature_names = metadata['feature_names']
            
        # Load preprocessors
        scaler_path = self.models_dir / 'scaler.pkl'
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
            
        encoders_path = self.models_dir / 'label_encoders.pkl'
        with open(encoders_path, 'rb') as f:
            self.label_encoders = pickle.load(f)
            
        # Silent load for API calls - no print statements
        
    def preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input data to match training format"""
        # Convert to DataFrame
        df = pd.DataFrame([input_data])
        
        # Feature engineering - match training pipeline
        if 'scheduledDay' in df.columns and 'appointmentDay' in df.columns:
            # Convert to datetime if string
            df['scheduledDay'] = pd.to_datetime(df['scheduledDay'])
            df['appointmentDay'] = pd.to_datetime(df['appointmentDay'])
            
            # Calculate derived features
            df['LeadTimeDays'] = (df['appointmentDay'] - df['scheduledDay']).dt.days
            df['ScheduledHour'] = df['scheduledDay'].dt.hour
            df['ScheduledDayOfWeek'] = df['scheduledDay'].dt.dayofweek
            df['AppointmentDayOfWeek'] = df['appointmentDay'].dt.dayofweek
            
            df = df.drop(['scheduledDay', 'appointmentDay'], axis=1)
        
        # Map field names to match training data
        field_mapping = {
            'gender': 'Gender',
            'age': 'Age',
            'neighbourhood': 'Neighbourhood',
            'scholarship': 'Scholarship',
            'hypertension': 'Hypertension',
            'diabetes': 'Diabetes',
            'alcoholism': 'Alcoholism',
            'handicap': 'Handicap',
            'smsReceived': 'SMS_received'
        }
        
        df = df.rename(columns=field_mapping)
        
        # Encode categorical variables using saved encoders
        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                # Handle unseen labels
                try:
                    df[col] = encoder.transform(df[col].astype(str))
                except ValueError:
                    # If label not seen during training, use most frequent class
                    df[col] = 0
        
        # Ensure all features are present and in correct order
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
                
        df = df[self.feature_names]
        
        # Scale features
        df_scaled = self.scaler.transform(df)
        df = pd.DataFrame(df_scaled, columns=self.feature_names)
        
        return df
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction on input data
        
        Args:
            input_data: Dictionary with patient information
            
        Returns:
            Dictionary with prediction probability and class
        """
        try:
            # Preprocess input
            processed_data = self.preprocess_input(input_data)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(processed_data)[0]
            prediction_class = self.model.predict(processed_data)[0]
            
            # Get probability of no-show (class 1)
            no_show_probability = float(prediction_proba[1])
            is_no_show = bool(prediction_class == 1)
            
            result = {
                'probability': no_show_probability,
                'isNoShow': is_no_show,
                'model_name': self.model_name,
                'prediction_time': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
    
    def batch_predict(self, input_data_list: list) -> list:
        """Make predictions on multiple inputs"""
        results = []
        for input_data in input_data_list:
            try:
                result = self.predict(input_data)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'input': input_data
                })
        return results


# Global inference service instance
_inference_service = None

def get_inference_service() -> ModelInferenceService:
    """Get or create global inference service instance"""
    global _inference_service
    if _inference_service is None:
        _inference_service = ModelInferenceService()
    return _inference_service


if __name__ == "__main__":
    # Test the inference service
    service = ModelInferenceService()
    
    # Test prediction
    test_input = {
        'gender': 'F',
        'age': 35,
        'neighbourhood': 'JARDIM CAMBURI',
        'scholarship': False,
        'hypertension': False,
        'diabetes': False,
        'alcoholism': False,
        'handicap': 0,
        'smsReceived': True,
        'scheduledDay': '2024-04-01T10:00:00',
        'appointmentDay': '2024-04-15T14:00:00'
    }
    
    result = service.predict(test_input)
    print("\nTest Prediction:")
    print(json.dumps(result, indent=2))
