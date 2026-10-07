"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { deleteDocument, listDocuments, uploadDocument } from "../../../lib/api";
import type { Document } from "../../../types";

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      setDocuments(await listDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load documents.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");
    try {
      const created = await uploadDocument(file);
      setDocuments((prev) => [created, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function remove(id: number) {
    if (!window.confirm("Delete this document and its indexed content?")) return;
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed.");
    }
  }

  return (
    <section className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">KNOWLEDGE BASE</p>
          <h1>Documents & RAG</h1>
          <p className="muted">
            Upload documents and let the backend index them for retrieval-augmented chat.
          </p>
        </div>

        <label className="primary-button upload-button">
          {uploading ? "Indexing…" : "Upload document"}
          <input
            type="file"
            hidden
            onChange={onFile}
            disabled={uploading}
            accept=".txt,.md,.pdf,.docx,.csv"
          />
        </label>
      </header>

      {error && <div className="error-box page-error">{error}</div>}

      <div className="stat-row">
        <div className="stat-card">
          <span>Documents</span>
          <strong>{documents.length}</strong>
        </div>
        <div className="stat-card">
          <span>Total indexed chunks</span>
          <strong>{documents.reduce((sum, item) => sum + item.chunk_count, 0)}</strong>
        </div>
        <div className="stat-card">
          <span>RAG status</span>
          <strong className="success-text">Ready</strong>
        </div>
      </div>

      <div className="data-card">
        <div className="data-card-header">
          <h2>Indexed documents</h2>
          <span>{documents.length} files</span>
        </div>

        {documents.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">▣</div>
            <h3>No documents yet</h3>
            <p>Upload a PDF, text, Markdown, DOCX or CSV file to start building EVU knowledge.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Size</th>
                  <th>Chunks</th>
                  <th>Added</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <strong>{doc.filename}</strong>
                      <small>{doc.content_type || "unknown type"}</small>
                    </td>
                    <td>{formatBytes(doc.size_bytes)}</td>
                    <td>{doc.chunk_count}</td>
                    <td>{new Date(doc.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className="danger-link" onClick={() => remove(doc.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
