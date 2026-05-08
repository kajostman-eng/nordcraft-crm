"use client";
import { Search, Sparkles } from "lucide-react";
import { usePathname } from "next/navigation";

const PAGE_TITLES: Record<string, string> = {
  "/": "Overview",
  "/leads": "Leads",
  "/pipeline": "Pipeline",
  "/assess": "AI Assessment",
  "/clients": "Clients",
  "/automations": "Automations",
  "/tasks": "Tasks",
  "/ai": "AI Tools",
  "/settings": "Settings",
};

export function Topbar() {
  const path = usePathname();
  const title = PAGE_TITLES[path] ?? "NordKraft CRM";

  return (
    <header className="h-[52px] bg-nk-surface border-b border-nk-border flex items-center px-5 gap-3 shrink-0">
      <span className="text-[15px] font-semibold flex-1">{title}</span>
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-nk-muted" />
        <input
          className="bg-nk-surface2 border border-nk-border2 rounded-[6px] pl-8 pr-3 py-[6px] text-[13px] text-nk-text placeholder:text-nk-muted w-52 outline-none focus:border-nk-accent/50 transition-colors"
          placeholder="Search leads, clients..."
        />
      </div>
      <button className="bg-nk-accent text-white text-[13px] font-medium px-3.5 py-[6px] rounded-[6px] flex items-center gap-1.5 hover:bg-nk-accent/90 transition-colors">
        <Sparkles size={13} />
        AI Generate
      </button>
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-nk-accent to-nk-green flex items-center justify-center text-[12px] font-semibold text-white cursor-pointer">
        EL
      </div>
    </header>
  );
}
