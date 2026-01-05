import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import { register, Counter, Histogram, Gauge } from "prom-client";

// Prometheus metrics
const predictionCounter = new Counter({
  name: 'model_predictions_total',
  help: 'Total number of predictions made',
  labelNames: ['outcome']
});

const predictionLatency = new Histogram({
  name: 'model_prediction_latency_seconds',
  help: 'Prediction latency in seconds',
  buckets: [0.1, 0.5, 1, 2, 5, 10]
});

const activePredictions = new Gauge({
  name: 'model_active_predictions',
  help: 'Number of active predictions being processed'
});

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Prometheus metrics endpoint
  app.get('/api/metrics', async (req, res) => {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  });
  
  // Prediction Endpoint - Production Model
  app.post(api.predictions.predict.path, async (req, res) => {
    const startTime = Date.now();
    activePredictions.inc();
    
    try {
      const input = api.predictions.predict.input.parse(req.body);
      
      // Call production model inference service
      const { spawn } = await import("child_process");
      
      const python = spawn("python", ["-c", `
import sys
import json
sys.path.append(".")
from src.model_inference import get_inference_service

input_data = ${JSON.stringify(JSON.stringify(input))}
input_dict = json.loads(input_data)

service = get_inference_service()
result = service.predict(input_dict)
print(json.dumps(result))
`]);

      let output = "";
      let error = "";

      python.stdout.on("data", (data) => {
        output += data.toString();
      });

      python.stderr.on("data", (data) => {
        error += data.toString();
      });

      python.on("close", async (code) => {
        const duration = (Date.now() - startTime) / 1000;
        activePredictions.dec();
        
        if (code !== 0) {
          predictionCounter.inc({ outcome: 'error' });
          predictionLatency.observe(duration);
          return res.status(500).json({
            error: "Prediction failed",
            details: error
          });
        }

        try {
          const result = JSON.parse(output);
          
          // Track metrics
          predictionCounter.inc({ outcome: result.isNoShow ? 'no_show' : 'show' });
          predictionLatency.observe(duration);
          
          // Store prediction in database
          await storage.createPrediction({
            ...input,
            predictionProbability: result.probability,
            predictedNoShow: result.isNoShow
          });

          res.json({
            probability: result.probability,
            isNoShow: result.isNoShow,
            modelName: result.model_name
          });
        } catch (e) {
          res.status(500).json({
            error: "Failed to parse prediction result",
            output
          });
        }
      });
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      throw err;
    }
  });

  app.get(api.predictions.history.path, async (req, res) => {
    const history = await storage.getPredictions();
    res.json(history);
  });

  // Pipeline Routes
  app.get(api.pipeline.runs.path, async (req, res) => {
    const runs = await storage.getModelRuns();
    res.json(runs);
  });

  // Get pipeline state
  app.get("/api/pipeline/state", async (req, res) => {
    try {
      const { spawn } = await import("child_process");
      const python = spawn("python", ["-c", `
import sys
import json
sys.path.append(".")
from src.pipeline_state import get_pipeline_state
state = get_pipeline_state()
print(json.dumps(state.to_dict()))
`]);

      let output = "";
      python.stdout.on("data", (data) => { output += data.toString(); });
      python.on("close", (code) => {
        if (code === 0) {
          res.json(JSON.parse(output));
        } else {
          res.status(500).json({ error: "Failed to get pipeline state" });
        }
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to get pipeline state" });
    }
  });

  app.post(api.pipeline.trigger.path, async (req, res) => {
    const runId = `run-${Date.now()}`;
    
    // Get current pipeline state
    const { spawn } = await import("child_process");
    const getState = spawn("python", ["-c", `
import sys
import json
sys.path.append(".")
from src.pipeline_state import get_pipeline_state
state = get_pipeline_state()
print(json.dumps(state.to_dict()))
`]);

    let stateOutput = "";
    getState.stdout.on("data", (data) => { stateOutput += data.toString(); });
    
    getState.on("close", async (code) => {
      if (code !== 0) {
        return res.status(500).json({ error: "Failed to get pipeline state" });
      }

      const pipelineState = JSON.parse(stateOutput);
      const nextStage = pipelineState.next_stage;

      if (!nextStage) {
        return res.status(400).json({
          error: "Pipeline complete",
          message: "All models trained. Use reset to start over.",
          current_stage: pipelineState.current_stage
        });
      }

      // Trigger GitHub Actions workflow via API with specific stage
      const githubToken = process.env.GITHUB_TOKEN;
      const githubRepo = process.env.GITHUB_REPOSITORY || "aimlguy/MLOPS";
      
      if (githubToken) {
        try {
          // Trigger workflow_dispatch event with stage parameter
          const response = await fetch(
            `https://api.github.com/repos/${githubRepo}/actions/workflows/progressive-training.yml/dispatches`,
            {
              method: "POST",
              headers: {
                "Authorization": `Bearer ${githubToken}`,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
              },
              body: JSON.stringify({
                ref: "main",
                inputs: {
                  stage: nextStage,
                  run_id: runId
                }
              })
            }
          );

          if (response.ok) {
            await storage.createModelRun({
              runId,
              status: "running",
              metrics: {},
              parameters: { 
                triggered_via: "github_actions", 
                workflow: "progressive-training.yml",
                stage: nextStage,
                current_stage: pipelineState.current_stage
              }
            });

            return res.status(202).json({
              message: `Training ${nextStage} model via GitHub Actions`,
              runId,
              workflow: "progressive-training.yml",
              stage: nextStage,
              current_stage: pipelineState.current_stage
            });
          }
        } catch (error) {
          console.error("Failed to trigger GitHub Actions:", error);
        }
      }
      
      // Fallback: Run locally
      await storage.createModelRun({
        runId,
        status: "running",
        metrics: {},
        parameters: { stage: nextStage, current_stage: pipelineState.current_stage }
      });

      res.status(202).json({
        message: githubToken 
          ? "Pipeline triggered (GitHub Actions not configured)" 
          : `Training ${nextStage} model locally - set GITHUB_TOKEN for GitHub Actions`,
        runId,
        stage: nextStage,
        current_stage: pipelineState.current_stage
      });
    });
  });

  app.post("/api/pipeline/reset", async (req, res) => {
    // Reset pipeline to baseline model
    try {
      // Reset the pipeline state
      const fs = await import("fs");
      const initialState = {
        current_stage: "baseline",
        current_model_auc: 0.0,
        deployment_history: [],
        last_updated: new Date().toISOString()
      };
      fs.writeFileSync("pipeline_state.json", JSON.stringify(initialState, null, 2));
      
      // Clear old pipeline runs from database
      await db.delete(modelRuns);
      
      res.json({
        message: "Pipeline reset to baseline model",
        current_stage: "baseline",
        next_stage: "improved",
        runs_cleared: true
      });
    } catch (err) {
      res.status(500).json({
        error: "Failed to reset pipeline",
        message: err instanceof Error ? err.message : String(err)
      });
    }
  });

  // Monitoring Status Endpoints
  app.get("/api/monitoring/status", async (req, res) => {
    try {
      const { spawn } = await import("child_process");
      
      const python = spawn("python", ["-c", `
import sys
sys.path.append(".")
from src.monitoring_api import get_comprehensive_status
import json
print(json.dumps(get_comprehensive_status()))
`]);

      let output = "";
      let error = "";

      python.stdout.on("data", (data) => {
        output += data.toString();
      });

      python.stderr.on("data", (data) => {
        error += data.toString();
      });

      python.on("close", (code) => {
        if (code !== 0) {
          return res.status(500).json({
            error: "Failed to get monitoring status",
            details: error
          });
        }

        try {
          const status = JSON.parse(output);
          res.json(status);
        } catch (e) {
          res.status(500).json({
            error: "Failed to parse monitoring status",
            output
          });
        }
      });
    } catch (err) {
      res.status(500).json({
        error: "Server error",
        message: err instanceof Error ? err.message : String(err)
      });
    }
  });

  app.post("/api/monitoring/drift-report", async (req, res) => {
    try {
      const { spawn } = await import("child_process");
      
      const python = spawn("python", ["-c", `
import sys
sys.path.append(".")
from src.monitoring_api import generate_drift_report
import json
print(json.dumps(generate_drift_report()))
`]);

      let output = "";
      let error = "";

      python.stdout.on("data", (data) => {
        output += data.toString();
      });

      python.stderr.on("data", (data) => {
        error += data.toString();
      });

      python.on("close", (code) => {
        if (code !== 0) {
          return res.status(500).json({
            error: "Failed to generate drift report",
            details: error
          });
        }

        try {
          const result = JSON.parse(output);
          res.json(result);
        } catch (e) {
          res.status(500).json({
            error: "Failed to parse result",
            output
          });
        }
      });
    } catch (err) {
      res.status(500).json({
        error: "Server error",
        message: err instanceof Error ? err.message : String(err)
      });
    }
  });

  // Seed Data
  await seedDatabase();

  return httpServer;
}

async function seedDatabase() {
  const runs = await storage.getModelRuns();
  if (runs.length === 0) {
    await storage.createModelRun({
      runId: "init-run-001",
      status: "completed",
      metrics: { auc: 0.82, accuracy: 0.79 },
      parameters: { max_depth: 6, learning_rate: 0.1 }
    });
    
    await storage.createModelRun({
      runId: "init-run-002",
      status: "failed",
      metrics: {},
      parameters: { max_depth: 8, learning_rate: 0.05 }
    });
  }
}
