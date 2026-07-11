const styles: Record<string, { cls: string; dot: string }> = {
  queued: { cls: "bg-amber-50 text-amber-700 border-amber-200", dot: "bg-amber-500" },
  running: { cls: "bg-blue-50 text-blue-700 border-blue-200", dot: "bg-blue-500 animate-pulse" },
  completed: { cls: "bg-emerald-50 text-emerald-700 border-emerald-200", dot: "bg-emerald-500" },
  failed: { cls: "bg-red-50 text-red-700 border-red-200", dot: "bg-red-500" },
};

export function StatusBadge({ status }: { status: string }) {
  const s = styles[status] ?? { cls: "bg-slate-100 text-slate-600 border-slate-200", dot: "bg-slate-400" };
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium capitalize ${s.cls}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {status}
    </span>
  );
}
