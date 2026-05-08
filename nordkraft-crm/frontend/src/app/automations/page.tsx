"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { automationsApi } from "@/lib/api";
import { Automation } from "@/types";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import {
  UserPlus, FileText, Calendar, Rocket, RefreshCw, BarChart2,
  Play, Pause, Plus, Zap,
} from "lucide-react";

const ICON_MAP: Record<string, React.ElementType> = {
  user: UserPlus,
  file: FileText,
  calendar: Calendar,
  rocket: Rocket,
  refresh: RefreshCw,
  chart: BarChart2,
};

const STATUS_CONFIG = {
  active:  { label: "Active",  color: "#00c98d", bg: "bg-nk-green/15"  },
  paused:  { label: "Paused",  color: "#f5a623", bg: "bg-nk-warn/15"   },
  error:   { label: "Error",   color: "#e84040", bg: "bg-nk-danger/15" },
  draft:   { label: "Draft",   color: "#8892a0", bg: "bg-nk-surface2"  },
};

function AutomationRow({ automation }: { automation: Automation }) {
  const qc = useQueryClient();

  const toggleMutation = useMutation({
    mutationFn: () => automationsApi.toggle(automation.id),
    onSuccess: () => {
      toast.success(`Automation ${automation.status === "active" ? "paused" : "activated"}`);
      qc.invalidateQueries({ queryKey: ["automations"] });
    },
  });

  const statusCfg = STATUS_CONFIG[automation.status] ?? STATUS_CONFIG.draft;
  const timeSavedTotal = Math.round((automation.total_runs * automation.estimated_time_saved_per_run_minutes) / 60);

  return (
    <div className="flex items-center gap-4 p-4 border-b border-nk-border last:border-none hover:bg-nk-surface2/40 transition-colors">
      <div className="w-8 h-8 rounded-lg bg-nk-accent/15 flex items-center justify-center shrink-0">
        <Zap size={15} className="text-nk-accent" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-medium text-nk-text">{automation.name}</div>
        {automation.description && (
          <div className="text-[11px] text-nk-muted truncate mt-0.5">{automation.description}</div>
        )}
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <div className="text-right">
          <div className="text-[12px] font-medium text-nk-text">{automation.total_runs.toLocaleString()}</div>
          <div className="text-[10px] text-nk-muted">runs total</div>
        </div>
        {timeSavedTotal > 0 && (
          <div className="text-right">
            <div className="text-[12px] font-medium text-nk-green">{timeSavedTotal}h</div>
            <div className="text-[10px] text-nk-muted">saved</div>
          </div>
        )}
        <span className={cn("text-[10px] font-medium px-2 py-0.5 rounded", statusCfg.bg)}
              style={{ color: statusCfg.color }}>
          {statusCfg.label}
        </span>
        <button
          onClick={() => toggleMutation.mutate()}
          disabled={toggleMutation.isPending || automation.status === "error" || automation.status === "draft"}
          className={cn(
            "w-10 h-[22px] rounded-full transition-colors relative flex-shrink-0",
            automation.status === "active" ? "bg-nk-green" : "bg-nk-surface2 border border-nk-border2"
          )}
          aria-label={automation.status === "active" ? "Pause automation" : "Activate automation"}
        >
          <span className={cn(
            "absolute top-[3px] w-4 h-4 rounded-full bg-white transition-all",
            automation.status === "active" ? "right-[3px]" : "left-[3px]"
          )} />
        </button>
      </div>
    </div>
  );
}

export default function AutomationsPage() {
  const { data: automations = [], isLoading } = useQuery<Automation[]>({
    queryKey: ["automations"],
    queryFn: () => automationsApi.list(),
  });

  const active  = automations.filter((a) => a.status === "active");
  const totalRuns = automations.reduce((s, a) => s + a.total_runs, 0);
  const totalHours = automations.reduce(
    (s, a) => s + Math.round((a.total_runs * a.estimated_time_saved_per_run_minutes) / 60), 0
  );

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Active automations</div>
          <div className="text-2xl font-semibold">{active.length}</div>
          <div className="text-[11px] text-nk-muted mt-1">of {automations.length} total</div>
        </div>
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Total runs</div>
          <div className="text-2xl font-semibold">{totalRuns.toLocaleString()}</div>
        </div>
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Hours saved total</div>
          <div className="text-2xl font-semibold text-nk-green">{totalHours.toLocaleString()}h</div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
          <h3 className="text-[13px] font-semibold">Automation workflows</h3>
          <button className="bg-nk-accent text-white text-[12px] font-medium px-3 py-1.5 rounded-lg flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors">
            <Plus size={12} /> New workflow
          </button>
        </div>
        {isLoading ? (
          <div className="text-center py-12 text-nk-muted text-[13px]">Loading...</div>
        ) : automations.length === 0 ? (
          <div className="text-center py-12 text-nk-muted text-[13px]">No automations yet</div>
        ) : (
          <div>
            {automations.map((automation) => (
              <AutomationRow key={automation.id} automation={automation} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
