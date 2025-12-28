import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === TABLE DEFINITIONS ===
// We'll use this to log predictions and model runs
export const modelRuns = sqliteTable("model_runs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  runId: text("run_id").notNull(), // MLflow Run ID
  status: text("status").notNull(), // running, completed, failed
  metrics: text("metrics"), // JSON string of metrics
  parameters: text("parameters"), // JSON string of parameters
  createdAt: integer("created_at", { mode: "timestamp" }).$defaultFn(() => new Date()),
});

export const predictions = sqliteTable("predictions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  // Input features
  gender: text("gender").notNull(),
  scheduledDay: integer("scheduled_day", { mode: "timestamp" }).notNull(),
  appointmentDay: integer("appointment_day", { mode: "timestamp" }).notNull(),
  age: integer("age").notNull(),
  neighbourhood: text("neighbourhood").notNull(),
  scholarship: integer("scholarship", { mode: "boolean" }).default(false),
  hypertension: integer("hypertension", { mode: "boolean" }).default(false),
  diabetes: integer("diabetes", { mode: "boolean" }).default(false),
  alcoholism: integer("alcoholism", { mode: "boolean" }).default(false),
  handicap: integer("handicap").default(0),
  smsReceived: integer("sms_received", { mode: "boolean" }).default(false),
  
  // Output
  predictionProbability: real("prediction_probability"),
  predictedNoShow: integer("predicted_no_show", { mode: "boolean" }),
  
  createdAt: integer("created_at", { mode: "timestamp" }).$defaultFn(() => new Date()),
});

// === SCHEMAS ===
export const insertPredictionSchema = createInsertSchema(predictions).omit({ 
  id: true, 
  createdAt: true,
  predictionProbability: true,
  predictedNoShow: true 
}).extend({
  scheduledDay: z.coerce.date(),
  appointmentDay: z.coerce.date()
});

export const insertModelRunSchema = createInsertSchema(modelRuns).omit({ id: true, createdAt: true });

// === EXPLICIT TYPES ===
export type ModelRun = typeof modelRuns.$inferSelect;
export type InsertModelRun = z.infer<typeof insertModelRunSchema>;

export type Prediction = typeof predictions.$inferSelect;
export type PredictionInput = z.infer<typeof insertPredictionSchema>;
export type InsertPrediction = PredictionInput;

// API Types
export type PredictionResponse = {
  probability: number;
  isNoShow: boolean;
};
