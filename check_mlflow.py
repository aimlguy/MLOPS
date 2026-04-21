"""Quick MLflow model status check"""
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
models = client.search_model_versions('name="noshow-prediction-model"')

print(f"\n{'='*60}")
print("MLFLOW MODEL REGISTRY STATUS")
print(f"{'='*60}\n")
print(f"Total model versions: {len(models)}\n")

for m in sorted(models, key=lambda x: int(x.version), reverse=True)[:8]:
    run = client.get_run(m.run_id)
    auc = run.data.metrics.get("auc", "N/A")
    print(f"Version {m.version}:")
    print(f"  Stage: {m.current_stage}")
    print(f"  AUC: {auc}")
    print(f"  Run ID: {m.run_id[:16]}...")
    print()

# Get production model
prod_models = [m for m in models if m.current_stage == "Production"]
if prod_models:
    prod = prod_models[0]
    run = client.get_run(prod.run_id)
    print(f"{'='*60}")
    print(f"PRODUCTION MODEL: Version {prod.version}")
    print(f"  AUC: {run.data.metrics.get('auc', 'N/A')}")
    print(f"  Accuracy: {run.data.metrics.get('accuracy', 'N/A')}")
    print(f"  F1 Score: {run.data.metrics.get('f1', 'N/A')}")
    print(f"{'='*60}\n")
