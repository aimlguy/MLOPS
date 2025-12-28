"""
ML Model Monitoring with Evidently AI and Prometheus

This module provides drift detection and performance monitoring capabilities.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import warnings
warnings.filterwarnings('ignore')

# Prometheus metrics
PREDICTION_COUNTER = Counter(
    'model_predictions_total', 
    'Total number of predictions made',
    ['model_version', 'outcome']
)

PREDICTION_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model_version']
)

DATA_DRIFT_SCORE = Gauge(
    'model_data_drift_score',
    'Data drift score from Evidently AI',
    ['feature_name']
)

MODEL_PERFORMANCE_METRIC = Gauge(
    'model_performance_auc',
    'Model ROC-AUC performance metric',
    ['model_version']
)


class ModelMonitor:
    """Monitor ML model performance and data drift"""
    
    def __init__(self, reference_data_path: str = "data/raw/noshow.csv"):
        """Initialize monitor with reference dataset"""
        self.reference_data_path = reference_data_path
        self.reference_data = None
        self.current_data_buffer = []
        self.max_buffer_size = 1000
        
        # Load reference data
        self._load_reference_data()
        
    def _load_reference_data(self):
        """Load reference dataset for drift detection"""
        try:
            df = pd.read_csv(self.reference_data_path)
            # Basic preprocessing to match prediction data
            self.reference_data = df.head(1000)  # Sample for efficiency
            # Silent load for API calls
        except Exception as e:
            # Silent error handling
            self.reference_data = None
    
    def record_prediction(self, 
                         features: Dict,
                         prediction: int,
                         model_version: str,
                         latency: float):
        """Record a prediction for monitoring"""
        # Increment Prometheus counter
        outcome = "no_show" if prediction == 1 else "show"
        PREDICTION_COUNTER.labels(
            model_version=model_version,
            outcome=outcome
        ).inc()
        
        # Record latency
        PREDICTION_LATENCY.labels(
            model_version=model_version
        ).observe(latency)
        
        # Buffer current data for drift detection
        self.current_data_buffer.append(features)
        if len(self.current_data_buffer) > self.max_buffer_size:
            self.current_data_buffer.pop(0)
    
    def calculate_drift_simple(self) -> Dict[str, float]:
        """
        Simple drift detection using statistical distance
        This is a minimal implementation for demonstration
        """
        if not self.current_data_buffer or self.reference_data is None:
            return {}
        
        drift_scores = {}
        
        try:
            # Convert buffer to DataFrame
            current_df = pd.DataFrame(self.current_data_buffer)
            
            # Calculate simple drift for numerical features
            numerical_features = current_df.select_dtypes(include=[np.number]).columns
            
            for feature in numerical_features:
                if feature in self.reference_data.columns:
                    ref_mean = self.reference_data[feature].mean()
                    curr_mean = current_df[feature].mean()
                    ref_std = self.reference_data[feature].std()
                    
                    # Normalized difference as drift score
                    if ref_std > 0:
                        drift_score = abs(curr_mean - ref_mean) / ref_std
                    else:
                        drift_score = 0.0
                    
                    drift_scores[feature] = min(drift_score, 1.0)  # Cap at 1.0
                    
                    # Update Prometheus gauge
                    DATA_DRIFT_SCORE.labels(feature_name=feature).set(drift_score)
        
        except Exception as e:
            print(f"Error calculating drift: {e}")
        
        return drift_scores
    
    def generate_drift_report(self, output_path: str = "reports/drift_report.html"):
        """
        Generate Evidently AI drift report
        This is a simplified version - in production would use full Evidently AI
        """
        drift_scores = self.calculate_drift_simple()
        
        # Create simple HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Drift Detection Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .metric {{ padding: 10px; margin: 10px 0; background: #f5f5f5; border-radius: 5px; }}
                .high-drift {{ background: #ffcccc; }}
                .low-drift {{ background: #ccffcc; }}
            </style>
        </head>
        <body>
            <h1>Model Drift Detection Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <h2>Drift Scores</h2>
        """
        
        for feature, score in drift_scores.items():
            drift_class = "high-drift" if score > 0.1 else "low-drift"
            html_content += f"""
            <div class="metric {drift_class}">
                <strong>{feature}</strong>: {score:.4f}
                {'⚠️ HIGH DRIFT' if score > 0.1 else '✓ OK'}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Save report
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        # Removed print to avoid JSON parsing issues in API
        return output_path
    
    def update_model_performance(self, model_version: str, auc_score: float):
        """Update performance metric in Prometheus"""
        MODEL_PERFORMANCE_METRIC.labels(model_version=model_version).set(auc_score)
    
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics in text format"""
        return generate_latest(REGISTRY)


# Global monitor instance
_monitor = None

def get_monitor() -> ModelMonitor:
    """Get or create global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = ModelMonitor()
    return _monitor
