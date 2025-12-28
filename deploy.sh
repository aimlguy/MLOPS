#!/bin/bash

# Quick Deployment Script for MLOps Project
# This script automates the complete deployment process

set -e  # Exit on error

echo "🚀 MLOps Production Deployment Script"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if user wants to skip certain steps
SKIP_GIT=${SKIP_GIT:-false}
SKIP_VERCEL=${SKIP_VERCEL:-false}
SKIP_GCP=${SKIP_GCP:-false}

# Step 1: Git Push
if [ "$SKIP_GIT" = false ]; then
  echo -e "\n${BLUE}Step 1: Pushing to GitHub${NC}"
  echo "-------------------------------"
  
  # Check if git repo exists
  if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git remote add origin https://github.com/discount-Pieter-Levels/MLops.git
  fi
  
  # Add all files
  git add .
  
  # Commit
  read -p "Enter commit message (default: 'Production deployment'): " COMMIT_MSG
  COMMIT_MSG=${COMMIT_MSG:-"Production deployment"}
  git commit -m "$COMMIT_MSG" || echo "No changes to commit"
  
  # Push
  echo "Pushing to GitHub..."
  git push -u origin main --force
  
  echo -e "${GREEN}✅ Code pushed to GitHub${NC}"
else
  echo -e "${BLUE}Skipping GitHub push${NC}"
fi

# Step 2: Deploy to GCP Cloud Run
if [ "$SKIP_GCP" = false ]; then
  echo -e "\n${BLUE}Step 2: Deploying Backend to Google Cloud Run${NC}"
  echo "----------------------------------------------"
  
  # Check if gcloud is installed
  if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
  fi
  
  # Check if logged in
  if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "Please login to Google Cloud..."
    gcloud auth login
  fi
  
  # Get current project
  PROJECT_ID=$(gcloud config get-value project)
  echo "Current GCP Project: $PROJECT_ID"
  
  read -p "Continue with this project? (y/n): " CONTINUE
  if [ "$CONTINUE" != "y" ]; then
    read -p "Enter GCP Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
  fi
  
  echo "Building and deploying to Cloud Run..."
  gcloud builds submit --config cloudbuild.yaml
  
  # Get the service URL
  GCP_URL=$(gcloud run services describe mlops-backend --region us-central1 --format='value(status.url)')
  echo -e "${GREEN}✅ Backend deployed to: $GCP_URL${NC}"
  
  # Save URL for Vercel deployment
  echo "$GCP_URL" > .gcp-url
else
  echo -e "${BLUE}Skipping GCP deployment${NC}"
  
  # Check if URL exists from previous deployment
  if [ -f ".gcp-url" ]; then
    GCP_URL=$(cat .gcp-url)
  else
    read -p "Enter your GCP Cloud Run URL: " GCP_URL
  fi
fi

# Step 3: Deploy to Vercel
if [ "$SKIP_VERCEL" = false ]; then
  echo -e "\n${BLUE}Step 3: Deploying Frontend to Vercel${NC}"
  echo "--------------------------------------"
  
  # Check if vercel is installed
  if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm i -g vercel
  fi
  
  # Update vercel.json with backend URL
  if [ ! -z "$GCP_URL" ]; then
    echo "Updating vercel.json with backend URL: $GCP_URL"
    cat > vercel.json << EOF
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist/public",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "$GCP_URL/api/\$1"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    }
  ]
}
EOF
  fi
  
  echo "Deploying to Vercel..."
  vercel --prod --yes
  
  echo -e "${GREEN}✅ Frontend deployed to Vercel${NC}"
else
  echo -e "${BLUE}Skipping Vercel deployment${NC}"
fi

# Summary
echo -e "\n${GREEN}======================================"
echo "🎉 Deployment Complete!"
echo "======================================${NC}"

if [ ! -z "$GCP_URL" ]; then
  echo -e "Backend (GCP): ${BLUE}$GCP_URL${NC}"
fi

echo -e "\nNext steps:"
echo "1. Visit your Vercel dashboard to get the frontend URL"
echo "2. Set GITHUB_TOKEN in GCP Cloud Run environment variables"
echo "3. Test the production deployment"
echo ""
echo "To set GitHub token in GCP:"
echo "  gcloud run services update mlops-backend \\"
echo "    --region us-central1 \\"
echo "    --update-env-vars GITHUB_TOKEN=your_token_here"
