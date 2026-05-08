export type LeadStatus =
  | "new" | "contacted" | "qualified" | "discovery_booked"
  | "proposal_sent" | "negotiation" | "won" | "lost" | "onboarding";

export type LeadSource = "linkedin" | "cold_email" | "referral" | "website" | "event" | "other";

export interface Lead {
  id: string;
  created_at: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  title?: string;
  company_name?: string;
  company_website?: string;
  industry?: string;
  country?: string;
  city?: string;
  status: LeadStatus;
  source: LeadSource;
  estimated_value: number;
  currency: string;
  notes?: string;
  ai_score: number;
  automation_readiness: number;
  ai_maturity_level: number;
  estimated_time_savings_hrs: number;
  estimated_roi_multiplier: number;
  enriched: boolean;
  assigned_to?: string;
}

export interface Client {
  id: string;
  created_at: string;
  company_name: string;
  industry?: string;
  country?: string;
  plan?: string;
  mrr: number;
  currency: string;
  health_score: number;
  health_status: "healthy" | "at_risk" | "churning";
  contract_start?: string;
  contract_end?: string;
  portal_url?: string;
}

export interface Task {
  id: string;
  created_at: string;
  title: string;
  description?: string;
  due_date?: string;
  completed: boolean;
  priority: "low" | "medium" | "high" | "urgent";
  source: "manual" | "ai_extracted" | "automation";
  lead_id?: string;
  client_id?: string;
  project_id?: string;
  assigned_to?: string;
}

export interface Automation {
  id: string;
  created_at: string;
  client_id?: string;
  name: string;
  description?: string;
  status: "active" | "paused" | "error" | "draft";
  total_runs: number;
  last_run_at?: string;
  last_run_status?: string;
  estimated_time_saved_per_run_minutes: number;
}

export interface DashboardStats {
  pipeline_value_eur: number;
  active_leads: number;
  active_clients: number;
  live_automations: number;
  automation_runs_today: number;
  hours_saved_this_month: number;
  new_leads_this_week: number;
  renewals_due_soon: number;
}

export interface AIAssessment {
  ai_score: number;
  automation_readiness: number;
  ai_maturity_level: number;
  estimated_time_savings_hrs: number;
  estimated_roi_multiplier: number;
  key_opportunities: string[];
  recommended_phases: Array<{
    phase: number;
    name: string;
    duration_weeks: string;
    description: string;
    deliverables: string[];
    estimated_cost_eur_min: number;
    estimated_cost_eur_max: number;
  }>;
  summary: string;
}
