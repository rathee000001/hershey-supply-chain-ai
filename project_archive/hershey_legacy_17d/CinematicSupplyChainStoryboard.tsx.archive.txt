"use client";

import {
  ArrowRight,
  Boxes,
  Factory,
  Milk,
  PackageCheck,
  ShoppingBag,
  Sprout,
  Store,
  Truck,
  Waves,
  Wheat,
} from "lucide-react";
import type {
  CostBreakdown,
  GraphPayload,
  IngredientCard,
  SupplierCard,
} from "@/lib/hershey/enrichedArtifacts";

type StoryboardProps = {
  ingredients: IngredientCard[];
  suppliers: SupplierCard[];
  graph: GraphPayload;
  costBreakdown: CostBreakdown;
};

function evidenceCountForPacket(ingredients: IngredientCard[], packet: string): number {
  return ingredients
    .filter((item) => item.packet === packet)
    .reduce((sum, item) => sum + (item.approved_evidence_count ?? 0), 0);
}

function supplierEvidence(suppliers: SupplierCard[], nameIncludes: string): number {
  const match = suppliers.find((supplier) =>
    String(supplier.safe_display_name || "")
      .toLowerCase()
      .includes(nameIncludes.toLowerCase())
  );

  return match?.approved_evidence_count ?? 0;
}

function MiniNode({
  title,
  subtitle,
  Icon,
  evidence,
}: {
  title: string;
  subtitle: string;
  Icon: React.ElementType;
  evidence?: number;
}) {
  return (
    <div className="group relative overflow-hidden rounded-[1.75rem] border border-amber-100/10 bg-white/[0.07] p-5 shadow-2xl backdrop-blur transition duration-500 hover:-translate-y-1 hover:border-amber-200/30 hover:bg-white/[0.1]">
      <div className="absolute -right-10 -top-10 h-28 w-28 rounded-full bg-amber-200/10 blur-2xl transition group-hover:bg-amber-200/20" />
      <Icon className="relative mb-4 text-amber-200" size={26} />
      <p className="relative text-lg font-black text-white">{title}</p>
      <p className="relative mt-2 min-h-10 text-sm leading-5 text-white/60">{subtitle}</p>
      {typeof evidence === "number" && (
        <p className="relative mt-4 rounded-full border border-white/10 bg-black/20 px-3 py-2 text-xs font-bold text-amber-100/70">
          {evidence} approved evidence links
        </p>
      )}
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="hidden items-center justify-center text-amber-200/60 lg:flex">
      <ArrowRight size={28} />
    </div>
  );
}

export default function CinematicSupplyChainStoryboard({
  ingredients,
  suppliers,
  graph,
  costBreakdown,
}: StoryboardProps) {
  const sugarEvidence = evidenceCountForPacket(ingredients, "sugar");
  const dairyEvidence = evidenceCountForPacket(ingredients, "dairy_milk_skim_milk_milk_fat");
  const cocoaEvidence = evidenceCountForPacket(ingredients, "cocoa_chocolate_cocoa_butter");
  const minorEvidence =
    evidenceCountForPacket(ingredients, "soy_lecithin") +
    evidenceCountForPacket(ingredients, "pgpr") +
    evidenceCountForPacket(ingredients, "natural_flavor");
  const packagingEvidence = evidenceCountForPacket(ingredients, "packaging_wrapper");

  const asrEvidence = supplierEvidence(suppliers, "ASR");
  const barryEvidence = supplierEvidence(suppliers, "Barry");
  const landEvidence = supplierEvidence(suppliers, "Land");
  const mclaneEvidence = supplierEvidence(suppliers, "McLane");

  const physicalBase = costBreakdown.physical_cost?.base_cents_per_bar;
  const retailBase = costBreakdown.retail_price?.base_usd_per_bar;

  return (
    <section className="relative overflow-hidden border-y border-white/10 bg-[#090202] px-6 py-20">
      <div className="absolute inset-0 opacity-40">
        <div className="absolute left-1/4 top-10 h-96 w-96 rounded-full bg-[#7a2b16] blur-3xl" />
        <div className="absolute bottom-10 right-1/4 h-96 w-96 rounded-full bg-amber-300/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl">
        <div className="mb-12 max-w-4xl">
          <p className="inline-flex rounded-full border border-amber-200/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
            Cinematic Supply Chain Storyboard
          </p>
          <h2 className="mt-5 text-4xl font-black tracking-tight md:text-6xl">
            From farm inputs to shelf purchase
          </h2>
          <p className="mt-5 text-lg leading-8 text-white/65">
            This is the structure for the final premium animation. Every count below is loaded from
            enriched JSON artifacts; the upcoming 3D layer will animate the same evidence-backed flow.
          </p>
        </div>

        <div className="space-y-8">
          <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Milk className="text-amber-200" />
              <h3 className="text-2xl font-black">Dairy Flow</h3>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_60px_1fr_60px_1fr_60px_1fr]">
              <MiniNode title="Cow / Dairy Farm" subtitle="Milk source context starts at farm level." Icon={Milk} evidence={dairyEvidence} />
              <FlowArrow />
              <MiniNode title="Land O'Lakes" subtitle="Company-level dairy supplier context." Icon={Boxes} evidence={landEvidence} />
              <FlowArrow />
              <MiniNode title="Refrigerated Truck" subtitle="Modeled cold-chain movement toward Hershey." Icon={Truck} />
              <FlowArrow />
              <MiniNode title="Hershey Intake" subtitle="Dairy enters the modeled chocolate process." Icon={Factory} />
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Wheat className="text-amber-200" />
              <h3 className="text-2xl font-black">Sugar Flow</h3>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_60px_1fr_60px_1fr_60px_1fr]">
              <MiniNode title="Sugarcane / Beet" subtitle="Agricultural origin and sourcing context." Icon={Wheat} evidence={sugarEvidence} />
              <FlowArrow />
              <MiniNode title="Mill / Refiner" subtitle="Sugar is processed before industrial shipment." Icon={Factory} />
              <FlowArrow />
              <MiniNode title="ASR / Domino Context" subtitle="Company-level sugar supplier relationship." Icon={Boxes} evidence={asrEvidence} />
              <FlowArrow />
              <MiniNode title="Hershey Intake" subtitle="Sugar stream joins chocolate production." Icon={Truck} />
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Sprout className="text-amber-200" />
              <h3 className="text-2xl font-black">Cocoa / Chocolate Flow</h3>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_60px_1fr_60px_1fr_60px_1fr]">
              <MiniNode title="Cocoa Origin" subtitle="Cocoa, cocoa butter, and chocolate evidence context." Icon={Sprout} evidence={cocoaEvidence} />
              <FlowArrow />
              <MiniNode title="Processor" subtitle="Chocolate/cocoa processing before Hershey." Icon={Waves} />
              <FlowArrow />
              <MiniNode title="Barry Callebaut" subtitle="Company-level cocoa/chocolate supplier context." Icon={Boxes} evidence={barryEvidence} />
              <FlowArrow />
              <MiniNode title="Hershey Chocolate Process" subtitle="Cocoa stream joins the modeled recipe process." Icon={Factory} />
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Factory className="text-amber-200" />
              <h3 className="text-2xl font-black">Inside Hershey: Combine → Form → Pack</h3>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_60px_1fr_60px_1fr_60px_1fr]">
              <MiniNode title="Ingredient Merge" subtitle="Sugar, dairy, cocoa, and minor ingredients combine." Icon={Factory} evidence={minorEvidence} />
              <FlowArrow />
              <MiniNode title="Chocolate Formation" subtitle="Modeled chocolate process and bar shaping." Icon={Waves} />
              <FlowArrow />
              <MiniNode title="Conveyor Line" subtitle="Bars move through the modeled production sequence." Icon={ArrowRight} />
              <FlowArrow />
              <MiniNode title="Wrapper / Packaging" subtitle="Bars are packed into retail-ready units." Icon={PackageCheck} evidence={packagingEvidence} />
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/[0.04] p-6">
            <div className="mb-5 flex items-center gap-3">
              <Store className="text-amber-200" />
              <h3 className="text-2xl font-black">Distribution → Retail → Consumer</h3>
            </div>
            <div className="grid gap-4 lg:grid-cols-[1fr_60px_1fr_60px_1fr_60px_1fr]">
              <MiniNode title="Warehouse / DC" subtitle="Modeled warehouse and distribution node." Icon={Boxes} evidence={graph.nodes.length} />
              <FlowArrow />
              <MiniNode title="McLane / Carrier Context" subtitle="Downstream distribution context." Icon={Truck} evidence={mclaneEvidence} />
              <FlowArrow />
              <MiniNode title="Retail Shelf" subtitle="Retailers shown generally until final retailer assets are added." Icon={Store} />
              <FlowArrow />
              <MiniNode title="Consumer Purchase" subtitle={`Retail base price loaded from JSON: $${retailBase ?? "—"}`} Icon={ShoppingBag} />
            </div>
          </div>
        </div>

        <div className="mt-10 rounded-[2rem] border border-amber-200/20 bg-gradient-to-r from-amber-200/10 to-white/[0.04] p-6">
          <p className="text-sm font-black uppercase tracking-[0.25em] text-amber-100/70">
            Cost pulse foundation
          </p>
          <p className="mt-3 text-3xl font-black">
            Physical base cost: {typeof physicalBase === "number" ? `${physicalBase.toFixed(2)}¢` : "—"}{" "}
            <span className="text-white/30">→</span>{" "}
            Retail base price: {typeof retailBase === "number" ? `$${retailBase.toFixed(2)}` : "—"}
          </p>
          <p className="mt-3 max-w-4xl text-sm leading-6 text-white/60">
            This line becomes the animated cost pulse in the final cinematic version. It remains
            benchmark-only and must not be presented as Hershey internal cost or margin.
          </p>
        </div>
      </div>
    </section>
  );
}