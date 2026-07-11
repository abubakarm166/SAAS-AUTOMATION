"use client";

import { useEffect, useState } from "react";

import { Nav } from "@/components/Nav";

/** Renders Nav only after mount to avoid SSR/localStorage hydration mismatch. */
export function ClientOnlyNav() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(true);
  }, []);

  if (!ready) return null;

  return <Nav />;
}
