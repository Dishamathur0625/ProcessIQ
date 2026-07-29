import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1/planner";

export interface PlannerRequest {
  job_id: string;
  target_column?: string;
}

export const getTargetCandidates = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/target-candidates`, payload);
  return response.data; // { candidates: [...] }
};

export const detectTask = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/task-detection`, payload);
  return response.data; // { detected_task: "..." }
};

export const analyzeReadiness = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/readiness`, payload);
  return response.data; // { readiness_score: 95, is_ready: true, issues: [...] }
};

export const recommendModels = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/recommend-models`, payload);
  return response.data; // { recommended_models: [...] }
};

export const generateEvaluationPlan = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/evaluation-plan`, payload);
  return response.data; // { cross_validation: "...", metrics: [...] }
};

export const generateTrainingPlan = async (payload: PlannerRequest) => {
  const response = await axios.post(`${API_BASE}/training-plan`, payload);
  return response.data; // { metadata: {...}, configuration: {...} }
};
