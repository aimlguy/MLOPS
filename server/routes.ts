import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Prediction Endpoint
  app.post(api.predictions.predict.path, async (req, res) => {
    try {
      const input = api.predictions.predict.input.parse(req.body);
      
      // In a real production environment, this would call the Python FastAPI service
      // For this demo, we'll simulate the XGBoost model logic with a simplified heuristic
      // or call a python script using child_process if we had the model trained.
      
      // Simple heuristic for demo purposes (since we can't train the XGBoost model instantly on startup)
      // Factors that increase no-show probability:
      // - Long lead time
      // - Previous no-shows (implied generic risk)
      // - Young age 
      // - No scholarship
      
      const leadTimeMs = new Date(input.appointmentDay).getTime() - new Date(input.scheduledDay).getTime();
      const leadTimeDays = leadTimeMs / (1000 * 60 * 60 * 24);
      
      let score = 0.2; // Base rate
      
      if (leadTimeDays > 10) score += 0.2;
      if (input.age < 30) score += 0.1;
      if (input.alcoholism) score += 0.1;
      if (!input.smsReceived && leadTimeDays > 3) score += 0.1;
      
      // Clamp between 0 and 1
      const probability = Math.min(Math.max(score, 0), 0.95);
      const isNoShow = probability > 0.5;

      const prediction = await storage.createPrediction({
        ...input,
        predictionProbability: probability,
        predictedNoShow: isNoShow
      });

      res.json({
        probability,
        isNoShow
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

  app.post(api.pipeline.trigger.path, async (req, res) => {
    // Simulate triggering an Airflow DAG
    const runId = `run-${Date.now()}`;
    
    await storage.createModelRun({
      runId,
      status: "running",
      metrics: {},
      parameters: { model: "xgboost", n_estimators: 300 }
    });

    // In background, we would update this to completed
    setTimeout(async () => {
      await storage.createModelRun({
        runId: `run-${Date.now()}`,
        status: "completed",
        metrics: { auc: 0.85, f1: 0.78 },
        parameters: { model: "xgboost", n_estimators: 300 }
      });
    }, 5000);

    res.status(202).json({
      message: "Pipeline triggered successfully",
      runId
    });
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
