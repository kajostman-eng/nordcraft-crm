"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { documentsApi } from "@/lib/api";
import type { Document } from "@/types";
import { toast } from "sonner";
import { Upload, Link as LinkIcon, Trash2 } from "lucide-react";

export default function DocumentsPage() {
  const qc = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [leadId, setLeadId] = useState("");
  const [clientId, setClientId] = useState("");

  const { data: docs = [], isLoading } = useQuery<Document[]>({
    queryKey: ["documents"],
    queryFn: () => documentsApi.list(),
  });

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file) throw new Error("Missing file");
      return documentsApi.upload({
        file,
        title: title || file.name,
        description: description || undefined,
        lead_id: leadId || undefined,
        client_id: clientId || undefined,
      });
    },
    onSuccess: async () => {
      toast.success("Uploaded");
      setFile(null);
      setTitle("");
      setDescription("");
      setLeadId("");
      setClientId("");
      await qc.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Upload failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: async () => {
      toast.success("Deleted");
      await qc.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Delete failed"),
  });

  const disabled = useMemo(() => uploadMutation.isPending || !file, [uploadMutation.isPending, file]);

  return (
    <div className="max-w-5xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[18px] font-semibold tracking-tight">Documents</div>
          <div className="text-[12px] text-nk-muted mt-0.5">Upload files and attach them to leads/clients (next step).</div>
        </div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
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
              placeholder={file?.name || "e.g. Contract, Proposal, Meeting notes"}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>
        <div className="mt-3">
          <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Description (optional)</div>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short context for this document"
            className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
          />
        </div>
        <div className="grid grid-cols-[1fr_1fr] gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Attach to lead (optional)</div>
            <input
              value={leadId}
              onChange={(e) => setLeadId(e.target.value)}
              placeholder="Lead ID (e.g. 4f3b...)"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Attach to client (optional)</div>
            <input
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              placeholder="Client ID (e.g. 9a2c...)"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>
        <div className="mt-3 flex justify-end">
          <button
            disabled={disabled}
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
          <div className="text-[13px] font-semibold">All documents</div>
          <div className="text-[11px] text-nk-muted">{isLoading ? "Loading…" : `${docs.length} total`}</div>
        </div>
        <div className="divide-y divide-nk-border">
          {(docs || []).map((d) => (
            <div key={d.id} className="px-4 py-3 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-medium truncate">{d.title}</div>
                <div className="text-[11px] text-nk-muted truncate">{d.file_name}</div>
                {(d.lead_id || d.client_id) && (
                  <div className="mt-1 flex items-center gap-2 text-[10px] text-nk-muted">
                    {d.lead_id && <span className="bg-nk-surface2 border border-nk-border rounded px-1.5 py-0.5">Lead</span>}
                    {d.client_id && <span className="bg-nk-surface2 border border-nk-border rounded px-1.5 py-0.5">Client</span>}
                  </div>
                )}
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
          {docs.length === 0 && !isLoading && (
            <div className="px-4 py-10 text-center text-[12px] text-nk-muted">No documents yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

