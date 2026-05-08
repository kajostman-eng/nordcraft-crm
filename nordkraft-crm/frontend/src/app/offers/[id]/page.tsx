"use client";

import { useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Offer, OfferItem, Product } from "@/types";
import { offersApi, productsApi } from "@/lib/api";
import { toast } from "sonner";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";

function money(n: number) {
  return (Number.isFinite(n) ? n : 0).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function OfferDetailPage() {
  const params = useParams<{ id: string }>();
  const offerId = params?.id;
  const router = useRouter();
  const qc = useQueryClient();

  const [selectedProductId, setSelectedProductId] = useState("");
  const [qty, setQty] = useState<number>(1);

  const { data: offer, isLoading: offerLoading } = useQuery<Offer>({
    queryKey: ["offer", offerId],
    queryFn: () => offersApi.get(String(offerId)),
    enabled: !!offerId,
  });

  const { data: items = [] } = useQuery<OfferItem[]>({
    queryKey: ["offer-items", offerId],
    queryFn: () => offersApi.items(String(offerId)),
    enabled: !!offerId,
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ["products-active"],
    queryFn: () => productsApi.list({ active_only: true }),
  });

  const addItemMutation = useMutation({
    mutationFn: () =>
      offersApi.addItem(String(offerId), {
        product_id: selectedProductId,
        quantity: qty,
      }),
    onSuccess: async () => {
      toast.success("Added");
      setSelectedProductId("");
      setQty(1);
      await qc.invalidateQueries({ queryKey: ["offer-items", offerId] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Add failed"),
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) =>
      offersApi.updateItem(String(offerId), itemId, { quantity }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["offer-items", offerId] });
    },
  });

  const deleteItemMutation = useMutation({
    mutationFn: (itemId: string) => offersApi.deleteItem(String(offerId), itemId),
    onSuccess: async () => {
      toast.success("Removed");
      await qc.invalidateQueries({ queryKey: ["offer-items", offerId] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Remove failed"),
  });

  const subtotal = useMemo(() => items.reduce((s, it) => s + (it.line_total || 0), 0), [items]);
  const discount = offer?.discount_amount || 0;
  const total = Math.max(0, subtotal - discount);

  const canAdd = !!selectedProductId && qty > 0 && !addItemMutation.isPending;

  const productById = useMemo(() => new Map(products.map((p) => [p.id, p])), [products]);

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
        {offerLoading || !offer ? (
          <div className="text-[13px] text-nk-muted">Loading offer…</div>
        ) : (
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-[18px] font-semibold tracking-tight">{offer.title}</div>
              <div className="text-[12px] text-nk-muted mt-0.5">
                {offer.status} · {offer.lead_id ? "Lead offer" : offer.client_id ? "Client offer" : "Unattached"}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px]">Total</div>
              <div className="text-[18px] font-semibold">
                {offer.currency} {money(total)}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl p-4 mb-4">
        <div className="text-[13px] font-semibold mb-3">Add product</div>
        <div className="grid grid-cols-[1fr_120px_140px] gap-3">
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Product</div>
            <select
              value={selectedProductId}
              onChange={(e) => setSelectedProductId(e.target.value)}
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none"
            >
              <option value="">Select product…</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.currency} {money(p.unit_price)})
                </option>
              ))}
            </select>
          </div>
          <div>
            <div className="text-[11px] text-nk-muted uppercase tracking-[0.5px] mb-1.5">Qty</div>
            <input
              value={String(qty)}
              onChange={(e) => setQty(Number(e.target.value))}
              type="number"
              className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-3 py-2 outline-none focus:border-nk-accent/60"
            />
          </div>
          <div className="flex items-end">
            <button
              disabled={!canAdd}
              onClick={() => addItemMutation.mutate()}
              className="w-full inline-flex items-center justify-center gap-2 text-[12px] font-semibold px-3 py-2 rounded-lg bg-nk-accent text-white disabled:opacity-50"
            >
              <Plus size={14} />
              Add
            </button>
          </div>
        </div>
      </div>

      <div className="bg-nk-surface border border-nk-border rounded-xl overflow-hidden">
        <div className="px-4 py-3.5 border-b border-nk-border flex items-center justify-between">
          <div className="text-[13px] font-semibold">Line items</div>
          <div className="text-[11px] text-nk-muted">{items.length} items</div>
        </div>
        <div className="divide-y divide-nk-border">
          {items.map((it) => {
            const p = productById.get(it.product_id);
            return (
              <div key={it.id} className="px-4 py-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="text-[13px] font-medium truncate">{p?.name || it.product_id}</div>
                  <div className="text-[11px] text-nk-muted">
                    Unit: {offer?.currency || "EUR"} {money(it.unit_price)}
                  </div>
                </div>
                <div className="w-[110px]">
                  <input
                    value={String(it.quantity)}
                    onChange={(e) =>
                      updateItemMutation.mutate({ itemId: it.id, quantity: Number(e.target.value) || 1 })
                    }
                    type="number"
                    className="w-full text-[12px] bg-nk-surface2 border border-nk-border rounded-lg px-2 py-1.5 outline-none focus:border-nk-accent/60"
                  />
                </div>
                <div className="w-[160px] text-right text-[12px] font-semibold">
                  {offer?.currency || "EUR"} {money(it.line_total)}
                </div>
                <button
                  onClick={() => deleteItemMutation.mutate(it.id)}
                  className="inline-flex items-center gap-1.5 text-[12px] text-nk-muted hover:text-red-300"
                >
                  <Trash2 size={14} />
                  Remove
                </button>
              </div>
            );
          })}
          {items.length === 0 && (
            <div className="px-4 py-10 text-center text-[12px] text-nk-muted">No items yet. Add products above.</div>
          )}
        </div>
        <div className="px-4 py-3.5 border-t border-nk-border flex items-center justify-end gap-6">
          <div className="text-[12px] text-nk-muted">
            Subtotal: <span className="text-nk-text font-semibold">{offer?.currency || "EUR"} {money(subtotal)}</span>
          </div>
          <div className="text-[12px] text-nk-muted">
            Discount: <span className="text-nk-text font-semibold">{offer?.currency || "EUR"} {money(discount)}</span>
          </div>
          <div className="text-[12px]">
            Total: <span className="text-nk-green font-semibold">{offer?.currency || "EUR"} {money(total)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

