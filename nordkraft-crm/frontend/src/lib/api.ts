import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach auth token from localStorage
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("nk_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }).then((r) => r.data as { access_token: string; token_type: string }),
  me: () => api.get("/auth/me").then((r) => r.data),
  bootstrap: (email: string, password: string, full_name?: string) =>
    api.post("/auth/bootstrap", { email, password, full_name }).then((r) => r.data),
};

// ─── Leads ────────────────────────────────────────────────────────────────────
export const leadsApi = {
  list: (params?: Record<string, string | number>) =>
    api.get("/leads", { params }).then((r) => r.data),
  get: (id: string) => api.get(`/leads/${id}`).then((r) => r.data),
  create: (data: object) => api.post("/leads", data).then((r) => r.data),
  update: (id: string, data: object) => api.patch(`/leads/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/leads/${id}`),
  move: (id: string, status: string) =>
    api.post(`/leads/${id}/move`, null, { params: { new_status: status } }).then((r) => r.data),
  assess: (id: string, contextNotes?: string) =>
    api.post(`/leads/${id}/assess`, { lead_id: id, context_notes: contextNotes }).then((r) => r.data),
};

// ─── Clients ──────────────────────────────────────────────────────────────────
export const clientsApi = {
  list: () => api.get("/clients").then((r) => r.data),
  get: (id: string) => api.get(`/clients/${id}`).then((r) => r.data),
  create: (data: object) => api.post("/clients", data).then((r) => r.data),
  update: (id: string, data: object) => api.patch(`/clients/${id}`, data).then((r) => r.data),
};

// ─── Tasks ────────────────────────────────────────────────────────────────────
export const tasksApi = {
  list: (params?: object) => api.get("/tasks", { params }).then((r) => r.data),
  create: (data: object) => api.post("/tasks", data).then((r) => r.data),
  complete: (id: string) => api.patch(`/tasks/${id}/complete`).then((r) => r.data),
};

// ─── Automations ──────────────────────────────────────────────────────────────
export const automationsApi = {
  list: (clientId?: string) =>
    api.get("/automations", { params: clientId ? { client_id: clientId } : {} }).then((r) => r.data),
  create: (data: object) => api.post("/automations", data).then((r) => r.data),
  toggle: (id: string) => api.patch(`/automations/${id}/toggle`).then((r) => r.data),
};

// ─── Dashboard ────────────────────────────────────────────────────────────────
export const dashboardApi = {
  stats: () => api.get("/dashboard/stats").then((r) => r.data),
};

// ─── AI ───────────────────────────────────────────────────────────────────────
export const aiApi = {
  assess: (leadId: string, notes?: string) =>
    api.post("/ai/assess", { lead_id: leadId, context_notes: notes }).then((r) => r.data),
  proposal: (leadId: string, tone?: string) =>
    api.post("/ai/proposal", { lead_id: leadId, tone: tone || "professional" }).then((r) => r.data),
  followUp: (leadId: string, context?: string) =>
    api.post("/ai/follow-up", { lead_id: leadId, context }).then((r) => r.data),
  meetingSummary: (transcript: string, leadId?: string, clientId?: string) =>
    api.post("/ai/meeting-summary", { transcript, lead_id: leadId, client_id: clientId }).then((r) => r.data),
  chat: (message: string, contextType: string, contextId?: string, history?: object[]) =>
    api.post("/ai/chat", { message, context_type: contextType, context_id: contextId, history }).then((r) => r.data),
};
