# Dataset Setup Guide

## Download the Kaggle Dataset

This project uses the **No Show Appointments** dataset from Kaggle.

### Option 1: Using Kaggle CLI (Recommended)

1. **Install Kaggle CLI:**
   ```bash
   pip install kaggle
   ```

2. **Setup Kaggle API credentials:**
   - Go to https://www.kaggle.com/settings
   - Scroll to "API" section
   - Click "Create New API Token"
   - Save `kaggle.json` to:
     - Windows: `C:\Users\<username>\.kaggle\kaggle.json`
     - Mac/Linux: `~/.kaggle/kaggle.json`

3. **Download dataset:**
   ```bash
   # Download and extract
   kaggle datasets download -d joniarroba/noshowappointments
   
   # Unzip (Windows PowerShell)
   Expand-Archive noshowappointments.zip -DestinationPath .
   
   # Unzip (Mac/Linux)
   unzip noshowappointments.zip
   
   # Move to correct location
   mv KaggleV2-May-2016.csv data/raw/noshow.csv
   ```

### Option 2: Manual Download

1. Go to https://www.kaggle.com/datasets/joniarroba/noshowappointments
2. Click "Download" button (requires Kaggle account)
3. Extract `KaggleV2-May-2016.csv`
4. Place in `data/raw/noshow.csv`

## Dataset Information

- **File:** KaggleV2-May-2016.csv
- **Size:** ~110,000 appointments
- **Period:** April-June 2016
- **Location:** Brazil
- **Target:** No-show (Yes/No)

### Columns

| Column | Description |
|--------|-------------|
| PatientId | Unique patient identifier |
| AppointmentID | Unique appointment identifier |
| Gender | M/F |
| ScheduledDay | When appointment was scheduled |
| AppointmentDay | Actual appointment date |
| Age | Patient age |
| Neighbourhood | Location |
| Scholarship | Has welfare scholarship (0/1) |
| Hipertension | Has hypertension (0/1) |
| Diabetes | Has diabetes (0/1) |
| Alcoholism | Has alcoholism (0/1) |
| Handcap | Handicap level (0-4) |
| SMS_received | Got SMS reminder (0/1) |
| No-show | Target - Did not attend (Yes/No) |

## Verify Dataset

After downloading, verify the file:

```bash
# Check file exists
ls -l data/raw/noshow.csv

# Check size (should be ~110K rows)
python -c "import pandas as pd; df = pd.read_csv('data/raw/noshow.csv'); print(f'Rows: {len(df)}, Columns: {len(df.columns)}')"
```

Expected output:
```
Rows: 110527, Columns: 14
```

## Troubleshooting

### Issue: Kaggle CLI not authenticated

**Solution:**
- Ensure `kaggle.json` is in the correct location
- Check file permissions: `chmod 600 ~/.kaggle/kaggle.json` (Mac/Linux)

### Issue: File too large for Git

The dataset file is already in `.gitignore`. If you accidentally committed it:

```bash
git rm --cached data/raw/noshow.csv
git commit -m "Remove dataset from Git"
```

### Issue: Wrong file name

The code expects `data/raw/noshow.csv`. If you downloaded with a different name:

```bash
# Windows
ren KaggleV2-May-2016.csv noshow.csv

# Mac/Linux
mv KaggleV2-May-2016.csv data/raw/noshow.csv
```

## Next Steps

Once the dataset is downloaded:

1. **Test data loading:**
   ```bash
   python scripts/check_data.py
   ```

2. **Train models:**
   ```bash
   python scripts/run_workflow.py
   ```

3. **Start MLflow UI:**
   ```bash
   mlflow ui --port 5000
   ```

---

**Dataset Source:** [Kaggle - No Show Appointments](https://www.kaggle.com/datasets/joniarroba/noshowappointments)  
**License:** CC0: Public Domain
