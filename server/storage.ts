import { db } from "./db";
import {
  modelRuns,
  predictions,
  type InsertModelRun,
  type InsertPrediction,
  type ModelRun,
  type Prediction
} from "@shared/schema";
import { desc } from "drizzle-orm";

export interface IStorage {
  // Model Runs
  createModelRun(run: Omit<InsertModelRun, 'metrics' | 'parameters'> & { metrics?: any, parameters?: any }): Promise<ModelRun>;
  getModelRuns(): Promise<ModelRun[]>;
  
  // Predictions
  createPrediction(prediction: InsertPrediction & { predictionProbability: number, predictedNoShow: boolean }): Promise<Prediction>;
  getPredictions(): Promise<Prediction[]>;
}

export class DatabaseStorage implements IStorage {
  db = db;
  
  async createModelRun(run: Omit<InsertModelRun, 'metrics' | 'parameters'> & { metrics?: any, parameters?: any }): Promise<ModelRun> {
    const runWithJsonStrings = {
      ...run,
      metrics: run.metrics ? JSON.stringify(run.metrics) : null,
      parameters: run.parameters ? JSON.stringify(run.parameters) : null,
    };
    const [newRun] = await db.insert(modelRuns).values(runWithJsonStrings).returning();
    return {
      ...newRun,
      metrics: newRun.metrics ? JSON.parse(newRun.metrics as string) : null,
      parameters: newRun.parameters ? JSON.parse(newRun.parameters as string) : null,
    };
  }

  async getModelRuns(): Promise<ModelRun[]> {
    const runs = await db.select().from(modelRuns).orderBy(desc(modelRuns.createdAt));
    return runs.map(run => ({
      ...run,
      metrics: run.metrics ? JSON.parse(run.metrics as string) : null,
      parameters: run.parameters ? JSON.parse(run.parameters as string) : null,
    }));
  }

  async createPrediction(prediction: InsertPrediction & { predictionProbability: number, predictedNoShow: boolean }): Promise<Prediction> {
    const [newPrediction] = await db.insert(predictions).values(prediction).returning();
    return newPrediction;
  }

  async getPredictions(): Promise<Prediction[]> {
    return await db.select().from(predictions).orderBy(desc(predictions.createdAt)).limit(100);
  }
}

export const storage = new DatabaseStorage();
