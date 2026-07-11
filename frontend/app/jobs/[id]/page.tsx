"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { AuthGuard } from "@/components/AuthGuard";
import { StatusBadge } from "@/components/StatusBadge";
import { api } from "@/lib/api";
import type { Job, JobFile } from "@/lib/types";

function FileIcon({ type }: { type: string }) {
  const isPdf = type.toLowerCase().includes("pdf");
  return (
    <span
      className={`flex h-10 w-10 items-center justify-center rounded-lg ${
        isPdf ? "bg-red-50 text-red-600" : "bg-emerald-50 text-emerald-600"
      }`}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6" />
      </svg>
    </span>
  );
}

function JobDetailContent() {
  const params = useParams();
  const jobId = params.id as string;
  const [job, setJob] = useState<Job | null>(null);
  const [files, setFiles] = useState<JobFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [jobData, fileData] = await Promise.all([
        api.getJob(jobId),
        api.listJobFiles(jobId).catch(() => [] as JobFile[]),
      ]);
      setJob(jobData);
      setFiles(fileData);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load job");
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!job || (job.status !== "queued" && job.status !== "running")) return;
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [job, load]);

  async function handleDownload(fileId: string) {
    setDownloading(fileId);
    try {
      const { url } = await api.getDownloadUrl(jobId, fileId);
      window.open(url, "_blank");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setDownloading(null);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="card h-40 animate-pulse bg-slate-100/60" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <p className="text-red-600">{error || "Job not found"}</p>
        <Link href="/dashboard" className="mt-4 inline-block text-sm text-brand-600 hover:underline">
          Back to jobs
        </Link>
      </div>
    );
  }

  const addresses = Array.isArray(job.inputs?.addresses) ? job.inputs.addresses : [];

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link href="/dashboard" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="m15 18-6-6 6-6" />
        </svg>
        Back to jobs
      </Link>

      <div className="mt-4 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job details</h1>
          <p className="mt-1 font-mono text-xs text-slate-400">{job.id}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
          {error}
        </div>
      )}

      {(job.status === "queued" || job.status === "running") && (
        <div className="mt-6 flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          Automation in progress — this page refreshes automatically.
        </div>
      )}

      <div className="card mt-6 space-y-5 p-6">
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">Addresses</h2>
          <ul className="mt-2 space-y-1.5">
            {addresses.map((a, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-slate-700">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-500">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                {String(a)}
              </li>
            ))}
          </ul>
        </div>

        {job.source_url && (
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">Source URL</h2>
            <a
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 block break-all text-sm text-brand-600 hover:underline"
            >
              {job.source_url}
            </a>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-5 text-sm">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Created</span>
            <p className="mt-1 text-slate-700">{new Date(job.created_at).toLocaleString()}</p>
          </div>
          {job.completed_at && (
            <div>
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Completed</span>
              <p className="mt-1 text-slate-700">{new Date(job.completed_at).toLocaleString()}</p>
            </div>
          )}
        </div>

        {job.error_message && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-700">
            {job.error_message}
          </div>
        )}
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-slate-900">Files</h2>
        {files.length === 0 ? (
          <p className="mt-2 text-sm text-slate-500">
            {job.status === "completed" ? "No files recorded." : "Files appear when the job completes."}
          </p>
        ) : (
          <ul className="mt-4 space-y-2.5">
            {files.map((file) => (
              <li key={file.id} className="card flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <FileIcon type={file.file_type} />
                  <div>
                    <p className="text-sm font-medium text-slate-800">{file.filename}</p>
                    <p className="text-xs uppercase tracking-wide text-slate-400">{file.file_type}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleDownload(file.id)}
                  disabled={downloading === file.id}
                  className="btn btn-primary"
                >
                  {downloading === file.id ? (
                    "…"
                  ) : (
                    <>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
                      </svg>
                      Download
                    </>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function JobDetailPage() {
  return (
    <AuthGuard>
      <JobDetailContent />
    </AuthGuard>
  );
}
