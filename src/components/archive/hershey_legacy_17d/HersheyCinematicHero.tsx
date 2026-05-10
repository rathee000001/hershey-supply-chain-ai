"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Sparkles } from "lucide-react";
import type {
  CostBreakdown,
  HersheyFrontendManifest,
  HomeCard,
} from "@/lib/hershey/enrichedArtifacts";
import ChocolateDripOverlay from "@/components/hershey/ChocolateDripOverlay";

type VisualAsset = {
  asset_key: string;
  label: string;
  url: string;
  asset_type: string;
  source_kind: string;
};

type VisualAssetManifest = {
  assets: Record<string, VisualAsset>;
};

type Props = {
  manifest: HersheyFrontendManifest;
  homeCards: HomeCard[];
  costBreakdown: CostBreakdown;
  evidenceCount: number;
  nodeCount: number;
  edgeCount: number;
  supplierCount: number;
  ingredientCount: number;
};

const VISUAL_ASSET_MANIFEST_URL =
  "/data/hershey/visual_assets/hershey_visual_assets_manifest.json";

export default function HersheyCinematicHero({
  manifest,
  homeCards,
  costBreakdown,
  evidenceCount,
  nodeCount,
  edgeCount,
  supplierCount,
  ingredientCount,
}: Props) {
  const [visualManifest, setVisualManifest] = useState<VisualAssetManifest | null>(null);

  useEffect(() => {
    fetch(VISUAL_ASSET_MANIFEST_URL, { cache: "no-store" })
      .then((response) => response.json())
      .then(setVisualManifest)
      .catch(() => setVisualManifest(null));
  }, []);

  const asset = (key: string) => visualManifest?.assets?.[key];
  const wrapperFront = asset("hershey_wrapper_front")?.url;
  const wrapperBack = asset("hershey_wrapper_back")?.url;
  const unwrappedBar = asset("hershey_unwrapped_bar")?.url;

  return (
    <section className="relative min-h-screen overflow-hidden border-b border-white/10 bg-[radial-gradient(circle_at_78%_24%,#7b2a15_0%,#2a0806_42%,#080202_100%)] text-white">
      <ChocolateDripOverlay variant="hero" />

      <div className="absolute inset-0 opacity-70">
        <div className="absolute left-[-8rem] top-28 h-[34rem] w-[34rem] rounded-full bg-[#4a130b] blur-3xl" />
        <div className="absolute right-[-8rem] top-20 h-[42rem] w-[42rem] rounded-full bg-amber-300/10 blur-3xl" />
        <div className="absolute bottom-10 left-1/3 h-[28rem] w-[28rem] rounded-full bg-red-900/30 blur-3xl" />
      </div>

      <div className="relative z-20 mx-auto grid min-h-screen max-w-7xl gap-12 px-6 pb-16 pt-36 lg:grid-cols-[1fr_0.95fr] lg:items-center">
        <div>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-amber-100/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/80 backdrop-blur">
            <ShieldCheck size={16} />
            Step 16K validated evidence brain
          </div>

          <h1 className="max-w-5xl text-5xl font-black leading-[0.92] tracking-tight md:text-7xl">
            {manifest.project || "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence"}
          </h1>

          <p className="mt-7 max-w-3xl text-lg leading-8 text-amber-50/78">
            An evidence-audited cinematic supply-chain experience for the 1.55 oz milk
            chocolate bar: origin streams, suppliers, Hershey processing, packaging,
            distribution, shelf, and consumer purchase.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
              <p className="text-sm text-amber-100/70">Approved evidence</p>
              <p className="mt-2 text-3xl font-black">{evidenceCount.toLocaleString()}</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
              <p className="text-sm text-amber-100/70">Graph model</p>
              <p className="mt-2 text-3xl font-black">
                {nodeCount} / {edgeCount}
              </p>
              <p className="text-xs text-amber-100/60">nodes / edges</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
              <p className="text-sm text-amber-100/70">Cards loaded</p>
              <p className="mt-2 text-3xl font-black">
                {supplierCount + ingredientCount}
              </p>
            </div>
          </div>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            <div className="rounded-3xl border border-amber-100/15 bg-black/25 p-5 backdrop-blur">
              <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-100/50">
                Benchmark physical cost
              </p>
              <p className="mt-2 text-3xl font-black">
                {costBreakdown.physical_cost?.base_cents_per_bar?.toFixed(2) ?? "—"}¢
              </p>
            </div>
            <div className="rounded-3xl border border-amber-100/15 bg-black/25 p-5 backdrop-blur">
              <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-100/50">
                Observed retail base
              </p>
              <p className="mt-2 text-3xl font-black">
                ${costBreakdown.retail_price?.base_usd_per_bar?.toFixed(2) ?? "—"}
              </p>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-12 rounded-full bg-amber-200/10 blur-3xl" />

          <div className="relative overflow-hidden rounded-[3rem] border border-amber-100/20 bg-white/[0.06] p-6 shadow-2xl backdrop-blur">
            <div className="rounded-[2.4rem] border border-white/10 bg-[#210706]/80 p-6">
              <p className="mb-5 text-xs font-black uppercase tracking-[0.32em] text-amber-100/55">
                Actual collected product visual
              </p>

              <div className="relative flex min-h-[260px] items-center justify-center rounded-[2rem] border border-white/10 bg-black/30 p-6">
                {wrapperFront ? (
                  <img
                    src={wrapperFront}
                    alt="Hershey wrapper front"
                    className="max-h-56 w-full object-contain drop-shadow-2xl"
                  />
                ) : (
                  <div className="text-5xl font-black tracking-tight text-amber-50">
                    HERSHEY
                  </div>
                )}
              </div>

              <div className="mt-5 grid grid-cols-2 gap-4">
                <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-4">
                  <p className="text-xs text-white/45">Back wrapper</p>
                  <div className="mt-3 flex h-24 items-center justify-center rounded-2xl bg-black/25 p-2">
                    {wrapperBack ? (
                      <img
                        src={wrapperBack}
                        alt="Hershey wrapper back"
                        className="h-full w-full object-contain"
                      />
                    ) : (
                      <Sparkles className="text-amber-200" />
                    )}
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.05] p-4">
                  <p className="text-xs text-white/45">Chocolate bar</p>
                  <div className="mt-3 flex h-24 items-center justify-center rounded-2xl bg-black/25 p-2">
                    {unwrappedBar ? (
                      <img
                        src={unwrappedBar}
                        alt="Unwrapped Hershey chocolate"
                        className="h-full w-full object-contain"
                      />
                    ) : (
                      <Sparkles className="text-amber-200" />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <p className="mt-5 text-sm leading-6 text-amber-50/60">
            Visuals are used for cinematic storytelling. Supplier, cost, and evidence claims
            still come only from audited JSON artifacts.
          </p>
        </div>
      </div>

      <div className="relative z-20 mx-auto max-w-7xl px-6 pb-14">
        <div className="grid gap-4 md:grid-cols-5">
          {homeCards.map((card) => (
            <div
              key={card.card_id}
              className="rounded-3xl border border-white/10 bg-white/[0.06] p-5 backdrop-blur"
            >
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-100/50">
                {card.title}
              </p>
              <p className="mt-3 text-2xl font-black text-amber-50">{card.value}</p>
              <p className="mt-2 text-sm leading-6 text-white/60">{card.subtitle}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}