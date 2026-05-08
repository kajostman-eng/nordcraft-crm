"use client";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi, leadsApi } from "@/lib/api";
import { DashboardStats, Lead } from "@/types";
import { TrendingUp, Clock, CheckCircle, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

const PIPELINE_STAGES = [
  "new", "qualified", "proposal_sent", "negotiation", "won",
] as const;

const STAGE_LABELS: Record<string, string> = {
  new: "New",
  qualified: "Qualified",
  proposal_sent: "Proposal",
  negotiation: "Negotiation",
  won: "Won",
};

function StatCard({
  label, value, delta, deltaUp, icon: Icon,
}: {
  label: string; value: string; delta: string; deltaUp: boolean; icon: React.ElementType;
}) {
  return (
    <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
      <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">{label}</div>
      <div className="text-2xl font-semibold tracking-tight">{value}</div>
      <div className={cn("text-[11px] mt-1 flex items-center gap-1", deltaUp ? "text-nk-green" : "text-nk-warn")}>
        <Icon size={11} />
        {delta}
      </div>
    </div>
  );
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 80 ? "#00c98d" : score >= 60 ? "#3b7ff5" : "#f5a623";
  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] font-semibold min-w-[24px]" style={{ color }}>{score}</span>
      <div className="w-12 h-1 rounded-full bg-nk-surface2 overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${score}%`, background: color }} />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardApi.stats,
  });

  const { data: leads = [] } = useQuery<Lead[]>({
    queryKey: ["leads"],
    queryFn: () => leadsApi.list({ limit: 50 }),
  });

  const byStage = PIPELINE_STAGES.reduce((acc, s) => {
    acc[s] = leads.filter((l) => l.status === s);
    return acc;
  }, {} as Record<string, Lead[]>);

  const topLeads = [...leads].sort((a, b) => b.ai_score - a.ai_score).slice(0, 4);

  return (
    <div>
      {/* Stats row */}
      <div className="grid grid-cols-4 gap-3 mb-5">
        <StatCard
          label="Pipeline Value"
          value={`€${((stats?.pipeline_value_eur ?? 284000) / 1000).toFixed(0)}k`}
          delta="+18% this month"
          deltaUp
          icon={TrendingUp}
        />
        <StatCard
          label="Active Leads"
          value={String(stats?.active_leads ?? 47)}
          delta={`+${stats?.new_leads_this_week ?? 6} new this week`}
          deltaUp
          icon={TrendingUp}
        />
        <StatCard
          label="Clients Running"
          value={String(stats?.active_clients ?? 12)}
          delta={`${stats?.renewals_due_soon ?? 2} renewal soon`}
          deltaUp={false}
          icon={Clock}
        />
        <StatCard
          label="Automations Live"
          value={String(stats?.live_automations ?? 38)}
          delta={`${stats?.automation_runs_today ?? 2400} runs today`}
          deltaUp
          icon={Zap}
        />
      </div>

      <div className="grid grid-cols-[1fr_340px] gap-4 mb-5">
        {/* Pipeline */}
        <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
          <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
            <h3 className="text-[13px] font-semibold">Pipeline snapshot</h3>
            <a href="/pipeline" className="text-[12px] text-nk-accent">View full →</a>
          </div>
          <div className="p-4 overflow-x-auto">
            <div className="flex gap-2.5" style={{ minWidth: "700px" }}>
              {PIPELINE_STAGES.map((stage) => (
                <div key={stage} className="min-w-[155px] max-w-[155px]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-semibold uppercase tracking-[0.6px] text-nk-muted">
                      {STAGE_LABELS[stage]}
                    </span>
                    <span className="bg-nk-surface2 text-nk-muted text-[10px] px-2 py-0.5 rounded-full">
                      {byStage[stage]?.length ?? 0}
                    </span>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {(byStage[stage] ?? []).slice(0, 3).map((lead) => (
                      <a
                        key={lead.id}
                        href={`/leads/${lead.id}`}
                        className="bg-nk-surface2 border border-nk-border rounded-lg p-2.5 hover:border-nk-accent/50 transition-colors block"
                      >
                        <div className="text-[12px] font-medium truncate">
                          {lead.first_name} {lead.last_name}
                        </div>
                        <div className="text-[11px] text-nk-muted truncate">{lead.company_name}</div>
                        <div className="text-[11px] font-semibold text-nk-green mt-1.5">
                          €{(lead.estimated_value / 1000).toFixed(1)}k / yr
                        </div>
                        {lead.ai_score > 0 && (
                          <span className="mt-1.5 inline-block text-[10px] bg-nk-purple/20 text-purple-300 px-1.5 py-0.5 rounded">
                            AI {lead.ai_score}
                          </span>
                        )}
                      </a>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className="flex flex-col gap-3">
          {/* Top leads */}
          <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
            <div className="px-4 py-3.5 border-b border-nk-border">
              <h3 className="text-[13px] font-semibold">Top leads by AI score</h3>
            </div>
            <div className="px-4 py-1 divide-y divide-nk-border">
              {topLeads.map((lead) => (
                <div key={lead.id} className="flex items-center gap-3 py-2.5">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-[11px] font-semibold text-white shrink-0"
                    style={{ background: `hsl(${lead.ai_score * 2}, 70%, 45%)` }}
                  >
                    {lead.first_name[0]}{lead.last_name[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] font-medium truncate">
                      {lead.first_name} {lead.last_name}
                    </div>
                    <div className="text-[11px] text-nk-muted truncate">{lead.company_name}</div>
                  </div>
                  <ScoreBar score={lead.ai_score} />
                </div>
              ))}
            </div>
          </div>

          {/* Activity */}
          <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
            <div className="px-4 py-3.5 border-b border-nk-border">
              <h3 className="text-[13px] font-semibold">Recent activity</h3>
            </div>
            <div className="px-4 py-1 divide-y divide-nk-border">
              {[
                { dot: "#00c98d", text: "AI proposal generated for Axellent AS — €52k", time: "2 min ago" },
                { dot: "#3b7ff5", text: "Meeting booked — Lars Eriksson discovery call", time: "1 hr ago" },
                { dot: "#f5a623", text: "Lead enriched — Mikkel Dahl via LinkedIn", time: "3 hr ago" },
                { dot: "#a855f7", text: "Onboarding triggered — Logistikas Oy (7 tasks)", time: "Yesterday" },
              ].map((a, i) => (
                <div key={i} className="flex gap-3 py-2.5">
                  <div className="w-2 h-2 rounded-full mt-1 shrink-0" style={{ background: a.dot }} />
                  <div>
                    <div className="text-[12px] text-nk-muted leading-relaxed">{a.text}</div>
                    <div className="text-[10px] text-nk-muted/70 mt-0.5">{a.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
