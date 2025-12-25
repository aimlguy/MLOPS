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
  createModelRun(run: InsertModelRun): Promise<ModelRun>;
  getModelRuns(): Promise<ModelRun[]>;
  
  // Predictions
  createPrediction(prediction: InsertPrediction & { predictionProbability: number, predictedNoShow: boolean }): Promise<Prediction>;
  getPredictions(): Promise<Prediction[]>;
}

export class DatabaseStorage implements IStorage {
  async createModelRun(run: InsertModelRun): Promise<ModelRun> {
    const [newRun] = await db.insert(modelRuns).values(run).returning();
    return newRun;
  }

  async getModelRuns(): Promise<ModelRun[]> {
    return await db.select().from(modelRuns).orderBy(desc(modelRuns.createdAt));
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
