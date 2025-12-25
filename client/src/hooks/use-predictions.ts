import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type PredictionInput, type PredictionResponse } from "@shared/routes";
import { z } from "zod";

export function usePredictionHistory() {
  return useQuery({
    queryKey: [api.predictions.history.path],
    queryFn: async () => {
      const res = await fetch(api.predictions.history.path);
      if (!res.ok) throw new Error("Failed to fetch history");
      return api.predictions.history.responses[200].parse(await res.json());
    },
  });
}

export function usePredict() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: PredictionInput) => {
      // Validate input before sending, though UI validation handles this mostly
      const validatedData = api.predictions.predict.input.parse(data);
      
      const res = await fetch(api.predictions.predict.path, {
        method: api.predictions.predict.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validatedData),
      });

      if (!res.ok) {
        if (res.status === 400) {
          const error = api.predictions.predict.responses[400].parse(await res.json());
          throw new Error(error.message);
        }
        throw new Error("Prediction failed");
      }

      return api.predictions.predict.responses[200].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.predictions.history.path] });
    },
  });
}
