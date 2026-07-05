import axios from "axios";
import type { FinalReport } from "../types/workflow";

const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const runAnalysis = async (ciLog: string): Promise<FinalReport> => {
  const response = await apiClient.post<FinalReport>("/analyze", {
    ci_log: ciLog,
  });
  return response.data;
};
