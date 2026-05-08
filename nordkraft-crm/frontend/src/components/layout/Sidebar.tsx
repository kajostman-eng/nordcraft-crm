"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, ArrowRightLeft, Bot,
  Building2, Zap, CheckSquare, Sparkles, Settings,
  FileText,
  Package,
  FileSignature,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { section: "Sales", items: [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/leads", label: "Leads", icon: Users, badge: "12" },
    { href: "/pipeline", label: "Pipeline", icon: ArrowRightLeft },
    { href: "/assess", label: "AI Assessment", icon: Bot, badgeColor: "green" as const },
    { href: "/offers", label: "Offers", icon: FileSignature },
    { href: "/products", label: "Products", icon: Package },
  ]},
  { section: "Delivery", items: [
    { href: "/clients", label: "Clients", icon: Building2 },
    { href: "/automations", label: "Automations", icon: Zap },
    { href: "/tasks", label: "Tasks", icon: CheckSquare },
    { href: "/documents", label: "Documents", icon: FileText },
  ]},
  { section: "System", items: [
    { href: "/ai", label: "AI Tools", icon: Sparkles },
    { href: "/settings", label: "Settings", icon: Settings },
  ]},
];

export function Sidebar() {
  const path = usePathname();

  return (
    <aside className="w-[200px] min-w-[200px] bg-nk-surface border-r border-nk-border flex flex-col">
      {/* Logo */}
      <div className="px-4 py-[18px] border-b border-nk-border flex items-center gap-2">
        <div className="w-7 h-7 rounded-[6px] bg-nk-accent flex items-center justify-center text-[13px] font-bold text-white tracking-tight">
          NK
        </div>
        <div>
          <div className="text-[13px] font-semibold tracking-tight text-nk-text">NordKraft</div>
          <div className="text-[10px] text-nk-muted tracking-widest uppercase">AI CRM</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 flex flex-col gap-0.5">
        {NAV.map((group) => (
          <div key={group.section}>
            <div className="text-[10px] text-nk-muted uppercase tracking-[0.8px] px-2 py-2 mt-2">
              {group.section}
            </div>
            {group.items.map(({ href, label, icon: Icon, badge, badgeColor }) => {
              const active = path === href || (href !== "/" && path.startsWith(href));
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-2 px-2 py-[7px] rounded-[6px] text-[13px] transition-all",
                    active
                      ? "bg-nk-accent/10 text-nk-accent"
                      : "text-nk-muted hover:bg-nk-surface2 hover:text-nk-text"
                  )}
                >
                  <Icon size={15} className="w-4 text-center" />
                  {label}
                  {badge && (
                    <span className={cn(
                      "ml-auto text-[10px] font-semibold px-[6px] py-px rounded-full text-white",
                      badgeColor === "green" ? "bg-nk-green" : "bg-nk-accent"
                    )}>
                      {badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
