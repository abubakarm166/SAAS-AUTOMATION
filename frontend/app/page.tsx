"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Logo } from "@/components/Logo";
import { isAuthenticated } from "@/lib/auth";

const steps = [
  { title: "Subscribe", body: "Activate SnapShot with Stripe in under a minute." },
  { title: "Submit addresses", body: "Use the dashboard or Chrome extension from any listing page." },
  { title: "Get reports", body: "Download PDF + Excel, or have them emailed when the job finishes." },
];

const features = [
  {
    title: "Cloud automation",
    body: "The same property-report engine you already know, running on a Windows worker in AWS.",
  },
  {
    title: "Dashboard + extension",
    body: "Create jobs from the web app, or scan auction pages in Chrome and submit in one click.",
  },
  {
    title: "Secure files",
    body: "Reports land in private cloud storage. You download with time-limited links — or by email.",
  },
];

export default function HomePage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (isAuthenticated()) {
      router.replace("/dashboard");
      return;
    }
    setChecking(false);
  }, [router]);

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200/70 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <Logo size={40} />
            <span className="text-lg font-bold tracking-tight text-slate-900">SnapShot</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link href="/login" className="btn btn-ghost">
              Log in
            </Link>
            <Link href="/signup" className="btn btn-primary">
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">
              Property report automation
            </p>
            <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Professional property reports, generated in the cloud.
            </h1>
            <p className="mt-4 text-lg text-slate-600">
              Submit addresses from the dashboard or Chrome extension. SnapShot builds your PDF and Excel
              reports automatically — then you download them or receive them by email.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/signup" className="btn btn-primary">
                Create an account
              </Link>
              <Link href="/login" className="btn btn-ghost">
                Sign in
              </Link>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200 bg-white">
          <div className="mx-auto grid max-w-6xl gap-8 px-4 py-14 sm:grid-cols-3 sm:px-6">
            {features.map((f) => (
              <div key={f.title}>
                <h2 className="text-base font-semibold text-slate-900">{f.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">How it works</h2>
          <ol className="mt-8 grid gap-6 sm:grid-cols-3">
            {steps.map((step, i) => (
              <li key={step.title} className="card p-6">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-50 text-sm font-bold text-brand-700">
                  {i + 1}
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">{step.title}</h3>
                <p className="mt-1.5 text-sm text-slate-600">{step.body}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>

      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-400">
        SnapShot Property Report
      </footer>
    </div>
  );
}
