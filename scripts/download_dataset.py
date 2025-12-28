"""
Dataset Downloader - Automated Kaggle Dataset Download

This script helps download the No-Show Appointments dataset from Kaggle.
"""

import os
import subprocess
import sys
from pathlib import Path


def check_kaggle_cli():
    """Check if Kaggle CLI is installed."""
    try:
        result = subprocess.run(['kaggle', '--version'], capture_output=True, text=True)
        print("✅ Kaggle CLI is installed:", result.stdout.strip())
        return True
    except FileNotFoundError:
        print("❌ Kaggle CLI not found!")
        return False


def check_kaggle_credentials():
    """Check if Kaggle credentials are configured."""
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'
    
    if kaggle_json.exists():
        print(f"✅ Kaggle credentials found: {kaggle_json}")
        return True
    else:
        print(f"❌ Kaggle credentials not found!")
        print(f"   Expected location: {kaggle_json}")
        return False


def download_dataset():
    """Download the No-Show Appointments dataset."""
    print("\n📥 Downloading dataset from Kaggle...")
    
    try:
        # Download dataset
        result = subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', 'joniarroba/noshowappointments'],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Dataset downloaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        print(f"   Error: {e.stderr}")
        return False


def extract_dataset():
    """Extract the downloaded dataset."""
    print("\n📦 Extracting dataset...")
    
    zip_file = 'noshowappointments.zip'
    if not os.path.exists(zip_file):
        print(f"❌ Zip file not found: {zip_file}")
        return False
    
    try:
        if sys.platform == 'win32':
            # Windows - use PowerShell
            subprocess.run(
                ['powershell', '-Command', f'Expand-Archive -Path {zip_file} -DestinationPath . -Force'],
                check=True
            )
        else:
            # Mac/Linux - use unzip
            subprocess.run(['unzip', '-o', zip_file], check=True)
        
        print("✅ Dataset extracted successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Extraction failed: {e}")
        return False


def move_dataset():
    """Move dataset to correct location."""
    print("\n📁 Moving dataset to data/raw/...")
    
    source = 'KaggleV2-May-2016.csv'
    destination = 'data/raw/noshow.csv'
    
    if not os.path.exists(source):
        print(f"❌ Source file not found: {source}")
        return False
    
    # Create directory if needed
    os.makedirs('data/raw', exist_ok=True)
    
    try:
        # Move/rename file
        if os.path.exists(destination):
            print(f"⚠️  Destination file already exists, backing up...")
            os.rename(destination, destination + '.backup')
        
        os.rename(source, destination)
        print(f"✅ Dataset moved to: {destination}")
        return True
    except Exception as e:
        print(f"❌ Move failed: {e}")
        return False


def verify_dataset():
    """Verify the dataset was downloaded correctly."""
    print("\n🔍 Verifying dataset...")
    
    dataset_path = 'data/raw/noshow.csv'
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found: {dataset_path}")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(dataset_path)
        
        print(f"✅ Dataset loaded successfully!")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Size: {os.path.getsize(dataset_path) / 1024 / 1024:.2f} MB")
        print(f"\n   Columns: {', '.join(df.columns.tolist())}")
        
        if len(df) > 100000:
            print(f"\n✅ Dataset looks good! Ready for training.")
            return True
        else:
            print(f"\n⚠️  Dataset seems too small ({len(df)} rows)")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main workflow for dataset download."""
    print("\n" + "="*60)
    print("  KAGGLE DATASET DOWNLOADER")
    print("  No-Show Appointments Dataset")
    print("="*60 + "\n")
    
    # Check if dataset already exists
    if os.path.exists('data/raw/noshow.csv'):
        print("ℹ️  Dataset already exists at data/raw/noshow.csv")
        choice = input("\n   Redownload? (y/n): ").lower()
        if choice != 'y':
            print("\n✅ Using existing dataset.")
            verify_dataset()
            return
    
    # Step 1: Check Kaggle CLI
    if not check_kaggle_cli():
        print("\n📦 Installing Kaggle CLI...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle'], check=True)
            print("✅ Kaggle CLI installed!")
        except subprocess.CalledProcessError:
            print("\n❌ Failed to install Kaggle CLI")
            print("\n💡 Manual installation:")
            print("   pip install kaggle")
            return
    
    # Step 2: Check credentials
    if not check_kaggle_credentials():
        print("\n📝 Setup Kaggle API credentials:")
        print("   1. Go to https://www.kaggle.com/settings")
        print("   2. Scroll to 'API' section")
        print("   3. Click 'Create New API Token'")
        print("   4. Save kaggle.json to:")
        print(f"      {Path.home() / '.kaggle' / 'kaggle.json'}")
        print("\n⚠️  Cannot proceed without credentials!")
        return
    
    # Step 3: Download
    if not download_dataset():
        print("\n💡 Manual download:")
        print("   https://www.kaggle.com/datasets/joniarroba/noshowappointments")
        return
    
    # Step 4: Extract
    if not extract_dataset():
        return
    
    # Step 5: Move to correct location
    if not move_dataset():
        return
    
    # Step 6: Verify
    if not verify_dataset():
        return
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    try:
        if os.path.exists('noshowappointments.zip'):
            os.remove('noshowappointments.zip')
            print("✅ Removed zip file")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n" + "="*60)
    print("  DATASET DOWNLOAD COMPLETE! ✅")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Train models: python scripts/run_workflow.py")
    print("   2. View MLflow: mlflow ui --port 5000")
    print("   3. Check results: reports/evaluation_report.md\n")


if __name__ == '__main__':
    main()
