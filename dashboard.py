"""
MLOps Model Dashboard - Streamlit Interface

Beautiful UI to demonstrate automatic model promotion and performance tracking.

Run: streamlit run dashboard.py
"""

import streamlit as st
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import subprocess
import threading
import time
import os

# Page config
st.set_page_config(
    page_title="MLOps Model Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Initialize MLflow
@st.cache_resource
def get_mlflow_client():
    return MlflowClient()

client = get_mlflow_client()

# Session state for pipeline execution
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'pipeline_logs' not in st.session_state:
    st.session_state.pipeline_logs = []
if 'deployment_status' not in st.session_state:
    st.session_state.deployment_status = None

def run_pipeline():
    """Run the complete training pipeline."""
    st.session_state.pipeline_logs = []
    st.session_state.pipeline_running = True
    
    python_exe = r"D:/MLops/.venv/Scripts/python.exe"
    workflow_script = "scripts/run_workflow.py"
    
    try:
        # Run workflow
        st.session_state.pipeline_logs.append("🚀 Starting training pipeline...")
        
        process = subprocess.Popen(
            [python_exe, workflow_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=os.getcwd()
        )
        
        # Auto-press Enter to start
        if process.stdin:
            process.stdin.write('\n')
            process.stdin.flush()
        
        # Capture output
        for line in iter(process.stdout.readline, ''):
            if line:
                st.session_state.pipeline_logs.append(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            st.session_state.pipeline_logs.append("✅ Pipeline completed successfully!")
            return True
        else:
            st.session_state.pipeline_logs.append(f"❌ Pipeline failed with code {process.returncode}")
            return False
            
    except Exception as e:
        st.session_state.pipeline_logs.append(f"❌ Error: {str(e)}")
        return False
    finally:
        st.session_state.pipeline_running = False

def deploy_to_gcp():
    """Deploy to GCP Cloud Run."""
    st.session_state.deployment_status = "deploying"
    
    try:
        st.session_state.pipeline_logs.append("\n🚀 Starting GCP deployment...")
        
        # Git add
        st.session_state.pipeline_logs.append("📦 Staging changes...")
        subprocess.run(["git", "add", "."], check=True, cwd=os.getcwd())
        
        # Git commit
        st.session_state.pipeline_logs.append("💾 Committing changes...")
        commit_msg = f"deploy: auto-deploy best model (triggered from dashboard)"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Git push (triggers GitHub Actions)
        st.session_state.pipeline_logs.append("☁️ Pushing to GitHub (triggers deployment)...")
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if push_result.returncode == 0:
            st.session_state.pipeline_logs.append("✅ Deployment triggered!")
            st.session_state.pipeline_logs.append("📋 GitHub Actions will deploy to Cloud Run")
            st.session_state.pipeline_logs.append("⏱️ ETA: 5-10 minutes")
            st.session_state.pipeline_logs.append("🔗 Check: https://github.com/your-repo/actions")
            st.session_state.deployment_status = "success"
        else:
            st.session_state.pipeline_logs.append(f"❌ Push failed: {push_result.stderr}")
            st.session_state.deployment_status = "failed"
            
    except Exception as e:
        st.session_state.pipeline_logs.append(f"❌ Deployment error: {str(e)}")
        st.session_state.deployment_status = "failed"

def run_pipeline_and_deploy():
    """Run complete pipeline and deploy."""
    # Reset logs
    st.session_state.pipeline_logs = []
    st.session_state.pipeline_running = True
    
    # Run in thread to not block UI
    def execute():
        success = run_pipeline()
        if success:
            time.sleep(2)
            deploy_to_gcp()
        else:
            st.session_state.pipeline_logs.append("⚠️ Skipping deployment due to pipeline failure")
    
    thread = threading.Thread(target=execute, daemon=True)
    thread.start()


# Header
st.title("🤖 MLOps Automatic Model Promotion Dashboard")
st.markdown("**Real-time Model Performance Tracking & Intelligent Promotion**")

# Prominent action button
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.button(
        "🚀 RUN COMPLETE PIPELINE & DEPLOY TO GCP",
        type="primary",
        disabled=st.session_state.pipeline_running,
        use_container_width=True,
        help="Trains all models, auto-promotes best, and deploys to Cloud Run"
    ):
        run_pipeline_and_deploy()
        st.rerun()

with col2:
    if st.button("🎯 Reset Demo", use_container_width=True, help="Reset to baseline for fresh demo"):
        try:
            python_exe = r"D:/MLops/.venv/Scripts/python.exe"
            result = subprocess.run(
                [python_exe, "scripts/reset_to_baseline.py"],
                capture_output=True,
                text=True
            )
            st.success("✅ Reset complete!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

# Pipeline status banner
if st.session_state.pipeline_running:
    st.info("⏳ **Pipeline is running...** Click 'Refresh Data' to see updates")
elif st.session_state.deployment_status == "success":
    st.success("✅ **Deployment triggered!** Check GitHub Actions for progress")
elif st.session_state.deployment_status == "failed":
    st.error("❌ **Deployment failed.** Check logs below")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    model_name = st.text_input("Model Name", "noshow-prediction-model")
    
    st.markdown("---")
    
    # Pipeline execution controls
    st.header("🚀 Pipeline Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Run Pipeline", disabled=st.session_state.pipeline_running, use_container_width=True):
            run_pipeline_and_deploy()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    
    if st.session_state.pipeline_running:
        st.warning("⏳ Pipeline running...")
        st.button("🔄 Update Logs", key="update", use_container_width=True)
    
    # Pipeline logs
    if st.session_state.pipeline_logs:
        st.markdown("---")
        st.subheader("📋 Execution Logs")
        log_container = st.container(height=300)
        with log_container:
            for log in st.session_state.pipeline_logs[-20:]:  # Last 20 lines
                if "✅" in log or "success" in log.lower():
                    st.success(log)
                elif "❌" in log or "error" in log.lower() or "failed" in log.lower():
                    st.error(log)
                elif "⚠️" in log or "warning" in log.lower():
                    st.warning(log)
                elif "🚀" in log or "Starting" in log:
                    st.info(log)
                else:
                    st.text(log)
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")


    # Main content
try:
    # Get all model versions
    versions = client.search_model_versions(f"name='{model_name}'")
    
    if not versions:
        st.warning("⚠️ No models found. Train some models first!")
        st.info("👆 Click the **RUN COMPLETE PIPELINE & DEPLOY** button above to start!")
        st.code("Or run manually: python scripts/run_workflow.py")
        st.stop()
    
    # Sort by version
    versions = sorted(versions, key=lambda x: int(x.version))
    
    # Get metrics for each version
    version_data = []
    for v in versions:
        run = client.get_run(v.run_id)
        version_data.append({
            'Version': f"v{v.version}",
            'Stage': v.current_stage,
            'AUC': run.data.metrics.get('auc', 0),
            'Accuracy': run.data.metrics.get('accuracy', 0),
            'F1': run.data.metrics.get('f1', 0),
            'Created': datetime.fromtimestamp(v.creation_timestamp / 1000).strftime('%Y-%m-%d %H:%M'),
            'Run ID': v.run_id[:8]
        })
    
    df = pd.DataFrame(version_data)
    
    # Production model highlight
    prod_versions = [v for v in versions if v.current_stage == "Production"]
    prod_model = prod_versions[0] if prod_versions else None
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if prod_model:
        prod_run = client.get_run(prod_model.run_id)
        prod_auc = prod_run.data.metrics.get('auc', 0)
        prod_acc = prod_run.data.metrics.get('accuracy', 0)
        prod_f1 = prod_run.data.metrics.get('f1', 0)
        
        with col1:
            st.metric("🏆 Production Model", f"v{prod_model.version}")
        with col2:
            st.metric("📊 ROC-AUC", f"{prod_auc:.4f}")
        with col3:
            st.metric("🎯 Accuracy", f"{prod_acc:.4f}")
        with col4:
            st.metric("⚖️ F1 Score", f"{prod_f1:.4f}")
    else:
        st.warning("⚠️ No model in Production stage")
    
    st.markdown("---")
    
    # Two columns layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Model Performance Progression")
        
        # AUC progression chart
        fig = go.Figure()
        
        # Add line chart
        fig.add_trace(go.Scatter(
            x=df['Version'],
            y=df['AUC'],
            mode='lines+markers',
            name='ROC-AUC',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=12)
        ))
        
        # Highlight production model
        if prod_model:
            prod_idx = df[df['Version'] == f"v{prod_model.version}"].index[0]
            fig.add_trace(go.Scatter(
                x=[df.loc[prod_idx, 'Version']],
                y=[df.loc[prod_idx, 'AUC']],
                mode='markers',
                name='Production',
                marker=dict(size=20, color='#51CF66', symbol='star')
            ))
        
        fig.update_layout(
            title="ROC-AUC Score Evolution",
            xaxis_title="Model Version",
            yaxis_title="ROC-AUC Score",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Model comparison table
        st.subheader("📋 All Model Versions")
        
        # Style the dataframe
        def highlight_production(row):
            if row['Stage'] == 'Production':
                return ['background-color: #51CF66; color: white'] * len(row)
            elif row['Stage'] == 'Archived':
                return ['background-color: #FFA94D; color: white'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df.style.apply(highlight_production, axis=1).format({
            'AUC': '{:.4f}',
            'Accuracy': '{:.4f}',
            'F1': '{:.4f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
    
    with col_right:
        st.subheader("🎯 Model Status")
        
        # Stage distribution
        stage_counts = df['Stage'].value_counts()
        
        fig_pie = px.pie(
            values=stage_counts.values,
            names=stage_counts.index,
            color=stage_counts.index,
            color_discrete_map={
                'Production': '#51CF66',
                'Archived': '#FFA94D',
                'None': '#868E96'
            }
        )
        fig_pie.update_layout(height=250)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Model improvement
        if len(df) > 1:
            baseline_auc = df.iloc[0]['AUC']
            best_auc = df['AUC'].max()
            improvement = ((best_auc - baseline_auc) / baseline_auc) * 100
            
            st.metric(
                "📈 Total Improvement",
                f"{improvement:.2f}%",
                f"from v1 to v{df.loc[df['AUC'].idxmax(), 'Version']}"
            )
        
        # Promotion decisions
        st.markdown("### 🤖 Promotion Decisions")
        for idx, row in df.iterrows():
            if row['Stage'] == 'Production':
                st.success(f"✅ {row['Version']} - **Promoted** (AUC: {row['AUC']:.4f})")
            elif row['Stage'] == 'Archived':
                st.warning(f"📦 {row['Version']} - Archived (replaced)")
            else:
                # Check if it was rejected (lower AUC than production)
                if prod_model:
                    if row['AUC'] < prod_auc:
                        st.error(f"❌ {row['Version']} - **Rejected** (AUC: {row['AUC']:.4f} < {prod_auc:.4f})")
                    else:
                        st.info(f"⏳ {row['Version']} - Pending")
    
    st.markdown("---")
    
    # Detailed comparison
    st.subheader("📊 Multi-Metric Comparison")
    
    # Create radar chart for all metrics
    fig_radar = go.Figure()
    
    for idx, row in df.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['AUC'], row['Accuracy'], row['F1']],
            theta=['AUC', 'Accuracy', 'F1'],
            fill='toself',
            name=row['Version'],
            line=dict(width=2)
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Sidebar stats
    with st.sidebar:
        st.metric("Total Models", len(versions))
        st.metric("In Production", len([v for v in versions if v.current_stage == "Production"]))
        st.metric("Archived", len([v for v in versions if v.current_stage == "Archived"]))
        st.metric("Pending", len([v for v in versions if v.current_stage == "None"]))

except Exception as e:
    st.error(f"❌ Error loading models: {str(e)}")
    st.code("Make sure MLflow tracking server is accessible and models are registered.")

# Footer
st.markdown("---")

# Action buttons at bottom
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎯 Reset to Baseline", help="Reset production to v1 for demo"):
        try:
            python_exe = r"D:/MLops/.venv/Scripts/python.exe"
            subprocess.run([python_exe, "scripts/reset_to_baseline.py"], check=True)
            st.success("✅ Reset to baseline v1")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Reset failed: {str(e)}")

with col2:
    if st.button("📊 Open MLflow UI", help="Open MLflow at localhost:5000"):
        st.info("💡 Run in terminal: mlflow ui --port 5000")
        st.code("mlflow ui --port 5000")

with col3:
    if st.button("☁️ Check Cloud Status", help="Check deployed model on Cloud Run"):
        st.info("🔗 Cloud Run Service")
        st.code("curl https://ethika-rag-model-583756314894.asia-south1.run.app/model-info")

st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 MLOps Automatic Model Promotion System | 
    Built with MLflow + Streamlit | 
    <a href='http://localhost:5000' target='_blank'>Open MLflow UI</a>
    </p>
</div>
""", unsafe_allow_html=True)
