"""
Quick Setup & Test Script

This script:
1. Checks if dataset exists
2. Runs a quick test to ensure everything works
3. Provides next steps
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if Python environment is properly set up."""
    print("🔍 Checking Python environment...")
    
    print(f"   Python version: {sys.version.split()[0]}")
    print(f"   Python path: {sys.executable}")
    
    # Check required packages
    required = ['pandas', 'numpy', 'sklearn', 'xgboost', 'mlflow']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install: pip install {' '.join(missing)}")
        return False
    
    print("✅ All required packages installed!\n")
    return True


def check_dataset():
    """Check if dataset exists and is valid."""
    print("📊 Checking dataset...")
    
    dataset_path = 'data/raw/noshow.csv'
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}\n")
        print("💡 Download the dataset:")
        print("   Option 1: python scripts/download_dataset.py")
        print("   Option 2: Manual download from Kaggle")
        print("   https://www.kaggle.com/datasets/joniarroba/noshowappointments\n")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(dataset_path)
        
        print(f"✅ Dataset found!")
        print(f"   Location: {dataset_path}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Size: {os.path.getsize(dataset_path) / 1024 / 1024:.2f} MB")
        
        # Check expected columns
        expected_cols = ['PatientId', 'AppointmentID', 'Gender', 'ScheduledDay', 
                        'AppointmentDay', 'Age', 'No-show']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            print(f"\n⚠️  Missing columns: {missing_cols}")
            print(f"   This might not be the correct dataset file!")
            return False
        
        # Check data quality
        if len(df) < 10000:
            print(f"\n⚠️  Dataset seems too small ({len(df)} rows)")
            print(f"   Expected: ~110,000 rows")
            return False
        
        print(f"\n✅ Dataset looks good!\n")
        return True
        
    except Exception as e:
        print(f"❌ Error reading dataset: {e}\n")
        return False


def check_mlflow():
    """Check if MLflow is set up."""
    print("📈 Checking MLflow setup...")
    
    if os.path.exists('mlruns'):
        print(f"✅ MLflow directory exists")
    else:
        print(f"ℹ️  MLflow directory will be created on first run")
    
    print()
    return True


def check_training_scripts():
    """Check if training scripts exist."""
    print("🎯 Checking training scripts...")
    
    scripts = [
        'src/train_baseline.py',
        'src/train_improved.py',
        'src/train_best.py',
        'src/evaluate.py'
    ]
    
    all_exist = True
    for script in scripts:
        if os.path.exists(script):
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script}")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Some training scripts are missing!")
        return False
    
    print("✅ All training scripts ready!\n")
    return True


def run_quick_test():
    """Run a quick test to ensure everything works."""
    print("🧪 Running quick test...")
    
    try:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LogisticRegression
        import mlflow
        
        # Load small sample
        df = pd.read_csv('data/raw/noshow.csv', nrows=1000)
        
        # Quick preprocessing
        df['NoShow'] = (df['No-show'] == 'Yes').astype(int)
        df = df[(df['Age'] >= 0) & (df['Age'] <= 100)]
        
        # Simple features
        X = df[['Age', 'Scholarship', 'SMS_received']].fillna(0)
        y = df['NoShow']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train quick model
        model = LogisticRegression(max_iter=100)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        
        print(f"✅ Quick test passed!")
        print(f"   Test accuracy: {score:.4f}")
        print(f"   Everything is working!\n")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}\n")
        return False


def print_next_steps(all_checks_passed):
    """Print next steps based on check results."""
    print("\n" + "="*60)
    
    if all_checks_passed:
        print("  ✅ ALL CHECKS PASSED - READY TO TRAIN!")
        print("="*60 + "\n")
        
        print("🚀 Next Steps:\n")
        
        print("1️⃣  Train all models (recommended):")
        print("   python scripts/run_workflow.py")
        print("   Duration: ~10-20 minutes\n")
        
        print("2️⃣  Or train models individually:")
        print("   python src/train_baseline.py --auto-promote")
        print("   python src/train_improved.py --auto-promote")
        print("   python src/train_best.py --auto-promote\n")
        
        print("3️⃣  View results:")
        print("   mlflow ui --port 5000")
        print("   Open: http://localhost:5000\n")
        
        print("4️⃣  Generate evaluation report:")
        print("   python src/evaluate.py\n")
        
    else:
        print("  ⚠️  SETUP INCOMPLETE - ACTION REQUIRED")
        print("="*60 + "\n")
        
        print("🔧 Required Actions:\n")
        
        if not os.path.exists('data/raw/noshow.csv'):
            print("📥 Download dataset:")
            print("   python scripts/download_dataset.py")
            print("   OR")
            print("   Manual: https://www.kaggle.com/datasets/joniarroba/noshowappointments\n")
        
        print("📚 Documentation:")
        print("   Setup Guide: docs/DATASET_SETUP.md")
        print("   Full Guide: docs/ACADEMIC_GUIDE.md")
        print("   Quick Start: README.md\n")


def main():
    """Main setup check workflow."""
    print("\n" + "="*60)
    print("  MLOPS PROJECT - SETUP CHECK")
    print("="*60 + "\n")
    
    checks = []
    
    # Run all checks
    checks.append(check_environment())
    checks.append(check_dataset())
    checks.append(check_mlflow())
    checks.append(check_training_scripts())
    
    # Run quick test only if everything else passes
    if all(checks):
        checks.append(run_quick_test())
    
    all_passed = all(checks)
    
    # Print summary
    print_next_steps(all_passed)


if __name__ == '__main__':
    main()
