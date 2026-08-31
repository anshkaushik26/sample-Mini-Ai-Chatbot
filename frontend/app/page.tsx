"use client";

import { useEffect, useRef, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import MessageBubble from "@/components/MessageBubble";
import ChatInput from "@/components/ChatInput";
import {
  type Conversation,
  type Message,
  createConversation,
  listConversations,
  getMessages,
  deleteConversation,
  streamChat,
} from "@/lib/api";

export default function Home() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    refreshConversations();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  async function refreshConversations() {
    try {
      const list = await listConversations();
      setConversations(list);
    } catch {
      setError("Could not reach backend. Is it running?");
    }
  }

  async function handleNewChat() {
    setError(null);
    try {
      const conv = await createConversation();
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
      setMessages([]);
    } catch {
      setError("Failed to create conversation.");
    }
  }

  async function handleSelect(id: string) {
    setError(null);
    setActiveId(id);
    try {
      const msgs = await getMessages(id);
      setMessages(msgs);
    } catch {
      setError("Failed to load messages.");
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeId === id) {
        setActiveId(null);
        setMessages([]);
      }
    } catch {
      setError("Failed to delete conversation.");
    }
  }

  async function handleSend(text: string) {
    setError(null);
    let conversationId = activeId;

    if (!conversationId) {
      try {
        const conv = await createConversation(text.slice(0, 40));
        setConversations((prev) => [conv, ...prev]);
        conversationId = conv.id;
        setActiveId(conv.id);
      } catch {
        setError("Failed to create conversation.");
        return;
      }
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);
    setStreamingText("");

    try {
      let full = "";
      await streamChat(conversationId, text, (chunk) => {
        full += chunk;
        setStreamingText(full);
      });
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: full,
          created_at: new Date().toISOString(),
        },
      ]);
      refreshConversations();
    } catch {
      setError("Streaming failed. Check backend and Gemini API key.");
    } finally {
      setIsStreaming(false);
      setStreamingText("");
    }
  }

  const activeConversation = conversations.find((c) => c.id === activeId);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-neutral-900 text-neutral-100">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelect}
        onNewChat={handleNewChat}
        onDelete={handleDelete}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header title={activeConversation?.title || "Rivram Mini"} />
        {error && (
          <div className="bg-red-900/40 px-4 py-2 text-center text-xs text-red-300">
            {error}
          </div>
        )}
        <main className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto flex max-w-3xl flex-col gap-4">
            {messages.length === 0 && !isStreaming && (
              <p className="mt-20 text-center text-sm text-neutral-500">
                Start a new conversation below.
              </p>
            )}
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} />
            ))}
            {isStreaming && (
              <MessageBubble
                message={{
                  id: "streaming",
                  role: "assistant",
                  content: streamingText || "…",
                  created_at: "",
                }}
              />
            )}
            <div ref={bottomRef} />
          </div>
        </main>
        <ChatInput onSend={handleSend} disabled={isStreaming} />
      </div>
    </div>
  );
}
