from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
page = root / "src" / "app" / "supply-chain" / "page.tsx"

content = r'''"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Factory,
  LineChart,
  Network,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  EnrichedArtifacts,
  loadEnrichedArtifacts,
} from "@/lib/hershey/enrichedArtifacts";
import HersheyCinematicHero from "@/components/hershey/HersheyCinematicHero";
import CinematicAssetScene from "@/components/hershey/CinematicAssetScene";
import CinematicConnectedMap from "@/components/hershey/CinematicConnectedMap";

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
    };
  }, [data]);

  if (error) {
    return (
      <main className="min-h-screen bg-[#140606] px-6 py-10 text-white">
        <section className="mx-auto max-w-4xl rounded-3xl border border-red-400/30 bg-red-950/40 p-8">
          <h1 className="text-3xl font-black">Artifact loading error</h1>
          <p className="mt-4 text-red-100">{error}</p>
          <p className="mt-4 text-sm text-red-200">
            Check that Step 16K and Step 17D visual asset registry passed.
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
          <p className="text-lg font-bold">Loading Hershey cinematic supply-chain artifacts...</p>
        </div>
      </main>
    );
  }

  const physical = data.costBreakdown.physical_cost;
  const retail = data.costBreakdown.retail_price;
  const residual = data.costBreakdown.residual_channel_pool;

  return (
    <main className="min-h-screen overflow-hidden bg-[#080202] text-white">
      <HersheyCinematicHero
        manifest={data.manifest}
        homeCards={data.homeCards}
        costBreakdown={data.costBreakdown}
        evidenceCount={stats.evidenceCount}
        nodeCount={stats.nodeCount}
        edgeCount={stats.edgeCount}
        supplierCount={stats.supplierCount}
        ingredientCount={stats.ingredientCount}
      />

      <CinematicAssetScene
        ingredients={data.ingredients}
        suppliers={data.suppliers}
        costBreakdown={data.costBreakdown}
      />

      <CinematicConnectedMap
        ingredients={data.ingredients}
        suppliers={data.suppliers}
        graph={data.graph}
        costBreakdown={data.costBreakdown}
      />

      <section className="relative border-y border-white/10 bg-[#100403] px-6 py-16">
        <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
            <LineChart className="mb-4 text-amber-200" />
            <h2 className="text-2xl font-black">Cost Intelligence</h2>
            <div className="mt-5 space-y-3 text-sm text-white/70">
              <p>
                Physical base cost:{" "}
                <span className="font-bold text-white">
                  {cents(physical?.base_cents_per_bar)}
                </span>
              </p>
              <p>
                Retail base price:{" "}
                <span className="font-bold text-white">
                  {usd(retail?.base_usd_per_bar)}
                </span>
              </p>
              <p>
                Residual pool:{" "}
                <span className="font-bold text-white">
                  {cents(residual?.base_cents_per_bar)}
                </span>
              </p>
            </div>
            <p className="mt-5 text-xs leading-5 text-amber-100/60">
              {data.costBreakdown.enriched_audit_note}
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
            <Network className="mb-4 text-amber-200" />
            <h2 className="text-2xl font-black">Evidence Graph</h2>
            <div className="mt-5 space-y-3 text-sm text-white/70">
              <p>
                Nodes loaded:{" "}
                <span className="font-bold text-white">{stats.nodeCount}</span>
              </p>
              <p>
                Edges loaded:{" "}
                <span className="font-bold text-white">{stats.edgeCount}</span>
              </p>
              <p>
                Packet summaries:{" "}
                <span className="font-bold text-white">{stats.packetCount}</span>
              </p>
            </div>
            <p className="mt-5 text-xs leading-5 text-white/50">
              The graph supports the visual supply-chain model but does not claim proprietary
              route or internal factory data.
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
            <ShieldCheck className="mb-4 text-amber-200" />
            <h2 className="text-2xl font-black">Safety Rules</h2>
            <ul className="mt-5 space-y-2 text-sm leading-6 text-white/70">
              {(data.manifest.safe_display_rules || []).slice(0, 5).map((rule) => (
                <li key={rule}>• {rule}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-black/30 px-6 py-8">
        <div className="mx-auto flex max-w-7xl items-center gap-3 text-sm text-white/50">
          <Factory size={18} />
          <p>
            Clean cinematic page ready. Next step converts the asset scene into a Three.js
            animated supply-chain experience.
          </p>
        </div>
      </section>
    </main>
  );
}
'''

page.write_text(content, encoding="utf-8")

print("STEP 17D-2 PAGE CLEANUP PATCH COMPLETE")
print(f"Updated: {page}")
print("Removed duplicate storyboard/ingredient/supplier debug sections from main page.")