import pandas as pd
import os

print("\n" + "="*60)
print("  DATASET VERIFICATION")
print("="*60 + "\n")

# Check if file exists
dataset_path = 'data/raw/noshow.csv'
if not os.path.exists(dataset_path):
    print(f"❌ Dataset not found: {dataset_path}\n")
    print("📥 Download from:")
    print("   https://www.kaggle.com/datasets/joniarroba/noshowappointments\n")
    print("💡 Or run: python scripts/download_dataset.py\n")
    exit(1)

# Load raw data
print("📊 Loading raw data...")
df_raw = pd.read_csv(dataset_path)
print(f"   Shape: {df_raw.shape}")
print(f"   Size: {os.path.getsize(dataset_path) / 1024 / 1024:.2f} MB")

# Check if it's the real dataset or sample
if len(df_raw) < 10000:
    print(f"\n⚠️  WARNING: Dataset seems to be a SAMPLE ({len(df_raw)} rows)")
    print(f"   Expected: ~110,000 rows")
    print(f"\n   This is NOT the full Kaggle dataset!")
    print(f"   Download the full dataset from:")
    print(f"   https://www.kaggle.com/datasets/joniarroba/noshowappointments\n")
else:
    print(f"   ✅ Full dataset detected ({len(df_raw):,} rows)")

print(f"\n📋 Columns ({len(df_raw.columns)}):")
for col in df_raw.columns:
    print(f"   - {col}")

print(f"\n📈 No-show distribution:")
print(df_raw['No-show'].value_counts())
print(f"   No-show rate: {(df_raw['No-show'] == 'Yes').mean():.2%}")

print(f"\n🔍 Sample data:")
print(df_raw.head(3))

# Quick stats
print(f"\n📊 Quick Statistics:")
print(f"   Age range: {df_raw['Age'].min()} - {df_raw['Age'].max()}")
print(f"   Gender distribution: {df_raw['Gender'].value_counts().to_dict()}")
print(f"   SMS received: {df_raw['SMS_received'].sum():,} / {len(df_raw):,} ({df_raw['SMS_received'].mean():.1%})")

# Check for issues
issues = []
if df_raw['Age'].min() < 0:
    issues.append("Negative ages found")
if df_raw['Age'].max() > 120:
    issues.append("Ages > 120 found")
if df_raw.isnull().sum().sum() > 0:
    issues.append(f"Missing values: {df_raw.isnull().sum().sum()}")

if issues:
    print(f"\n⚠️  Data Quality Issues:")
    for issue in issues:
        print(f"   - {issue}")
else:
    print(f"\n✅ No obvious data quality issues detected")

print("\n" + "="*60)
if len(df_raw) >= 100000:
    print("  ✅ DATASET READY FOR TRAINING!")
    print("="*60)
    print("\n💡 Next: python scripts/run_workflow.py\n")
else:
    print("  ⚠️  SAMPLE DATASET - NOT RECOMMENDED")
    print("="*60)
    print("\n📥 Download full dataset first!\n")
