export type User = {
  id: number;
  email: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type Conversation = {
  id: number;
  title: string;
  created_at: string;
};

export type Message = {
  id: number;
  role: string;
  content: string;
  created_at: string;
};

export type ConversationDetail = Conversation & {
  messages: Message[];
};

export type RAGSource = {
  document_id: number;
  filename: string;
  chunk_index: number;
  score: number;
};

export type ChatResponse = {
  response: string;
  provider: string;
  model?: string | null;
  rag_used: boolean;
  sources: RAGSource[];
};

export type Document = {
  id: number;
  filename: string;
  content_type?: string | null;
  size_bytes: number;
  chunk_count: number;
  created_at: string;
};

export type Memory = {
  id: number;
  category: string;
  key: string;
  value: string;
  source: string;
  confidence: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ProviderStatus = {
  provider: string;
  enabled?: boolean;
  configured?: boolean;
  model?: string;
  [key: string]: unknown;
};

export type WebResult = {
  title: string;
  url: string;
  snippet: string;
  source: string;
  score: number;
};

export type WebSearchResponse = {
  query: string;
  provider: string;
  results: WebResult[];
};

export type HealthResponse = {
  status: string;
  database: boolean;
  redis: boolean;
  redis_enabled: boolean;
  rag_enabled: boolean;
  memory_enabled: boolean;
  security_enabled: boolean;
  observability_enabled: boolean;
  research_enabled: boolean;
};
