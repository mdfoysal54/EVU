"use client";

import { FormEvent, useEffect, useState } from "react";
import { createMemory, deleteMemory, listMemories } from "../../../lib/api";
import type { Memory } from "../../../types";

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [category, setCategory] = useState("general");
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      setMemories(await listMemories());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load memory.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!key.trim() || !value.trim()) return;

    setSaving(true);
    setError("");
    try {
      const created = await createMemory({
        category,
        key: key.trim(),
        value: value.trim(),
        source: "frontend",
        confidence: 1,
      });
      setMemories((prev) => [created, ...prev]);
      setKey("");
      setValue("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save memory.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(id: number) {
    try {
      await deleteMemory(id);
      setMemories((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete memory.");
    }
  }

  return (
    <section className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">PERSONAL CONTEXT</p>
          <h1>EVU Memory</h1>
          <p className="muted">
            Manage durable user facts that the current backend can inject into conversations.
          </p>
        </div>
      </header>

      {error && <div className="error-box page-error">{error}</div>}

      <div className="memory-layout">
        <form className="data-card memory-form" onSubmit={submit}>
          <div className="data-card-header">
            <h2>Add memory</h2>
            <span>Explicit</span>
          </div>

          <label>
            Category
            <input value={category} onChange={(e) => setCategory(e.target.value)} />
          </label>

          <label>
            Key
            <input
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="e.g. preferred_language"
              required
            />
          </label>

          <label>
            Value
            <textarea
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="e.g. English"
              rows={5}
              required
            />
          </label>

          <button className="primary-button" disabled={saving}>
            {saving ? "Saving…" : "Save memory"}
          </button>
        </form>

        <div className="data-card">
          <div className="data-card-header">
            <h2>Saved memories</h2>
            <span>{memories.length}</span>
          </div>

          {memories.length === 0 ? (
            <div className="empty-state compact">
              <div className="empty-icon">◈</div>
              <h3>No memories saved</h3>
              <p>Explicit memories captured through chat will also appear here.</p>
            </div>
          ) : (
            <div className="memory-list">
              {memories.map((memory) => (
                <article className="memory-item" key={memory.id}>
                  <div className="memory-top">
                    <span className="badge">{memory.category}</span>
                    <button className="danger-link" onClick={() => remove(memory.id)}>
                      Delete
                    </button>
                  </div>
                  <strong>{memory.key}</strong>
                  <p>{memory.value}</p>
                  <small>
                    Confidence {Math.round(memory.confidence * 100)}% · {memory.source}
                  </small>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
