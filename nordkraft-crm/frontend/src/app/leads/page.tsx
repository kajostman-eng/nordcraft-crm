"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { leadsApi, aiApi } from "@/lib/api";
import { Lead } from "@/types";
import { useState } from "react";
import { Sparkles, Plus, ExternalLink } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const STATUS_COLORS: Record<string, string> = {
  new: "bg-nk-accent/20 text-blue-300",
  contacted: "bg-nk-accent/20 text-blue-300",
  qualified: "bg-nk-green/20 text-green-300",
  discovery_booked: "bg-nk-green/20 text-green-300",
  proposal_sent: "bg-nk-warn/20 text-yellow-300",
  negotiation: "bg-nk-warn/20 text-yellow-300",
  won: "bg-nk-green/20 text-nk-green",
  lost: "bg-nk-danger/20 text-red-300",
  onboarding: "bg-nk-green/20 text-nk-green",
};

export default function LeadsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  const { data: leads = [], isLoading } = useQuery<Lead[]>({
    queryKey: ["leads", search, filterStatus],
    queryFn: () => leadsApi.list({
      ...(search ? { search } : {}),
      ...(filterStatus ? { status: filterStatus } : {}),
      limit: 100,
    }),
  });

  const assessMutation = useMutation({
    mutationFn: (leadId: string) => aiApi.assess(leadId),
    onSuccess: (data, leadId) => {
      toast.success(`AI score: ${data.ai_score} · ROI: ${data.estimated_roi_multiplier}x`);
      qc.invalidateQueries({ queryKey: ["leads"] });
    },
  });

  return (
    <div>
      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-nk-surface border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text placeholder:text-nk-muted w-64 outline-none focus:border-nk-accent/50"
          placeholder="Search leads..."
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-nk-surface border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text outline-none"
        >
          <option value="">All stages</option>
          <option value="new">New</option>
          <option value="qualified">Qualified</option>
          <option value="proposal_sent">Proposal sent</option>
          <option value="negotiation">Negotiation</option>
          <option value="won">Won</option>
        </select>
        <div className="flex-1" />
        <a
          href="/leads/new"
          className="bg-nk-accent text-white text-[13px] font-medium px-3.5 py-2 rounded-lg flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors"
        >
          <Plus size={13} /> New lead
        </a>
      </div>

      {/* Table */}
      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-nk-border text-[11px] text-nk-muted uppercase tracking-[0.5px]">
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Company</th>
              <th className="text-left px-4 py-3 font-medium">Industry</th>
              <th className="text-left px-4 py-3 font-medium">Stage</th>
              <th className="text-left px-4 py-3 font-medium">Value</th>
              <th className="text-left px-4 py-3 font-medium">AI Score</th>
              <th className="text-left px-4 py-3 font-medium">ROI est.</th>
              <th className="text-right px-4 py-3 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-nk-border">
            {isLoading ? (
              <tr><td colSpan={8} className="text-center py-12 text-nk-muted text-[13px]">Loading...</td></tr>
            ) : leads.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-12 text-nk-muted text-[13px]">No leads found</td></tr>
            ) : leads.map((lead) => (
              <tr key={lead.id} className="hover:bg-nk-surface2/50 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center text-[11px] font-semibold text-white shrink-0"
                      style={{ background: `hsl(${(lead.ai_score || 50) * 2}, 65%, 42%)` }}
                    >
                      {lead.first_name[0]}{lead.last_name[0]}
                    </div>
                    <div>
                      <div className="text-[13px] font-medium">{lead.first_name} {lead.last_name}</div>
                      <div className="text-[11px] text-nk-muted">{lead.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-[13px]">{lead.company_name || "—"}</td>
                <td className="px-4 py-3 text-[13px] text-nk-muted">{lead.industry || "—"}</td>
                <td className="px-4 py-3">
                  <span className={cn("text-[11px] font-medium px-2 py-0.5 rounded capitalize", STATUS_COLORS[lead.status] || "bg-nk-surface2 text-nk-muted")}>
                    {lead.status.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-4 py-3 text-[13px] font-medium text-nk-green">
                  €{(lead.estimated_value / 1000).toFixed(1)}k
                </td>
                <td className="px-4 py-3">
                  {lead.ai_score > 0 ? (
                    <div className="flex items-center gap-2">
                      <span className={cn("text-[13px] font-semibold",
                        lead.ai_score >= 80 ? "text-nk-green" : lead.ai_score >= 60 ? "text-nk-accent" : "text-nk-warn"
                      )}>
                        {lead.ai_score}
                      </span>
                      <div className="w-10 h-1 rounded-full bg-nk-surface2 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${lead.ai_score}%`,
                            background: lead.ai_score >= 80 ? "#00c98d" : lead.ai_score >= 60 ? "#3b7ff5" : "#f5a623",
                          }}
                        />
                      </div>
                    </div>
                  ) : (
                    <span className="text-[11px] text-nk-muted">Not scored</span>
                  )}
                </td>
                <td className="px-4 py-3 text-[13px]">
                  {lead.estimated_roi_multiplier > 0
                    ? <span className="text-nk-green font-medium">{lead.estimated_roi_multiplier}×</span>
                    : <span className="text-nk-muted">—</span>
                  }
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => assessMutation.mutate(lead.id)}
                      disabled={assessMutation.isPending}
                      className="text-[11px] text-nk-purple border border-nk-purple/30 px-2 py-1 rounded hover:bg-nk-purple/10 transition-colors flex items-center gap-1"
                    >
                      <Sparkles size={11} /> Assess
                    </button>
                    <a
                      href={`/leads/${lead.id}`}
                      className="text-[11px] text-nk-muted border border-nk-border2 px-2 py-1 rounded hover:bg-nk-surface2 transition-colors"
                    >
                      <ExternalLink size={11} />
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
