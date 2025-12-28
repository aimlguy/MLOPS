import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import * as schema from "@shared/schema";

const sqlite = new Database(process.env.DATABASE_URL || "mlops.db");
export const db = drizzle(sqlite, { schema });
