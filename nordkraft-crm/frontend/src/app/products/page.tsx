"use client";

import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Product } from "@/types";
import { productsApi } from "@/lib/api";
import { toast } from "sonner";
import { Plus, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ProductsPage() {
  const qc = useQueryClient();
  const [q, setQ] = useState("");

  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [unitPrice, setUnitPrice] = useState<number>(0);
  const [currency, setCurrency] = useState("EUR");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");

  const { data: products = [], isLoading } = useQuery<Product[]>({
    queryKey: ["products", q],
    queryFn: () => productsApi.list({ q, active_only: false }),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      productsApi.create({
        name,
        sku: sku || undefined,
        unit_price: Number.isFinite(unitPrice) ? unitPrice : 0,
        currency,
        description: description || undefined,
        tags: tags || undefined,
        is_active: true,
      }),
    onSuccess: async () => {
      toast.success("Product added");
      setName("");
      setSku("");
      setUnitPrice(0);
      setCurrency("EUR");
      setDescription("");
      setTags("");
      await qc.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Create failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => productsApi.delete(id),
    onSuccess: async () => {
      toast.success("Deleted");
      await qc.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Delete failed"),
  });

  const createDisabled = !name || createMutation.isPending;

  const activeCount = useMemo(() => products.filter((p) => p.is_active).length, [products]);

  return (
    <div className="max-w-5xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[18px] font-semibold tracking-tight">Products</div>
          <div className="text-[12px] text-nk-muted mt-0.5">Your product portfolio for building offers.</div>
        </div>
        <div className="text-[11px] text-nk-muted">{isLoading ? "Loading…" : `${activeCount}/${products.length} active`}</div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
        <div className="grid grid-cols-[1fr_200px_140px_140px] gap-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Name</div>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">SKU</div>
            <input
              value={sku}
              onChange={(e) => setSku(e.target.value)}
              placeholder="optional"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Unit price</div>
            <input
              value={String(unitPrice)}
              onChange={(e) => setUnitPrice(Number(e.target.value))}
              type="number"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Currency</div>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none"
            >
              <option value="EUR">EUR</option>
              <option value="SEK">SEK</option>
              <option value="NOK">NOK</option>
              <option value="DKK">DKK</option>
              <option value="USD">USD</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-[1fr_1fr] gap-3 mt-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Description (optional)</div>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Tags (optional)</div>
            <input
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="comma,separated"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
        </div>

        <div className="mt-3 flex justify-end">
          <button
            disabled={createDisabled}
            onClick={() => createMutation.mutate()}
            className="inline-flex items-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
          >
            <Plus size={14} />
            Add product
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search products..."
          className="bg-nk-surface border border-nk-border2 rounded-lg px-3 py-2 text-[13px] text-nk-text placeholder:text-nk-muted w-64 outline-none focus:border-nk-accent/50"
        />
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
          <div className="text-[13px] font-semibold">Portfolio</div>
          <div className="text-[11px] text-nk-muted">{isLoading ? "Loading…" : `${products.length} total`}</div>
        </div>
        <div className="divide-y divide-nk-border">
          {products.map((p) => (
            <div key={p.id} className="px-4 py-3 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-medium truncate">
                  {p.name} {p.sku ? <span className="text-[11px] text-nk-muted">· {p.sku}</span> : null}
                </div>
                {p.description && <div className="text-[11px] text-nk-muted truncate">{p.description}</div>}
              </div>
              <div className={cn("text-[12px] font-semibold", p.is_active ? "text-nk-green" : "text-nk-muted")}>
                {p.currency} {p.unit_price.toLocaleString()}
              </div>
              <button
                onClick={() => deleteMutation.mutate(p.id)}
                className="inline-flex items-center gap-1.5 text-[12px] text-nk-muted hover:text-red-300"
              >
                <Trash2 size={14} />
                Delete
              </button>
            </div>
          ))}
          {products.length === 0 && !isLoading && (
            <div className="px-4 py-10 text-center text-[12px] text-nk-muted">No products yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}

