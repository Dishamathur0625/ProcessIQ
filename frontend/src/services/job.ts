import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface PipelineConfig {
  validation?: boolean;
  cleaning?: boolean;
  feature_engineering?: boolean;
  feature_selection?: boolean;
  visualization?: boolean;
  reports?: boolean;
}

export interface RunPipelineRequest {
  dataset_id: string;
  pipeline: PipelineConfig;
}

export interface JobStatusResponse {
  job_id: string;
  status: "QUEUED" | "RUNNING" | "GENERATING_REPORTS" | "GENERATING_VISUALIZATIONS" | "COMPLETED" | "FAILED" | "CANCELLED";
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  execution_time_ms?: number;
}

export const runPipeline = async (request: RunPipelineRequest): Promise<{ job_id: string; message: string }> => {
  const response = await axios.post(`${API_BASE}/pipeline/run`, request);
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  const response = await axios.get(`${API_BASE}/job/${jobId}`);
  return response.data;
};
