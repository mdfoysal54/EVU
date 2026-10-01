"use client";

import React, { useState, type ChangeEvent } from "react";
import { apiPost } from "@/lib/api";
import { Card, Page } from "@/components/ui/Page";

export default function AgentPage() {
  const [message, setMessage] = useState<string>("");
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState<boolean>(false);

  async function run() {
    if (!message.trim() || loading) return;
    setLoading(true);
    try {
      const res = await apiPost("/agent/run", {
        message,
        provider: "openai",
        use_rag: true,
        max_steps: 4,
      });
      setData(res);
    } catch (error) {
      console.error("Failed to run agent:", error);
    } finally {
      setLoading(false);
    }
  }

  const handleMessageChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  return (
    <Page title="Agents" description="Run the current EVU agent runtime.">
      <Card className="form">
        <label className="label">
          Task
          <textarea
            className="textarea"
            value={message}
            onChange={handleMessageChange}
            placeholder="Enter instructions for the agent..."
          />
        </label>
        <button className="button" onClick={run} disabled={loading}>
          {loading ? "Running..." : "Run agent"}
        </button>
        {data !== null && data !== undefined ? (
          <pre className="json">{JSON.stringify(data, null, 2)}</pre>
        ) : null}
      </Card>
    </Page>
  );
}