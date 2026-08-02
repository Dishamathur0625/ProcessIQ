import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const getReports = async (jobId: string): Promise<any> => {
  const response = await axios.get(`${API_BASE}/reports/${jobId}`);
  return response.data;
};

export const getVisualizations = async (jobId: string): Promise<any> => {
  const response = await axios.get(`${API_BASE}/visualizations/${jobId}`);
  return response.data;
};

export const getDownloadUrl = (jobId: string): string => {
  return `${API_BASE}/download/${jobId}`;
};

export const getEdaStats = async (jobId: string): Promise<any> => {
  const response = await axios.post(`${API_BASE}/copilot/eda-stats`, { job_id: jobId });
  return response.data;
};
