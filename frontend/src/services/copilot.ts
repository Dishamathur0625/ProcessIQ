import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1/copilot";

export interface CopilotRequestPayload {
  job_id: string;
  question?: string;
  context_keys?: string[];
}

export const understandDataset = async (payload: CopilotRequestPayload) => {
  const response = await axios.post(`${API_BASE}/dataset-understanding`, payload);
  return response.data;
};

export const suggestPipeline = async (payload: CopilotRequestPayload) => {
  const response = await axios.post(`${API_BASE}/pipeline-suggestion`, payload);
  return response.data;
};

export const explainChart = async (payload: CopilotRequestPayload) => {
  const response = await axios.post(`${API_BASE}/explain-chart`, payload);
  return response.data;
};

export const explainReport = async (payload: CopilotRequestPayload) => {
  const response = await axios.post(`${API_BASE}/explain-report`, payload);
  return response.data;
};

export const chatCopilot = async (payload: CopilotRequestPayload) => {
  const response = await axios.post(`${API_BASE}/chat`, payload);
  return response.data;
};

export interface InteractiveTransformPayload {
  job_id: string;
  user_intent: string;
  dataset_path: string;
  output_path: string;
}

export const interactiveTransform = async (payload: InteractiveTransformPayload) => {
  const response = await axios.post(`${API_BASE}/interactive-transform`, payload);
  return response.data;
};
