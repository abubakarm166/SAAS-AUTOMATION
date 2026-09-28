"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { api } from "@/lib/api";

function SuccessContent() {
  const [status, setStatus] = useState<string>("activating");
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    async function sync() {
      try {
        const sub = await api.syncSubscription();
        if (cancelled) return;
        setStatus(sub.status);
        if (
          sub.status !== "active" &&
          sub.status !== "trialing" &&
          attempts < 6
        ) {
          attempts += 1;
          setTimeout(sync, 2000);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Could not refresh subscription");
        setStatus("unknown");
      }
    }

    sync();
    return () => {
      cancelled = true;
    };
  }, []);

  const isActive = status === "active" || status === "trialing";

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-20 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <path d="m9 11 3 3L22 4" />
        </svg>
      </span>
      <h1 className="mt-6 text-2xl font-bold tracking-tight text-slate-900">Payment successful</h1>
      <p className="mt-2 text-slate-600">
        {isActive
          ? "Your subscription is active. You can create jobs now."
          : "Your subscription is being activated. This may take a few seconds."}
      </p>
      {error && <p className="mt-3 text-sm text-amber-700">{error}</p>}
      <p className="mt-2 text-xs uppercase tracking-wide text-slate-400">Status: {status}</p>
      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
        <Link href="/jobs/new" className="btn btn-primary">Create a job</Link>
        <Link href="/billing" className="btn btn-ghost">View billing</Link>
      </div>
    </div>
  );
}

export default function BillingSuccessPage() {
  return (
    <AuthGuard>
      <SuccessContent />
    </AuthGuard>
  );
}
