import { clearToken, getToken } from "./auth";
import type {
  CheckoutSession,
  FileDownload,
  Job,
  JobFile,
  Subscription,
  TokenResponse,
  User,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
      if (Array.isArray(detail)) {
        detail = detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(", ");
      }
    } catch {
      /* ignore */
    }
    if (res.status === 401) clearToken();
    throw new ApiError(String(detail), res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  signup: (email: string, password: string) =>
    request<User>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }, false),

  me: () => request<User>("/auth/me"),

  listJobs: () => request<Job[]>("/jobs"),

  getJob: (id: string) => request<Job>(`/jobs/${id}`),

  createJob: (payload: { source_url?: string; inputs: Record<string, unknown> }) =>
    request<Job>("/jobs", { method: "POST", body: JSON.stringify(payload) }),

  listJobFiles: (jobId: string) => request<JobFile[]>(`/jobs/${jobId}/files`),

  getDownloadUrl: (jobId: string, fileId: string) =>
    request<FileDownload>(`/jobs/${jobId}/files/${fileId}/download`),

  getSubscription: () => request<Subscription>("/billing/subscription"),

  createCheckoutSession: () =>
    request<CheckoutSession>("/billing/checkout-session", { method: "POST" }),
};
