"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsApi } from "@/lib/api";
import { Lead, LeadStatus } from "@/types";
import { useState } from "react";
import { Sparkles, Plus } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const STAGES: { key: LeadStatus; label: string; color: string }[] = [
  { key: "new",           label: "New",         color: "#8892a0" },
  { key: "qualified",     label: "Qualified",    color: "#3b7ff5" },
  { key: "proposal_sent", label: "Proposal",     color: "#f5a623" },
  { key: "negotiation",   label: "Negotiation",  color: "#a855f7" },
  { key: "won",           label: "Won",          color: "#00c98d" },
  { key: "lost",          label: "Lost",         color: "#e84040" },
];

function LeadCard({ lead, onMove }: { lead: Lead; onMove: (id: string, status: string) => void }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const nextStages = STAGES.filter((s) => s.key !== lead.status);

  return (
    <div
      className="bg-nk-surface2 border border-nk-border rounded-lg p-3 hover:border-nk-accent/40 transition-colors cursor-pointer group relative"
      onClick={() => setMenuOpen((v) => !v)}
    >
      <div className="text-[12px] font-medium text-nk-text truncate">
        {lead.first_name} {lead.last_name}
      </div>
      <div className="text-[11px] text-nk-muted truncate mt-0.5">{lead.company_name}</div>
      <div className="flex items-center justify-between mt-2">
        <span className="text-[11px] font-semibold text-nk-green">
          €{(lead.estimated_value / 1000).toFixed(1)}k/yr
        </span>
        {lead.ai_score > 0 && (
          <span className="text-[10px] bg-purple-900/40 text-purple-300 px-1.5 py-0.5 rounded">
            AI {lead.ai_score}
          </span>
        )}
      </div>
      {lead.industry && (
        <div className="mt-1.5">
          <span className="text-[10px] bg-nk-accent/15 text-blue-300 px-1.5 py-0.5 rounded">
            {lead.industry}
          </span>
        </div>
      )}

      {/* Move menu */}
      {menuOpen && (
        <div
          className="absolute top-full left-0 mt-1 w-44 bg-nk-surface border border-nk-border2 rounded-lg shadow-xl z-50 overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="px-3 py-2 text-[10px] text-nk-muted uppercase tracking-[0.5px] border-b border-nk-border">
            Move to stage
          </div>
          {nextStages.map((s) => (
            <button
              key={s.key}
              onClick={() => { onMove(lead.id, s.key); setMenuOpen(false); }}
              className="w-full text-left px-3 py-2 text-[12px] text-nk-text hover:bg-nk-surface2 flex items-center gap-2"
            >
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: s.color }} />
              {s.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PipelinePage() {
  const qc = useQueryClient();

  const { data: leads = [], isLoading } = useQuery<Lead[]>({
    queryKey: ["leads-pipeline"],
    queryFn: () => leadsApi.list({ limit: 200 }),
  });

  const moveMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      leadsApi.move(id, status),
    onSuccess: () => {
      toast.success("Stage updated");
      qc.invalidateQueries({ queryKey: ["leads-pipeline"] });
      qc.invalidateQueries({ queryKey: ["leads"] });
    },
    onError: () => toast.error("Failed to move lead"),
  });

  const byStage = STAGES.reduce((acc, s) => {
    acc[s.key] = leads.filter((l) => l.status === s.key);
    return acc;
  }, {} as Record<string, Lead[]>);

  const pipelineValue = leads
    .filter((l) => !["won", "lost"].includes(l.status))
    .reduce((sum, l) => sum + l.estimated_value, 0);

  return (
    <div>
      {/* Header bar */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-4">
          <div className="bg-nk-surface border border-nk-border rounded-xl px-4 py-3">
            <div className="text-[10px] text-nk-muted uppercase tracking-[0.5px]">Pipeline value</div>
            <div className="text-[18px] font-semibold text-nk-text mt-0.5">
              €{(pipelineValue / 1000).toFixed(0)}k
            </div>
          </div>
          <div className="bg-nk-surface border border-nk-border rounded-xl px-4 py-3">
            <div className="text-[10px] text-nk-muted uppercase tracking-[0.5px]">Active deals</div>
            <div className="text-[18px] font-semibold text-nk-text mt-0.5">
              {leads.filter((l) => !["won", "lost"].includes(l.status)).length}
            </div>
          </div>
        </div>
        <a
          href="/leads/new"
          className="bg-nk-accent text-white text-[13px] font-medium px-3.5 py-2 rounded-lg flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors"
        >
          <Plus size={13} /> New lead
        </a>
      </div>

      {/* Kanban board */}
      {isLoading ? (
        <div className="text-center py-20 text-nk-muted text-[13px]">Loading pipeline...</div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-4" style={{ minHeight: "500px" }}>
          {STAGES.map((stage) => {
            const stageLeads = byStage[stage.key] ?? [];
            const stageValue = stageLeads.reduce((s, l) => s + l.estimated_value, 0);
            return (
              <div key={stage.key} className="min-w-[200px] max-w-[200px] flex flex-col">
                {/* Column header */}
                <div className="flex items-center justify-between mb-3 px-0.5">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full" style={{ background: stage.color }} />
                    <span className="text-[11px] font-semibold uppercase tracking-[0.6px] text-nk-muted">
                      {stage.label}
                    </span>
                  </div>
                  <span className="bg-nk-surface2 border border-nk-border text-nk-muted text-[10px] px-2 py-0.5 rounded-full">
                    {stageLeads.length}
                  </span>
                </div>

                {/* Stage value */}
                {stageValue > 0 && (
                  <div className="text-[10px] text-nk-muted mb-2 px-0.5">
                    €{(stageValue / 1000).toFixed(0)}k total
                  </div>
                )}

                {/* Cards */}
                <div className="flex flex-col gap-2 flex-1">
                  {stageLeads.map((lead) => (
                    <LeadCard
                      key={lead.id}
                      lead={lead}
                      onMove={(id, status) => moveMutation.mutate({ id, status })}
                    />
                  ))}
                  {stageLeads.length === 0 && (
                    <div className="border border-dashed border-nk-border rounded-lg p-4 text-center text-[11px] text-nk-muted/50">
                      No leads
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
