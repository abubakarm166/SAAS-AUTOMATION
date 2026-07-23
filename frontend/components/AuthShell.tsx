import { Logo } from "@/components/Logo";

const features = [
  "Cloud-run property reports (PDF + Excel)",
  "Submit addresses, track jobs in real time",
  "Secure downloads and email delivery",
];

export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="auth-bg grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden overflow-hidden lg:block">
        <div className="brand-gradient absolute inset-0" />
        <div className="absolute inset-0 opacity-20 [background-image:radial-gradient(circle_at_1px_1px,white_1px,transparent_0)] [background-size:22px_22px]" />
        <div className="relative flex h-full flex-col justify-between p-12 text-white">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center overflow-hidden rounded-xl bg-white/15 p-1.5 backdrop-blur">
              <Logo size={36} />
            </span>
            <span className="text-xl font-bold tracking-tight">SnapShot</span>
          </div>

          <div className="max-w-md">
            <h2 className="text-3xl font-bold leading-tight">
              Property report automation, in the cloud.
            </h2>
            <ul className="mt-8 space-y-4">
              {features.map((f) => (
                <li key={f} className="flex items-start gap-3 text-white/90">
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white/20">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 6 9 17l-5-5" />
                    </svg>
                  </span>
                  {f}
                </li>
              ))}
            </ul>
          </div>

          <p className="text-sm text-white/60">SnapShot Property Report SaaS</p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <Logo size={36} />
            <span className="text-xl font-bold tracking-tight text-slate-900">SnapShot</span>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
