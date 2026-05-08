"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api";
import { Task } from "@/types";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { CheckCircle2, Circle, Clock, Plus, Bot, Zap } from "lucide-react";
import { formatDate } from "@/lib/utils";
import { useState } from "react";

const PRIORITY_CONFIG = {
  urgent: { label: "Urgent", color: "#e84040", bg: "bg-nk-danger/15" },
  high:   { label: "High",   color: "#f5a623", bg: "bg-nk-warn/15"   },
  medium: { label: "Medium", color: "#3b7ff5", bg: "bg-nk-accent/15" },
  low:    { label: "Low",    color: "#8892a0", bg: "bg-nk-surface2"  },
};

const SOURCE_ICON: Record<string, React.ElementType> = {
  ai_extracted: Bot,
  automation:   Zap,
  manual:       Circle,
};

function TaskRow({ task }: { task: Task }) {
  const qc = useQueryClient();

  const completeMutation = useMutation({
    mutationFn: () => tasksApi.complete(task.id),
    onSuccess: () => {
      toast.success("Task completed");
      qc.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const priority = PRIORITY_CONFIG[task.priority] ?? PRIORITY_CONFIG.medium;
  const SourceIcon = SOURCE_ICON[task.source] ?? Circle;

  const isOverdue = task.due_date && !task.completed
    ? new Date(task.due_date) < new Date()
    : false;

  return (
    <div className={cn(
      "flex items-center gap-4 px-4 py-3 border-b border-nk-border last:border-none transition-colors",
      task.completed ? "opacity-50" : "hover:bg-nk-surface2/40"
    )}>
      <button
        onClick={() => !task.completed && completeMutation.mutate()}
        disabled={task.completed || completeMutation.isPending}
        className="shrink-0 text-nk-muted hover:text-nk-green transition-colors"
        aria-label={task.completed ? "Completed" : "Mark complete"}
      >
        {task.completed
          ? <CheckCircle2 size={18} className="text-nk-green" />
          : <Circle size={18} />
        }
      </button>

      <div className="flex-1 min-w-0">
        <div className={cn("text-[13px] font-medium", task.completed && "line-through")}>{task.title}</div>
        {task.description && (
          <div className="text-[11px] text-nk-muted truncate mt-0.5">{task.description}</div>
        )}
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {/* Source */}
        <SourceIcon size={13} className="text-nk-muted" title={task.source} />

        {/* Priority */}
        <span className={cn("text-[10px] font-medium px-2 py-0.5 rounded", priority.bg)}
              style={{ color: priority.color }}>
          {priority.label}
        </span>

        {/* Due date */}
        {task.due_date && (
          <span className={cn("text-[11px]", isOverdue ? "text-nk-danger" : "text-nk-muted")}>
            <Clock size={11} className="inline mr-1" />
            {formatDate(task.due_date)}
          </span>
        )}
      </div>
    </div>
  );
}

export default function TasksPage() {
  const [showCompleted, setShowCompleted] = useState(false);

  const { data: tasks = [], isLoading } = useQuery<Task[]>({
    queryKey: ["tasks", showCompleted],
    queryFn: () => tasksApi.list({ ...(showCompleted ? {} : { completed: false }) }),
  });

  const open      = tasks.filter((t) => !t.completed);
  const overdue   = open.filter((t) => t.due_date && new Date(t.due_date) < new Date());
  const urgent    = open.filter((t) => t.priority === "urgent" || t.priority === "high");

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Open tasks</div>
          <div className="text-2xl font-semibold">{open.length}</div>
        </div>
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Overdue</div>
          <div className={cn("text-2xl font-semibold", overdue.length > 0 ? "text-nk-danger" : "")}>
            {overdue.length}
          </div>
        </div>
        <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">High priority</div>
          <div className={cn("text-2xl font-semibold", urgent.length > 0 ? "text-nk-warn" : "")}>
            {urgent.length}
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => setShowCompleted((v) => !v)}
          className={cn(
            "text-[12px] px-3 py-1.5 rounded-lg border transition-colors",
            showCompleted
              ? "border-nk-accent/50 text-nk-accent bg-nk-accent/10"
              : "border-nk-border2 text-nk-muted hover:text-nk-text"
          )}
        >
          {showCompleted ? "Hide completed" : "Show completed"}
        </button>
        <div className="flex-1" />
        <button className="bg-nk-accent text-white text-[12px] font-medium px-3 py-1.5 rounded-lg flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors">
          <Plus size={12} /> New task
        </button>
      </div>

      {/* Task list */}
      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border">
          <h3 className="text-[13px] font-semibold">All tasks</h3>
        </div>
        {isLoading ? (
          <div className="text-center py-12 text-nk-muted text-[13px]">Loading...</div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12 text-nk-muted text-[13px]">No tasks found</div>
        ) : (
          tasks.map((task) => <TaskRow key={task.id} task={task} />)
        )}
      </div>
    </div>
  );
}
