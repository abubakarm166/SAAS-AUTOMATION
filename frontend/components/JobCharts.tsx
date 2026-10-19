import type { DailyCount } from "@/lib/types";
import { formatDayLabel } from "@/lib/jobs";

type StatusCounts = {
  completed: number;
  failed: number;
  queued: number;
  running: number;
};

const STATUS_COLORS: { key: keyof StatusCounts; label: string; color: string }[] = [
  { key: "completed", label: "Completed", color: "#059669" },
  { key: "failed", label: "Failed", color: "#dc2626" },
  { key: "running", label: "Running", color: "#2563eb" },
  { key: "queued", label: "Queued", color: "#d97706" },
];

function Donut({ counts }: { counts: StatusCounts }) {
  const total = STATUS_COLORS.reduce((sum, s) => sum + counts[s.key], 0);
  const r = 42;
  const c = 2 * Math.PI * r;
  let offset = 0;

  if (total === 0) {
    return (
      <svg viewBox="0 0 120 120" className="h-36 w-36">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#e2e8f0" strokeWidth="14" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 120 120" className="h-36 w-36 -rotate-90">
      {STATUS_COLORS.map((s) => {
        const value = counts[s.key];
        if (!value) return null;
        const len = (value / total) * c;
        const dash = `${len} ${c - len}`;
        const el = (
          <circle
            key={s.key}
            cx="60"
            cy="60"
            r={r}
            fill="none"
            stroke={s.color}
            strokeWidth="14"
            strokeDasharray={dash}
            strokeDashoffset={-offset}
            strokeLinecap="butt"
          />
        );
        offset += len;
        return el;
      })}
    </svg>
  );
}

function BarChart({ daily }: { daily: DailyCount[] }) {
  const max = Math.max(1, ...daily.map((d) => d.count));
  return (
    <div className="flex h-36 items-end gap-1.5">
      {daily.map((d) => {
        const h = Math.max(d.count ? 8 : 2, Math.round((d.count / max) * 128));
        return (
          <div key={d.date} className="flex min-w-0 flex-1 flex-col items-center gap-1">
            <span className="text-[10px] font-medium text-slate-500">{d.count || ""}</span>
            <div
              className="w-full rounded-t-md bg-brand-500/80"
              style={{ height: h }}
              title={`${formatDayLabel(d.date)}: ${d.count}`}
            />
            <span className="w-full truncate text-center text-[10px] text-slate-400">
              {formatDayLabel(d.date)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function JobCharts({
  daily,
  counts,
}: {
  daily: DailyCount[];
  counts: StatusCounts;
}) {
  const total = counts.completed + counts.failed + counts.queued + counts.running;

  return (
    <div className="mt-6 grid gap-4 lg:grid-cols-5">
      <div className="card p-5 lg:col-span-3">
        <h2 className="text-sm font-semibold text-slate-900">Jobs over the last 14 days</h2>
        <p className="mt-0.5 text-xs text-slate-500">New jobs created each day</p>
        <div className="mt-4 overflow-x-auto">
          <div className="min-w-[28rem]">
            <BarChart daily={daily} />
          </div>
        </div>
      </div>
      <div className="card p-5 lg:col-span-2">
        <h2 className="text-sm font-semibold text-slate-900">Status mix</h2>
        <p className="mt-0.5 text-xs text-slate-500">Share of all jobs by status</p>
        <div className="mt-3 flex items-center gap-4">
          <div className="relative shrink-0">
            <Donut counts={counts} />
            <div className="pointer-events-none absolute inset-0 flex rotate-0 items-center justify-center">
              <span className="text-lg font-bold text-slate-900">{total}</span>
            </div>
          </div>
          <ul className="space-y-1.5 text-xs">
            {STATUS_COLORS.map((s) => (
              <li key={s.key} className="flex items-center gap-2 text-slate-600">
                <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                <span className="w-20">{s.label}</span>
                <span className="font-semibold text-slate-800">{counts[s.key]}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
