"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { api } from "@/lib/api";
import type { Subscription } from "@/lib/types";

const planFeatures = [
  "Unlimited property report jobs",
  "PDF + Excel report generation",
  "Cloud automation on demand",
  "Secure downloads & email delivery",
];

function BillingContent() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    api
      .getSubscription()
      .then(setSubscription)
      .catch(() => setSubscription(null))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubscribe() {
    setError("");
    setCheckoutLoading(true);
    try {
      const { checkout_url } = await api.createCheckoutSession();
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start checkout");
      setCheckoutLoading(false);
    }
  }

  const isActive = subscription?.status === "active" || subscription?.status === "trialing";

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">Billing</h1>
      <p className="mt-1 text-sm text-slate-500">Manage your SnapShot subscription</p>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="card mt-8 h-48 animate-pulse bg-slate-100/60" />
      ) : (
        <div className="card mt-8 overflow-hidden">
          <div className="brand-gradient flex items-center justify-between px-6 py-5 text-white">
            <div>
              <p className="text-sm text-white/80">SnapShot Pro</p>
              <p className="text-2xl font-bold">Property Reports</p>
            </div>
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${
                isActive ? "bg-white/20 text-white" : "bg-white/15 text-white/90"
              }`}
            >
              {subscription?.status ?? "no subscription"}
            </span>
          </div>

          <div className="p-6">
            <ul className="space-y-3">
              {planFeatures.map((f) => (
                <li key={f} className="flex items-center gap-3 text-sm text-slate-700">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 6 9 17l-5-5" />
                    </svg>
                  </span>
                  {f}
                </li>
              ))}
            </ul>

            {subscription?.current_period_end && (
              <div className="mt-6 flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3 text-sm">
                <span className="text-slate-500">Renews</span>
                <span className="font-medium text-slate-800">
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </span>
              </div>
            )}

            {isActive ? (
              <div className="mt-6 flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <path d="m9 11 3 3L22 4" />
                </svg>
                Your subscription is active. Create jobs anytime.
              </div>
            ) : (
              <button
                type="button"
                onClick={handleSubscribe}
                disabled={checkoutLoading}
                className="btn btn-primary mt-6 w-full"
              >
                {checkoutLoading ? "Redirecting…" : "Subscribe now"}
              </button>
            )}
          </div>
        </div>
      )}

      <Link href="/dashboard" className="mt-6 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
        Back to jobs
      </Link>
    </div>
  );
}

export default function BillingPage() {
  return (
    <AuthGuard>
      <BillingContent />
    </AuthGuard>
  );
}
