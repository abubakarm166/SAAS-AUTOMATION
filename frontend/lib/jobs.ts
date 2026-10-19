import type { DailyCount, Job, JobStats } from "./types";

export function jobAddresses(job: Job): string[] {
  const addrs = job.inputs?.addresses;
  return Array.isArray(addrs) ? addrs.map(String) : [];
}

export function primaryAddress(job: Job): string {
  const addrs = jobAddresses(job);
  if (addrs.length === 0) return "—";
  const more = addrs.length > 1 ? ` +${addrs.length - 1}` : "";
  return addrs[0] + more;
}

export function addressCount(job: Job): number {
  return jobAddresses(job).length;
}

export function localDateKey(value: Date): string {
  const y = value.getFullYear();
  const m = String(value.getMonth() + 1).padStart(2, "0");
  const d = String(value.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function formatDayLabel(isoDate: string): string {
  const d = new Date(`${isoDate}T00:00:00`);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function emptyJobStats(): JobStats {
  return {
    total: 0,
    queued: 0,
    running: 0,
    completed: 0,
    failed: 0,
    canceled: 0,
    addresses_total: 0,
    addresses_completed: 0,
    success_rate: 0,
    this_month: 0,
    last_30_days: 0,
    daily: [],
  };
}

export function statsFromJobs(jobs: Job[], days = 14): JobStats {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const last30 = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const counts: Record<string, number> = {};
  const stats = emptyJobStats();
  stats.total = jobs.length;

  for (const job of jobs) {
    if (job.status === "queued") stats.queued += 1;
    else if (job.status === "running") stats.running += 1;
    else if (job.status === "completed") stats.completed += 1;
    else if (job.status === "failed") stats.failed += 1;
    else if (job.status === "canceled") stats.canceled += 1;

    const n = addressCount(job);
    stats.addresses_total += n;
    if (job.status === "completed") stats.addresses_completed += n;

    const created = new Date(job.created_at);
    if (created >= monthStart) stats.this_month += 1;
    if (created >= last30) stats.last_30_days += 1;
    const key = localDateKey(created);
    counts[key] = (counts[key] ?? 0) + 1;
  }

  const decided = stats.completed + stats.failed;
  stats.success_rate = decided ? Math.round((stats.completed / decided) * 1000) / 10 : 0;

  const daily: DailyCount[] = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    const key = localDateKey(d);
    daily.push({ date: key, count: counts[key] ?? 0 });
  }
  stats.daily = daily;
  return stats;
}
