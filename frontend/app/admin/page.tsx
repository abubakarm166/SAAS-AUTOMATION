"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { JobCharts } from "@/components/JobCharts";
import { StatusBadge } from "@/components/StatusBadge";
import { ApiError, api } from "@/lib/api";
import { addressCount, emptyJobStats, primaryAddress } from "@/lib/jobs";
import type { AdminJob, AdminStats, AdminUser, User } from "@/lib/types";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "users", label: "Users" },
  { id: "subscribers", label: "Subscribers" },
  { id: "jobs", label: "Jobs" },
] as const;

type Tab = (typeof TABS)[number]["id"];

const JOB_STATUS_FILTERS = ["all", "queued", "running", "completed", "failed"] as const;

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

function SubBadge({ status }: { status: string | null }) {
  const key = (status ?? "").toLowerCase();
  const styles: Record<string, string> = {
    active: "bg-emerald-50 text-emerald-700 border-emerald-200",
    trialing: "bg-blue-50 text-blue-700 border-blue-200",
    past_due: "bg-amber-50 text-amber-700 border-amber-200",
    canceled: "bg-slate-100 text-slate-600 border-slate-200",
    unpaid: "bg-red-50 text-red-700 border-red-200",
  };
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium capitalize ${styles[key] ?? "bg-slate-100 text-slate-600 border-slate-200"}`}>
      {status ? status.replace("_", " ") : "None"}
    </span>
  );
}

function AdminContent() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("overview");
  const [me, setMe] = useState<User | null>(null);
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [subscribers, setSubscribers] = useState<AdminUser[]>([]);
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [error, setError] = useState("");
  const [userQuery, setUserQuery] = useState("");
  const [subQuery, setSubQuery] = useState("");
  const [jobQuery, setJobQuery] = useState("");
  const [jobStatus, setJobStatus] = useState<(typeof JOB_STATUS_FILTERS)[number]>("all");
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const profile = await api.me();
      if (!profile.is_admin) {
        setAllowed(false);
        router.replace("/dashboard");
        return;
      }
      setMe(profile);
      setAllowed(true);
      const [s, u, sub, j] = await Promise.all([
        api.adminStats(),
        api.adminUsers(),
        api.adminSubscribers(),
        api.adminJobs(),
      ]);
      setStats(s);
      setUsers(u);
      setSubscribers(sub);
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

  const filteredSubscribers = useMemo(() => {
    const q = subQuery.trim().toLowerCase();
    if (!q) return subscribers;
    return subscribers.filter((u) => {
      const hay = [u.email, u.plan_label ?? "", u.subscription_status ?? ""].join(" ").toLowerCase();
      return hay.includes(q);
    });
  }, [subscribers, subQuery]);

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

  async function toggleAdmin(user: AdminUser) {
    const next = !user.is_admin;
    const action = next ? `Give admin access to ${user.email}?` : `Remove admin access from ${user.email}?`;
    if (!window.confirm(action)) return;
    setBusyId(user.id);
    setError("");
    try {
      const updated = await api.setAdminAccess(user.id, next);
      setUsers((rows) => rows.map((row) => (row.id === updated.id ? { ...row, ...updated } : row)));
      setSubscribers((rows) => rows.map((row) => (row.id === updated.id ? { ...row, ...updated } : row)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update admin access");
    } finally {
      setBusyId(null);
    }
  }

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
          <p className="mt-1 text-sm text-slate-500">Users, subscribers, and jobs across SnapShot</p>
        </div>
        <div className="flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={`rounded-md px-3 py-1.5 text-sm font-semibold ${
                tab === item.id ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {item.label}
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
          <p className="mt-6 text-sm text-slate-500">
            Grant or remove admin access here. The other person only needs to refresh the site.
          </p>
          <input
            type="search"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Search users by email…"
            className="input mt-3 sm:max-w-xs"
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
                      Role
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Subscription
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Jobs
                    </th>
                    <th className="px-5 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUsers.map((user) => {
                    const self = me?.id === user.id;
                    const locked = Boolean(user.is_bootstrap_admin) && user.is_admin;
                    return (
                      <tr key={user.id} className="hover:bg-slate-50">
                        <td className="px-5 py-4">
                          <p className="font-medium text-slate-800">{user.email}</p>
                          <p className="text-xs text-slate-400">
                            {self ? "You · " : ""}
                            {user.is_active ? "Active" : "Disabled"}
                          </p>
                        </td>
                        <td className="px-5 py-4 text-slate-600">{user.is_admin ? "Admin" : "User"}</td>
                        <td className="px-5 py-4">
                          <SubBadge status={user.subscription_status} />
                        </td>
                        <td className="px-5 py-4 text-slate-600">{user.job_count}</td>
                        <td className="px-5 py-4 text-right">
                          <button
                            type="button"
                            disabled={busyId === user.id || (user.is_admin && (self || locked))}
                            onClick={() => toggleAdmin(user)}
                            className="btn btn-ghost px-3 py-1.5 text-xs"
                            title={
                              self
                                ? "You cannot remove your own admin access"
                                : locked
                                  ? "This admin is set on the server and cannot be removed here"
                                  : undefined
                            }
                          >
                            {busyId === user.id ? "Saving…" : user.is_admin ? "Remove admin" : "Make admin"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {tab === "subscribers" && (
        <>
          <p className="mt-6 text-sm text-slate-500">
            Accounts with an active or trialing subscription ({subscribers.length}).
          </p>
          <input
            type="search"
            value={subQuery}
            onChange={(e) => setSubQuery(e.target.value)}
            placeholder="Search subscribers by email or plan…"
            className="input mt-3 sm:max-w-xs"
          />
          <div className="card mt-3 overflow-hidden">
            {filteredSubscribers.length === 0 ? (
              <p className="px-5 py-10 text-center text-sm text-slate-500">No subscribed users to show.</p>
            ) : (
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Email
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Plan
                    </th>
                    <th className="hidden px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 sm:table-cell">
                      Renews
                    </th>
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Jobs
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredSubscribers.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-50">
                      <td className="px-5 py-4 font-medium text-slate-800">{user.email}</td>
                      <td className="px-5 py-4">
                        <SubBadge status={user.subscription_status} />
                      </td>
                      <td className="px-5 py-4 text-slate-600">{user.plan_label ?? "—"}</td>
                      <td className="hidden px-5 py-4 text-slate-500 sm:table-cell">
                        {user.current_period_end ? new Date(user.current_period_end).toLocaleDateString() : "—"}
                      </td>
                      <td className="px-5 py-4 text-slate-600">{user.job_count}</td>
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
