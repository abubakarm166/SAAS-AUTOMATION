"use client";

import Link from "next/link";

import { AuthGuard } from "@/components/AuthGuard";

function CancelContent() {
  return (
    <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-20 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="m15 9-6 6M9 9l6 6" />
        </svg>
      </span>
      <h1 className="mt-6 text-2xl font-bold tracking-tight text-slate-900">Checkout cancelled</h1>
      <p className="mt-2 text-slate-600">No charges were made. You can subscribe anytime.</p>
      <Link href="/billing" className="btn btn-primary mt-8">Back to billing</Link>
    </div>
  );
}

export default function BillingCancelPage() {
  return (
    <AuthGuard>
      <CancelContent />
    </AuthGuard>
  );
}
