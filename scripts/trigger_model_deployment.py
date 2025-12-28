"""
Model Promotion Helper Script

This script should be called after promoting a model to Production in MLflow.
It triggers the GitHub Actions workflow to redeploy the Cloud Run service.
"""

import os
import sys
import subprocess
import argparse
from typing import Optional


def trigger_github_workflow(
    model_version: str,
    repo_owner: str,
    repo_name: str,
    workflow_file: str = "model-promotion.yml",
    github_token: Optional[str] = None
) -> None:
    """
    Trigger GitHub Actions workflow after model promotion.
    
    Args:
        model_version: The version of the promoted model
        repo_owner: GitHub repository owner/organization
        repo_name: GitHub repository name
        workflow_file: Workflow file name
        github_token: GitHub personal access token (optional, uses gh CLI if not provided)
    """
    
    print(f"🔄 Triggering model promotion workflow for version {model_version}")
    
    # Option 1: Use GitHub CLI (recommended)
    try:
        cmd = [
            "gh", "workflow", "run", workflow_file,
            "-f", f"model_version={model_version}",
            "-R", f"{repo_owner}/{repo_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Workflow triggered successfully!")
            print(f"📦 Model version: {model_version}")
            print(f"🔗 View at: https://github.com/{repo_owner}/{repo_name}/actions")
            return
        else:
            print(f"⚠️ gh CLI failed: {result.stderr}")
            print("Falling back to direct API call...")
            
    except FileNotFoundError:
        print("⚠️ GitHub CLI (gh) not found. Install from: https://cli.github.com/")
        print("Falling back to direct API call...")
    
    # Option 2: Use GitHub API directly
    if github_token:
        trigger_via_api(model_version, repo_owner, repo_name, workflow_file, github_token)
    else:
        print("❌ No GitHub token provided. Please either:")
        print("   1. Install GitHub CLI: https://cli.github.com/")
        print("   2. Provide --github-token parameter")
        print("   3. Manually trigger at: https://github.com/{repo_owner}/{repo_name}/actions")
        sys.exit(1)


def trigger_via_api(
    model_version: str,
    repo_owner: str,
    repo_name: str,
    workflow_file: str,
    github_token: str
) -> None:
    """Trigger workflow using GitHub REST API."""
    import requests
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_file}/dispatches"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "ref": "main",
        "inputs": {
            "model_version": model_version
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print(f"✅ Workflow triggered successfully via API!")
        print(f"📦 Model version: {model_version}")
        print(f"🔗 View at: https://github.com/{repo_owner}/{repo_name}/actions")
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Trigger model promotion deployment workflow"
    )
    parser.add_argument(
        "--model-version",
        required=True,
        help="Version of the model promoted to Production"
    )
    parser.add_argument(
        "--repo-owner",
        required=True,
        help="GitHub repository owner (username or organization)"
    )
    parser.add_argument(
        "--repo-name",
        required=True,
        help="GitHub repository name"
    )
    parser.add_argument(
        "--workflow-file",
        default="model-promotion.yml",
        help="Workflow file name (default: model-promotion.yml)"
    )
    parser.add_argument(
        "--github-token",
        help="GitHub personal access token (optional if gh CLI is installed)"
    )
    
    args = parser.parse_args()
    
    trigger_github_workflow(
        model_version=args.model_version,
        repo_owner=args.repo_owner,
        repo_name=args.repo_name,
        workflow_file=args.workflow_file,
        github_token=args.github_token
    )


if __name__ == "__main__":
    main()
