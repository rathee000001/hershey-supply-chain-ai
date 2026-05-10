"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Boxes,
  Factory,
  LineChart,
  Network,
  ShieldCheck,
  Sparkles,
  Truck,
} from "lucide-react";
import {
  EnrichedArtifacts,
  loadEnrichedArtifacts,
} from "@/lib/hershey/enrichedArtifacts";

function formatNumber(value: unknown): string {
  if (typeof value === "number") return value.toLocaleString();
  if (typeof value === "string") return value;
  return "—";
}

function cents(value: unknown): string {
  if (typeof value === "number") return `${value.toFixed(2)}¢`;
  return "—";
}

function usd(value: unknown): string {
  if (typeof value === "number") return `$${value.toFixed(2)}`;
  return "—";
}

export default function SupplyChainPage() {
  const [data, setData] = useState<EnrichedArtifacts | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    loadEnrichedArtifacts()
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Unknown artifact loading error");
      });
  }, []);

  const stats = useMemo(() => {
    if (!data) return null;

    return {
      evidenceCount: Object.keys(data.evidence || {}).length,
      packetCount: data.packetSummary?.length ?? 0,
      supplierCount: data.suppliers?.length ?? 0,
      ingredientCount: data.ingredients?.length ?? 0,
      nodeCount: data.graph?.nodes?.length ?? 0,
      edgeCount: data.graph?.edges?.length ?? 0,
      homeCardCount: data.homeCards?.length ?? 0,
    };
  }, [data]);

  if (error) {
    return (
      <main className="min-h-screen bg-[#140606] px-6 py-10 text-white">
        <section className="mx-auto max-w-4xl rounded-3xl border border-red-400/30 bg-red-950/40 p-8">
          <h1 className="text-3xl font-black">Artifact loading error</h1>
          <p className="mt-4 text-red-100">{error}</p>
          <p className="mt-4 text-sm text-red-200">
            Check that Step 16K passed and that public/data/hershey/enriched_display exists.
          </p>
        </section>
      </main>
    );
  }

  if (!data || !stats) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#140606] text-white">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl">
          <Sparkles className="mb-4 animate-pulse text-amber-200" />
          <p className="text-lg font-bold">Loading enriched Hershey supply-chain artifacts...</p>
        </div>
      </main>
    );
  }

  const physical = data.costBreakdown.physical_cost;
  const retail = data.costBreakdown.retail_price;
  const residual = data.costBreakdown.residual_channel_pool;

  return (
    <main className="min-h-screen overflow-hidden bg-[#140606] text-white">
      <section className="relative border-b border-white/10 bg-[radial-gradient(circle_at_top_right,#6d2c18_0%,#2b0909_42%,#140606_100%)]">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute left-10 top-20 h-72 w-72 rounded-full bg-amber-300 blur-3xl" />
          <div className="absolute bottom-10 right-16 h-96 w-96 rounded-full bg-red-900 blur-3xl" />
        </div>

        <div className="relative mx-auto grid min-h-[82vh] max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-amber-200/25 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100 backdrop-blur">
              <ShieldCheck size={16} />
              Step 16K Validated Artifact Frontend
            </div>

            <h1 className="max-w-5xl text-5xl font-black leading-[0.95] tracking-tight md:text-7xl">
              {data.manifest.project || "Hershey Supply Chain Intelligence"}
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-amber-50/80">
              A JSON-first, evidence-audited supply-chain intelligence platform for the
              1.55 oz milk chocolate bar. This page is the first frontend proof that the
              enriched v2 artifact brain is loading correctly.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Approved evidence</p>
                <p className="mt-2 text-3xl font-black">{formatNumber(stats.evidenceCount)}</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Graph model</p>
                <p className="mt-2 text-3xl font-black">
                  {stats.nodeCount} / {stats.edgeCount}
                </p>
                <p className="text-xs text-amber-100/60">nodes / edges</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Cards loaded</p>
                <p className="mt-2 text-3xl font-black">
                  {stats.supplierCount + stats.ingredientCount}
                </p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-10 rounded-full bg-amber-200/10 blur-3xl" />
            <div className="relative rounded-[2.5rem] border border-amber-100/20 bg-[#35120d]/80 p-8 shadow-2xl backdrop-blur">
              <div className="rounded-[2rem] border border-white/10 bg-gradient-to-br from-[#4b1d16] to-[#210807] p-8">
                <p className="text-xs font-black uppercase tracking-[0.35em] text-amber-100/70">
                  Cinematic frontend starts after loader validation
                </p>
                <div className="mt-8 rounded-3xl bg-[#2b0909] p-8 shadow-inner">
                  <p className="text-6xl font-black tracking-tight text-amber-50">HERSHEY</p>
                  <p className="mt-2 text-xl tracking-[0.35em] text-amber-100/70">milk chocolate</p>
                  <div className="mt-8 grid grid-cols-4 gap-2">
                    {Array.from({ length: 12 }).map((_, index) => (
                      <div
                        key={index}
                        className="h-12 rounded-xl border border-amber-100/10 bg-gradient-to-br from-[#7a3a22] to-[#3b120d] shadow"
                      />
                    ))}
                  </div>
                </div>
                <p className="mt-5 text-sm leading-6 text-amber-50/70">
                  Next steps will replace this proof block with cinematic ingredient streams,
                  manufacturing animation, logistics routes, cost pulses, and evidence panels.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-4 md:grid-cols-5">
          {data.homeCards.map((card) => (
            <div key={card.card_id} className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-100/50">
                {card.title}
              </p>
              <p className="mt-3 text-2xl font-black text-amber-50">{card.value}</p>
              <p className="mt-2 text-sm leading-6 text-white/60">{card.subtitle}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-3">
        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <LineChart className="mb-4 text-amber-200" />
          <h2 className="text-2xl font-black">Cost Intelligence</h2>
          <div className="mt-5 space-y-3 text-sm text-white/70">
            <p>Physical base cost: <span className="font-bold text-white">{cents(physical?.base_cents_per_bar)}</span></p>
            <p>Retail base price: <span className="font-bold text-white">{usd(retail?.base_usd_per_bar)}</span></p>
            <p>Residual pool: <span className="font-bold text-white">{cents(residual?.base_cents_per_bar)}</span></p>
          </div>
          <p className="mt-5 text-xs leading-5 text-amber-100/60">
            {data.costBreakdown.enriched_audit_note}
          </p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <Network className="mb-4 text-amber-200" />
          <h2 className="text-2xl font-black">Graph Payload</h2>
          <div className="mt-5 space-y-3 text-sm text-white/70">
            <p>Nodes loaded: <span className="font-bold text-white">{stats.nodeCount}</span></p>
            <p>Edges loaded: <span className="font-bold text-white">{stats.edgeCount}</span></p>
            <p>Packet summaries: <span className="font-bold text-white">{stats.packetCount}</span></p>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
          <ShieldCheck className="mb-4 text-amber-200" />
          <h2 className="text-2xl font-black">Safety Rules</h2>
          <ul className="mt-5 space-y-2 text-sm leading-6 text-white/70">
            {(data.manifest.safe_display_rules || []).slice(0, 4).map((rule) => (
              <li key={rule}>• {rule}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-5 flex items-center gap-3">
          <Boxes className="text-amber-200" />
          <h2 className="text-3xl font-black">Ingredient Cards from JSON</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
          {data.ingredients.map((ingredient) => (
            <div key={ingredient.ingredient_id} className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
              <p className="text-lg font-black">{ingredient.ingredient_name}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.2em] text-amber-100/50">
                {ingredient.packet}
              </p>
              <p className="mt-4 text-sm text-white/65">
                Evidence count:{" "}
                <span className="font-bold text-white">{ingredient.approved_evidence_count ?? 0}</span>
              </p>
              <p className="mt-2 text-sm text-white/65">
                Supplier status: {ingredient.supplier_status || "—"}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-8 pb-20">
        <div className="mb-5 flex items-center gap-3">
          <Truck className="text-amber-200" />
          <h2 className="text-3xl font-black">Supplier / Stage Cards from JSON</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {data.suppliers.map((supplier) => (
            <div key={supplier.supplier_packet_id} className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
              <p className="text-xl font-black">{supplier.safe_display_name}</p>
              <p className="mt-2 text-sm text-amber-100/70">{supplier.related_ingredient_or_stage}</p>
              <p className="mt-4 text-sm text-white/65">
                Approved evidence:{" "}
                <span className="font-bold text-white">{supplier.approved_evidence_count ?? 0}</span>
              </p>
              <p className="mt-3 text-xs leading-5 text-white/55">{supplier.safe_website_wording}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-white/10 bg-black/20 px-6 py-8">
        <div className="mx-auto flex max-w-7xl items-center gap-3 text-sm text-white/50">
          <Factory size={18} />
          <p>
            Frontend loader proof complete. The cinematic supply-chain animation starts in Step 17B.
          </p>
        </div>
      </section>
    </main>
  );
}