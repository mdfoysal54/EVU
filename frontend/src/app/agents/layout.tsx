"use client";

import type React from "react";
import { useEffect, useState } from "react";
import Authed from "@/components/layout/Authed";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Avoid rendering client-only auth wrapper before hydration is complete
  if (!mounted) {
    return <div style={{ visibility: "hidden" }}>{children}</div>;
  }

  return <Authed>{children}</Authed>;
}