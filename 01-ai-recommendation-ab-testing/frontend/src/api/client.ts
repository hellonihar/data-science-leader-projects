import axios from "axios";
import type {
  Experiment,
  ExperimentAnalytics,
  ExperimentCreate,
  RecommendationResponse,
} from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export async function getRecommendations(
  userId: string,
  topK: number = 10
): Promise<RecommendationResponse> {
  const { data } = await api.post("/api/recommendations", {
    user_id: userId,
    top_k: topK,
  });
  return data;
}

export async function getExperiments(): Promise<Experiment[]> {
  const { data } = await api.get("/api/experiments");
  return data;
}

export async function createExperiment(
  payload: ExperimentCreate
): Promise<Experiment> {
  const { data } = await api.post("/api/experiments", payload);
  return data;
}

export async function getExperimentAnalytics(
  experimentId: string
): Promise<ExperimentAnalytics> {
  const { data } = await api.get(
    `/api/analytics/experiments/${experimentId}`
  );
  return data;
}
