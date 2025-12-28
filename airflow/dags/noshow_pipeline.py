from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os
import sys

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)

default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def validate_data_task():
    """Validate data quality using statistical checks"""
    print("Running data validation...")
    import pandas as pd
    
    data_path = os.path.join(PROJECT_ROOT, 'data/raw/noshow.csv')
    df = pd.read_csv(data_path)
    
    # Basic validation checks
    assert len(df) > 0, "Dataset is empty"
    assert df['No-show'].notna().all(), "Missing target values"
    assert df['Age'].min() >= 0, "Invalid age values"
    
    print(f"✅ Data validation passed: {len(df)} records")
    return True

def feature_engineering_task():
    """Generate engineered features"""
    print("Running feature engineering...")
    import pandas as pd
    from src.feature_engineering import preprocess, build_features
    
    # Load and process data
    data_path = os.path.join(PROJECT_ROOT, 'data/raw/noshow.csv')
    df = pd.read_csv(data_path)
    
    # Apply preprocessing and feature engineering
    df = preprocess(df)
    df = build_features(df)
    
    # Save processed data
    output_path = os.path.join(PROJECT_ROOT, 'data/processed/features.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Feature engineering complete: {len(df)} records, {len(df.columns)} features")
    return True

def train_models_task():
    """Train all three progressive models"""
    print("Training all models...")
    import subprocess
    
    models = [
        ('baseline', 'src/train_baseline.py'),
        ('improved', 'src/train_improved.py'),
        ('best', 'src/train_best.py')
    ]
    
    for name, script in models:
        print(f"\n{'='*60}\nTraining {name} model...\n{'='*60}")
        result = subprocess.run(
            ['python', script, '--auto-promote'],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ {name} training failed: {result.stderr}")
            raise Exception(f"Training failed for {name}")
        
        print(f"✅ {name} model trained successfully")
    
    return True

def evaluate_models_task():
    """Generate evaluation report"""
    print("Evaluating models...")
    import subprocess
    
    result = subprocess.run(
        ['python', 'src/evaluate.py'],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Evaluation failed: {result.stderr}")
        raise Exception("Evaluation failed")
    
    print("✅ Evaluation complete")
    return True

def check_deployment_task():
    """Check if model is properly deployed"""
    print("Checking model deployment status...")
    import mlflow
    
    mlflow.set_tracking_uri(os.path.join(PROJECT_ROOT, 'mlruns'))
    client = mlflow.MlflowClient()
    
    try:
        # Check for production model
        prod_models = client.get_latest_versions("noshow-prediction-model", stages=["Production"])
        
        if prod_models:
            model = prod_models[0]
            print(f"✅ Production model found: v{model.version}")
            return True
        else:
            print("⚠️ No production model found")
            return False
    except Exception as e:
        print(f"❌ Deployment check failed: {e}")
        return False

with DAG(
    'noshow_prediction_pipeline',
    default_args=default_args,
    description='End-to-end No-Show Prediction MLOps Pipeline',
    schedule_interval=timedelta(days=7),  # Run weekly
    catchup=False,
    tags=['mlops', 'ml-pipeline', 'production']
) as dag:
    
    # Task 1: Pull latest data from DVC
    pull_data = BashOperator(
        task_id='pull_data_dvc',
        bash_command=f'cd {PROJECT_ROOT} && python -m dvc pull data/raw/noshow.csv.dvc',
        doc_md="""
        ## Pull Data from DVC
        Pulls the latest version of the dataset from DVC storage.
        Ensures we're training on the most recent data.
        """
    )
    
    # Task 2: Validate data quality
    validate_data = PythonOperator(
        task_id='validate_data_quality',
        python_callable=validate_data_task,
        doc_md="""
        ## Data Quality Validation
        Performs statistical validation checks on the dataset.
        Ensures data meets quality requirements before training.
        """
    )
    
    # Task 3: Feature engineering
    engineer_features = PythonOperator(
        task_id='engineer_features',
        python_callable=feature_engineering_task,
        doc_md="""
        ## Feature Engineering
        Generates derived features from raw data.
        Creates temporal, historical, and aggregate features.
        """
    )
    
    # Task 4: Train all models (baseline → improved → best)
    train_models = PythonOperator(
        task_id='train_all_models',
        python_callable=train_models_task,
        execution_timeout=timedelta(hours=2),
        doc_md="""
        ## Train Progressive Models
        Trains three models:
        1. Baseline (Logistic Regression + Random Forest)
        2. Improved (XGBoost with downsampling)
        3. Best (XGBoost with Grid Search)
        
        Automatically promotes better models to Production.
        """
    )
    
    # Task 5: Evaluate and compare models
    evaluate_models = PythonOperator(
        task_id='evaluate_models',
        python_callable=evaluate_models_task,
        doc_md="""
        ## Model Evaluation
        Generates comprehensive evaluation report.
        Compares all trained models and validates promotion decisions.
        """
    )
    
    # Task 6: Check deployment status
    check_deployment = PythonOperator(
        task_id='check_deployment_status',
        python_callable=check_deployment_task,
        doc_md="""
        ## Deployment Status Check
        Verifies that a model is properly registered in Production stage.
        Ensures the pipeline completed successfully.
        """
    )
    
    # Task 7: Generate monitoring baseline (optional)
    generate_monitoring_baseline = BashOperator(
        task_id='generate_monitoring_baseline',
        bash_command=f'cd {PROJECT_ROOT} && python -c "from src.monitoring import get_monitor; m = get_monitor(); m.generate_drift_report()"',
        trigger_rule='all_success',
        doc_md="""
        ## Generate Monitoring Baseline
        Creates initial drift detection baseline using Evidently AI.
        Sets reference data for future drift comparisons.
        """
    )
    
    # Define task dependencies (DAG structure)
    pull_data >> validate_data >> engineer_features >> train_models >> evaluate_models >> check_deployment >> generate_monitoring_baseline
