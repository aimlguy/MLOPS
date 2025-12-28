# 🎨 Beautiful Dashboard Demo Guide

## Two Dashboard Options

### Option 1: MLflow UI (Built-in, Quick) ⚡

```bash
mlflow ui --port 5000
```

Open: http://localhost:5000

**Best for:**
- Quick model inspection
- Detailed experiment tracking
- Parameter comparison
- Built-in visualizations

---

### Option 2: Custom Streamlit Dashboard (Beautiful, Custom) 🎨

```bash
streamlit run dashboard.py
```

Open: http://localhost:8501

**Best for:**
- Visual demonstrations
- Instructor presentations
- Real-time metrics display
- Custom visualizations
- Clear promotion decisions

---

## Demo Flow with Streamlit Dashboard

### Setup (Do Once)
```bash
# Install if needed (already installed)
pip install streamlit plotly

# Start dashboard
streamlit run dashboard.py
```

### Demonstration Steps

1. **Show Initial State**
   ```bash
   # Open dashboard (auto-opens in browser)
   streamlit run dashboard.py
   ```
   - Show v1 in Production (baseline)
   - Display current metrics (AUC 0.7088)

2. **Run Workflow in Separate Terminal**
   ```bash
   # New terminal window
   python scripts/run_workflow.py
   ```

3. **Click "🔄 Refresh Data" in Dashboard**
   - After baseline: Same metrics
   - After improved: v3 shows "❌ Rejected" (worse AUC)
   - After best: v4 shows "✅ Promoted" (better AUC)

4. **Show Final State**
   - Production Model: v4
   - AUC: 0.9347
   - Improvement: +31.87%
   - v3 marked as "Rejected"

---

## Dashboard Features

### 📊 Visual Elements
- **Production Model Badge**: Highlighted in green
- **Performance Charts**: Line graph showing progression
- **Promotion Decisions**: Clear ✅/❌ indicators
- **Radar Chart**: Multi-metric comparison
- **Stage Distribution**: Pie chart of model statuses

### 🎯 What to Point Out
1. **Intelligent Rejection**: v3 clearly marked as rejected
2. **Automatic Promotion**: v4 auto-promoted without intervention
3. **Metrics Improvement**: Visual 31.87% improvement
4. **Version Control**: All models tracked and accessible

---

## Side-by-Side Demo (Impressive!)

**Terminal 1: Dashboard**
```bash
streamlit run dashboard.py
```

**Terminal 2: MLflow UI**
```bash
mlflow ui --port 5000
```

**Terminal 3: Workflow**
```bash
python scripts/run_workflow.py
```

**Show instructor:**
- Streamlit: Beautiful metrics and promotion decisions
- MLflow UI: Detailed experiment tracking
- Terminal: Real-time training logs

---

## Screenshots for Report

Take these screenshots from the dashboard:

1. **Before workflow**: v1 in Production
2. **After workflow**: v4 in Production
3. **Rejected model**: v3 with ❌ indicator
4. **Performance chart**: AUC progression
5. **Comparison radar**: All metrics together

---

## Quick Commands Summary

```bash
# 1. Reset to baseline
python scripts/reset_to_baseline.py

# 2. Start dashboard (auto-opens browser)
streamlit run dashboard.py

# 3. In new terminal: Run workflow
python scripts/run_workflow.py

# 4. Refresh dashboard to see updates
# (Click "🔄 Refresh Data" button)

# 5. Check final state
python scripts/check_registry.py
```

---

## Pro Tips

- **Keep dashboard open** during workflow
- **Refresh after each model** trains
- **Use full screen** for presentation (F11)
- **Dark mode available** in Streamlit settings (⋮ menu)
- **Take screenshots** for documentation

---

## Bonus: Deploy Dashboard to Cloud (Optional)

If you want the dashboard accessible online:

```bash
# Add to requirements.txt
echo streamlit >> requirements.txt
echo plotly >> requirements.txt

# Deploy to Streamlit Cloud (free)
# 1. Push to GitHub
# 2. Visit share.streamlit.io
# 3. Connect repo
# 4. Deploy!
```

Your instructor can access it anywhere! 🌐
