# Cloud Run Deployment Verification Script
# Run this to verify your setup before deploying

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host " Cloud Run Deployment Verification"  -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

function Test-Cmd {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check Prerequisites
Write-Host "[1/7] Checking Prerequisites..." -ForegroundColor White
Write-Host ""

# gcloud CLI
if (Test-Cmd "gcloud") {
    Write-Host "  OK gcloud CLI installed" -ForegroundColor Green
    $account = (gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null)
    if ($account) {
        Write-Host "  OK Authenticated as: $account" -ForegroundColor Green
    } else {
        Write-Host "  WARNING Not authenticated. Run: gcloud auth login" -ForegroundColor Yellow
        $warnings += "gcloud not authenticated"
    }
    $project = (gcloud config get-value project 2>$null)
    if ($project) {
        Write-Host "  OK Active project: $project" -ForegroundColor Green
        $script:PROJECT_ID = $project
    } else {
        Write-Host "  WARNING No active project" -ForegroundColor Yellow
        $warnings += "No GCP project set"
    }
} else {
    Write-Host "  ERROR gcloud CLI not found" -ForegroundColor Red
    $issues += "gcloud CLI missing"
}

# Docker
if (Test-Cmd "docker") {
    Write-Host "  OK Docker installed" -ForegroundColor Green
    docker ps >$null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Docker daemon running" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Docker daemon not running" -ForegroundColor Red
        $issues += "Docker not running"
    }
} else {
    Write-Host "  ERROR Docker not found" -ForegroundColor Red
    $issues += "Docker missing"
}

# Git
if (Test-Cmd "git") {
    Write-Host "  OK Git installed" -ForegroundColor Green
} else {
    Write-Host "  ERROR Git not found" -ForegroundColor Red
    $issues += "Git missing"
}

Write-Host ""

# Check Files
Write-Host "[2/7] Checking Required Files..." -ForegroundColor White
Write-Host ""

$files = @(
    "requirements.txt",
    "docker/Dockerfile",
    ".dockerignore",
    ".github/workflows/deploy-gcp.yml",
    "src/predict.py",
    "src/train.py"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  OK $file" -ForegroundColor Green
    } else {
        Write-Host "  ERROR $file missing" -ForegroundColor Red
        $issues += "$file missing"
    }
}

Write-Host ""

# Check Docker Configuration
Write-Host "[3/7] Checking Docker Configuration..." -ForegroundColor White
Write-Host ""

if (Test-Path "docker/Dockerfile") {
    $content = Get-Content "docker/Dockerfile" -Raw
    if ($content -match "python:3\.11") {
        Write-Host "  OK Python 3.11 image" -ForegroundColor Green
    }
    if ($content -match "EXPOSE 8080") {
        Write-Host "  OK Port 8080 exposed" -ForegroundColor Green
    }
    if ($content -match "uvicorn") {
        Write-Host "  OK uvicorn configured" -ForegroundColor Green
    }
}

Write-Host ""

# Check Python Dependencies
Write-Host "[4/7] Checking Python Dependencies..." -ForegroundColor White
Write-Host ""

if (Test-Path "requirements.txt") {
    $reqs = Get-Content "requirements.txt" -Raw
    $packages = @("mlflow", "fastapi", "uvicorn", "xgboost", "pandas")
    foreach ($pkg in $packages) {
        if ($reqs -match $pkg) {
            Write-Host "  OK $pkg" -ForegroundColor Green
        } else {
            Write-Host "  ERROR $pkg missing" -ForegroundColor Red
            $issues += "$pkg not in requirements.txt"
        }
    }
}

Write-Host ""

# Check GCP Setup
Write-Host "[5/7] Checking GCP Configuration..." -ForegroundColor White
Write-Host ""

if ($script:PROJECT_ID) {
    Write-Host "  Project: $script:PROJECT_ID" -ForegroundColor Cyan
    
    $apis = @("run.googleapis.com", "artifactregistry.googleapis.com")
    foreach ($api in $apis) {
        $enabled = (gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null)
        if ($enabled) {
            Write-Host "  OK $api enabled" -ForegroundColor Green
        } else {
            Write-Host "  WARNING $api not enabled" -ForegroundColor Yellow
            $warnings += "$api not enabled"
        }
    }
} else {
    Write-Host "  WARNING Cannot check without active project" -ForegroundColor Yellow
}

Write-Host ""

# Check GitHub
Write-Host "[6/7] Checking GitHub Configuration..." -ForegroundColor White
Write-Host ""

try {
    $remote = (git remote get-url origin 2>$null)
    if ($remote -match "github\.com") {
        Write-Host "  OK GitHub repository configured" -ForegroundColor Green
        Write-Host "  INFO Required secrets:" -ForegroundColor Cyan
        Write-Host "       - GCP_PROJECT_ID" -ForegroundColor Gray
        Write-Host "       - GCP_SA_KEY" -ForegroundColor Gray
        Write-Host "       - GCP_SERVICE_ACCOUNT_EMAIL" -ForegroundColor Gray
    } else {
        Write-Host "  WARNING Not a GitHub repository" -ForegroundColor Yellow
        $warnings += "Not a GitHub repo"
    }
} catch {
    Write-Host "  WARNING Could not check repository" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "[7/7] Summary" -ForegroundColor White
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "  SUCCESS No critical issues!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test local build: .\scripts\test-local-deployment.ps1" -ForegroundColor White
    Write-Host "  2. Set up GCP: See docs/GCP_DEPLOYMENT_GUIDE.md" -ForegroundColor White
    Write-Host "  3. Configure GitHub secrets" -ForegroundColor White
    Write-Host "  4. Push to deploy: git push origin main" -ForegroundColor White
} else {
    Write-Host "  ISSUES FOUND: $($issues.Count)" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "    - $issue" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "  WARNINGS: $($warnings.Count)" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "    - $warning" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
