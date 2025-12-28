# GCP Setup Script for Cloud Run Deployment
# Run this script to set up all required GCP resources

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceAccountName = "mlops-deployer",
    
    [Parameter(Mandatory=$false)]
    [string]$ArtifactRepo = "mlops-models"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GCP Cloud Run Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project: $ProjectId" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host ""

# Set project
Write-Host "[1/6] Setting active project..." -ForegroundColor White
gcloud config set project $ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to set project" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Project set" -ForegroundColor Green
Write-Host ""

# Enable APIs
Write-Host "[2/6] Enabling required APIs (this may take a minute)..." -ForegroundColor White
$apis = @(
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK $api" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Failed to enable $api" -ForegroundColor Red
    }
}
Write-Host ""

# Create Artifact Registry
Write-Host "[3/6] Creating Artifact Registry..." -ForegroundColor White
$existingRepo = (gcloud artifacts repositories list --location=$Region --filter="name:$ArtifactRepo" --format="value(name)" 2>$null)

if ($existingRepo) {
    Write-Host "  OK Artifact Registry '$ArtifactRepo' already exists" -ForegroundColor Green
} else {
    gcloud artifacts repositories create $ArtifactRepo `
        --repository-format=docker `
        --location=$Region `
        --description="MLOps Docker images" `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Created '$ArtifactRepo'" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Failed to create Artifact Registry" -ForegroundColor Red
    }
}
Write-Host ""

# Create Service Account for GitHub Actions
Write-Host "[4/6] Creating service account for deployments..." -ForegroundColor White
$existingSA = (gcloud iam service-accounts list --filter="email:$ServiceAccountName@$ProjectId.iam.gserviceaccount.com" --format="value(email)" 2>$null)

if ($existingSA) {
    Write-Host "  OK Service account already exists" -ForegroundColor Green
} else {
    gcloud iam service-accounts create $ServiceAccountName `
        --display-name="MLOps GitHub Actions Deployer" `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Created service account" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Failed to create service account" -ForegroundColor Red
    }
}
Write-Host ""

# Grant permissions
Write-Host "[5/6] Granting IAM permissions..." -ForegroundColor White
$saEmail = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"

$roles = @(
    "roles/run.admin",
    "roles/artifactregistry.writer",
    "roles/iam.serviceAccountUser"
)

foreach ($role in $roles) {
    Write-Host "  Granting $role..." -ForegroundColor Gray
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$saEmail" `
        --role="$role" `
        --quiet >$null 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK $role" -ForegroundColor Green
    }
}
Write-Host ""

# Create service account key
Write-Host "[6/6] Creating service account key..." -ForegroundColor White
$keyFile = "gcp-key-$ServiceAccountName.json"

gcloud iam service-accounts keys create $keyFile `
    --iam-account=$saEmail `
    --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Key created: $keyFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "  WARNING: Keep this file secure!" -ForegroundColor Yellow
    Write-Host "  This file contains credentials for your GCP project" -ForegroundColor Yellow
} else {
    Write-Host "  ERROR Failed to create key" -ForegroundColor Red
}
Write-Host ""

# Create runtime service account
Write-Host "Creating runtime service account..." -ForegroundColor White
$runtimeSA = "noshow-api-runtime"
$existingRuntime = (gcloud iam service-accounts list --filter="email:$runtimeSA@$ProjectId.iam.gserviceaccount.com" --format="value(email)" 2>$null)

if ($existingRuntime) {
    Write-Host "  OK Runtime service account exists" -ForegroundColor Green
} else {
    gcloud iam service-accounts create $runtimeSA `
        --display-name="No-Show API Runtime" `
        --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Created runtime service account" -ForegroundColor Green
    }
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GitHub Secrets to configure:" -ForegroundColor White
Write-Host ""
Write-Host "1. GCP_PROJECT_ID" -ForegroundColor Cyan
Write-Host "   Value: $ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "2. GCP_SA_KEY" -ForegroundColor Cyan
Write-Host "   Value: Contents of $keyFile" -ForegroundColor Gray
Write-Host "   Command: Get-Content $keyFile -Raw | Set-Clipboard" -ForegroundColor Gray
Write-Host ""
Write-Host "3. GCP_SERVICE_ACCOUNT_EMAIL" -ForegroundColor Cyan
Write-Host "   Value: $runtimeSA@$ProjectId.iam.gserviceaccount.com" -ForegroundColor Gray
Write-Host ""
Write-Host "Configure at:" -ForegroundColor White
Write-Host "https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions" -ForegroundColor Blue
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Configure GitHub secrets (above)" -ForegroundColor Gray
Write-Host "  2. Push code to GitHub: git push origin main" -ForegroundColor Gray
Write-Host "  3. Monitor deployment in Actions tab" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
