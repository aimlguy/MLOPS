#!/bin/bash
# Local deployment test script

set -e

echo "🔧 Building Docker image locally..."
docker build -f docker/Dockerfile -t noshow-predictor:local .

echo "🚀 Starting container on port 8080..."
docker run -d \
  --name noshow-api-test \
  -p 8080:8080 \
  -e MODEL_NAME=noshow-prediction-model \
  -e MLFLOW_TRACKING_URI=file:///app/mlruns \
  noshow-predictor:local

echo "⏳ Waiting for service to start..."
sleep 5

echo "✅ Testing health endpoint..."
curl -f http://localhost:8080/health || (echo "❌ Health check failed" && exit 1)

echo ""
echo "🎉 Service is running successfully!"
echo "📍 Health: http://localhost:8080/health"
echo "🔮 Predict: http://localhost:8080/predict"
echo ""
echo "To stop: docker stop noshow-api-test && docker rm noshow-api-test"
