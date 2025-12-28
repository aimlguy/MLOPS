# Local deployment test script for Windows

Write-Host "🔧 Building Docker image locally..." -ForegroundColor Cyan
docker build -f docker/Dockerfile -t noshow-predictor:local .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting container on port 8080..." -ForegroundColor Cyan
docker run -d `
  --name noshow-api-test `
  -p 8080:8080 `
  -e MODEL_NAME=noshow-prediction-model `
  -e MLFLOW_TRACKING_URI=file:///app/mlruns `
  noshow-predictor:local

Write-Host "⏳ Waiting for service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "✅ Testing health endpoint..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri http://localhost:8080/health -UseBasicParsing
    Write-Host "Health check response: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    docker stop noshow-api-test
    docker rm noshow-api-test
    exit 1
}

Write-Host ""
Write-Host "🎉 Service is running successfully!" -ForegroundColor Green
Write-Host "📍 Health: http://localhost:8080/health" -ForegroundColor Cyan
Write-Host "🔮 Predict: http://localhost:8080/predict" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop: docker stop noshow-api-test; docker rm noshow-api-test" -ForegroundColor Yellow
