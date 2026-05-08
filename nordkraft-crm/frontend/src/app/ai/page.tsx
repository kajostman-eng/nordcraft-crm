"use client";
import { useState, useRef, useEffect } from "react";
import { aiApi } from "@/lib/api";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import {
  Sparkles, Send, FileText, Mail, Mic, Bot, Brain, Zap,
} from "lucide-react";

type Message = { role: "user" | "assistant"; content: string };

function AIChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm your NordKraft AI assistant. I can help with lead qualification, proposal writing, client health analysis, and automation recommendations. What do you need?" },
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      aiApi.chat(message, "general", undefined, messages),
    onSuccess: (data, message) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    },
    onError: () => toast.error("AI chat failed"),
  });

  const send = () => {
    if (!input.trim() || chatMutation.isPending) return;
    const msg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    chatMutation.mutate(msg);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden flex flex-col h-[520px]">
      <div className="px-4 py-3.5 border-b border-nk-border flex items-center gap-2">
        <Bot size={15} className="text-nk-accent" />
        <h3 className="text-[13px] font-semibold">AI Assistant</h3>
        <span className="ml-auto text-[10px] bg-nk-green/15 text-nk-green px-2 py-0.5 rounded-full">Online</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {messages.map((m, i) => (
          <div key={i} className={cn("flex gap-2.5", m.role === "user" && "flex-row-reverse")}>
            <div className={cn(
              "w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[11px] font-semibold",
              m.role === "assistant" ? "bg-nk-accent/20 text-nk-accent" : "bg-nk-surface2 text-nk-muted"
            )}>
              {m.role === "assistant" ? <Bot size={13} /> : "Me"}
            </div>
            <div className={cn(
              "max-w-[80%] text-[13px] leading-relaxed px-3 py-2 rounded-xl",
              m.role === "assistant"
                ? "bg-nk-surface2 text-nk-text"
                : "bg-nk-accent text-white"
            )}>
              {m.content}
            </div>
          </div>
        ))}
        {chatMutation.isPending && (
          <div className="flex gap-2.5">
            <div className="w-7 h-7 rounded-full bg-nk-accent/20 flex items-center justify-center">
              <Bot size={13} className="text-nk-accent" />
            </div>
            <div className="bg-nk-surface2 px-3 py-2 rounded-xl text-nk-muted text-[13px]">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-3 border-t border-nk-border">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
            placeholder="Ask about leads, proposals, automation..."
            className="flex-1 bg-nk-surface2 border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text placeholder:text-nk-muted outline-none focus:border-nk-accent/50"
          />
          <button
            onClick={send}
            disabled={chatMutation.isPending || !input.trim()}
            className="bg-nk-accent text-white px-3 py-2 rounded-lg hover:bg-nk-accent/90 disabled:opacity-50 transition-colors"
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

function MeetingSummaryPanel() {
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: () => aiApi.meetingSummary(transcript),
    onSuccess: (data) => setResult(data),
    onError: () => toast.error("Summary failed"),
  });

  return (
    <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
      <div className="px-4 py-3.5 border-b border-nk-border flex items-center gap-2">
        <Mic size={15} className="text-nk-green" />
        <h3 className="text-[13px] font-semibold">Meeting summarizer</h3>
      </div>
      <div className="p-4">
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Paste meeting transcript here..."
          rows={5}
          className="w-full bg-nk-surface2 border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text placeholder:text-nk-muted outline-none focus:border-nk-accent/50 resize-none"
        />
        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || !transcript.trim()}
          className="mt-3 bg-nk-green text-white text-[13px] font-medium px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-nk-green/90 disabled:opacity-50 transition-colors"
        >
          <Sparkles size={13} />
          {mutation.isPending ? "Summarising..." : "Summarise & extract tasks"}
        </button>

        {result && (
          <div className="mt-4 space-y-3">
            <div className="bg-nk-surface2 rounded-lg p-3">
              <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Summary</div>
              <p className="text-[13px] text-nk-text leading-relaxed">{result.summary}</p>
            </div>
            {result.action_items?.length > 0 && (
              <div className="bg-nk-surface2 rounded-lg p-3">
                <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-2">Action items</div>
                {result.action_items.map((item: any, i: number) => (
                  <div key={i} className="flex items-start gap-2 mb-1.5">
                    <span className="text-nk-accent text-[12px] mt-0.5">›</span>
                    <div>
                      <span className="text-[12px] text-nk-text">{item.title}</span>
                      <span className="text-[11px] text-nk-muted ml-2">— {item.due}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className={cn(
                "text-[10px] font-medium px-2 py-0.5 rounded capitalize",
                result.sentiment === "positive"
                  ? "bg-nk-green/15 text-nk-green"
                  : result.sentiment === "negative"
                  ? "bg-nk-danger/15 text-nk-danger"
                  : "bg-nk-surface2 text-nk-muted"
              )}>
                {result.sentiment} sentiment
              </span>
              {result.next_meeting_suggested && (
                <span className="text-[10px] bg-nk-accent/15 text-nk-accent px-2 py-0.5 rounded">
                  Follow-up meeting suggested
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const QUICK_PROMPTS = [
  { icon: Brain,    color: "text-purple-400",  label: "Qualify top leads",         msg: "Review all leads in the pipeline and rank top 5 by AI score. Suggest the next action for each." },
  { icon: FileText, color: "text-blue-400",    label: "Generate proposals",         msg: "List all leads in the proposal stage and generate a follow-up strategy for each." },
  { icon: Zap,      color: "text-nk-green",    label: "Automation opportunities",  msg: "What are the best automation opportunities we should be building for our current clients?" },
  { icon: Mail,     color: "text-nk-warn",     label: "Draft renewal emails",       msg: "Draft renewal outreach emails for clients whose contracts are expiring in the next 30 days." },
  { icon: Bot,      color: "text-nk-accent",   label: "Client health check",        msg: "Analyse which clients may be at risk of churning based on their health scores and suggest interventions." },
  { icon: Sparkles, color: "text-nk-muted",    label: "Weekly report",              msg: "Generate a brief weekly summary of NordKraft CRM activity: leads, pipeline changes, and automation stats." },
];

export default function AIToolsPage() {
  const [chatInput, setChatInput] = useState("");

  return (
    <div>
      <div className="grid grid-cols-[1fr_340px] gap-4">
        <div className="space-y-4">
          <AIChatPanel />
          <MeetingSummaryPanel />
        </div>

        <div className="space-y-4">
          {/* Quick prompts */}
          <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
            <div className="px-4 py-3.5 border-b border-nk-border">
              <h3 className="text-[13px] font-semibold">Quick actions</h3>
            </div>
            <div className="p-3 flex flex-col gap-2">
              {QUICK_PROMPTS.map(({ icon: Icon, color, label, msg }) => (
                <button
                  key={label}
                  onClick={() => {
                    // Inject into chat (scroll to chat)
                    const el = document.querySelector("input[placeholder*='Ask']") as HTMLInputElement;
                    if (el) { el.value = msg; el.focus(); }
                  }}
                  className="flex items-center gap-2.5 text-left w-full bg-nk-surface2 border border-nk-border hover:border-nk-accent/30 rounded-lg px-3 py-2.5 transition-colors"
                >
                  <Icon size={14} className={color} />
                  <span className="text-[12px] text-nk-text">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Knowledge assistant hint */}
          <div className="bg-nk-accent/10 border border-nk-accent/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Brain size={14} className="text-nk-accent" />
              <span className="text-[12px] font-semibold text-nk-accent">Knowledge assistant</span>
            </div>
            <p className="text-[11px] text-nk-muted leading-relaxed">
              Ask the AI to recall past projects, SOPs, automation patterns, or client context. Example:
            </p>
            <div className="mt-2 bg-nk-surface2 rounded-lg px-3 py-2 text-[11px] text-nk-muted italic">
              "How did we implement WhatsApp automation for a logistics client?"
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
