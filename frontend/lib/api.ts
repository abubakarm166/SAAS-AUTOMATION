import { clearToken, getToken } from "./auth";

function redirectToLogin() {
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/signup") || path.startsWith("/forgot-password") || path.startsWith("/reset-password")) {
    return;
  }
  const next = encodeURIComponent(`${path}${window.location.search}`);
  window.location.replace(`/login?expired=1&next=${next}`);
}
import type {
  AdminJob,
  AdminStats,
  AdminUser,
  BillingConfig,
  CheckoutSession,
  ExtractedAddresses,
  FileDownload,
  Job,
  JobFile,
  JobStats,
  MessageResponse,
  PortalSession,
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
    if (res.status === 401) {
      clearToken();
      redirectToLogin();
    }
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

  forgotPassword: (email: string) =>
    request<MessageResponse>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }, false),

  resetPassword: (token: string, password: string) =>
    request<MessageResponse>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, password }),
    }, false),

  me: () => request<User>("/auth/me"),

  listJobs: () => request<Job[]>("/jobs"),

  getJobStats: () => request<JobStats>("/jobs/stats"),

  adminStats: () => request<AdminStats>("/admin/stats"),

  adminUsers: () => request<AdminUser[]>("/admin/users"),

  adminJobs: () => request<AdminJob[]>("/admin/jobs"),

  getJob: (id: string) => request<Job>(`/jobs/${id}`),

  createJob: (payload: { source_url?: string; inputs: Record<string, unknown> }) =>
    request<Job>("/jobs", { method: "POST", body: JSON.stringify(payload) }),

  extractAddresses: (url: string) =>
    request<ExtractedAddresses>("/jobs/extract-addresses", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  retryJob: (jobId: string) =>
    request<Job>(`/jobs/${jobId}/retry`, { method: "POST" }),

  listJobFiles: (jobId: string) => request<JobFile[]>(`/jobs/${jobId}/files`),

  getDownloadUrl: (jobId: string, fileId: string) =>
    request<FileDownload>(`/jobs/${jobId}/files/${fileId}/download`),

  getBillingConfig: () => request<BillingConfig>("/billing/config", {}, false),

  getSubscription: () => request<Subscription>("/billing/subscription"),

  createCheckoutSession: (plan: "monthly" | "yearly" = "monthly") =>
    request<CheckoutSession>("/billing/checkout-session", {
      method: "POST",
      body: JSON.stringify({ plan }),
    }),

  createPortalSession: () =>
    request<PortalSession>("/billing/portal-session", { method: "POST" }),

  syncSubscription: () =>
    request<Subscription>("/billing/sync", { method: "POST" }),
};
