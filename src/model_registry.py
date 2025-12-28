"""
MLflow Model Registration and Promotion Helper

This module provides utilities to register trained models in MLflow
and promote them to Production stage based on performance metrics.
"""

import mlflow
from mlflow.tracking import MlflowClient
from typing import Dict, Optional, List
import os


class ModelRegistry:
    """Helper class for MLflow model registration and promotion."""
    
    def __init__(
        self,
        tracking_uri: str = "file:///app/mlruns",
        model_name: str = "noshow-prediction-model"
    ):
        self.tracking_uri = tracking_uri
        self.model_name = model_name
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
    
    def register_model(
        self,
        run_id: str,
        artifact_path: str = "model",
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Register a model from an MLflow run.
        
        Args:
            run_id: MLflow run ID containing the model
            artifact_path: Path to model artifact in the run
            tags: Optional tags for the model version
            
        Returns:
            Model version as string
        """
        model_uri = f"runs:/{run_id}/{artifact_path}"
        
        print(f"📦 Registering model from run: {run_id}")
        
        model_version = mlflow.register_model(
            model_uri=model_uri,
            name=self.model_name,
            tags=tags
        )
        
        version = model_version.version
        print(f"✅ Model registered: {self.model_name} v{version}")
        
        return version
    
    def get_production_model_metrics(self) -> Optional[Dict[str, float]]:
        """
        Get metrics of the current Production model.
        
        Returns:
            Dictionary of metrics or None if no Production model exists
        """
        try:
            prod_versions = self.client.get_latest_versions(
                self.model_name,
                stages=["Production"]
            )
            
            if not prod_versions:
                print("ℹ️ No Production model found")
                return None
            
            prod_version = prod_versions[0]
            run = self.client.get_run(prod_version.run_id)
            
            return run.data.metrics
            
        except Exception as e:
            print(f"⚠️ Error getting Production model metrics: {e}")
            return None
    
    def compare_models(
        self,
        candidate_run_id: str,
        metric_name: str = "auc",
        higher_is_better: bool = True
    ) -> bool:
        """
        Compare candidate model against current Production model.
        
        Args:
            candidate_run_id: Run ID of the candidate model
            metric_name: Metric to compare (e.g., 'auc', 'f1')
            higher_is_better: Whether higher metric values are better
            
        Returns:
            True if candidate is better, False otherwise
        """
        # Get candidate metrics
        candidate_run = self.client.get_run(candidate_run_id)
        candidate_metric = candidate_run.data.metrics.get(metric_name)
        
        if candidate_metric is None:
            print(f"⚠️ Metric '{metric_name}' not found in candidate run")
            return False
        
        # Get production metrics
        prod_metrics = self.get_production_model_metrics()
        
        if prod_metrics is None:
            print("✅ No Production model - candidate will be promoted")
            return True
        
        prod_metric = prod_metrics.get(metric_name)
        
        if prod_metric is None:
            print(f"⚠️ Metric '{metric_name}' not found in Production model")
            return True
        
        # Compare
        if higher_is_better:
            is_better = candidate_metric > prod_metric
        else:
            is_better = candidate_metric < prod_metric
        
        print(f"\n📊 Model Comparison ({metric_name}):")
        print(f"   Production: {prod_metric:.4f}")
        print(f"   Candidate:  {candidate_metric:.4f}")
        print(f"   Result: {'✅ BETTER' if is_better else '❌ WORSE'}\n")
        
        return is_better
    
    def promote_to_production(
        self,
        version: str,
        archive_existing: bool = True
    ) -> bool:
        """
        Promote a model version to Production stage.
        
        Args:
            version: Model version to promote
            archive_existing: Whether to archive existing Production models
            
        Returns:
            True if promotion succeeded
        """
        try:
            # Archive existing Production models
            if archive_existing:
                prod_versions = self.client.get_latest_versions(
                    self.model_name,
                    stages=["Production"]
                )
                
                for prod_version in prod_versions:
                    print(f"📦 Archiving v{prod_version.version}")
                    self.client.transition_model_version_stage(
                        name=self.model_name,
                        version=prod_version.version,
                        stage="Archived"
                    )
            
            # Promote new version
            print(f"🚀 Promoting v{version} to Production")
            self.client.transition_model_version_stage(
                name=self.model_name,
                version=version,
                stage="Production"
            )
            
            print(f"✅ Model v{version} is now in Production!")
            return True
            
        except Exception as e:
            print(f"❌ Promotion failed: {e}")
            return False
    
    def auto_promote_if_better(
        self,
        run_id: str,
        metric_name: str = "auc",
        higher_is_better: bool = True,
        artifact_path: str = "model"
    ) -> Optional[str]:
        """
        Automatically register and promote model if it performs better.
        
        This is the main function to use after training a model.
        
        Args:
            run_id: MLflow run ID of the trained model
            metric_name: Metric to use for comparison
            higher_is_better: Whether higher is better for this metric
            artifact_path: Path to model artifact in the run
            
        Returns:
            Model version if promoted, None otherwise
        """
        print("\n" + "="*60)
        print("🤖 AUTOMATIC MODEL PROMOTION EVALUATION")
        print("="*60)
        
        # Register the model
        version = self.register_model(run_id, artifact_path)
        
        # Compare with production
        is_better = self.compare_models(
            candidate_run_id=run_id,
            metric_name=metric_name,
            higher_is_better=higher_is_better
        )
        
        if is_better:
            success = self.promote_to_production(version)
            
            if success:
                print("\n" + "="*60)
                print(f"✅ MODEL v{version} PROMOTED TO PRODUCTION")
                print("="*60 + "\n")
                return version
        else:
            print("\n" + "="*60)
            print(f"❌ MODEL v{version} NOT PROMOTED (performance insufficient)")
            print("="*60 + "\n")
        
        return None


# Example usage function
def example_usage():
    """Example of how to use the ModelRegistry after training."""
    
    # Initialize registry
    registry = ModelRegistry()
    
    # After training (you'll have a run_id from mlflow.start_run())
    run_id = "your_run_id_here"
    
    # Automatically promote if better
    promoted_version = registry.auto_promote_if_better(
        run_id=run_id,
        metric_name="auc",
        higher_is_better=True
    )
    
    if promoted_version:
        print(f"🎉 New model v{promoted_version} is now serving!")
        print("🔄 Trigger redeployment to load new model")
    else:
        print("ℹ️ Keeping current Production model")


if __name__ == "__main__":
    print(__doc__)
    print("\nThis module should be imported and used after model training.")
    print("See example_usage() function for details.")
