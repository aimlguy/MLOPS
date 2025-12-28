# 🎨 MLflow UI - Visual Demonstration Interface

## Launch MLflow UI

```bash
# Start MLflow UI server
mlflow ui --port 5000
```

Then open: **http://localhost:5000**

---

## What You Can Demonstrate

### 1. Experiments Tab 📊
- **All Training Runs**: See baseline, improved, best
- **Metrics Comparison**: AUC, accuracy, F1 side-by-side
- **Parameter Tracking**: Features, algorithms, hyperparameters
- **Visualizations**: Built-in charts and graphs

### 2. Models Tab 🏆
- **Version History**: v1, v2, v3, v4
- **Stage Management**: Production, Archived, None
- **Metrics per Version**: See which performed best
- **Promotion Timeline**: When models were promoted

### 3. Model Comparison View 📈
1. Select multiple runs (baseline, improved, best)
2. Click "Compare"
3. See side-by-side metrics, parameters, charts
4. **Perfect for demonstration!**

---

## Demo Script for Instructors

### Before Workflow
```bash
# 1. Start MLflow UI
mlflow ui --port 5000

# 2. Open http://localhost:5000
# 3. Show Models tab - v1 is in Production (AUC 0.7088)
```

### Run Workflow
```bash
# In another terminal
python scripts/run_workflow.py
```

**While it's running, show in MLflow UI:**
- New experiments appearing in real-time
- Metrics being logged
- Models being registered

### After Workflow
**In MLflow UI, demonstrate:**

1. **Experiments Tab**:
   - Sort by AUC (show progression)
   - Click each run to see detailed metrics
   - Show feature engineering differences

2. **Models Tab**:
   - v1: Archived (baseline replaced)
   - v3: Never promoted (AUC 0.6127 < baseline)
   - v4: Production (AUC 0.9347 - 31% improvement!)

3. **Compare Runs**:
   - Select baseline + improved + best
   - Click "Compare"
   - Show metrics table
   - Display parameter differences
   - Prove v3 was intelligently rejected

---

## Screenshots to Take

For your report/presentation:

1. **Model Registry**: Show v4 in Production
2. **Experiments List**: All runs with metrics
3. **Comparison View**: Baseline vs Best
4. **Charts**: AUC progression over time
5. **Parameters**: Feature engineering evolution

---

## Quick Demo Flow (2 minutes)

```
Instructor: "Show me your MLOps pipeline"

You:
1. Open MLflow UI (localhost:5000)
2. Models tab → "See v1 baseline in Production"
3. Run: python scripts/run_workflow.py
4. Experiments tab → "Watch new runs appear"
5. After completion:
   - Models tab → "v4 automatically promoted"
   - Compare → "Show 31% AUC improvement"
   - Experiments → "v3 was rejected (worse performance)"

Instructor: "Impressive! This demonstrates real MLOps automation."
```

---

## Pro Tips for Demo

- **Keep MLflow UI open** during workflow execution
- **Refresh page** after each model trains
- **Use Compare feature** to show intelligent decision-making
- **Highlight Production badge** on best model
- **Show archived models** to prove version control

---

## Alternative: Custom Dashboard (Optional)

If you want a custom UI, I can create a simple Streamlit dashboard showing:
- Current Production model stats
- Model comparison charts
- Prediction testing interface
- Real-time metrics updates

Let me know if you want this!
