"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await authApi.login(email, password);
      localStorage.setItem("nk_token", res.access_token);
      router.replace("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-nk-bg flex items-center justify-center p-6">
      <div className="w-full max-w-sm bg-nk-surface border border-nk-border rounded-[10px] p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-[8px] bg-nk-accent flex items-center justify-center text-[13px] font-bold text-white">
            NK
          </div>
          <div>
            <div className="text-[14px] font-semibold">NordKraft AI CRM</div>
            <div className="text-[12px] text-nk-muted">Sign in</div>
          </div>
        </div>

        <form onSubmit={onSubmit} className="space-y-3">
          <div className="space-y-1">
            <label className="text-[12px] text-nk-muted">Email</label>
            <input
              className="w-full bg-nk-surface2 border border-nk-border2 rounded-[8px] px-3 py-2 text-[13px] outline-none focus:border-nk-accent/60"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              placeholder="you@nordkraftgroup.com"
              required
            />
          </div>
          <div className="space-y-1">
            <label className="text-[12px] text-nk-muted">Password</label>
            <input
              type="password"
              className="w-full bg-nk-surface2 border border-nk-border2 rounded-[8px] px-3 py-2 text-[13px] outline-none focus:border-nk-accent/60"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="text-[12px] text-nk-danger bg-nk-danger/10 border border-nk-danger/20 rounded-[8px] px-3 py-2">
              {error}
            </div>
          )}

          <button
            disabled={loading}
            className="w-full bg-nk-accent text-white text-[13px] font-medium px-3.5 py-2 rounded-[8px] hover:bg-nk-accent/90 transition-colors disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

          <div className="text-[11px] text-nk-muted leading-relaxed">
            First time? Create the first admin via API: <span className="font-mono">POST /api/v1/auth/bootstrap</span>
          </div>
        </form>
      </div>
    </div>
  );
}

