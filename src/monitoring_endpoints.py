"""
Monitoring Endpoints for FastAPI

Add these endpoints to your FastAPI application for Prometheus metrics and drift monitoring.
"""

from fastapi import Response
import time

# Import monitoring
try:
    from src.monitoring import get_monitor
    monitor = get_monitor()
    MONITORING_ENABLED = True
except ImportError:
    monitor = None
    MONITORING_ENABLED = False


def add_monitoring_endpoints(app):
    """Add monitoring endpoints to FastAPI app"""
    
    @app.get("/metrics")
    def get_prometheus_metrics():
        """
        Prometheus metrics endpoint.
        Prometheus will scrape this endpoint for metrics.
        """
        if not MONITORING_ENABLED or monitor is None:
            return Response(content="# Monitoring not enabled\n", media_type="text/plain")
        
        try:
            metrics_data = monitor.get_metrics()
            return Response(content=metrics_data, media_type="text/plain")
        except Exception as e:
            return Response(content=f"# Error: {str(e)}\n", media_type="text/plain")
    
    @app.get("/drift-report")
    def get_drift_report():
        """
        Generate and return drift detection report.
        Uses Evidently AI for comprehensive drift analysis.
        """
        if not MONITORING_ENABLED or monitor is None:
            return {"status": "error", "message": "Monitoring not enabled"}
        
        try:
            report_path = monitor.generate_drift_report()
            drift_scores = monitor.calculate_drift_simple()
            
            return {
                "status": "success",
                "report_path": report_path,
                "drift_scores": drift_scores,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @app.post("/update-performance")
    def update_model_performance(model_version: str, auc_score: float):
        """
        Update model performance metrics in Prometheus.
        Called after model evaluation.
        """
        if not MONITORING_ENABLED or monitor is None:
            return {"status": "error", "message": "Monitoring not enabled"}
        
        try:
            monitor.update_model_performance(model_version, auc_score)
            return {
                "status": "success",
                "model_version": model_version,
                "auc_score": auc_score
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    return app
