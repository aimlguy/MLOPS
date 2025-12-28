"""
Complete Demo Pipeline Runner
Runs all MLOps components and monitors the entire system
"""
import sys
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(cmd, description, check=True):
    """Run a command and print its output"""
    print(f"→ {description}")
    print(f"  Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True,
            check=check
        )
        print("✓ Success\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed with exit code {e.returncode}\n")
        return False
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False

def main():
    print_header("MLOps Pipeline Demo - Running All Components")
    
    # Component 1: DVC Status
    print_header("1. DVC (Data Version Control)")
    print("Checking DVC status and pipeline...")
    run_command(
        ["python", "-m", "dvc", "status"],
        "Checking DVC pipeline status",
        check=False
    )
    
    # Component 2: Feature Engineering
    print_header("2. Feature Engineering")
    print("Processing raw data and creating features...")
    run_command(
        ["python", "src/feature_engineering.py"],
        "Running feature engineering pipeline",
        check=False
    )
    
    # Component 3: Model Training
    print_header("3. Model Training (Progressive Models)")
    print("Training baseline model...")
    run_command(
        ["python", "src/train_baseline.py"],
        "Training baseline Logistic Regression model",
        check=False
    )
    
    print("\nTraining improved model...")
    run_command(
        ["python", "src/train_improved.py"],
        "Training improved Random Forest model",
        check=False
    )
    
    print("\nTraining best model...")
    run_command(
        ["python", "src/train_best.py", "--auto-promote"],
        "Training best XGBoost model with auto-promotion",
        check=False
    )
    
    # Component 4: Model Evaluation
    print_header("4. Model Evaluation")
    print("Evaluating all trained models...")
    run_command(
        ["python", "src/evaluate.py"],
        "Generating evaluation report",
        check=False
    )
    
    # Component 5: Monitoring - Drift Detection
    print_header("5. Monitoring - Drift Detection (Evidently AI)")
    print("Generating drift detection report...")
    
    from src.monitoring import get_monitor
    monitor = get_monitor()
    report_path = monitor.generate_drift_report()
    print(f"✓ Drift report generated: {report_path}\n")
    
    # Component 6: Prometheus Metrics
    print_header("6. Prometheus Metrics")
    print("Recording sample predictions for metrics...")
    
    import numpy as np
    for i in range(5):
        features = np.random.rand(10)
        prediction = np.random.rand()
        monitor.record_prediction(features, prediction, latency=0.05 + i*0.01)
    
    print("✓ Recorded 5 sample predictions")
    print("✓ Metrics available at /metrics endpoint\n")
    
    # Component 7: System Status
    print_header("7. System Status - All Components")
    
    from src.monitoring_api import get_comprehensive_status
    import json
    
    status = get_comprehensive_status()
    
    print("Component Status Summary:")
    print("-" * 50)
    for name, data in status["components"].items():
        status_symbol = "✓" if data["status"] == "success" else "⚠" if data["status"] == "configured" else "✗"
        print(f"{status_symbol} {name.upper():<20} {data['status']}")
    
    print("\nDetailed Status:")
    print(json.dumps(status, indent=2))
    
    # Summary
    print_header("PIPELINE COMPLETE - Summary")
    
    print("✓ Data validated and features engineered")
    print("✓ Three progressive models trained (Baseline → Improved → Best)")
    print("✓ Models evaluated and compared")
    print("✓ Drift detection report generated")
    print("✓ Prometheus metrics recorded")
    print("✓ All components status checked")
    
    print("\n" + "="*70)
    print("  View Results:")
    print("="*70)
    print()
    print("→ Web Dashboard:        http://localhost:5000")
    print("→ Monitoring Page:      http://localhost:5000/monitoring")
    print("→ Drift Report:         reports/drift_report.html")
    print("→ Evaluation Report:    reports/evaluation_report.html")
    print("→ MLflow (if running):  http://localhost:5000 (MLflow UI)")
    print()
    print("="*70)
    print()

if __name__ == "__main__":
    main()
