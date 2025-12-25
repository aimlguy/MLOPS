from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

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
    print("Running Great Expectations validation...")
    # import great_expectations as ge
    # context = ge.data_context.DataContext()
    # result = context.run_checkpoint(checkpoint_name="noshow_checkpoint")
    # if not result["success"]: raise ValueError("Data validation failed")

def feature_eng_task():
    print("Running feature engineering...")
    # Call src.feature_engineering.build_features()

with DAG(
    'noshow_pipeline',
    default_args=default_args,
    description='End-to-end No-Show Prediction Pipeline',
    schedule_interval=timedelta(days=1),
) as dag:

    pull_data = BashOperator(
        task_id='pull_data',
        bash_command='dvc pull',
    )

    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data_task,
    )

    process_features = PythonOperator(
        task_id='feature_engineering',
        python_callable=feature_eng_task,
    )

    train = BashOperator(
        task_id='train_model',
        bash_command='python src/train.py',
    )

    evaluate = BashOperator(
        task_id='evaluate_model',
        bash_command='python src/evaluate.py',
    )

    register = BashOperator(
        task_id='register_model',
        bash_command='echo "Registering model to MLflow registry..."',
    )

    pull_data >> validate >> process_features >> train >> evaluate >> register
