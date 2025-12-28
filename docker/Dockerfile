# Multi-stage build for production Cloud Run deployment
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ src/
COPY data/ data/

# Create directories for MLflow artifacts
RUN mkdir -p /app/mlruns /app/models

# Environment variables for Cloud Run
ENV MLFLOW_TRACKING_URI=file:///app/mlruns \
    MODEL_NAME=noshow-prediction-model \
    PORT=8080

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')"

# Expose Cloud Run default port
EXPOSE 8080

# Run with production settings
CMD exec uvicorn src.predict:app \
    --host 0.0.0.0 \
    --port ${PORT} \
    --workers 1 \
    --log-level info \
    --no-access-log
