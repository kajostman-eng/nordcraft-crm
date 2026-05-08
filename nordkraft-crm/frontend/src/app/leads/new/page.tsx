"use client";

import { useMutation } from "@tanstack/react-query";
import { leadsApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useState } from "react";
import { ArrowLeft, Plus } from "lucide-react";

export default function NewLeadPage() {
  const router = useRouter();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [estimatedValue, setEstimatedValue] = useState<number>(0);
  const [notes, setNotes] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      leadsApi.create({
        first_name: firstName,
        last_name: lastName,
        email,
        company_name: companyName || undefined,
        estimated_value: Number.isFinite(estimatedValue) ? estimatedValue : 0,
        notes: notes || undefined,
      }),
    onSuccess: (lead: any) => {
      toast.success("Lead created");
      router.push(`/leads/${lead.id}`);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Create failed"),
  });

  const disabled = !firstName || !lastName || !email || createMutation.isPending;

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
        <div className="text-[18px] font-semibold tracking-tight">New lead</div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">First name</div>
            <input
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Last name</div>
            <input
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="mt-3">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Email</div>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
          />
        </div>

        <div className="grid grid-cols-2 gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Company</div>
            <input
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Estimated value (EUR)</div>
            <input
              value={String(estimatedValue)}
              onChange={(e) => setEstimatedValue(Number(e.target.value))}
              type="number"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="mt-3">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Notes (optional)</div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={5}
            className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60 resize-none"
          />
        </div>

        <div className="mt-4 flex justify-end">
          <button
            disabled={disabled}
            onClick={() => createMutation.mutate()}
            className="inline-flex items-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
          >
            <Plus size={14} />
            Create lead
          </button>
        </div>
      </div>
    </div>
  );
}

