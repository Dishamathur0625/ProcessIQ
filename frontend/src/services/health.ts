import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface HealthStatus {
  api: string;
  postgres: string;
  redis: string;
  worker: string;
}

export const getHealth = async (): Promise<HealthStatus> => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};
