# GitHub Secrets Configuration

## 🔐 Required Secrets

Go to: **https://github.com/discount-Pieter-Levels/MLops/settings/secrets/actions**

Click **"New repository secret"** for each of the following:

---

### Secret 1: GCP_PROJECT_ID

**Name:** `GCP_PROJECT_ID`

**Value:**
```
ethika-rag-model
```

---

### Secret 2: GCP_SA_KEY

**Name:** `GCP_SA_KEY`

**Value:** The service account key JSON has been copied to your clipboard!

Just paste (Ctrl+V) into the secret value field.

If you need to copy it again:
```powershell
Get-Content gcp-key-mlops-deployer.json -Raw | Set-Clipboard
```

---

### Secret 3: GCP_SERVICE_ACCOUNT_EMAIL

**Name:** `GCP_SERVICE_ACCOUNT_EMAIL`

**Value:**
```
noshow-api-runtime@ethika-rag-model.iam.gserviceaccount.com
```

---

## ✅ Verification

After adding all three secrets, they should appear in your repository secrets list:
- ✓ GCP_PROJECT_ID
- ✓ GCP_SA_KEY
- ✓ GCP_SERVICE_ACCOUNT_EMAIL

---

## 🚀 Ready to Deploy!

Once secrets are configured:

```powershell
git add .
git commit -m "feat: Deploy to Cloud Run with dynamic model loading"
git push origin main
```

GitHub Actions will automatically:
1. Run CI tests
2. Build Docker image
3. Push to Artifact Registry
4. Deploy to Cloud Run
5. Output service URL

Monitor at: https://github.com/discount-Pieter-Levels/MLops/actions
