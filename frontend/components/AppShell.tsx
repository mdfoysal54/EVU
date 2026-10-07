"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "../lib/auth";

const items = [
  { href: "/chat", label: "Chat", icon: "✦" },
  { href: "/documents", label: "Knowledge", icon: "▣" },
  { href: "/memory", label: "Memory", icon: "◈" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export default function AppShell({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearToken();
    router.replace("/login");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark small">EVU</div>
          <div>
            <strong>EVU AI</strong>
            <span>Workspace</span>
          </div>
        </div>

        <nav className="main-nav">
          {items.map((item) => {
            const active =
              pathname === item.href ||
              (item.href === "/chat" && pathname.startsWith("/chat/"));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item ${active ? "active" : ""}`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="independence-card">
            <span className="status-dot" />
            <div>
              <strong>EVU Core</strong>
              <small>Platform connected</small>
            </div>
          </div>

          <button className="ghost-button full" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
