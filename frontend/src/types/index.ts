export interface ChatMessage {
  id: string;
  question: string;
  answer?: string;
  timestamp: Date;
  isLoading?: boolean;
  sources?: string[];
  processingTime?: number;
  error?: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  timestamp: string;
  processing_time: number;
}

export interface ApiError {
  detail: string;
}
