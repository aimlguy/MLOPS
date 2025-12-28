# Quick Deployment Script for Windows (PowerShell)
# MLOps Production Deployment

param(
    [switch]$SkipGit,
    [switch]$SkipGCP,
    [switch]$SkipVercel
)

Write-Host "🚀 MLOps Production Deployment Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Step 1: Git Push
if (-not $SkipGit) {
    Write-Host "`n📦 Step 1: Pushing to GitHub" -ForegroundColor Blue
    Write-Host "-------------------------------" -ForegroundColor Blue
    
    # Check if git repo exists
    if (-not (Test-Path ".git")) {
        Write-Host "Initializing git repository..."
        git init
        git remote add origin https://github.com/discount-Pieter-Levels/MLops.git
    }
    
    # Add all files
    git add .
    
    # Commit
    $commitMsg = Read-Host "Enter commit message (default: 'Production deployment')"
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "Production deployment"
    }
    git commit -m $commitMsg
    
    # Push
    Write-Host "Pushing to GitHub..."
    git push -u origin main --force
    
    Write-Host "✅ Code pushed to GitHub" -ForegroundColor Green
} else {
    Write-Host "Skipping GitHub push" -ForegroundColor Yellow
}

# Step 2: Deploy to GCP Cloud Run
if (-not $SkipGCP) {
    Write-Host "`n☁️ Step 2: Deploying Backend to Google Cloud Run" -ForegroundColor Blue
    Write-Host "----------------------------------------------" -ForegroundColor Blue
    
    # Check if gcloud is installed
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Host "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
        exit 1
    }
    
    # Get current project
    $projectId = gcloud config get-value project 2>$null
    Write-Host "Current GCP Project: $projectId"
    
    $continue = Read-Host "Continue with this project? (y/n)"
    if ($continue -ne "y") {
        $projectId = Read-Host "Enter GCP Project ID"
        gcloud config set project $projectId
    }
    
    Write-Host "Building and deploying to Cloud Run..."
    gcloud builds submit --config cloudbuild.yaml
    
    # Get the service URL
    $gcpUrl = gcloud run services describe mlops-backend --region us-central1 --format='value(status.url)' 2>$null
    Write-Host "✅ Backend deployed to: $gcpUrl" -ForegroundColor Green
    
    # Save URL for Vercel deployment
    $gcpUrl | Out-File -FilePath ".gcp-url" -Encoding utf8
} else {
    Write-Host "Skipping GCP deployment" -ForegroundColor Yellow
    
    # Check if URL exists from previous deployment
    if (Test-Path ".gcp-url") {
        $gcpUrl = Get-Content ".gcp-url" -Raw
        $gcpUrl = $gcpUrl.Trim()
    } else {
        $gcpUrl = Read-Host "Enter your GCP Cloud Run URL"
    }
}

# Step 3: Deploy to Vercel
if (-not $SkipVercel) {
    Write-Host "`n🌐 Step 3: Deploying Frontend to Vercel" -ForegroundColor Blue
    Write-Host "--------------------------------------" -ForegroundColor Blue
    
    # Check if vercel is installed
    if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Vercel CLI..."
        npm i -g vercel
    }
    
    # Update vercel.json with backend URL
    if (-not [string]::IsNullOrWhiteSpace($gcpUrl)) {
        Write-Host "Updating vercel.json with backend URL: $gcpUrl"
        $vercelConfig = @"
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist/public",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "$gcpUrl/api/`$1"
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
"@
        $vercelConfig | Out-File -FilePath "vercel.json" -Encoding utf8
    }
    
    Write-Host "Deploying to Vercel..."
    vercel --prod --yes
    
    Write-Host "✅ Frontend deployed to Vercel" -ForegroundColor Green
} else {
    Write-Host "Skipping Vercel deployment" -ForegroundColor Yellow
}

# Summary
Write-Host "`n======================================" -ForegroundColor Green
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

if (-not [string]::IsNullOrWhiteSpace($gcpUrl)) {
    Write-Host "Backend (GCP): $gcpUrl" -ForegroundColor Cyan
}

Write-Host "`nNext steps:"
Write-Host "1. Visit your Vercel dashboard to get the frontend URL"
Write-Host "2. Set GITHUB_TOKEN in GCP Cloud Run environment variables"
Write-Host "3. Test the production deployment"
Write-Host ""
Write-Host "To set GitHub token in GCP:"
Write-Host "  gcloud run services update mlops-backend \"
Write-Host "    --region us-central1 \"
Write-Host "    --update-env-vars GITHUB_TOKEN=your_token_here"
