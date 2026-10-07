"use client";

import { useEffect, useState } from "react";
import { getLocalModels, getProviders, health, me } from "../../../lib/api";
import type { HealthResponse, ProviderStatus, User } from "../../../types";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [localModels, setLocalModels] = useState<unknown>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [userData, providerData, healthDataValue, localData] =
          await Promise.all([me(), getProviders(), health(), getLocalModels()]);
        setUser(userData);
        setProviders(providerData);
        setHealthData(healthDataValue);
        setLocalModels(localData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load settings.");
      }
    })();
  }, []);

  return (
    <section className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">SYSTEM</p>
          <h1>Settings & status</h1>
          <p className="muted">
            This page reads the current backend directly. It does not invent provider or model state.
          </p>
        </div>
      </header>

      {error && <div className="error-box page-error">{error}</div>}

      <div className="settings-grid">
        <div className="data-card">
          <div className="data-card-header">
            <h2>Account</h2>
          </div>
          <div className="setting-line">
            <span>Email</span>
            <strong>{user?.email || "—"}</strong>
          </div>
          <div className="setting-line">
            <span>User ID</span>
            <strong>{user?.id ?? "—"}</strong>
          </div>
        </div>

        <div className="data-card">
          <div className="data-card-header">
            <h2>Backend health</h2>
          </div>
          {healthData ? (
            <div className="health-grid">
              <HealthItem label="API" value={healthData.status} good={healthData.status === "healthy"} />
              <HealthItem label="Database" value={String(healthData.database)} good={healthData.database} />
              <HealthItem label="Redis" value={healthData.redis_enabled ? String(healthData.redis) : "disabled"} good={!healthData.redis_enabled || healthData.redis} />
              <HealthItem label="RAG" value={String(healthData.rag_enabled)} good={healthData.rag_enabled} />
              <HealthItem label="Memory" value={String(healthData.memory_enabled)} good={healthData.memory_enabled} />
              <HealthItem label="Research" value={String(healthData.research_enabled)} good={healthData.research_enabled} />
            </div>
          ) : (
            <p className="muted">Loading…</p>
          )}
        </div>

        <div className="data-card">
          <div className="data-card-header">
            <h2>Providers</h2>
            <span>{providers.length}</span>
          </div>
          <div className="provider-list">
            {providers.length === 0 ? (
              <p className="muted">No provider metadata returned by the backend.</p>
            ) : (
              providers.map((item) => (
                <div className="provider-row" key={item.provider}>
                  <div>
                    <strong>{item.provider}</strong>
                    <small>{item.model || "Model managed by backend"}</small>
                  </div>
                  <span className={`status-pill ${item.configured || item.enabled ? "online" : "neutral"}`}>
                    {item.configured || item.enabled ? "available" : "not configured"}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="data-card">
          <div className="data-card-header">
            <h2>Local model runtime</h2>
          </div>
          <pre className="json-view">
            {localModels ? JSON.stringify(localModels, null, 2) : "No local model data returned."}
          </pre>
        </div>
      </div>
    </section>
  );
}

function HealthItem({
  label,
  value,
  good,
}: {
  label: string;
  value: string;
  good: boolean;
}) {
  return (
    <div className="health-item">
      <span className={`status-dot ${good ? "" : "bad"}`} />
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
      </div>
    </div>
  );
}
