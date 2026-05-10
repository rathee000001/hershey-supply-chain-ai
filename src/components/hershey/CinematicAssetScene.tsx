"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  Factory,
  PackageCheck,
  ShoppingBag,
  Store,
  Truck,
} from "lucide-react";
import type {
  CostBreakdown,
  IngredientCard,
  SupplierCard,
} from "@/lib/hershey/enrichedArtifacts";

type VisualAsset = {
  asset_key: string;
  label: string;
  url: string;
  asset_type: string;
  source_kind: string;
  usage_note?: string;
};

type VisualAssetManifest = {
  visual_assets_version?: string;
  base_public_path?: string;
  assets: Record<string, VisualAsset>;
};

type Props = {
  ingredients: IngredientCard[];
  suppliers: SupplierCard[];
  costBreakdown: CostBreakdown;
};

const MANIFEST_URL = "/data/hershey/visual_assets/hershey_visual_assets_manifest.json";

function countIngredientEvidence(ingredients: IngredientCard[], packet: string): number {
  return ingredients
    .filter((item) => item.packet === packet)
    .reduce((sum, item) => sum + (item.approved_evidence_count ?? 0), 0);
}

function supplierEvidence(suppliers: SupplierCard[], name: string): number {
  return (
    suppliers.find((supplier) =>
      String(supplier.safe_display_name || "").toLowerCase().includes(name.toLowerCase())
    )?.approved_evidence_count ?? 0
  );
}

function AssetImage({
  src,
  label,
  className = "",
}: {
  src?: string;
  label: string;
  className?: string;
}) {
  if (!src) {
    return (
      <div className={`flex items-center justify-center rounded-3xl bg-white/10 ${className}`}>
        <span className="text-xs font-black uppercase tracking-[0.2em] text-white/40">
          {label}
        </span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={label}
      className={`object-contain ${className}`}
      loading="lazy"
    />
  );
}

function StageCard({
  title,
  subtitle,
  image,
  evidence,
  sourceKind,
}: {
  title: string;
  subtitle: string;
  image?: string;
  evidence: number | string;
  sourceKind?: string;
}) {
  return (
    <div className="group relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.06] p-4 shadow-2xl backdrop-blur transition duration-500 hover:-translate-y-1 hover:border-amber-200/30 hover:bg-white/[0.1]">
      <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-amber-200/10 blur-3xl transition group-hover:bg-amber-200/20" />

      <div className="relative mb-4 flex h-32 items-center justify-center rounded-[1.5rem] border border-white/10 bg-black/25 p-3">
        <AssetImage src={image} label={title} className="h-full w-full" />
      </div>

      <p className="relative text-lg font-black text-white">{title}</p>
      <p className="relative mt-2 min-h-10 text-sm leading-5 text-white/60">{subtitle}</p>

      <div className="relative mt-4 flex items-center justify-between gap-3">
        <span className="rounded-full border border-amber-100/15 bg-black/25 px-3 py-2 text-xs font-bold text-amber-100/70">
          {evidence} evidence
        </span>
        <span className="rounded-full bg-white/[0.06] px-3 py-2 text-[10px] font-black uppercase tracking-[0.18em] text-white/35">
          {sourceKind || "asset"}
        </span>
      </div>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="hidden items-center justify-center text-amber-200/60 xl:flex">
      <ArrowRight size={30} />
    </div>
  );
}

export default function CinematicAssetScene({
  ingredients,
  suppliers,
  costBreakdown,
}: Props) {
  const [manifest, setManifest] = useState<VisualAssetManifest | null>(null);

  useEffect(() => {
    fetch(MANIFEST_URL, { cache: "no-store" })
      .then((response) => response.json())
      .then(setManifest)
      .catch(() => setManifest(null));
  }, []);

  const asset = (key: string) => manifest?.assets?.[key];

  const counts = useMemo(() => {
    return {
      dairy: countIngredientEvidence(ingredients, "dairy_milk_skim_milk_milk_fat"),
      sugar: countIngredientEvidence(ingredients, "sugar"),
      cocoa: countIngredientEvidence(ingredients, "cocoa_chocolate_cocoa_butter"),
      minor:
        countIngredientEvidence(ingredients, "soy_lecithin") +
        countIngredientEvidence(ingredients, "pgpr") +
        countIngredientEvidence(ingredients, "natural_flavor"),
      packaging: countIngredientEvidence(ingredients, "packaging_wrapper"),
      asr: supplierEvidence(suppliers, "ASR"),
      barry: supplierEvidence(suppliers, "Barry"),
      land: supplierEvidence(suppliers, "Land"),
      mclane: supplierEvidence(suppliers, "McLane"),
    };
  }, [ingredients, suppliers]);

  return (
    <section className="relative overflow-hidden border-y border-white/10 bg-[#070202] px-6 py-20">
      <style>{`
        @keyframes assetFloat {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-8px) scale(1.02); }
        }
        @keyframes assetGlow {
          0%, 100% { opacity: .35; }
          50% { opacity: .75; }
        }
        .asset-float {
          animation: assetFloat 5s ease-in-out infinite;
        }
        .asset-glow {
          animation: assetGlow 3.5s ease-in-out infinite;
        }
      `}</style>

      <div className="absolute inset-0">
        <div className="asset-glow absolute left-10 top-10 h-96 w-96 rounded-full bg-amber-200/10 blur-3xl" />
        <div className="asset-glow absolute bottom-10 right-10 h-[30rem] w-[30rem] rounded-full bg-red-900/35 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl">
        <div className="mb-12 grid gap-8 lg:grid-cols-[1fr_0.8fr] lg:items-end">
          <div>
            <p className="inline-flex rounded-full border border-amber-200/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
              Actual asset-driven scene layer
            </p>
            <h2 className="mt-5 text-4xl font-black leading-tight tracking-tight md:text-6xl">
              The supply chain now uses collected visuals and logos
            </h2>
            <p className="mt-5 max-w-4xl text-lg leading-8 text-white/65">
              Hershey wrapper, chocolate visuals, company logos, and generated placeholders are
              registered for the final Three.js cinematic experience. Evidence counts still come
              from audited JSON.
            </p>
          </div>

          <div className="asset-float rounded-[2.5rem] border border-amber-100/20 bg-white/[0.06] p-6 shadow-2xl">
            <AssetImage
              src={asset("hershey_wrapper_front")?.url}
              label="Hershey wrapper front"
              className="h-44 w-full"
            />
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="rounded-2xl border border-white/10 bg-black/25 p-3">
                <p className="text-xs text-white/45">Physical cost</p>
                <p className="mt-1 text-xl font-black">
                  {costBreakdown.physical_cost?.base_cents_per_bar?.toFixed(2) ?? "—"}¢
                </p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/25 p-3">
                <p className="text-xs text-white/45">Retail base</p>
                <p className="mt-1 text-xl font-black">
                  ${costBreakdown.retail_price?.base_usd_per_bar?.toFixed(2) ?? "—"}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <div className="rounded-[2.5rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Factory className="text-amber-200" />
              <h3 className="text-2xl font-black">Ingredient streams into Hershey</h3>
            </div>

            <div className="grid gap-4 xl:grid-cols-[1fr_44px_1fr_44px_1fr_44px_1fr]">
              <StageCard
                title="Cow / Dairy Farm"
                subtitle="Milk begins at farm-origin context before supplier movement."
                image={asset("dairy_origin")?.url}
                evidence={counts.dairy}
                sourceKind={asset("dairy_origin")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Land O'Lakes"
                subtitle="Company-level dairy supplier context."
                image={asset("land_olakes_logo")?.url}
                evidence={counts.land}
                sourceKind={asset("land_olakes_logo")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Refrigerated Truck"
                subtitle="Modeled cold-chain movement into Hershey."
                image={asset("truck_visual")?.url}
                evidence="modeled"
                sourceKind={asset("truck_visual")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Hershey Intake"
                subtitle="Dairy stream enters modeled chocolate production."
                image={asset("hershey_logo")?.url}
                evidence="factory"
                sourceKind={asset("hershey_logo")?.source_kind}
              />
            </div>

            <div className="mt-5 grid gap-4 xl:grid-cols-[1fr_44px_1fr_44px_1fr_44px_1fr]">
              <StageCard
                title="Sugarcane / Beet"
                subtitle="Agricultural sugar origin and sourcing context."
                image={asset("sugarcane_origin")?.url}
                evidence={counts.sugar}
                sourceKind={asset("sugarcane_origin")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="ASR / Domino"
                subtitle="Company-level sugar supplier/refiner context."
                image={asset("asr_logo")?.url}
                evidence={counts.asr}
                sourceKind={asset("asr_logo")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Packed Sugar"
                subtitle="Industrial sugar shipment toward Hershey."
                image={asset("truck_visual")?.url}
                evidence="modeled"
                sourceKind={asset("truck_visual")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Hershey Intake"
                subtitle="Sugar stream joins chocolate production."
                image={asset("hershey_logo")?.url}
                evidence="factory"
                sourceKind={asset("hershey_logo")?.source_kind}
              />
            </div>

            <div className="mt-5 grid gap-4 xl:grid-cols-[1fr_44px_1fr_44px_1fr_44px_1fr]">
              <StageCard
                title="Cocoa Origin"
                subtitle="Cocoa/chocolate/cocoa butter context begins upstream."
                image={asset("cocoa_origin")?.url}
                evidence={counts.cocoa}
                sourceKind={asset("cocoa_origin")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Barry Callebaut"
                subtitle="Company-level cocoa/chocolate supplier context."
                image={asset("barry_callebaut_logo")?.url}
                evidence={counts.barry}
                sourceKind={asset("barry_callebaut_logo")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Chocolate Input"
                subtitle="Cocoa/chocolate stream moves into Hershey."
                image={asset("hershey_unwrapped_bar")?.url}
                evidence={counts.cocoa}
                sourceKind={asset("hershey_unwrapped_bar")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Hershey Intake"
                subtitle="Cocoa stream joins the modeled production process."
                image={asset("hershey_logo")?.url}
                evidence="factory"
                sourceKind={asset("hershey_logo")?.source_kind}
              />
            </div>
          </div>

          <div className="rounded-[2.5rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <PackageCheck className="text-amber-200" />
              <h3 className="text-2xl font-black">Inside Hershey: combine, form, wrap, distribute</h3>
            </div>

            <div className="grid gap-4 xl:grid-cols-[1fr_44px_1fr_44px_1fr_44px_1fr_44px_1fr]">
              <StageCard
                title="Ingredient Merge"
                subtitle="Sugar, dairy, cocoa, and minor ingredients combine."
                image={asset("factory_visual")?.url}
                evidence={counts.minor}
                sourceKind={asset("factory_visual")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Chocolate Bar"
                subtitle="Chocolate is formed into the recognizable bar shape."
                image={asset("hershey_unwrapped_bar")?.url}
                evidence={counts.cocoa}
                sourceKind={asset("hershey_unwrapped_bar")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Wrapper"
                subtitle="Finished bars move into wrapper/packaging flow."
                image={asset("hershey_wrapper_front")?.url}
                evidence={counts.packaging}
                sourceKind={asset("hershey_wrapper_front")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Distribution"
                subtitle="Packed bars move through warehouse / carrier context."
                image={asset("mclane_logo")?.url || asset("truck_visual")?.url}
                evidence={counts.mclane}
                sourceKind={asset("mclane_logo")?.source_kind || asset("truck_visual")?.source_kind}
              />
              <FlowArrow />
              <StageCard
                title="Retail Shelf"
                subtitle="Retail shelf is general until final retailer visuals are collected."
                image={asset("retail_shelf_visual")?.url}
                evidence="retail"
                sourceKind={asset("retail_shelf_visual")?.source_kind}
              />
            </div>
          </div>

          <div className="rounded-[2.5rem] border border-amber-100/15 bg-gradient-to-r from-amber-100/10 to-white/[0.04] p-6">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.25em] text-amber-100/55">
                  Three.js ready
                </p>
                <h3 className="mt-2 text-3xl font-black">Next: turn these assets into 3D planes and animated objects</h3>
                <p className="mt-3 max-w-3xl text-sm leading-6 text-white/60">
                  The registry now gives us stable URLs for image textures. Step 17E will use
                  these images inside a real Three.js scene with camera movement, animated trucks,
                  ingredient particles, conveyor motion, and hover evidence panels.
                </p>
              </div>

              <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-black/25 p-4">
                <Store className="text-amber-200" />
                <ShoppingBag className="text-amber-200" />
                <Truck className="text-amber-200" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}