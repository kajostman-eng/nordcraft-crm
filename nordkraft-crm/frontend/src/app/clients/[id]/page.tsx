"use client";

import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Client, Document } from "@/types";
import { clientsApi, documentsApi } from "@/lib/api";
import { toast } from "sonner";
import { ArrowLeft, Link as LinkIcon, Trash2, Upload, FileSignature } from "lucide-react";
import { useMemo, useState } from "react";
import { offersApi } from "@/lib/api";

export default function ClientDetailPage() {
  const params = useParams<{ id: string }>();
  const clientId = params?.id;
  const router = useRouter();
  const qc = useQueryClient();

  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const { data: client, isLoading: clientLoading } = useQuery<Client>({
    queryKey: ["client", clientId],
    queryFn: () => clientsApi.get(String(clientId)),
    enabled: !!clientId,
  });

  const { data: docs = [], isLoading: docsLoading } = useQuery<Document[]>({
    queryKey: ["documents", "client", clientId],
    queryFn: () => documentsApi.list({ client_id: String(clientId) }),
    enabled: !!clientId,
  });

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Missing file");
      return documentsApi.upload({
        file,
        title: title || file.name,
        description: description || undefined,
        client_id: String(clientId),
      });
    },
    onSuccess: async () => {
      toast.success("Uploaded");
      setFile(null);
      setTitle("");
      setDescription("");
      await qc.invalidateQueries({ queryKey: ["documents", "client", clientId] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Upload failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: async () => {
      toast.success("Deleted");
      await qc.invalidateQueries({ queryKey: ["documents", "client", clientId] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Delete failed"),
  });

  const uploadDisabled = useMemo(() => uploadMutation.isPending || !file, [uploadMutation.isPending, file]);

  const createOfferMutation = useMutation({
    mutationFn: () =>
      offersApi.create({
        title: client ? `Offer — ${client.company_name}` : "Offer",
        client_id: String(clientId),
        currency: "EUR",
      }),
    onSuccess: (offer: any) => {
      toast.success("Offer created");
      if (offer?.id) window.location.href = `/offers/${offer.id}`;
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Create offer failed"),
  });

  return (
    <div className="max-w-5xl">
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={() => router.back()}
          className="text-[12px] text-nk-muted hover:text-nk-text inline-flex items-center gap-1.5"
        >
          <ArrowLeft size={14} />
          Back
        </button>
        <div className="flex-1" />
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
        {clientLoading || !client ? (
          <div className="text-[13px] text-nk-muted">Loading client…</div>
        ) : (
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-[18px] font-semibold tracking-tight">{client.company_name}</div>
              <div className="text-[12px] text-nk-muted mt-0.5">
                {client.plan ?? "No plan"} · {client.country ?? "—"} · {client.health_status}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px]">MRR</div>
              <div className="text-[18px] font-semibold">€{client.mrr.toLocaleString()}</div>
              <button
                onClick={() => createOfferMutation.mutate()}
                disabled={!client || createOfferMutation.isPending}
                className="mt-2 inline-flex items-center gap-2 text-[11px] font-semibold px-2.5 py-1.5 rounded-lg border border-nk-accent/30 text-nk-accent hover:bg-nk-accent/10 disabled:opacity-50"
              >
                <FileSignature size={13} />
                Create offer
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
        <div className="text-[13px] font-semibold mb-3">Attach document</div>
        <div className="grid grid-cols-[1fr_1fr] gap-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">File</div>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Title</div>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={file?.name || "e.g. Contract, Proposal"}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Description (optional)</div>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short context"
            className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
          />
        </div>
        <div className="mt-3 flex justify-end">
          <button
            disabled={uploadDisabled}
            onClick={() => uploadMutation.mutate()}
            className="inline-flex items-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
          >
            <Upload size={14} />
            Upload
          </button>
        </div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
          <div className="text-[13px] font-semibold">Documents</div>
          <div className="text-[11px] text-nk-muted">{docsLoading ? "Loading…" : `${docs.length} total`}</div>
        </div>
        <div className="divide-y divide-nk-border">
          {docs.map((d) => (
            <div key={d.id} className="px-4 py-3 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-medium truncate">{d.title}</div>
                <div className="text-[11px] text-nk-muted truncate">{d.file_name}</div>
              </div>
              {d.url && (
                <a
                  href={d.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-[12px] text-nk-accent hover:underline"
                >
                  <LinkIcon size={14} />
                  Open
                </a>
              )}
              <button
                onClick={() => deleteMutation.mutate(d.id)}
                className="inline-flex items-center gap-1.5 text-[12px] text-nk-muted hover:text-red-300"
              >
                <Trash2 size={14} />
                Delete
              </button>
            </div>
          ))}
          {docs.length === 0 && !docsLoading && (
            <div className="px-4 py-10 text-center text-[12px] text-nk-muted">No documents for this client yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

