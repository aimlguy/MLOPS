import { pgTable, text, serial, integer, boolean, timestamp, doublePrecision, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === TABLE DEFINITIONS ===
// We'll use this to log predictions and model runs
export const modelRuns = pgTable("model_runs", {
  id: serial("id").primaryKey(),
  runId: text("run_id").notNull(), // MLflow Run ID
  status: text("status").notNull(), // running, completed, failed
  metrics: jsonb("metrics"), // Accuracy, F1, AUC
  parameters: jsonb("parameters"), // XGBoost params
  createdAt: timestamp("created_at").defaultNow(),
});

export const predictions = pgTable("predictions", {
  id: serial("id").primaryKey(),
  // Input features
  gender: text("gender").notNull(),
  scheduledDay: timestamp("scheduled_day").notNull(),
  appointmentDay: timestamp("appointment_day").notNull(),
  age: integer("age").notNull(),
  neighbourhood: text("neighbourhood").notNull(),
  scholarship: boolean("scholarship").default(false),
  hypertension: boolean("hypertension").default(false),
  diabetes: boolean("diabetes").default(false),
  alcoholism: boolean("alcoholism").default(false),
  handicap: integer("handicap").default(0),
  smsReceived: boolean("sms_received").default(false),
  
  // Output
  predictionProbability: doublePrecision("prediction_probability"),
  predictedNoShow: boolean("predicted_no_show"),
  
  createdAt: timestamp("created_at").defaultNow(),
});

// === SCHEMAS ===
export const insertPredictionSchema = createInsertSchema(predictions).omit({ 
  id: true, 
  createdAt: true,
  predictionProbability: true,
  predictedNoShow: true 
});

export const insertModelRunSchema = createInsertSchema(modelRuns).omit({ id: true, createdAt: true });

// === EXPLICIT TYPES ===
export type ModelRun = typeof modelRuns.$inferSelect;
export type InsertModelRun = z.infer<typeof insertModelRunSchema>;

export type Prediction = typeof predictions.$inferSelect;
export type PredictionInput = z.infer<typeof insertPredictionSchema>;

// API Types
export type PredictionResponse = {
  probability: number;
  isNoShow: boolean;
};
