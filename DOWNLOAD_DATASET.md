# Quick Start Guide - Download Real Dataset

## Current Status

✅ Environment set up correctly  
✅ Training scripts ready  
❌ **Dataset is sample only (2 rows) - Need full Kaggle dataset (110K rows)**

## Download the Real Dataset

### Option 1: Automated Download (Recommended)

```bash
# Run the automated downloader
python scripts/download_dataset.py
```

This will:
1. Check if Kaggle CLI is installed (installs if needed)
2. Check for API credentials
3. Download the full dataset automatically
4. Extract and move to correct location
5. Verify the data

### Option 2: Manual Download

If automated download doesn't work:

1. **Go to Kaggle:**
   https://www.kaggle.com/datasets/joniarroba/noshowappointments

2. **Download the dataset:**
   - Click "Download" button (requires free Kaggle account)
   - You'll get `noshowappointments.zip`

3. **Extract the file:**
   - Windows: Right-click → Extract All
   - Mac/Linux: `unzip noshowappointments.zip`
   - You'll get `KaggleV2-May-2016.csv`

4. **Move to correct location:**
   ```bash
   # Windows PowerShell
   Move-Item KaggleV2-May-2016.csv data/raw/noshow.csv -Force
   
   # Mac/Linux
   mv KaggleV2-May-2016.csv data/raw/noshow.csv
   ```

### Option 3: Kaggle CLI (Manual Setup)

```bash
# 1. Install Kaggle CLI
pip install kaggle

# 2. Get API credentials
# Go to: https://www.kaggle.com/settings
# Scroll to "API" section
# Click "Create New API Token"
# This downloads kaggle.json

# 3. Place kaggle.json in correct location
# Windows: C:\Users\<username>\.kaggle\kaggle.json
# Mac/Linux: ~/.kaggle/kaggle.json

# 4. Download dataset
kaggle datasets download -d joniarroba/noshowappointments

# 5. Extract
Expand-Archive noshowappointments.zip  # Windows
unzip noshowappointments.zip          # Mac/Linux

# 6. Move to correct location
mv KaggleV2-May-2016.csv data/raw/noshow.csv
```

## Verify Dataset

After downloading, run:

```bash
python scripts/setup_check.py
```

You should see:
```
✅ Dataset found!
   Rows: 110,527
   Columns: 14
   ✅ ALL CHECKS PASSED - READY TO TRAIN!
```

## Train Models

Once the dataset is downloaded:

```bash
# Train all 3 models at once (~10-20 minutes)
python scripts/run_workflow.py
```

Or train individually:

```bash
python src/train_baseline.py --auto-promote
python src/train_improved.py --auto-promote
python src/train_best.py --auto-promote
```

## View Results

```bash
# Start MLflow UI
mlflow ui --port 5000

# Open browser to http://localhost:5000
```

## Troubleshooting

### Issue: Kaggle API not authenticated

**Solution:**
1. Go to https://www.kaggle.com/settings
2. Create API token
3. Save `kaggle.json` to `C:\Users\<you>\.kaggle\kaggle.json`

### Issue: File too large to download

The dataset is ~25MB. If download fails:
- Check internet connection
- Try manual download from Kaggle website

### Issue: Wrong file

Make sure you have `KaggleV2-May-2016.csv`, not `noshow-appointments.csv` or similar.

## Expected File Structure

After downloading:
```
MLops/
└── data/
    └── raw/
        └── noshow.csv  ← Must be 110,527 rows, 14 columns
```

## Next Actions

1. ✅ Environment ready
2. 📥 **Download dataset** ← You are here
3. 🧪 Run setup check
4. 🚀 Train models
5. 📊 View results

---

**Dataset Link:** https://www.kaggle.com/datasets/joniarroba/noshowappointments  
**File Name:** KaggleV2-May-2016.csv  
**Expected Rows:** 110,527  
**Size:** ~25 MB
