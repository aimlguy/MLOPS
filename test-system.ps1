# ========================================
# MLOPS PIPELINE VALIDATION SCRIPT
# ========================================
# Tests all components of the MLOps system

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   MLOPS PIPELINE VALIDATION SUITE     " -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$results = @{
    passed = 0
    failed = 0
    warnings = 0
}

function Test-Component {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    Write-Host "`n--- Testing: $Name ---" -ForegroundColor Yellow
    try {
        $result = & $Test
        if ($result) {
            Write-Host "[PASS] $Name" -ForegroundColor Green
            $script:results.passed++
            return $true
        } else {
            Write-Host "[FAIL] $Name" -ForegroundColor Red
            $script:results.failed++
            return $false
        }
    } catch {
        Write-Host "[ERROR] $Name - $_" -ForegroundColor Red
        $script:results.failed++
        return $false
    }
}

# ========================================
# 1. GCP CLOUD RUN API TESTS
# ========================================
Write-Host "`n[CLOUD] TESTING CLOUD RUN DEPLOYMENT" -ForegroundColor Cyan

Test-Component "Cloud Run Health Endpoint" {
    $health = Invoke-RestMethod -Uri "https://noshow-prediction-api-865778656829.asia-south1.run.app/health" -Method GET
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    $health.status -eq "healthy"
}

Test-Component "Cloud Run Prediction Endpoint" {
    $body = @{
        patient_id = 99999
        gender = "M"
        age = 45
        scheduled_day = "2024-06-01T09:00:00"
        appointment_day = "2024-06-05T14:00:00"
        neighbourhood = "CENTRO"
        scholarship = $false
        hypertension = $true
        diabetes = $false
        alcoholism = $false
        handicap = 0
        sms_received = $true
    } | ConvertTo-Json
    
    $prediction = Invoke-RestMethod -Uri "https://noshow-prediction-api-865778656829.asia-south1.run.app/predict" -Method POST -Body $body -ContentType "application/json"
    Write-Host "   Prediction: $($prediction.is_no_show)" -ForegroundColor Gray
    Write-Host "   Probability: $([math]::Round($prediction.probability * 100, 2))%" -ForegroundColor Gray
    Write-Host "   Model: $($prediction.model_name) v$($prediction.model_version)" -ForegroundColor Gray
    $prediction.PSObject.Properties.Name -contains "probability"
}

Test-Component "Cloud Run Model Info Endpoint" {
    $info = Invoke-RestMethod -Uri "https://noshow-prediction-api-865778656829.asia-south1.run.app/model-info" -Method GET
    Write-Host "   Model Name: $($info.name)" -ForegroundColor Gray
    Write-Host "   Model Version: $($info.version)" -ForegroundColor Gray
    $info.PSObject.Properties.Name -contains "name"
}

# ========================================
# 2. LOCAL DEVELOPMENT SERVER TESTS
# ========================================
Write-Host "`n[LOCAL] TESTING LOCAL DEVELOPMENT SERVER" -ForegroundColor Cyan

Test-Component "Local Server Accessibility" {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
    Write-Host "   Status Code: $($response.StatusCode)" -ForegroundColor Gray
    $response.StatusCode -eq 200
}

Test-Component "Local Monitoring API" {
    $status = Invoke-RestMethod -Uri "http://localhost:5000/api/monitoring/status" -Method GET
    Write-Host "   Components checked: $($status.components.Count)" -ForegroundColor Gray
    $status.components.Count -gt 0
}

Test-Component "Local Frontend (React)" {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
    $response.Content -like "*<!DOCTYPE html>*"
}

# ========================================
# 3. FILE SYSTEM CHECKS
# ========================================
Write-Host "`n[FILE] TESTING FILE SYSTEM & STRUCTURE" -ForegroundColor Cyan

Test-Component "Essential Directories Exist" {
    $dirs = @("src", "client", "server", "data", "models", ".github/workflows")
    $missing = @()
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            $missing += $dir
            Write-Host "   [WARN] Missing: $dir" -ForegroundColor Yellow
        }
    }
    if ($missing.Count -eq 0) {
        Write-Host "   All essential directories present" -ForegroundColor Gray
        $true
    } else {
        $false
    }
}

Test-Component "Python Scripts Present" {
    $scripts = @("src/train.py", "src/predict.py", "src/feature_engineering.py")
    $found = 0
    foreach ($script in $scripts) {
        if (Test-Path $script) {
            $found++
        }
    }
    Write-Host "   Found $found/$($scripts.Count) Python scripts" -ForegroundColor Gray
    $found -eq $scripts.Count
}

Test-Component "GitHub Actions Workflows" {
    $workflows = Get-ChildItem ".github/workflows/*.yml" -ErrorAction SilentlyContinue
    Write-Host "   Found $($workflows.Count) workflow files" -ForegroundColor Gray
    foreach ($wf in $workflows) {
        Write-Host "     - $($wf.Name)" -ForegroundColor Gray
    }
    $workflows.Count -ge 3
}

Test-Component "Docker Configuration" {
    $dockerfiles = Get-ChildItem "Dockerfile*" -ErrorAction SilentlyContinue
    Write-Host "   Found $($dockerfiles.Count) Dockerfile(s)" -ForegroundColor Gray
    foreach ($df in $dockerfiles) {
        Write-Host "     - $($df.Name)" -ForegroundColor Gray
    }
    $dockerfiles.Count -gt 0
}

# ========================================
# 4. GIT REPOSITORY STATUS
# ========================================
Write-Host "`n[GIT] TESTING GIT REPOSITORY" -ForegroundColor Cyan

Test-Component "Git Repository Initialized" {
    $isGit = Test-Path ".git"
    if ($isGit) {
        $branch = git branch --show-current
        Write-Host "   Current branch: $branch" -ForegroundColor Gray
    }
    $isGit
}

Test-Component "Git Has Remote Origin" {
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Host "   Remote: $remote" -ForegroundColor Gray
        $true
    } else {
        Write-Host "   No remote configured" -ForegroundColor Yellow
        $false
    }
}

# ========================================
# 5. PYTHON ENVIRONMENT
# ========================================
Write-Host "`n[PYTHON] TESTING PYTHON ENVIRONMENT" -ForegroundColor Cyan

Test-Component "Virtual Environment Exists" {
    $venvExists = Test-Path ".venv"
    if ($venvExists) {
        Write-Host "   Virtual environment found" -ForegroundColor Gray
    }
    $venvExists
}

Test-Component "Python Packages Installed" {
    & .venv\Scripts\Activate.ps1
    $packages = @("fastapi", "uvicorn", "mlflow", "xgboost", "pandas", "numpy")
    $installed = @()
    foreach ($pkg in $packages) {
        $check = python -c "import $pkg; print('$pkg')" 2>$null
        if ($check) {
            $installed += $pkg
        }
    }
    Write-Host "   Installed: $($installed.Count)/$($packages.Count) packages" -ForegroundColor Gray
    $installed.Count -ge 4
}

# ========================================
# 6. NODE/NPM ENVIRONMENT
# ========================================
Write-Host "`n[NODE] TESTING NODE/NPM ENVIRONMENT" -ForegroundColor Cyan

Test-Component "Node.js Installed" {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Host "   Node version: $nodeVersion" -ForegroundColor Gray
        $true
    } else {
        $false
    }
}

Test-Component "NPM Dependencies Installed" {
    $nodeModules = Test-Path "node_modules"
    if ($nodeModules) {
        $pkgCount = (Get-ChildItem "node_modules" -Directory).Count
        Write-Host "   $pkgCount packages in node_modules" -ForegroundColor Gray
    }
    $nodeModules
}

# ========================================
# 7. DATA & MODELS
# ========================================
Write-Host "`n[DATA] TESTING DATA & MODELS" -ForegroundColor Cyan

Test-Component "Training Data Present" {
    $dataFile = "data/raw/noshow.csv"
    $exists = Test-Path $dataFile
    if ($exists) {
        $lines = (Get-Content $dataFile).Count
        Write-Host "   Dataset: $lines lines" -ForegroundColor Gray
    }
    $exists
}

Test-Component "Trained Models Exist" {
    $modelFiles = Get-ChildItem "models/*.pkl" -ErrorAction SilentlyContinue
    Write-Host "   Found $($modelFiles.Count) model file(s)" -ForegroundColor Gray
    foreach ($model in $modelFiles) {
        $sizeMB = [math]::Round($model.Length / 1MB, 2)
        Write-Host "     - $($model.Name) ($sizeMB MB)" -ForegroundColor Gray
    }
    $modelFiles.Count -gt 0
}

# ========================================
# FINAL SUMMARY
# ========================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "        VALIDATION SUMMARY              " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nPASSED:   $($results.passed)" -ForegroundColor Green
Write-Host "FAILED:   $($results.failed)" -ForegroundColor Red
Write-Host "WARNINGS: $($results.warnings)" -ForegroundColor Yellow

$totalTests = $results.passed + $results.failed
$successRate = [math]::Round(($results.passed / $totalTests) * 100, 1)

if ($successRate -ge 80) {
    $rateColor = "Green"
} elseif ($successRate -ge 60) {
    $rateColor = "Yellow"
} else {
    $rateColor = "Red"
}
Write-Host "`nSuccess Rate: $successRate%" -ForegroundColor $rateColor

if ($successRate -ge 90) {
    Write-Host "`nEXCELLENT! System is production-ready!" -ForegroundColor Green
} elseif ($successRate -ge 75) {
    Write-Host "`nGOOD! System is functional with minor issues" -ForegroundColor Yellow
} else {
    Write-Host "`nATTENTION NEEDED! Multiple failures detected" -ForegroundColor Red
}

Write-Host "`nProduction API: https://noshow-prediction-api-865778656829.asia-south1.run.app" -ForegroundColor Cyan
Write-Host "Local Server:   http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
