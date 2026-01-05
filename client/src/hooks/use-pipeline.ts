import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@shared/routes";

export function usePipelineRuns() {
  return useQuery({
    queryKey: [api.pipeline.runs.path],
    queryFn: async () => {
      const res = await fetch(api.pipeline.runs.path);
      if (!res.ok) throw new Error("Failed to fetch pipeline runs");
      return api.pipeline.runs.responses[200].parse(await res.json());
    },
  });
}

export function usePipelineState() {
  return useQuery({
    queryKey: ["/api/pipeline/state"],
    queryFn: async () => {
      const res = await fetch("/api/pipeline/state");
      if (!res.ok) throw new Error("Failed to fetch pipeline state");
      return res.json();
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}

export function useTriggerPipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const res = await fetch(api.pipeline.trigger.path, {
        method: api.pipeline.trigger.method,
      });

      if (!res.ok) throw new Error("Failed to trigger pipeline");
      return api.pipeline.trigger.responses[202].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.pipeline.runs.path] });
      queryClient.invalidateQueries({ queryKey: ["/api/pipeline/state"] });
    },
  });
}

export function useResetPipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/pipeline/reset", {
        method: "POST",
      });

      if (!res.ok) throw new Error("Failed to reset pipeline");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.pipeline.runs.path] });
      queryClient.invalidateQueries({ queryKey: ["/api/pipeline/state"] });
    },
  });
}

