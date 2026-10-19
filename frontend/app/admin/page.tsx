"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { JobCharts } from "@/components/JobCharts";
import { StatusBadge } from "@/components/StatusBadge";
import { ApiError, api } from "@/lib/api";
import { addressCount, emptyJobStats, primaryAddress } from "@/lib/jobs";
import type { AdminJob, AdminStats, AdminUser } from "@/lib/types";

type Tab = "overview" | "users" | "jobs";

const JOB_STATUS_FILTERS = ["all", "queued", "running", "completed", "failed"] as const;

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function AdminContent() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("overview");
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [error, setError] = useState("");
  const [userQuery, setUserQuery] = useState("");
  const [jobQuery, setJobQuery] = useState("");
  const [jobStatus, setJobStatus] = useState<(typeof JOB_STATUS_FILTERS)[number]>("all");

  const load = useCallback(async () => {
    try {
      const me = await api.me();
      if (!me.is_admin) {
        setAllowed(false);
        router.replace("/dashboard");
        return;
      }
      setAllowed(true);
      const [s, u, j] = await Promise.all([api.adminStats(), api.adminUsers(), api.adminJobs()]);
      setStats(s);
      setUsers(u);
      setJobs(j);
      setError("");
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setAllowed(false);
        router.replace("/dashboard");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load admin data");
      setAllowed(true);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredUsers = useMemo(() => {
    const q = userQuery.trim().toLowerCase();
    if (!q) return users;
    return users.filter((u) => u.email.toLowerCase().includes(q));
  }, [users, userQuery]);

  const filteredJobs = useMemo(() => {
    const q = jobQuery.trim().toLowerCase();
    return jobs.filter((job) => {
      if (jobStatus !== "all" && job.status !== jobStatus) return false;
      if (!q) return true;
      const hay = [primaryAddress(job), job.user_email, job.status, job.source_url ?? "", job.id]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
  }, [jobs, jobQuery, jobStatus]);

  if (allowed !== true) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <span className="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-600" />
      </div>
    );
  }

  const s = stats ?? { ...emptyJobStats(), users_total: 0, subscribers_active: 0 };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Admin</h1>
          <p className="mt-1 text-sm text-slate-500">All users and jobs across SnapShot</p>
        </div>
        <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
          {(["overview", "users", "jobs"] as const).map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => setTab(id)}
              className={`rounded-md px-3 py-1.5 text-sm font-semibold capitalize ${
                tab === id ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">{error}</div>
      )}

      {tab === "overview" && (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <StatCard label="Users" value={s.users_total} />
            <StatCard label="Subscribers" value={s.subscribers_active} />
            <StatCard label="Jobs" value={s.total} />
            <StatCard label="Completed" value={s.completed} />
            <StatCard label="Failed" value={s.failed} />
            <StatCard label="Success rate" value={`${s.success_rate}%`} />
          </div>
          <JobCharts
            daily={s.daily}
            counts={{
              completed: s.completed,
              failed: s.failed,
              queued: s.queued,
              running: s.running,
            }}
          />
          <p className="mt-3 text-xs text-slate-500">
            {s.this_month} jobs this month · {s.last_30_days} in the last 30 days · {s.addresses_completed} addresses
            completed
          </p>
        </>
      )}

      {tab === "users" && (
        <>
          <input
            type="search"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Search users by email…"
            className="input mt-6 sm:max-w-xs"
          />
          <div className="card mt-3 overflow-hidden">
            {filteredUsers.length === 0 ? (
              <p className="px-5 py-10 text-center text-sm text-slate-500">No users match that search.</p>
            ) : (
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Email
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Subscription
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Jobs
                    </th>
                    <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">
                      Joined
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-50">
                      <td className="px-5 py-4">
                        <p className="font-medium text-slate-800">{user.email}</p>
                        <p className="text-xs text-slate-400">
                          {user.is_admin ? "Admin" : user.is_active ? "Active" : "Disabled"}
                        </p>
                      </td>
                      <td className="px-5 py-4 capitalize text-slate-600">{user.subscription_status ?? "—"}</td>
                      <td className="px-5 py-4 text-slate-600">{user.job_count}</td>
                      <td className="hidden px-5 py-4 text-slate-500 sm:table-cell">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {tab === "jobs" && (
        <>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <input
              type="search"
              value={jobQuery}
              onChange={(e) => setJobQuery(e.target.value)}
              placeholder="Search address, email, or URL…"
              className="input sm:max-w-xs"
            />
            <div className="flex flex-wrap gap-1.5">
              {JOB_STATUS_FILTERS.map((id) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setJobStatus(id)}
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold capitalize ${
                    jobStatus === id
                      ? "bg-brand-600 text-white"
                      : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                  }`}
                >
                  {id}
                </button>
              ))}
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-500">Showing {filteredJobs.length} of {jobs.length} jobs</p>
          <div className="card mt-3 overflow-hidden">
            {filteredJobs.length === 0 ? (
              <p className="px-5 py-10 text-center text-sm text-slate-500">No jobs match those filters.</p>
            ) : (
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Address
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      User
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>
                    <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">
                      Created
                    </th>
                    <th className="px-5 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredJobs.map((job) => (
                    <tr
                      key={job.id}
                      onClick={() => router.push(`/jobs/${job.id}`)}
                      className="cursor-pointer hover:bg-slate-50"
                    >
                      <td className="max-w-xs truncate px-5 py-4 font-medium text-slate-800">
                        {primaryAddress(job)}
                        <span className="ml-1 text-xs font-normal text-slate-400">×{addressCount(job)}</span>
                      </td>
                      <td className="max-w-[10rem] truncate px-5 py-4 text-slate-600">{job.user_email}</td>
                      <td className="px-5 py-4">
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="hidden px-5 py-4 text-slate-500 sm:table-cell">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <Link href={`/jobs/${job.id}`} className="text-sm font-medium text-brand-600" onClick={(e) => e.stopPropagation()}>
                          View
                        </Link>
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

export default function AdminPage() {
  return (
    <AuthGuard>
      <AdminContent />
    </AuthGuard>
  );
}
