import axios from "axios";
import { ChatResponse, ApiError } from "../types";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    "Content-Type": "application/json",
  },
});

export class ChatService {
  static async sendMessage(question: string): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>("/chat", {
        question: question.trim(),
        timestamp: new Date().toISOString(),
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const apiError = error.response?.data as ApiError;
        throw new Error(apiError?.detail || "Failed to send message");
      }
      throw new Error("Network error occurred");
    }
  }

  static async checkHealth(): Promise<boolean> {
    try {
      const response = await api.get("/health");
      return response.data.rag_system_loaded;
    } catch (error) {
      return false;
    }
  }

  static async getSources(): Promise<string[]> {
    try {
      const response = await api.get("/sources");
      return response.data.sources || [];
    } catch (error) {
      return [];
    }
  }
}

export default ChatService;
