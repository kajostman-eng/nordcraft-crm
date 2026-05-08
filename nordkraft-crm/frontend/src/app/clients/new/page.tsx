"use client";

import { useMutation } from "@tanstack/react-query";
import { clientsApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useState } from "react";
import { ArrowLeft, Plus } from "lucide-react";

export default function NewClientPage() {
  const router = useRouter();
  const [companyName, setCompanyName] = useState("");
  const [industry, setIndustry] = useState("");
  const [country, setCountry] = useState("");
  const [plan, setPlan] = useState("");
  const [mrr, setMrr] = useState<number>(0);

  const createMutation = useMutation({
    mutationFn: () =>
      clientsApi.create({
        company_name: companyName,
        industry: industry || undefined,
        country: country || undefined,
        plan: plan || undefined,
        mrr: Number.isFinite(mrr) ? mrr : 0,
      }),
    onSuccess: () => {
      toast.success("Client created");
      router.push("/clients");
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Create failed"),
  });

  const disabled = !companyName || createMutation.isPending;

  return (
    <div className="max-w-3xl">
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => router.back()}
          className="text-[12px] text-nk-muted hover:text-nk-text inline-flex items-center gap-1.5"
        >
          <ArrowLeft size={14} />
          Back
        </button>
        <div className="text-[18px] font-semibold tracking-tight">New client</div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
        <div>
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Company name</div>
          <input
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
          />
        </div>

        <div className="grid grid-cols-2 gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Industry</div>
            <input
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Country</div>
            <input
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Plan</div>
            <input
              value={plan}
              onChange={(e) => setPlan(e.target.value)}
              placeholder="e.g. Growth, Enterprise"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">MRR (EUR)</div>
            <input
              value={String(mrr)}
              onChange={(e) => setMrr(Number(e.target.value))}
              type="number"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            disabled={disabled}
            onClick={() => createMutation.mutate()}
            className="inline-flex items-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
          >
            <Plus size={14} />
            Create client
          </button>
        </div>
      </div>
    </div>
  );
}

