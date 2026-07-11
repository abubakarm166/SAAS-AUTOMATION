"use client";

import Link from "next/link";

import { AuthGuard } from "@/components/AuthGuard";

function SuccessContent() {
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
        Your subscription is being activated. This may take a few seconds.
      </p>
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
