"""Check MLflow model registry status"""
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

print("\n=== Registered Models ===")
models = client.search_registered_models()
print(f"Found {len(models)} registered models\n")

for model in models:
    print(f"Model: {model.name}")
    versions = client.search_model_versions(f"name='{model.name}'")
    for v in sorted(versions, key=lambda x: int(x.version)):
        print(f"  v{v.version} - Stage: {v.current_stage}, Run: {v.run_id[:8]}")
    print()
