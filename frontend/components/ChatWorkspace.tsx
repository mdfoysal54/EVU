"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  createConversation,
  getConversation,
  getProviders,
  listConversations,
  streamConversation,
} from "../lib/api";
import type { Conversation, Message, ProviderStatus } from "../types";

export default function ChatWorkspace() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [active, setActive] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState("evu");
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [useRag, setUseRag] = useState(true);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const activeTitle = useMemo(
    () => conversations.find((c) => c.id === active)?.title ?? "New conversation",
    [conversations, active],
  );

  async function refreshConversations(selectFirst = true) {
    const data = await listConversations();
    setConversations(data);

    if (data.length && (selectFirst || active === null)) {
      await openConversation(data[0].id);
    }
  }

  async function openConversation(id: number) {
    setActive(id);
    const data = await getConversation(id);
    setMessages(data.messages ?? []);
  }

  async function newConversation() {
    const title = input.trim()
      ? input.trim().slice(0, 48)
      : "New conversation";
    const conversation = await createConversation(title);
    setConversations((prev) => [conversation, ...prev.filter((c) => c.id !== conversation.id)]);
    setActive(conversation.id);
    setMessages([]);
    setInput("");
  }

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const [convs, providerList] = await Promise.all([
          listConversations(),
          getProviders(),
        ]);
        setConversations(convs);
        setProviders(providerList);

        if (convs.length) {
          await openConversation(convs[0].id);
        } else {
          const conversation = await createConversation("New conversation");
          setConversations([conversation]);
          setActive(conversation.id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load EVU.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || !active || sending) return;

    setError("");
    setSending(true);
    setInput("");

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    const assistantMessage: Message = {
      id: Date.now() + 1,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    try {
      await streamConversation(
        active,
        text,
        provider,
        null,
        useRag,
        (delta) => {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last?.role === "assistant") {
              next[next.length - 1] = {
                ...last,
                content: last.content + delta,
              };
            }
            return next;
          });
        },
      );
      const refreshed = await getConversation(active);
      setMessages(refreshed.messages ?? []);
      await refreshConversations(false);
    } catch (err) {
      setMessages((prev) =>
        prev.map((message) =>
          message.id === assistantMessage.id
            ? {
                ...message,
                content:
                  err instanceof Error ? `Error: ${err.message}` : "EVU could not answer.",
              }
            : message,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  if (loading) {
    return <section className="workspace-loading">Loading EVU workspace…</section>;
  }

  return (
    <section className="chat-page">
      <div className="chat-sidebar">
        <div className="section-heading">
          <div>
            <p className="eyebrow">CONVERSATIONS</p>
            <h2>Your chats</h2>
          </div>
          <button className="icon-button" onClick={newConversation} title="New conversation">
            +
          </button>
        </div>

        <button className="new-chat-button" onClick={newConversation}>
          <span>＋</span> New conversation
        </button>

        <div className="conversation-list">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              className={`conversation-item ${active === conversation.id ? "active" : ""}`}
              onClick={() => openConversation(conversation.id)}
            >
              <span className="conversation-dot" />
              <span>{conversation.title}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="chat-main">
        <header className="chat-header">
          <div>
            <p className="eyebrow">EVU SESSION</p>
            <h1>{activeTitle}</h1>
          </div>

          <div className="chat-controls">
            <label className="select-wrap">
              <span>Model</span>
              <select value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="evu">EVU</option>
                {providers.map((item) => (
                  <option key={item.provider} value={item.provider}>
                    {item.provider}
                  </option>
                ))}
              </select>
            </label>

            <label className="toggle">
              <input
                type="checkbox"
                checked={useRag}
                onChange={(e) => setUseRag(e.target.checked)}
              />
              <span />
              RAG
            </label>
          </div>
        </header>

        {error && <div className="error-box page-error">{error}</div>}

        <div className="message-area">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="hero-orb">E</div>
              <p className="eyebrow">EVU AI</p>
              <h2>What are we building today?</h2>
              <p>
                Ask questions, work with your knowledge base, or continue a project.
                EVU is connected to your current backend.
              </p>

              <div className="suggestion-grid">
                {[
                  "Explain my current EVU architecture",
                  "Help me plan a coding task",
                  "Search my uploaded knowledge",
                  "What should I test before model training?",
                ].map((suggestion) => (
                  <button key={suggestion} onClick={() => setInput(suggestion)}>
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <article
                key={message.id}
                className={`message ${message.role === "user" ? "user-message" : "assistant-message"}`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? "Y" : "E"}
                </div>
                <div className="message-body">
                  <div className="message-meta">
                    {message.role === "user" ? "You" : "EVU"}
                  </div>
                  <div className="message-content">
                    {message.content || (sending ? "Thinking…" : "")}
                  </div>
                </div>
              </article>
            ))
          )}
        </div>

        <form className="composer" onSubmit={submit}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message EVU…"
            rows={1}
            disabled={sending}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <button
            className="send-button"
            disabled={sending || !input.trim() || !active}
            aria-label="Send message"
          >
            {sending ? "…" : "↑"}
          </button>
        </form>
        <p className="composer-note">
          EVU can use your conversation context and RAG knowledge when enabled.
        </p>
      </div>
    </section>
  );
}
