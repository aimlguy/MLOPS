import { z } from 'zod';
import { insertPredictionSchema, insertModelRunSchema, modelRuns, predictions } from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  predictions: {
    predict: {
      method: 'POST' as const,
      path: '/api/predict',
      input: insertPredictionSchema,
      responses: {
        200: z.object({
          probability: z.number(),
          isNoShow: z.boolean(),
        }),
        400: errorSchemas.validation,
      },
    },
    history: {
      method: 'GET' as const,
      path: '/api/predictions/history',
      responses: {
        200: z.array(z.custom<typeof predictions.$inferSelect>()),
      },
    }
  },
  pipeline: {
    runs: {
      method: 'GET' as const,
      path: '/api/pipeline/runs',
      responses: {
        200: z.array(z.custom<typeof modelRuns.$inferSelect>()),
      },
    },
    trigger: {
      method: 'POST' as const,
      path: '/api/pipeline/trigger',
      responses: {
        202: z.object({ message: z.string(), runId: z.string() }),
      },
    }
  }
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}
