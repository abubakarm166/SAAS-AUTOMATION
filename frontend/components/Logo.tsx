import Image from "next/image";

export function Logo({ size = 32 }: { size?: number }) {
  return (
    <Image
      src="/logo.png"
      alt="SnapShot"
      width={size}
      height={size}
      className="rounded-lg object-contain"
      priority
    />
  );
}

export function Wordmark({ size = 32 }: { size?: number }) {
  return (
    <span className="flex items-center gap-2">
      <Logo size={size} />
      <span className="text-lg font-bold tracking-tight text-slate-900">SnapShot</span>
    </span>
  );
}
