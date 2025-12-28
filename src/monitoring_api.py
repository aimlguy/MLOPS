"""
Comprehensive Monitoring API for all MLOps components
"""
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


def get_dvc_status() -> Dict[str, Any]:
    """Get DVC repository status"""
    try:
        result = subprocess.run(
            ["python", "-m", "dvc", "status"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=10
        )
        
        is_clean = "Data and pipelines are up to date" in result.stdout
        
        return {
            "status": "success",
            "initialized": os.path.exists(PROJECT_ROOT / ".dvc"),
            "is_clean": is_clean,
            "output": result.stdout[:500],
            "tracked_files": len(list(PROJECT_ROOT.glob("**/*.dvc"))),
            "pipeline_stages": get_dvc_pipeline_stages()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "initialized": os.path.exists(PROJECT_ROOT / ".dvc")
        }


def get_dvc_pipeline_stages() -> List[Dict[str, str]]:
    """Parse dvc.yaml for pipeline stages"""
    dvc_file = PROJECT_ROOT / "dvc.yaml"
    if not dvc_file.exists():
        return []
    
    try:
        import yaml
        with open(dvc_file) as f:
            data = yaml.safe_load(f)
        
        stages = []
        if data and "stages" in data:
            for name, config in data["stages"].items():
                stages.append({
                    "name": name,
                    "command": config.get("cmd", "N/A")[:50] + "..."
                })
        return stages
    except:
        return []


def get_airflow_status() -> Dict[str, Any]:
    """Get Airflow DAG status"""
    try:
        # Check if DAG file exists
        dag_file = PROJECT_ROOT / "airflow" / "dags" / "noshow_pipeline.py"
        
        if not dag_file.exists():
            return {
                "status": "not_configured",
                "message": "DAG file not found"
            }
        
        # Try to list DAGs
        result = subprocess.run(
            ["airflow", "dags", "list"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=PROJECT_ROOT
        )
        
        has_dag = "noshow_prediction_pipeline" in result.stdout
        
        return {
            "status": "success" if has_dag else "configured",
            "dag_file_exists": True,
            "dag_registered": has_dag,
            "dag_name": "noshow_prediction_pipeline",
            "tasks": [
                "pull_data_dvc",
                "validate_data_quality",
                "engineer_features",
                "train_all_models",
                "evaluate_models",
                "check_deployment_status",
                "generate_monitoring_baseline"
            ],
            "output": result.stdout[:500] if has_dag else "DAG configured but not registered yet"
        }
    except FileNotFoundError:
        return {
            "status": "not_installed",
            "message": "Airflow not installed or not in PATH"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "dag_file_exists": dag_file.exists() if 'dag_file' in locals() else False
        }


def get_mlflow_status() -> Dict[str, Any]:
    """Get MLflow tracking and registry status"""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        client = MlflowClient()
        
        # Get registered models
        registered_models = []
        try:
            models = client.search_registered_models()
            for model in models:
                versions = client.search_model_versions(f"name='{model.name}'")
                registered_models.append({
                    "name": model.name,
                    "version_count": len(versions),
                    "latest_version": max([int(v.version) for v in versions]) if versions else 0
                })
        except:
            pass
        
        # Get recent runs
        try:
            runs = mlflow.search_runs(max_results=5)
            recent_runs = len(runs)
        except:
            recent_runs = 0
        
        return {
            "status": "success",
            "tracking_uri": mlflow.get_tracking_uri(),
            "registered_models": registered_models,
            "recent_runs_count": recent_runs,
            "experiments_count": len(client.search_experiments())
        }
    except ImportError:
        return {
            "status": "not_installed",
            "message": "MLflow not installed"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_evidently_status() -> Dict[str, Any]:
    """Get Evidently AI drift detection status"""
    try:
        import sys
        import os
        sys.path.insert(0, str(PROJECT_ROOT))
        
        from src.monitoring import get_monitor
        
        monitor = get_monitor()
        
        # Check if reports exist
        reports_dir = PROJECT_ROOT / "reports"
        drift_reports = list(reports_dir.glob("drift_report*.html")) if reports_dir.exists() else []
        
        return {
            "status": "success",
            "installed": True,
            "reports_generated": len(drift_reports),
            "latest_report": drift_reports[-1].name if drift_reports else None,
            "monitoring_active": monitor is not None,
            "drift_calculation": "Statistical distance-based"
        }
    except ImportError as e:
        return {
            "status": "not_installed",
            "message": f"Monitoring module not available: {str(e)}",
            "installed": False
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "installed": False
        }


def get_prometheus_status() -> Dict[str, Any]:
    """Get Prometheus metrics status"""
    try:
        import prometheus_client
        
        # Check if config exists
        config_file = PROJECT_ROOT / "monitoring" / "prometheus.yml"
        
        # Try to count registered metrics
        metrics_count = 0
        try:
            from prometheus_client import REGISTRY
            metrics_count = len(list(REGISTRY._collector_to_names.values()))
        except:
            pass
        
        return {
            "status": "success",
            "installed": True,
            "config_exists": config_file.exists(),
            "registered_metrics": metrics_count,
            "alert_rules_configured": os.path.exists(PROJECT_ROOT / "monitoring" / "alert_rules.yml"),
            "metrics_endpoint": "/metrics"
        }
    except ImportError:
        return {
            "status": "not_installed",
            "message": "Prometheus client not installed",
            "installed": False
        }
    except Exception as e:
        return {
            "status": "configured",
            "message": f"Prometheus configured but metrics collection not active: {str(e)}",
            "config_exists": os.path.exists(PROJECT_ROOT / "monitoring" / "prometheus.yml")
        }


def get_grafana_status() -> Dict[str, Any]:
    """Get Grafana dashboard status"""
    try:
        dashboard_file = PROJECT_ROOT / "monitoring" / "grafana_dashboard.json"
        
        if not dashboard_file.exists():
            return {
                "status": "not_configured",
                "message": "Dashboard file not found"
            }
        
        with open(dashboard_file) as f:
            dashboard = json.load(f)
        
        # Count panels
        panels = dashboard.get("panels", [])
        
        return {
            "status": "success",
            "dashboard_configured": True,
            "dashboard_title": dashboard.get("title", "ML Model Monitoring"),
            "panel_count": len(panels),
            "panels": [
                {
                    "title": panel.get("title", "Untitled"),
                    "type": panel.get("type", "unknown")
                }
                for panel in panels
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_docker_status() -> Dict[str, Any]:
    """Get Docker configuration status"""
    try:
        dockerfile = PROJECT_ROOT / "docker" / "Dockerfile"
        
        if not dockerfile.exists():
            return {
                "status": "not_configured",
                "message": "Dockerfile not found"
            }
        
        # Try to check Docker daemon
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        docker_running = result.returncode == 0
        
        return {
            "status": "success",
            "dockerfile_exists": True,
            "docker_daemon_running": docker_running,
            "dockerfile_path": str(dockerfile.relative_to(PROJECT_ROOT))
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Docker not installed",
            "dockerfile_exists": dockerfile.exists() if 'dockerfile' in locals() else False
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_github_actions_status() -> Dict[str, Any]:
    """Get GitHub Actions CI/CD status"""
    try:
        workflows_dir = PROJECT_ROOT / ".github" / "workflows"
        
        if not workflows_dir.exists():
            return {
                "status": "not_configured",
                "message": "No workflows found"
            }
        
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        workflows = []
        for wf in workflow_files:
            workflows.append({
                "name": wf.name,
                "path": str(wf.relative_to(PROJECT_ROOT))
            })
        
        return {
            "status": "success",
            "configured": True,
            "workflow_count": len(workflows),
            "workflows": workflows
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_comprehensive_status() -> Dict[str, Any]:
    """Get status of all MLOps components"""
    return {
        "timestamp": datetime.now().isoformat(),
        "components": {
            "dvc": get_dvc_status(),
            "airflow": get_airflow_status(),
            "mlflow": get_mlflow_status(),
            "evidently": get_evidently_status(),
            "prometheus": get_prometheus_status(),
            "grafana": get_grafana_status(),
            "docker": get_docker_status(),
            "github_actions": get_github_actions_status()
        }
    }


def generate_drift_report() -> Dict[str, Any]:
    """Generate a new drift detection report"""
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        
        from src.monitoring import get_monitor
        
        monitor = get_monitor()
        report_path = monitor.generate_drift_report()
        
        return {
            "status": "success",
            "report_path": str(report_path),
            "message": "Drift report generated successfully"
        }
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Monitoring module not available: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test all components
    status = get_comprehensive_status()
    print(json.dumps(status, indent=2))
