export interface ArxivResult {
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  published: string | null;
}

export interface WebResult {
  title: string;
  url: string;
  snippet: string;
}

export interface Critique {
  verdict?: "STRONG" | "RETRY";
  critique?: string;
  follow_up_queries?: string[];
}

export interface FinalReport {
  summary?: string;
  key_findings?: string[];
  sources?: string[];
  confidence_score?: number;
}

export interface ResearchResponse {
  report: FinalReport;
  sources: string[];
  critique: Critique;
  retry_count: number;
  status: string;
}

export interface HealthResponse {
  status: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API request failed (${res.status}): ${text || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export function research(question: string): Promise<ResearchResponse> {
  return request<ResearchResponse>("/research", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function health(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}
