"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Offer } from "@/types";
import { offersApi } from "@/lib/api";
import { toast } from "sonner";
import { Plus } from "lucide-react";

export default function OffersPage() {
  const qc = useQueryClient();
  const [title, setTitle] = useState("");
  const [leadId, setLeadId] = useState("");
  const [clientId, setClientId] = useState("");
  const [notes, setNotes] = useState("");

  const { data: offers = [], isLoading } = useQuery<Offer[]>({
    queryKey: ["offers"],
    queryFn: () => offersApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      offersApi.create({
        title,
        lead_id: leadId || undefined,
        client_id: clientId || undefined,
        notes: notes || undefined,
        currency: "EUR",
        discount_amount: 0,
      }),
    onSuccess: async (offer: Offer) => {
      toast.success("Offer created");
      setTitle("");
      setLeadId("");
      setClientId("");
      setNotes("");
      await qc.invalidateQueries({ queryKey: ["offers"] });
      if (offer?.id) window.location.href = `/offers/${offer.id}`;
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Create failed"),
  });

  const disabled = !title || createMutation.isPending;
  const draftCount = useMemo(() => offers.filter((o) => o.status === "draft").length, [offers]);

  return (
    <div className="max-w-5xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[18px] font-semibold tracking-tight">Offers</div>
          <div className="text-[12px] text-nk-muted mt-0.5">Build an offer from your product portfolio.</div>
        </div>
        <div className="text-[11px] text-nk-muted">{isLoading ? "Loading…" : `${draftCount}/${offers.length} drafts`}</div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
        <div className="grid grid-cols-[1fr_1fr] gap-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Title</div>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. NordKraft AI Automation Phase 1–3"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Notes (optional)</div>
            <input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="internal notes"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="grid grid-cols-[1fr_1fr] gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Attach to lead (optional)</div>
            <input
              value={leadId}
              onChange={(e) => setLeadId(e.target.value)}
              placeholder="Lead ID"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Attach to client (optional)</div>
            <input
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="Client ID"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="mt-3 flex justify-end">
          <button
            disabled={disabled}
            onClick={() => createMutation.mutate()}
            className="inline-flex items-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
          >
            <Plus size={14} />
            Create offer
          </button>
        </div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
          <div className="text-[13px] font-semibold">All offers</div>
          <div className="text-[11px] text-nk-muted">{isLoading ? "Loading…" : `${offers.length} total`}</div>
        </div>
        <div className="divide-y divide-nk-border">
          {offers.map((o) => (
            <Link
              key={o.id}
              href={`/offers/${o.id}`}
              className="px-4 py-3 flex items-center gap-3 hover:bg-nk-surface2/50 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-medium truncate">{o.title}</div>
                <div className="text-[11px] text-nk-muted truncate">
                  {o.status} · {new Date(o.created_at).toLocaleString()}
                </div>
              </div>
              <div className="text-[11px] text-nk-muted">
                {o.lead_id ? "Lead" : o.client_id ? "Client" : "—"}
              </div>
            </Link>
          ))}
          {offers.length === 0 && !isLoading && (
            <div className="px-4 py-10 text-center text-[12px] text-nk-muted">No offers yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

