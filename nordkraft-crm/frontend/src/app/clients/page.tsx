"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clientsApi } from "@/lib/api";
import { Client } from "@/types";
import { useState } from "react";
import { Plus, ExternalLink, TrendingUp, AlertTriangle, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";

function HealthBadge({ status, score }: { status: Client["health_status"]; score: number }) {
  const config = {
    healthy:  { label: "Healthy",  color: "#00c98d", bg: "bg-nk-green/15",  icon: CheckCircle },
    at_risk:  { label: "At risk",  color: "#f5a623", bg: "bg-nk-warn/15",   icon: AlertTriangle },
    churning: { label: "Churning", color: "#e84040", bg: "bg-nk-danger/15", icon: AlertTriangle },
  }[status] ?? { label: status, color: "#8892a0", bg: "bg-nk-surface2", icon: CheckCircle };

  const Icon = config.icon;
  return (
    <span className={cn("flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded", config.bg)}
          style={{ color: config.color }}>
      <Icon size={10} />
      {config.label} · {score}%
    </span>
  );
}

function ClientCard({ client }: { client: Client }) {
  const initials = client.company_name.slice(0, 2).toUpperCase();
  const hue = client.company_name.charCodeAt(0) * 11 % 360;
  const daysUntilRenewal = client.contract_end
    ? Math.ceil((new Date(client.contract_end).getTime() - Date.now()) / 86400000)
    : null;

  return (
    <div className="bg-nk-surface border border-nk-border rounded-xl p-4 hover:border-nk-accent/30 transition-colors">
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center text-[13px] font-bold text-white shrink-0"
          style={{ background: `hsl(${hue},55%,40%)` }}
        >
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[13px] font-semibold text-nk-text truncate">{client.company_name}</div>
          <div className="text-[11px] text-nk-muted">{client.plan ?? "No plan"} · {client.country ?? "—"}</div>
        </div>
        {client.portal_url && (
          <a href={client.portal_url} target="_blank" rel="noreferrer"
             className="text-nk-muted hover:text-nk-accent transition-colors">
            <ExternalLink size={13} />
          </a>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        {[
          { label: "MRR",   value: `€${client.mrr.toLocaleString()}`, color: "text-nk-green" },
          { label: "ARR",   value: `€${(client.mrr * 12 / 1000).toFixed(0)}k`, color: "text-nk-accent" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-nk-surface2 rounded-lg p-2.5">
            <div className="text-[10px] text-nk-muted">{label}</div>
            <div className={cn("text-[14px] font-semibold mt-0.5", color)}>{value}</div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <HealthBadge status={client.health_status} score={client.health_score} />
        {daysUntilRenewal !== null && (
          <span className={cn(
            "text-[10px] px-2 py-0.5 rounded",
            daysUntilRenewal <= 30
              ? "bg-nk-warn/15 text-nk-warn"
              : "bg-nk-surface2 text-nk-muted"
          )}>
            Renews in {daysUntilRenewal}d
          </span>
        )}
      </div>
    </div>
  );
}

export default function ClientsPage() {
  const [filter, setFilter] = useState<"all" | "healthy" | "at_risk" | "churning">("all");

  const { data: clients = [], isLoading } = useQuery<Client[]>({
    queryKey: ["clients"],
    queryFn: clientsApi.list,
  });

  const filtered = filter === "all" ? clients : clients.filter((c) => c.health_status === filter);

  const totalMrr   = clients.reduce((s, c) => s + c.mrr, 0);
  const healthyPct = clients.length
    ? Math.round(clients.filter((c) => c.health_status === "healthy").length / clients.length * 100)
    : 0;

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-4 gap-3 mb-5">
        {[
          { label: "Total clients",  value: String(clients.length) },
          { label: "Total MRR",      value: `€${totalMrr.toLocaleString()}` },
          { label: "Total ARR",      value: `€${(totalMrr * 12 / 1000).toFixed(0)}k` },
          { label: "Health score",   value: `${healthyPct}%` },
        ].map(({ label, value }) => (
          <div key={label} className="bg-nk-surface border border-nk-border rounded-xl p-4">
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">{label}</div>
            <div className="text-2xl font-semibold">{value}</div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex bg-nk-surface2 border border-nk-border rounded-lg p-0.5 gap-0.5">
          {(["all", "healthy", "at_risk", "churning"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "text-[12px] px-3 py-1.5 rounded transition-all",
                filter === f
                  ? "bg-nk-accent text-white"
                  : "text-nk-muted hover:text-nk-text"
              )}
            >
              {f === "all" ? "All" : f === "at_risk" ? "At risk" : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex-1" />
        <a
          href="/clients/new"
          className="bg-nk-accent text-white text-[13px] font-medium px-3.5 py-2 rounded-lg flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors"
        >
          <Plus size={13} /> New client
        </a>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="text-center py-20 text-nk-muted text-[13px]">Loading clients...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-nk-muted text-[13px]">No clients found</div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {filtered.map((client) => (
            <ClientCard key={client.id} client={client} />
          ))}
        </div>
      )}
    </div>
  );
}
