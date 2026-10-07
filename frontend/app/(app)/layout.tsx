"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "../../components/AppShell";
import { isAuthenticated } from "../../lib/auth";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }

    const handler = () => router.replace("/login");
    window.addEventListener("evu:auth-expired", handler);
    setReady(true);

    return () => window.removeEventListener("evu:auth-expired", handler);
  }, [router]);

  if (!ready) return <main className="boot-screen">Loading workspace…</main>;

  return <AppShell>{children}</AppShell>;
}
