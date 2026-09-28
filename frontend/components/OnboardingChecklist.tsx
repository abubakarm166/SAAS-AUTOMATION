"use client";

import Link from "next/link";

type Props = {
  subscribed: boolean;
  hasJob: boolean;
  welcome?: boolean;
  onDismiss: () => void;
};

export function OnboardingChecklist({ subscribed, hasJob, welcome, onDismiss }: Props) {
  const steps = [
    { done: true, title: "Create your account", href: null as string | null },
    {
      done: subscribed,
      title: "Activate your subscription",
      href: subscribed ? null : "/billing",
    },
    {
      done: hasJob,
      title: "Create your first report job",
      href: hasJob ? null : "/jobs/new",
    },
  ];
  const remaining = steps.filter((s) => !s.done).length;
  if (remaining === 0) return null;

  return (
    <div className="card mt-6 overflow-hidden">
      <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">
            {welcome ? "Welcome to SnapShot" : "Get started"}
          </h2>
          <p className="mt-0.5 text-sm text-slate-500">
            {remaining} step{remaining === 1 ? "" : "s"} left to run your first cloud report.
          </p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="rounded-lg px-2 py-1 text-xs font-medium text-slate-400 hover:bg-slate-50 hover:text-slate-600"
        >
          Dismiss
        </button>
      </div>
      <ol className="divide-y divide-slate-100">
        {steps.map((step, i) => (
          <li key={step.title} className="flex items-center justify-between gap-4 px-5 py-3.5">
            <div className="flex items-center gap-3">
              <span
                className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                  step.done ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"
                }`}
              >
                {step.done ? "✓" : i + 1}
              </span>
              <span className={`text-sm ${step.done ? "text-slate-400 line-through" : "font-medium text-slate-800"}`}>
                {step.title}
              </span>
            </div>
            {step.href && (
              <Link href={step.href} className="text-sm font-semibold text-brand-600 hover:text-brand-700">
                {i === 1 ? "Subscribe" : "Create job"}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
