"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useMemo, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { OnboardingChecklist } from "@/components/OnboardingChecklist";
import { StatusBadge } from "@/components/StatusBadge";
import { api } from "@/lib/api";
import type { Job } from "@/lib/types";

const STATUS_FILTERS = [
  { id: "all", label: "All" },
  { id: "active", label: "Active" },
  { id: "completed", label: "Completed" },
  { id: "failed", label: "Failed" },
] as const;

const DISMISS_KEY = "snapshot_onboarding_dismissed";

function StatCard({ label, value, accent }: { label: string; value: number; accent: string }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${accent}`}>{value}</p>
    </div>
  );
}

function primaryAddress(job: Job): string {
  const addrs = job.inputs?.addresses;
  if (Array.isArray(addrs) && addrs.length > 0) {
    const first = String(addrs[0]);
    const more = addrs.length > 1 ? ` +${addrs.length - 1}` : "";
    return first + more;
  }
  return "—";
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const welcome = searchParams.get("welcome") === "1";
  const [jobs, setJobs] = useState<Job[]>([]);
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<(typeof STATUS_FILTERS)[number]["id"]>("all");
  const [showOnboarding, setShowOnboarding] = useState(false);

  const load = useCallback(async () => {
    try {
      const [data, sub] = await Promise.all([
        api.listJobs(),
        api.getSubscription().catch(() => null),
      ]);
      setJobs(data);
      setSubscribed(sub?.status === "active" || sub?.status === "trialing");
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const dismissed = typeof window !== "undefined" && localStorage.getItem(DISMISS_KEY) === "1";
    setShowOnboarding(!dismissed);
  }, []);

  useEffect(() => {
    const hasActive = jobs.some((j) => j.status === "queued" || j.status === "running");
    if (!hasActive) return;
    const id = setInterval(load, 4000);
    return () => clearInterval(id);
  }, [jobs, load]);

  const stats = useMemo(() => {
    return {
      total: jobs.length,
      active: jobs.filter((j) => j.status === "queued" || j.status === "running").length,
      completed: jobs.filter((j) => j.status === "completed").length,
      failed: jobs.filter((j) => j.status === "failed").length,
    };
  }, [jobs]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return jobs.filter((job) => {
      if (statusFilter === "active" && job.status !== "queued" && job.status !== "running") return false;
      if (statusFilter === "completed" && job.status !== "completed") return false;
      if (statusFilter === "failed" && job.status !== "failed") return false;
      if (!q) return true;
      const hay = [
        primaryAddress(job),
        job.status,
        job.source_url ?? "",
        job.id,
        ...(Array.isArray(job.inputs?.addresses) ? job.inputs.addresses.map(String) : []),
      ]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
  }, [jobs, query, statusFilter]);

  function dismissOnboarding() {
    localStorage.setItem(DISMISS_KEY, "1");
    setShowOnboarding(false);
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Your jobs</h1>
          <p className="mt-1 text-sm text-slate-500">Track automation runs and download reports</p>
        </div>
        <Link href="/jobs/new" className="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          New job
        </Link>
      </div>

      {showOnboarding && (
        <OnboardingChecklist
          subscribed={subscribed}
          hasJob={jobs.length > 0}
          welcome={welcome}
          onDismiss={dismissOnboarding}
        />
      )}

      {!loading && jobs.length > 0 && (
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Total" value={stats.total} accent="text-slate-900" />
          <StatCard label="Active" value={stats.active} accent="text-blue-600" />
          <StatCard label="Completed" value={stats.completed} accent="text-emerald-600" />
          <StatCard label="Failed" value={stats.failed} accent="text-red-600" />
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="mt-6 space-y-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card h-16 animate-pulse bg-slate-100/60" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="card mt-8 flex flex-col items-center px-6 py-16 text-center">
          <span className="brand-gradient flex h-14 w-14 items-center justify-center rounded-2xl text-white">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6M12 18v-6M9 15h6" />
            </svg>
          </span>
          <h3 className="mt-4 text-lg font-semibold text-slate-900">No jobs yet</h3>
          <p className="mt-1 max-w-sm text-sm text-slate-500">
            {subscribed
              ? "Create your first job to run property automation in the cloud."
              : "Subscribe first, then create a job to generate PDF and Excel reports."}
          </p>
          <Link href={subscribed ? "/jobs/new" : "/billing"} className="btn btn-primary mt-6">
            {subscribed ? "Create your first job" : "Go to billing"}
          </Link>
        </div>
      ) : (
        <>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by address…"
              className="input sm:max-w-xs"
            />
            <div className="flex flex-wrap gap-1.5">
              {STATUS_FILTERS.map((f) => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setStatusFilter(f.id)}
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold ${
                    statusFilter === f.id
                      ? "bg-brand-600 text-white"
                      : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div className="card mt-4 overflow-hidden">
            {filtered.length === 0 ? (
              <p className="px-5 py-10 text-center text-sm text-slate-500">No jobs match that search.</p>
            ) : (
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Address</th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
                    <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">Created</th>
                    <th className="px-5 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.map((job) => (
                    <tr
                      key={job.id}
                      onClick={() => router.push(`/jobs/${job.id}`)}
                      className="cursor-pointer transition-colors hover:bg-slate-50"
                    >
                      <td className="max-w-xs truncate px-5 py-4 font-medium text-slate-800">
                        {primaryAddress(job)}
                      </td>
                      <td className="px-5 py-4">
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="hidden px-5 py-4 text-slate-500 sm:table-cell">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="inline-flex items-center gap-1 text-sm font-medium text-brand-600">
                          View
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="m9 18 6-6-6-6" />
                          </svg>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthGuard>
      <Suspense
        fallback={
          <div className="flex min-h-[40vh] items-center justify-center">
            <span className="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-600" />
          </div>
        }
      >
        <DashboardContent />
      </Suspense>
    </AuthGuard>
  );
}
