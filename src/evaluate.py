"""
Model Evaluation and Comparison Script

This script compares all trained models and generates a comprehensive report.

Purpose:
- Load all model versions from MLflow
- Compare their metrics (AUC, Accuracy, F1)
- Generate visualizations
- Create comparison report
- Demonstrate model progression: Baseline → Improved → Best
"""

import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def get_all_runs(experiment_name: str = "noshow-prediction"):
    """Get all runs from the experiment."""
    client = MlflowClient()
    
    # Get experiment
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"❌ Experiment '{experiment_name}' not found!")
        return []
    
    # Get all runs
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )
    
    return runs


def extract_run_data(runs):
    """Extract relevant data from runs."""
    data = []
    
    for run in runs:
        metrics = run.data.metrics
        params = run.data.params
        
        model_type = params.get('model_type', 'unknown')
        
        data.append({
            'run_id': run.info.run_id,
            'run_name': run.info.run_name,
            'model_type': model_type,
            'auc': metrics.get('auc', 0),
            'accuracy': metrics.get('accuracy', 0),
            'f1': metrics.get('f1', 0),
            'num_features': params.get('num_features', 0),
            'timestamp': run.info.start_time
        })
    
    return pd.DataFrame(data)


def plot_model_comparison(df: pd.DataFrame, output_dir: str = "reports"):
    """Create comparison plots."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter to latest run for each model type
    df_latest = df.sort_values('timestamp', ascending=False).groupby('model_type').first().reset_index()
    
    # Sort by model progression
    model_order = ['baseline', 'improved', 'best']
    df_latest = df_latest[df_latest['model_type'].isin(model_order)]
    df_latest['model_type'] = pd.Categorical(df_latest['model_type'], categories=model_order, ordered=True)
    df_latest = df_latest.sort_values('model_type')
    
    # 1. Metrics Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    metrics = ['auc', 'accuracy', 'f1']
    x = range(len(df_latest))
    width = 0.25
    
    for i, metric in enumerate(metrics):
        ax.bar([xi + i * width for xi in x], df_latest[metric], 
               width, label=metric.upper(), alpha=0.8)
    
    ax.set_xlabel('Model Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison\n(Demonstrating Progressive Improvement)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks([xi + width for xi in x])
    ax.set_xticklabels(df_latest['model_type'].str.capitalize())
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/model_comparison.png", dpi=300)
    print(f"   ✅ Saved: {output_dir}/model_comparison.png")
    plt.close()
    
    # 2. AUC Progression Line Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(df_latest['model_type'].str.capitalize(), df_latest['auc'], 
            marker='o', linewidth=2, markersize=10, color='#2E86AB')
    ax.fill_between(range(len(df_latest)), df_latest['auc'], alpha=0.3, color='#2E86AB')
    
    # Add value labels
    for i, (model, auc) in enumerate(zip(df_latest['model_type'], df_latest['auc'])):
        ax.text(i, auc + 0.01, f'{auc:.4f}', ha='center', fontweight='bold')
    
    ax.set_xlabel('Model Progression', fontsize=12, fontweight='bold')
    ax.set_ylabel('ROC-AUC Score', fontsize=12, fontweight='bold')
    ax.set_title('Model AUC Improvement Over Time\n(Automatic Promotion Based on Metrics)', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim([df_latest['auc'].min() - 0.05, df_latest['auc'].max() + 0.05])
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/auc_progression.png", dpi=300)
    print(f"   ✅ Saved: {output_dir}/auc_progression.png")
    plt.close()
    
    # 3. Feature Count vs AUC
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for i, (_, row) in enumerate(df_latest.iterrows()):
        ax.scatter(row['num_features'], row['auc'], s=300, 
                  color=colors[i], label=row['model_type'].capitalize(),
                  alpha=0.7, edgecolors='black', linewidth=2)
        ax.text(row['num_features'], row['auc'] - 0.02, 
               f"{row['model_type'].capitalize()}\nAUC: {row['auc']:.4f}", 
               ha='center', fontsize=9)
    
    ax.set_xlabel('Number of Features', fontsize=12, fontweight='bold')
    ax.set_ylabel('ROC-AUC Score', fontsize=12, fontweight='bold')
    ax.set_title('Feature Engineering Impact on Performance', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/features_vs_auc.png", dpi=300)
    print(f"   ✅ Saved: {output_dir}/features_vs_auc.png")
    plt.close()


def generate_markdown_report(df: pd.DataFrame, output_dir: str = "reports"):
    """Generate a comprehensive markdown report."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter to latest run for each model type
    df_latest = df.sort_values('timestamp', ascending=False).groupby('model_type').first().reset_index()
    
    # Sort by model progression
    model_order = ['baseline', 'improved', 'best']
    df_latest = df_latest[df_latest['model_type'].isin(model_order)]
    df_latest['model_type'] = pd.Categorical(df_latest['model_type'], categories=model_order, ordered=True)
    df_latest = df_latest.sort_values('model_type')
    
    report = f"""# Model Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report demonstrates the **progressive improvement** of machine learning models through systematic feature engineering and algorithm selection. The MLOps pipeline automatically promotes better-performing models to production based on ROC-AUC metrics.

### Key Findings

"""
    
    if len(df_latest) >= 2:
        baseline_auc = df_latest.iloc[0]['auc']
        best_auc = df_latest.iloc[-1]['auc']
        improvement = ((best_auc - baseline_auc) / baseline_auc) * 100
        
        report += f"""- **Total AUC Improvement:** {improvement:.2f}% (from {baseline_auc:.4f} to {best_auc:.4f})
- **Models Trained:** {len(df_latest)}
- **Best Model:** {df_latest.iloc[-1]['model_type'].capitalize()}
- **Feature Expansion:** {df_latest.iloc[0]['num_features']} → {df_latest.iloc[-1]['num_features']} features

"""
    
    report += """---

## Model Comparison

### Performance Metrics

| Model | ROC-AUC | Accuracy | F1 Score | Features | Improvement |
|-------|---------|----------|----------|----------|-------------|
"""
    
    prev_auc = None
    for _, row in df_latest.iterrows():
        improvement = ""
        if prev_auc:
            imp_pct = ((row['auc'] - prev_auc) / prev_auc) * 100
            improvement = f"+{imp_pct:.2f}%"
        else:
            improvement = "Baseline"
        
        report += f"| {row['model_type'].capitalize()} | {row['auc']:.4f} | {row['accuracy']:.4f} | {row['f1']:.4f} | {int(row['num_features'])} | {improvement} |\n"
        prev_auc = row['auc']
    
    report += """
### Visualizations

![Model Comparison](model_comparison.png)
*Performance across all metrics showing progressive improvement*

![AUC Progression](auc_progression.png)
*ROC-AUC improvement through model iterations*

![Features vs AUC](features_vs_auc.png)
*Impact of feature engineering on model performance*

---

## Model Details

"""
    
    descriptions = {
        'baseline': """
#### 1. Baseline Model (Logistic Regression)

**Purpose:** Establish a simple baseline for comparison

**Characteristics:**
- Algorithm: Logistic Regression (linear model)
- Features: 6 basic features (age, gender, scholarship, hypertension, diabetes, sms_received)
- Tuning: None (default parameters)
- Expected Performance: Moderate (AUC ~0.60-0.65)

**Rationale:** Start with the simplest model to demonstrate improvement potential.
""",
        'improved': """
#### 2. Improved Model (Random Forest)

**Purpose:** Show significant improvement through better algorithm and features

**Characteristics:**
- Algorithm: Random Forest (ensemble method)
- Features: 16 features (includes time-based and patient history)
- Tuning: Basic hyperparameter optimization
- Expected Performance: Good (AUC ~0.70-0.75)

**Improvements:**
- Better algorithm capable of capturing non-linear relationships
- Advanced feature engineering (time patterns, patient history)
- Handles feature interactions automatically

**Rationale:** Demonstrate that algorithm choice and feature engineering matter.
""",
        'best': """
#### 3. Best Model (XGBoost)

**Purpose:** Achieve optimal performance through state-of-the-art techniques

**Characteristics:**
- Algorithm: XGBoost (gradient boosting)
- Features: 16 comprehensive features (full engineering pipeline)
- Tuning: Advanced hyperparameter optimization (grid search)
- Expected Performance: Excellent (AUC ~0.78-0.82)

**Improvements:**
- Industry-standard algorithm for tabular data
- Extensive hyperparameter tuning
- Early stopping and regularization
- Optimized for class imbalance

**Rationale:** Show that systematic optimization yields the best results.
"""
    }
    
    for model_type in model_order:
        if model_type in df_latest['model_type'].values:
            report += descriptions[model_type]
    
    report += """
---

## MLOps Pipeline Demonstration

### Automatic Model Promotion

The pipeline demonstrates **automated model promotion** based on metrics:

1. **Baseline Model Training**
   ```bash
   python src/train_baseline.py --auto-promote
   ```
   - Trains simple model
   - Logs metrics to MLflow
   - Promoted to Production (first model)

2. **Improved Model Training**
   ```bash
   python src/train_improved.py --auto-promote
   ```
   - Trains better model
   - Compares with current Production
   - **Automatically replaces** baseline if AUC is higher

3. **Best Model Training**
   ```bash
   python src/train_best.py --auto-promote
   ```
   - Trains optimized model
   - Compares with current Production
   - **Automatically replaces** improved model if AUC is higher

### Key Pipeline Features

✅ **Automated Promotion:** Models automatically replace inferior predecessors  
✅ **Metrics-Driven:** Decisions based on ROC-AUC comparison  
✅ **Zero-Downtime:** New models deployed without service interruption  
✅ **Version Control:** All models tracked and retrievable  
✅ **Rollback Capable:** Previous versions archived for safety  

---

## Academic Value

This project demonstrates:

1. **End-to-End ML Pipeline:** From data ingestion to production deployment
2. **Continuous Improvement:** Systematic model enhancement through experimentation
3. **Automated Decision-Making:** Metrics-driven promotion without manual intervention
4. **MLOps Best Practices:** Model registry, versioning, monitoring
5. **Cloud Deployment:** Serverless architecture on GCP Cloud Run

### Learning Outcomes

- Feature engineering impact on performance
- Algorithm selection importance
- Hyperparameter tuning benefits
- Automated ML workflows
- Production deployment strategies

---

*Generated by MLOps Pipeline | MLflow + Cloud Run + GitHub Actions*
"""
    
    output_path = f"{output_dir}/evaluation_report.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"   ✅ Saved: {output_path}")


def main():
    """Main evaluation workflow."""
    print("\n" + "="*60)
    print("MODEL EVALUATION & COMPARISON")
    print("="*60 + "\n")
    
    print("📊 Fetching runs from MLflow...")
    runs = get_all_runs()
    
    if not runs:
        print("\n❌ No runs found! Train models first:")
        print("   python src/train_baseline.py --auto-promote")
        print("   python src/train_improved.py --auto-promote")
        print("   python src/train_best.py --auto-promote\n")
        return
    
    print(f"   Found {len(runs)} total runs\n")
    
    print("🔍 Extracting run data...")
    df = extract_run_data(runs)
    
    if df.empty:
        print("❌ No valid run data found!")
        return
    
    print(f"   Extracted {len(df)} runs with metrics\n")
    
    # Show summary
    print("📈 Model Summary:")
    model_types = df.groupby('model_type').agg({
        'auc': 'max',
        'run_id': 'count'
    }).round(4)
    print(model_types.to_string())
    print()
    
    print("🎨 Generating visualizations...")
    plot_model_comparison(df)
    print()
    
    print("📝 Generating markdown report...")
    generate_markdown_report(df)
    print()
    
    print("="*60)
    print("EVALUATION COMPLETE")
    print("="*60 + "\n")
    
    print("📁 Output files created:")
    print("   - reports/model_comparison.png")
    print("   - reports/auc_progression.png")
    print("   - reports/features_vs_auc.png")
    print("   - reports/evaluation_report.md")
    print()
    
    print("💡 Next steps:")
    print("   1. Review reports/ directory")
    print("   2. Check MLflow UI for detailed metrics")
    print("   3. Deploy best model: git push origin main")
    print("   4. Test production endpoint on Cloud Run\n")


if __name__ == "__main__":
    main()
