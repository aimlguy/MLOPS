"""
Check GitHub Actions deployment status

This helps verify if the automatic deployment to GCP Cloud Run succeeded.
"""

import subprocess
import sys
import json

def check_github_actions():
    """Check latest GitHub Actions workflow run."""
    try:
        # Get latest workflow run
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "1", "--json", "status,conclusion,name,createdAt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            if runs:
                run = runs[0]
                print(f"\n📋 Latest Workflow: {run['name']}")
                print(f"⏰ Started: {run['createdAt']}")
                print(f"📊 Status: {run['status']}")
                print(f"✅ Conclusion: {run.get('conclusion', 'N/A')}")
                
                if run['status'] == 'completed' and run['conclusion'] == 'success':
                    print("\n✅ Deployment succeeded!")
                    print("🔗 Your model should be live at:")
                    print("   https://ethika-rag-model-583756314894.asia-south1.run.app")
                elif run['status'] == 'in_progress':
                    print("\n⏳ Deployment in progress...")
                else:
                    print(f"\n⚠️ Status: {run['status']}")
                
                # Get workflow URL
                run_id_result = subprocess.run(
                    ["gh", "run", "list", "--limit", "1", "--json", "databaseId"],
                    capture_output=True,
                    text=True
                )
                if run_id_result.returncode == 0:
                    run_data = json.loads(run_id_result.stdout)
                    if run_data:
                        print(f"\n🔗 View logs: https://github.com/YOUR-USERNAME/YOUR-REPO/actions/runs/{run_data[0]['databaseId']}")
            else:
                print("No workflow runs found")
        else:
            print("❌ Error: GitHub CLI not found or not authenticated")
            print("💡 Install: https://cli.github.com/")
            print("💡 Or check manually: https://github.com/YOUR-USERNAME/YOUR-REPO/actions")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Alternative: Check deployment manually")
        print("   1. Visit: https://github.com/YOUR-USERNAME/YOUR-REPO/actions")
        print("   2. Look for latest workflow run")
        print("   3. Wait for green checkmark ✅")

def check_cloud_run():
    """Check if Cloud Run service is accessible."""
    print("\n🌐 Checking Cloud Run Service...")
    
    try:
        result = subprocess.run(
            ["curl", "-s", "https://ethika-rag-model-583756314894.asia-south1.run.app/model-info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            print("✅ Cloud Run service is accessible!")
            print(f"📊 Response: {result.stdout}")
        else:
            print("⏳ Service not yet deployed or not responding")
            
    except Exception as e:
        print(f"⚠️ Could not reach service: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("CHECKING DEPLOYMENT STATUS")
    print("="*60)
    
    check_github_actions()
    check_cloud_run()
    
    print("\n" + "="*60)
    print("💡 TIP: Run this script periodically to check deployment progress")
    print("="*60)
