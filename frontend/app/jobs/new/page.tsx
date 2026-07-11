"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { api, ApiError } from "@/lib/api";
import { DEFAULT_JOB_INPUTS, type JobInputs } from "@/lib/types";

function NewJobContent() {
  const router = useRouter();
  const [sourceUrl, setSourceUrl] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [addresses, setAddresses] = useState<string[]>([""]);
  const [inputs, setInputs] = useState<Omit<JobInputs, "addresses" | "recipient_email">>({
    interest_rate: DEFAULT_JOB_INPUTS.interest_rate,
    years: DEFAULT_JOB_INPUTS.years,
    discount_percentage: DEFAULT_JOB_INPUTS.discount_percentage,
    closing_costs_input: DEFAULT_JOB_INPUTS.closing_costs_input,
    money_down_input: DEFAULT_JOB_INPUTS.money_down_input,
    operating_expenses_input: DEFAULT_JOB_INPUTS.operating_expenses_input,
    additional_annual_income_input: DEFAULT_JOB_INPUTS.additional_annual_income_input,
    vacancy_allowance_percent_input: DEFAULT_JOB_INPUTS.vacancy_allowance_percent_input,
    lender_ltv_input: DEFAULT_JOB_INPUTS.lender_ltv_input,
    rehab_costs_est_input: DEFAULT_JOB_INPUTS.rehab_costs_est_input,
    refi_loan_amount_input: DEFAULT_JOB_INPUTS.refi_loan_amount_input,
    refi_closing_costs_est_input: DEFAULT_JOB_INPUTS.refi_closing_costs_est_input,
    num_months_holding: DEFAULT_JOB_INPUTS.num_months_holding,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  function updateAddress(i: number, value: string) {
    setAddresses((prev) => prev.map((a, idx) => (idx === i ? value : a)));
  }
  function addAddress() {
    setAddresses((prev) => [...prev, ""]);
  }
  function removeAddress(i: number) {
    if (addresses.length <= 1) return;
    setAddresses((prev) => prev.filter((_, idx) => idx !== i));
  }
  function setNum<K extends keyof typeof inputs>(key: K, value: string) {
    setInputs((prev) => ({ ...prev, [key]: parseFloat(value) || 0 }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    const cleaned = addresses.map((a) => a.trim()).filter(Boolean);
    if (cleaned.length === 0) {
      setError("At least one address is required");
      return;
    }
    setLoading(true);
    try {
      const job = await api.createJob({
        source_url: sourceUrl.trim() || undefined,
        inputs: { ...inputs, addresses: cleaned, recipient_email: recipientEmail.trim() || null },
      });
      router.push(`/jobs/${job.id}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        router.push("/billing");
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to create job");
    } finally {
      setLoading(false);
    }
  }

  const numFields: { key: keyof typeof inputs; label: string; step?: string }[] = [
    { key: "interest_rate", label: "Interest rate", step: "0.01" },
    { key: "years", label: "Loan years", step: "1" },
    { key: "discount_percentage", label: "Discount %", step: "0.01" },
    { key: "closing_costs_input", label: "Closing costs", step: "0.01" },
    { key: "money_down_input", label: "Money down", step: "0.01" },
    { key: "operating_expenses_input", label: "Operating expenses", step: "0.01" },
    { key: "additional_annual_income_input", label: "Additional annual income", step: "0.01" },
    { key: "vacancy_allowance_percent_input", label: "Vacancy allowance %", step: "0.01" },
    { key: "lender_ltv_input", label: "Lender LTV", step: "0.01" },
    { key: "rehab_costs_est_input", label: "Rehab costs est.", step: "0.01" },
    { key: "refi_loan_amount_input", label: "Refi loan amount", step: "0.01" },
    { key: "refi_closing_costs_est_input", label: "Refi closing costs", step: "0.01" },
    { key: "num_months_holding", label: "Months holding", step: "1" },
  ];

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
        Back to jobs
      </Link>
      <h1 className="mt-4 text-2xl font-bold tracking-tight text-slate-900">New job</h1>
      <p className="mt-1 text-sm text-slate-500">Submit addresses for cloud automation</p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="card space-y-5 p-6">
          <div>
            <label className="label">Auction / source URL</label>
            <input
              type="url"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://www.example-auction.com/..."
              className="input"
            />
          </div>

          <div>
            <label className="label">Recipient email (optional)</label>
            <input
              type="email"
              value={recipientEmail}
              onChange={(e) => setRecipientEmail(e.target.value)}
              placeholder="reports@example.com"
              className="input"
            />
          </div>

          <div>
            <label className="label">Addresses</label>
            <div className="space-y-2">
              {addresses.map((addr, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    required={i === 0}
                    value={addr}
                    onChange={(e) => updateAddress(i, e.target.value)}
                    placeholder="123 Main St, City, ST 12345"
                    className="input flex-1"
                  />
                  {addresses.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeAddress(i)}
                      className="btn btn-ghost px-3"
                      aria-label="Remove address"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={addAddress}
              className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 5v14M5 12h14" />
              </svg>
              Add address
            </button>
          </div>
        </div>

        <div className="card p-6">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex w-full items-center justify-between text-sm font-semibold text-slate-700"
          >
            Financial inputs
            <svg
              width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round"
              className={`text-slate-400 transition-transform ${showAdvanced ? "rotate-180" : ""}`}
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </button>
          {showAdvanced && (
            <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
              {numFields.map(({ key, label, step }) => (
                <div key={key}>
                  <label className="label">{label}</label>
                  <input
                    type="number"
                    step={step ?? "0.01"}
                    value={inputs[key]}
                    onChange={(e) => setNum(key, e.target.value)}
                    className="input"
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? "Submitting…" : "Create job"}
          </button>
          <Link href="/dashboard" className="btn btn-ghost">Cancel</Link>
        </div>
      </form>
    </div>
  );
}

export default function NewJobPage() {
  return (
    <AuthGuard>
      <NewJobContent />
    </AuthGuard>
  );
}
