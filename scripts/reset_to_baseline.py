"""
Reset Production Model to Baseline

This script sets the production model back to v1 (baseline, AUC 0.7088)
so you can re-run the workflow and demonstrate automatic model promotion.
"""

import mlflow
from mlflow.tracking import MlflowClient

def reset_to_baseline():
    """Reset production model to baseline (v1)."""
    
    # Use default tracking URI (finds mlruns automatically)
    client = MlflowClient()
    model_name = "noshow-prediction-model"
    
    print("\n" + "="*60)
    print("RESETTING PRODUCTION MODEL TO BASELINE")
    print("="*60 + "\n")
    
    try:
        # Get all versions
        versions = client.search_model_versions(f"name='{model_name}'")
        
        print(f"Found {len(versions)} model versions:")
        for v in sorted(versions, key=lambda x: int(x.version)):
            print(f"  v{v.version} - Stage: {v.current_stage}")
        
        # Archive all current Production models
        prod_versions = client.get_latest_versions(model_name, stages=["Production"])
        for pv in prod_versions:
            print(f"\n>> Archiving v{pv.version} from Production")
            client.transition_model_version_stage(
                name=model_name,
                version=pv.version,
                stage="Archived"
            )
        
        # Promote v1 (baseline) to Production
        print(f"\n>> Promoting v1 (Baseline) to Production")
        client.transition_model_version_stage(
            name=model_name,
            version="1",
            stage="Production"
        )
        
        print("\n" + "="*60)
        print("RESET COMPLETE")
        print("="*60)
        print("\nCurrent Production Model: v1 (Baseline, AUC 0.7088)")
        print("\nNext steps:")
        print("  1. Run: python scripts/run_workflow.py")
        print("  2. Watch as better models automatically replace baseline")
        print("  3. Final result: v4 (Best, AUC 0.9347) in Production\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have trained models in mlruns/")

if __name__ == "__main__":
    reset_to_baseline()
