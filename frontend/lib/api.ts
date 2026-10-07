import { clearToken, getToken } from "./auth";
import type {
  ChatResponse,
  Conversation,
  ConversationDetail,
  Document,
  HealthResponse,
  Memory,
  ProviderStatus,
  TokenResponse,
  User,
  WebSearchResponse,
} from "../types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

type RequestOptions = RequestInit & {
  auth?: boolean;
};

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (options.auth !== false) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("evu:auth-expired"));
    }
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // Keep the HTTP status message.
    }
    throw new Error(detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function register(email: string, password: string): Promise<User> {
  return request<User>("/api/v1/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password }),
  });
}

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  return request<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    auth: false,
    body,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
}

export async function me(): Promise<User> {
  return request<User>("/api/v1/auth/me");
}

export async function health(): Promise<HealthResponse> {
  return request<HealthResponse>("/health", { auth: false });
}

export async function listConversations(): Promise<Conversation[]> {
  return request<Conversation[]>("/api/v1/conversations");
}

export async function createConversation(
  title = "New conversation",
): Promise<Conversation> {
  return request<Conversation>("/api/v1/conversations", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getConversation(
  id: number,
): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/api/v1/conversations/${id}`);
}

export async function sendConversationMessage(
  id: number,
  message: string,
  provider: string,
  model: string | null,
  useRag: boolean,
): Promise<ChatResponse> {
  return request<ChatResponse>(`/api/v1/conversations/${id}/chat`, {
    method: "POST",
    body: JSON.stringify({
      message,
      provider,
      model,
      use_rag: useRag,
    }),
  });
}

export async function streamConversation(
  id: number,
  message: string,
  provider: string,
  model: string | null,
  useRag: boolean,
  onDelta: (delta: string) => void,
): Promise<void> {
  const token = getToken();
  const response = await fetch(`${API_URL}/api/v1/conversations/${id}/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      message,
      provider,
      model,
      use_rag: useRag,
    }),
  });

  if (response.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("evu:auth-expired"));
    }
  }

  if (!response.ok) {
    let detail = `Streaming request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {}
    throw new Error(detail);
  }

  if (!response.body) throw new Error("Streaming is not supported by this response.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const line = event
        .split("\n")
        .find((item) => item.startsWith("data:"));

      if (!line) continue;

      const raw = line.slice(5).trim();
      if (!raw || raw === "[DONE]") continue;

      try {
        const payload = JSON.parse(raw);
        if (typeof payload.delta === "string") onDelta(payload.delta);
      } catch {
        // Ignore malformed partial SSE frames.
      }
    }
  }

  if (buffer.trim()) {
    const line = buffer
      .split("\n")
      .find((item) => item.startsWith("data:"));
    if (line) {
      const raw = line.slice(5).trim();
      if (raw && raw !== "[DONE]") {
        try {
          const payload = JSON.parse(raw);
          if (typeof payload.delta === "string") onDelta(payload.delta);
        } catch {}
      }
    }
  }
}

export async function listDocuments(): Promise<Document[]> {
  return request<Document[]>("/api/v1/documents");
}

export async function uploadDocument(file: File): Promise<Document> {
  const form = new FormData();
  form.append("file", file);

  return request<Document>("/api/v1/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function deleteDocument(id: number): Promise<void> {
  return request<void>(`/api/v1/documents/${id}`, { method: "DELETE" });
}

export async function listMemories(): Promise<Memory[]> {
  return request<Memory[]>("/api/v1/memory");
}

export async function createMemory(payload: {
  category: string;
  key: string;
  value: string;
  source: string;
  confidence: number;
}): Promise<Memory> {
  return request<Memory>("/api/v1/memory", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateMemory(
  id: number,
  payload: Partial<Pick<Memory, "category" | "key" | "value" | "confidence" | "is_active">>,
): Promise<Memory> {
  return request<Memory>(`/api/v1/memory/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteMemory(id: number): Promise<void> {
  await request(`/api/v1/memory/${id}`, { method: "DELETE" });
}

export async function getProviders(): Promise<ProviderStatus[]> {
  const result = await request<unknown>("/api/v1/providers", { auth: false });
  if (Array.isArray(result)) return result as ProviderStatus[];
  if (result && typeof result === "object") {
    const values = Object.entries(result as Record<string, unknown>).map(
      ([provider, value]) => ({
        provider,
        ...(typeof value === "object" && value !== null
          ? (value as Record<string, unknown>)
          : { configured: Boolean(value) }),
      }),
    );
    return values as ProviderStatus[];
  }
  return [];
}

export async function getLocalModels(): Promise<unknown> {
  return request("/api/v1/models/local");
}

export async function searchWeb(
  query: string,
  maxResults = 5,
): Promise<WebSearchResponse> {
  return request<WebSearchResponse>("/api/v1/web/search", {
    method: "POST",
    body: JSON.stringify({ query, max_results: maxResults }),
  });
}