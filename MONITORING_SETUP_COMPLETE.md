# Prometheus & Grafana Setup Guide
**Date**: December 29, 2025  
**Status**: ✅ FULLY INSTALLED AND RUNNING

## 🎉 Installation Complete!

### Services Running:

1. **Prometheus** - http://localhost:9090 ✅
   - Location: `C:\prometheus\`
   - Config: `C:\prometheus\prometheus.yml`
   - Scraping: `http://localhost:5000/api/metrics` every 30 seconds
   - Alert Rules: `D:\MLops\monitoring\alert_rules.yml`

2. **Grafana** - http://localhost:3000 ✅
   - Service: Running as Windows Service
   - Default Login: `admin / admin`
   - Dashboard JSON: `D:\MLops\monitoring\grafana_dashboard.json`

3. **Express API with Metrics** - http://localhost:5000 ✅
   - Metrics Endpoint: http://localhost:5000/api/metrics
   - Exposing Prometheus metrics:
     - `model_predictions_total` - Counter
     - `model_prediction_latency_seconds` - Histogram
     - `model_active_predictions` - Gauge

---

## 📊 How to Configure Grafana Dashboard

### Step 1: Login to Grafana
1. Open http://localhost:3000
2. Username: `admin`
3. Password: `admin` (you'll be prompted to change it)

### Step 2: Add Prometheus Data Source
1. Click **☰ Menu** (top left) → **Connections** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://localhost:9090`
5. Click **Save & Test** (should show green checkmark)

### Step 3: Import Dashboard
1. Click **☰ Menu** → **Dashboards**
2. Click **New** → **Import**
3. Click **Upload JSON file**
4. Select: `D:\MLops\monitoring\grafana_dashboard.json`
5. Select Prometheus data source
6. Click **Import**

### Step 4: View Your Dashboard
- You should now see 6 panels:
  1. **Prediction Volume** - Rate of predictions over time
  2. **Prediction Latency** - Response time metrics
  3. **Active Predictions** - Current processing load
  4. **No-Show Rate** - Percentage of no-show predictions
  5. **Error Rate** - Failed predictions
  6. **Total Predictions** - Cumulative count

---

## 🧪 Test the System

### Make a Prediction to Generate Metrics:

```powershell
$body = @{
  patient_id = 12345
  gender = "M"
  age = 35
  scheduled_day = "2024-01-15T10:30:00"
  appointment_day = "2024-01-20T14:00:00"
  neighbourhood = "Downtown"
  scholarship = $false
  hypertension = $false
  diabetes = $false
  alcoholism = $false
  handicap = 0
  sms_received = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict" -Method POST -Body $body -ContentType "application/json"
```

### View Metrics:
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/metrics" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Check Prometheus Targets:
1. Go to http://localhost:9090/targets
2. Verify `ml_model_api` shows **UP** status

### Query in Prometheus:
Try these queries in http://localhost:9090/graph:
- `model_predictions_total`
- `rate(model_predictions_total[5m])`
- `histogram_quantile(0.95, rate(model_prediction_latency_seconds_bucket[5m]))`

---

## 🔧 Service Management

### Start Services:
```powershell
# Start Prometheus
Start-Process -FilePath "C:\prometheus\prometheus.exe" -ArgumentList "--config.file=C:\prometheus\prometheus.yml" -WorkingDirectory "C:\prometheus"

# Start Grafana (Windows Service)
Start-Service Grafana

# Start Express API
$env:NODE_ENV='production'; node D:\MLops\dist\index.cjs
```

### Stop Services:
```powershell
# Stop Prometheus
Stop-Process -Name prometheus -Force

# Stop Grafana
Stop-Service Grafana

# Stop Express
Get-Process node | Stop-Process -Force
```

### Check Service Status:
```powershell
# Prometheus
Test-NetConnection -ComputerName localhost -Port 9090 -InformationLevel Quiet

# Grafana
Get-Service Grafana

# Express API
Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet
```

---

## 📈 Metrics Exposed

### Current Metrics (from Express):

```
# Prediction Counter
model_predictions_total{outcome="show"} 
model_predictions_total{outcome="no_show"}
model_predictions_total{outcome="error"}

# Latency Histogram
model_prediction_latency_seconds_bucket{le="0.1"}
model_prediction_latency_seconds_bucket{le="0.5"}
model_prediction_latency_seconds_bucket{le="1"}
model_prediction_latency_seconds_bucket{le="2"}
model_prediction_latency_seconds_bucket{le="5"}
model_prediction_latency_seconds_bucket{le="10"}
model_prediction_latency_seconds_bucket{le="+Inf"}
model_prediction_latency_seconds_sum
model_prediction_latency_seconds_count

# Active Requests Gauge
model_active_predictions
```

---

## 🚨 Alert Rules

Configured in `D:\MLops\monitoring\alert_rules.yml`:

1. **HighPredictionLatency**: Fires if 95th percentile > 0.5s for 5 minutes
2. **DataDriftDetected**: Fires if drift score > 0.15 for 10 minutes
3. **ModelPerformanceDegradation**: Fires if AUC < 0.75 for 15 minutes
4. **LowPredictionVolume**: Fires if rate < 0.1/s for 10 minutes
5. **HighErrorRate**: Fires if error rate > 5% for 5 minutes

View alerts in Prometheus: http://localhost:9090/alerts

---

## ✅ Verification Checklist

- [x] Prometheus installed (`C:\prometheus\`)
- [x] Grafana installed (Windows Service)
- [x] Express API exposing metrics endpoint
- [x] Prometheus scraping metrics (http://localhost:9090/targets)
- [x] Grafana running (http://localhost:3000)
- [x] prom-client installed in Node.js
- [ ] Grafana data source configured (manual step)
- [ ] Dashboard imported in Grafana (manual step)

---

## 🎯 Next Steps

1. **Login to Grafana**: http://localhost:3000 (admin/admin)
2. **Add Prometheus data source** (see Step 2 above)
3. **Import dashboard JSON** (see Step 3 above)
4. **Make predictions** to generate metrics
5. **Watch dashboard update** in real-time

---

## 📝 Files Modified

- ✅ `server/routes.ts` - Added Prometheus metrics
- ✅ `package.json` - Added prom-client dependency
- ✅ `C:\prometheus\prometheus.yml` - Updated to scrape Express API
- ✅ Created metrics endpoint: `/api/metrics`

---

## 🐛 Troubleshooting

### Prometheus not scraping:
- Check targets: http://localhost:9090/targets
- Verify Express API is running on port 5000
- Check firewall settings

### Grafana shows no data:
- Verify Prometheus data source is configured
- Check Prometheus is scraping (should show metrics in http://localhost:9090/graph)
- Make some predictions to generate data

### Metrics endpoint returns 404:
- Rebuild application: `npm run build`
- Restart Express server
- Check http://localhost:5000/api/metrics directly

---

## 🎊 Success!

Your monitoring stack is now fully operational:
- **Prometheus** collecting metrics every 30 seconds
- **Grafana** ready to visualize data
- **Express API** exposing real-time metrics
- **Alert rules** configured and active

**Dashboard will show data once you:**
1. Configure Prometheus data source in Grafana
2. Import the dashboard JSON
3. Make a few predictions to generate metrics
