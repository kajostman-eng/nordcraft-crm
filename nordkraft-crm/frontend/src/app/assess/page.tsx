"use client";
import { useQuery, useMutation } from "@tanstack/react-query";
import { leadsApi, aiApi } from "@/lib/api";
import { Lead, AIAssessment } from "@/types";
import { useState } from "react";
import { Sparkles, FileText, Mail, TrendingUp, Clock, Star } from "lucide-react";
import { toast } from "sonner";

export default function AssessPage() {
  const [selectedLeadId, setSelectedLeadId] = useState("");
  const [assessment, setAssessment] = useState<AIAssessment | null>(null);
  const [proposal, setProposal] = useState<any>(null);
  const [followUp, setFollowUp] = useState<any>(null);

  const { data: leads = [] } = useQuery<Lead[]>({
    queryKey: ["leads-qualified"],
    queryFn: () => leadsApi.list({ limit: 50 }),
  });

  const selectedLead = leads.find((l) => l.id === selectedLeadId);

  const assessMutation = useMutation({
    mutationFn: (leadId: string) => aiApi.assess(leadId),
    onSuccess: (data) => {
      setAssessment(data);
      toast.success("AI assessment complete");
    },
    onError: () => toast.error("Assessment failed"),
  });

  const proposalMutation = useMutation({
    mutationFn: (leadId: string) => aiApi.proposal(leadId),
    onSuccess: (data) => {
      setProposal(data);
      toast.success("Proposal generated");
    },
  });

  const followUpMutation = useMutation({
    mutationFn: (leadId: string) => aiApi.followUp(leadId),
    onSuccess: (data) => {
      setFollowUp(data);
      toast.success("Follow-up email drafted");
    },
  });

  const scoreColor = (n: number) =>
    n >= 80 ? "#00c98d" : n >= 60 ? "#3b7ff5" : "#f5a623";

  return (
    <div>
      {/* Lead selector */}
      <div className="bg-nk-surface border border-nk-border rounded-xl p-5 mb-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <label className="text-[11px] text-nk-muted uppercase tracking-[0.5px] block mb-1.5">Select lead to assess</label>
            <select
              value={selectedLeadId}
              onChange={(e) => { setSelectedLeadId(e.target.value); setAssessment(null); setProposal(null); setFollowUp(null); }}
              className="bg-nk-surface2 border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text outline-none w-full max-w-sm"
            >
              <option value="">Select a lead...</option>
              {leads.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.first_name} {l.last_name} — {l.company_name}
                </option>
              ))}
            </select>
          </div>
          {selectedLeadId && (
            <button
              onClick={() => assessMutation.mutate(selectedLeadId)}
              disabled={assessMutation.isPending}
              className="bg-nk-accent text-white text-[13px] font-medium px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-nk-accent/90 disabled:opacity-50 transition-colors mt-5"
            >
              <Sparkles size={14} />
              {assessMutation.isPending ? "Analysing..." : "Run AI Assessment"}
            </button>
          )}
        </div>
      </div>

      {/* Assessment results */}
      {assessment && selectedLead && (
        <>
          {/* Score cards */}
          <div className="grid grid-cols-4 gap-3 mb-4">
            {[
              { label: "AI Score", value: `${assessment.ai_score} / 100`, color: scoreColor(assessment.ai_score), icon: Star },
              { label: "Automation Readiness", value: `${assessment.automation_readiness} / 100`, color: scoreColor(assessment.automation_readiness), icon: TrendingUp },
              { label: "Time Savings / yr", value: `${assessment.estimated_time_savings_hrs} hrs`, color: "#3b7ff5", icon: Clock },
              { label: "Projected ROI", value: `${assessment.estimated_roi_multiplier}×`, color: "#00c98d", icon: TrendingUp },
            ].map(({ label, value, color, icon: Icon }) => (
              <div key={label} className="bg-nk-surface border border-nk-border rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Icon size={14} style={{ color }} />
                  <span className="text-[11px] text-nk-muted uppercase tracking-[0.5px]">{label}</span>
                </div>
                <div className="text-xl font-semibold" style={{ color }}>{value}</div>
                <div className="text-[11px] text-nk-muted mt-1">AI Maturity: Level {assessment.ai_maturity_level} / 5</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-[1fr_300px] gap-4 mb-4">
            {/* Phases */}
            <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
              <div className="px-4 py-3.5 border-b border-nk-border">
                <h3 className="text-[13px] font-semibold">Recommended implementation phases</h3>
              </div>
              <div className="p-4 flex flex-col gap-3">
                {assessment.recommended_phases.map((phase) => {
                  const colors = ["#00c98d", "#3b7ff5", "#a855f7"];
                  const c = colors[(phase.phase - 1) % 3];
                  return (
                    <div
                      key={phase.phase}
                      className="bg-nk-surface2 border border-nk-border rounded-lg p-3.5"
                      style={{ borderLeft: `3px solid ${c}`, borderRadius: "0 8px 8px 0" }}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[13px] font-semibold text-nk-text">
                          Phase {phase.phase} — {phase.name}
                        </span>
                        <span
                          className="text-[11px] font-medium px-2 py-0.5 rounded"
                          style={{ background: `${c}20`, color: c }}
                        >
                          €{phase.estimated_cost_eur_min / 1000}–{phase.estimated_cost_eur_max / 1000}k
                        </span>
                      </div>
                      <div className="text-[12px] text-nk-muted mb-2">{phase.description}</div>
                      <div className="flex flex-wrap gap-1.5">
                        {phase.deliverables.map((d, i) => (
                          <span key={i} className="text-[10px] bg-nk-surface px-2 py-0.5 rounded text-nk-muted">
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* AI actions */}
            <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
              <div className="px-4 py-3.5 border-b border-nk-border">
                <h3 className="text-[13px] font-semibold">AI actions</h3>
              </div>
              <div className="p-4 flex flex-col gap-3">
                <div className="bg-nk-surface2 border border-nk-border rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1.5">
                    <FileText size={14} className="text-purple-400" />
                    <span className="text-[12px] font-semibold">Generate proposal</span>
                  </div>
                  <p className="text-[11px] text-nk-muted mb-2.5">Auto-draft a tailored PDF proposal with ROI calculations and phase timeline.</p>
                  <button
                    onClick={() => proposalMutation.mutate(selectedLeadId)}
                    disabled={proposalMutation.isPending}
                    className="text-[11px] text-nk-accent border border-nk-accent/30 px-2.5 py-1.5 rounded hover:bg-nk-accent/10 transition-colors disabled:opacity-50"
                  >
                    {proposalMutation.isPending ? "Generating..." : "Generate proposal →"}
                  </button>
                </div>

                <div className="bg-nk-surface2 border border-nk-border rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1.5">
                    <Mail size={14} className="text-blue-400" />
                    <span className="text-[12px] font-semibold">Write follow-up email</span>
                  </div>
                  <p className="text-[11px] text-nk-muted mb-2.5">Draft a personalised email referencing their assessment data.</p>
                  <button
                    onClick={() => followUpMutation.mutate(selectedLeadId)}
                    disabled={followUpMutation.isPending}
                    className="text-[11px] text-nk-accent border border-nk-accent/30 px-2.5 py-1.5 rounded hover:bg-nk-accent/10 transition-colors disabled:opacity-50"
                  >
                    {followUpMutation.isPending ? "Drafting..." : "Draft email →"}
                  </button>
                </div>

                {/* Key opportunities */}
                <div className="bg-nk-surface2 border border-nk-border rounded-lg p-3">
                  <div className="text-[12px] font-semibold mb-2">Key opportunities</div>
                  <ul className="space-y-1">
                    {assessment.key_opportunities.map((opp, i) => (
                      <li key={i} className="text-[11px] text-nk-muted flex gap-2">
                        <span className="text-nk-green">›</span> {opp}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
            <div className="text-[12px] font-semibold text-nk-muted uppercase tracking-[0.5px] mb-2">Executive summary</div>
            <p className="text-[13px] text-nk-text leading-relaxed">{assessment.summary}</p>
          </div>
        </>
      )}

      {/* Proposal output */}
      {proposal && (
        <div className="bg-nk-surface border border-nk-border rounded-xl p-5 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText size={15} className="text-purple-400" />
            <h3 className="text-[13px] font-semibold">{proposal.title}</h3>
          </div>
          <p className="text-[13px] text-nk-muted leading-relaxed mb-3">{proposal.executive_summary}</p>
          <div className="grid grid-cols-3 gap-3">
            {["total_investment_min", "total_investment_max"].map((k) => (
              <div key={k} className="bg-nk-surface2 rounded-lg p-3">
                <div className="text-[10px] text-nk-muted uppercase tracking-[0.5px]">{k.replace(/_/g, " ")}</div>
                <div className="text-[16px] font-semibold text-nk-green">€{((proposal[k] as number) / 1000).toFixed(0)}k</div>
              </div>
            ))}
            <div className="bg-nk-surface2 rounded-lg p-3">
              <div className="text-[10px] text-nk-muted uppercase tracking-[0.5px]">Payback period</div>
              <div className="text-[16px] font-semibold text-nk-accent">{proposal.roi_section?.payback_period_months} months</div>
            </div>
          </div>
        </div>
      )}

      {/* Follow-up output */}
      {followUp && (
        <div className="bg-nk-surface border border-nk-border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Mail size={15} className="text-blue-400" />
            <h3 className="text-[13px] font-semibold">Follow-up email draft</h3>
          </div>
          <div className="text-[11px] text-nk-muted mb-1">Subject:</div>
          <div className="text-[13px] font-medium text-nk-text mb-3">{followUp.subject}</div>
          <div className="text-[11px] text-nk-muted mb-1">Body:</div>
          <pre className="text-[13px] text-nk-muted leading-relaxed whitespace-pre-wrap font-sans bg-nk-surface2 rounded-lg p-3">
            {followUp.body}
          </pre>
        </div>
      )}
    </div>
  );
}
