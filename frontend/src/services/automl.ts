import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1/automl";

export interface AutoMLStartRequest {
  job_id: string;
  target_column?: string;
  training_plan_id?: string;
  parallel_jobs?: number;
  random_seed?: number;
  hyperparameter_strategy?: string;
}

export const startAutoML = async (payload: AutoMLStartRequest) => {
  const response = await axios.post(`${API_BASE}/start`, payload);
  return response.data;
};

export const getAutoMLStatus = async (jobId: string) => {
  const response = await axios.get(`${API_BASE}/${jobId}`);
  return response.data;
};

export const getAutoMLLeaderboard = async (jobId: string) => {
  const response = await axios.get(`${API_BASE}/${jobId}/leaderboard`);
  return response.data;
};

export const getAutoMLReport = async (jobId: string) => {
  const response = await axios.get(`${API_BASE}/${jobId}/report`);
  return response.data;
};
