"""
Complete MLOps Workflow Runner

This script runs the entire model training and evaluation workflow
in the correct sequence to demonstrate automatic model promotion.

Workflow:
1. Train baseline model (poor) → Auto-promote to Production
2. Train improved model (better) → Auto-replace baseline
3. Train best model (best) → Auto-replace improved
4. Evaluate and compare all models
5. Generate comprehensive report

Purpose: Academic demonstration of CI/CD for ML models
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def get_python_executable():
    """Get the correct Python executable (venv if exists, else system)."""
    # Check for venv
    if sys.platform == "win32":
        venv_python = Path("D:/MLops/.venv/Scripts/python.exe")
    else:
        venv_python = Path(".venv/bin/python")
    
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def run_command(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"🚀 {description}...")
    print(f"   Command: {' '.join(cmd)}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Completed in {elapsed:.1f}s\n")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: {e}")
        if e.stdout:
            print("\nStdout:")
            print(e.stdout)
        if e.stderr:
            print("\nStderr:")
            print(e.stderr)
        return False


def main():
    """Run the complete workflow."""
    python_exe = get_python_executable()
    print("\n" + "="*70)
    print("  MLOps COMPLETE WORKFLOW")
    print("  Demonstrating Automatic Model Promotion")
    print("="*70)
    print(f"\n  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Using Python: {python_exe}")
    print("\n  This workflow will:")
    print("    1. Train 3 progressive models (baseline → improved → best)")
    print("    2. Automatically promote better models to Production")
    print("    3. Generate comparison visualizations")
    print("    4. Create comprehensive evaluation report")
    print("\n  Expected duration: ~5-10 minutes\n")
    
    input("  Press Enter to begin...")
    
    # Step 1: Baseline Model
    print_section("STEP 1: Training Baseline Model")
    print("  Purpose: Establish a simple starting point")
    print("  Model: Logistic Regression")
    print("  Features: 6 basic features")
    print("  Expected AUC: ~0.60-0.65\n")
    
    success = run_command(
        [python_exe, "src/train_baseline.py", "--auto-promote"],
        "Training baseline model"
    )
    
    if not success:
        print("❌ Workflow failed at baseline training!")
        return
    
    print("  ✅ Baseline model promoted to Production\n")
    time.sleep(2)
    
    # Step 2: Improved Model
    print_section("STEP 2: Training Improved Model")
    print("  Purpose: Demonstrate significant improvement")
    print("  Model: Random Forest")
    print("  Features: 16 features (with engineering)")
    print("  Expected AUC: ~0.70-0.75\n")
    
    success = run_command(
        [python_exe, "src/train_improved.py", "--auto-promote"],
        "Training improved model"
    )
    
    if not success:
        print("❌ Workflow failed at improved training!")
        return
    
    print("  ✅ Improved model should replace baseline\n")
    time.sleep(2)
    
    # Step 3: Best Model
    print_section("STEP 3: Training Best Model")
    print("  Purpose: Achieve optimal performance")
    print("  Model: XGBoost (tuned)")
    print("  Features: 16 features (comprehensive)")
    print("  Expected AUC: ~0.78-0.82\n")
    
    success = run_command(
        [python_exe, "src/train_best.py", "--auto-promote"],
        "Training best model"
    )
    
    if not success:
        print("❌ Workflow failed at best training!")
        return
    
    print("  ✅ Best model should replace improved\n")
    time.sleep(2)
    
    # Step 4: Evaluation
    print_section("STEP 4: Evaluating All Models")
    print("  Purpose: Compare performance and generate report")
    print("  Output:")
    print("    - reports/model_comparison.png")
    print("    - reports/auc_progression.png")
    print("    - reports/features_vs_auc.png")
    print("    - reports/evaluation_report.md\n")
    
    success = run_command(
        [python_exe, "src/evaluate.py"],
        "Generating evaluation report"
    )
    
    if not success:
        print("❌ Workflow failed at evaluation!")
        return
    
    # Final Summary
    print_section("WORKFLOW COMPLETE ✨")
    
    print("  📊 Results:")
    print("     - 3 models trained and compared")
    print("     - Best model automatically promoted to Production")
    print("     - Comprehensive evaluation report generated")
    print()
    print("  📁 Generated Files:")
    print("     - reports/evaluation_report.md (main report)")
    print("     - reports/model_comparison.png")
    print("     - reports/auc_progression.png")
    print("     - reports/features_vs_auc.png")
    print()
    print("  🎯 Academic Demonstration:")
    print("     ✅ End-to-end ML pipeline")
    print("     ✅ Automatic model promotion based on metrics")
    print("     ✅ Progressive improvement visualization")
    print("     ✅ MLOps best practices")
    print()
    print("  📖 Next Steps:")
    print("     1. Review: reports/evaluation_report.md")
    print("     2. Check MLflow UI: mlflow ui --port 5000")
    print("     3. Deploy to Cloud Run: git push origin main")
    print("     4. Test production API: curl <CLOUD_RUN_URL>/predict")
    print()
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("="*70)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}\n")
        sys.exit(1)
