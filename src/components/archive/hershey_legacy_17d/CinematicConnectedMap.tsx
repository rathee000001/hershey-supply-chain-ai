"use client";

import { useMemo, useState } from "react";
import {
  Beef,
  Boxes,
  Factory,
  Info,
  Milk,
  PackageCheck,
  ShoppingBag,
  Sprout,
  Store,
  Truck,
  Wheat,
  Waves,
} from "lucide-react";
import type {
  CostBreakdown,
  EvidencePreview,
  GraphPayload,
  IngredientCard,
  SupplierCard,
} from "@/lib/hershey/enrichedArtifacts";

type CinematicConnectedMapProps = {
  ingredients: IngredientCard[];
  suppliers: SupplierCard[];
  graph: GraphPayload;
  costBreakdown: CostBreakdown;
};

type FlowNode = {
  id: string;
  title: string;
  subtitle: string;
  stage: string;
  x: number;
  y: number;
  icon: React.ElementType;
  packet?: string;
  evidenceCount: number;
  safeNote: string;
  evidencePreview: EvidencePreview[];
  tone: "origin" | "supplier" | "factory" | "process" | "distribution" | "retail";
};

type FlowEdge = {
  id: string;
  from: string;
  to: string;
  label: string;
};

function countIngredientEvidence(ingredients: IngredientCard[], packet: string): number {
  return ingredients
    .filter((item) => item.packet === packet)
    .reduce((sum, item) => sum + (item.approved_evidence_count ?? 0), 0);
}

function evidenceForIngredientPacket(ingredients: IngredientCard[], packet: string): EvidencePreview[] {
  return ingredients
    .filter((item) => item.packet === packet)
    .flatMap((item) => item.approved_evidence_preview || [])
    .slice(0, 5);
}

function supplierByName(suppliers: SupplierCard[], nameIncludes: string): SupplierCard | undefined {
  return suppliers.find((supplier) =>
    String(supplier.safe_display_name || "").toLowerCase().includes(nameIncludes.toLowerCase())
  );
}

function supplierEvidenceCount(suppliers: SupplierCard[], nameIncludes: string): number {
  return supplierByName(suppliers, nameIncludes)?.approved_evidence_count ?? 0;
}

function supplierEvidencePreview(suppliers: SupplierCard[], nameIncludes: string): EvidencePreview[] {
  return supplierByName(suppliers, nameIncludes)?.approved_evidence_preview?.slice(0, 5) ?? [];
}

function supplierSafeNote(suppliers: SupplierCard[], nameIncludes: string): string {
  return (
    supplierByName(suppliers, nameIncludes)?.safe_website_wording ||
    "Displayed as public-evidence supply-chain context only."
  );
}

function toneClasses(tone: FlowNode["tone"]): string {
  const map = {
    origin: "border-emerald-200/20 bg-emerald-200/[0.07]",
    supplier: "border-amber-200/20 bg-amber-200/[0.08]",
    factory: "border-orange-200/25 bg-orange-300/[0.09]",
    process: "border-purple-200/20 bg-purple-200/[0.07]",
    distribution: "border-sky-200/20 bg-sky-200/[0.07]",
    retail: "border-pink-200/20 bg-pink-200/[0.07]",
  };

  return map[tone];
}

function pathBetween(from: FlowNode, to: FlowNode): string {
  const startX = from.x + 6;
  const startY = from.y + 4;
  const endX = to.x - 6;
  const endY = to.y + 4;
  const midX = (startX + endX) / 2;

  return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`;
}

function DetailPanel({ node }: { node: FlowNode }) {
  return (
    <div className="rounded-[1.75rem] border border-amber-100/20 bg-[#160706]/95 p-5 shadow-2xl backdrop-blur">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-100/50">
            {node.stage}
          </p>
          <h3 className="mt-2 text-xl font-black text-white">{node.title}</h3>
        </div>
        <Info className="shrink-0 text-amber-200" size={20} />
      </div>

      <p className="text-sm leading-6 text-white/65">{node.subtitle}</p>

      <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-100/50">
          Approved evidence
        </p>
        <p className="mt-1 text-3xl font-black text-amber-50">{node.evidenceCount}</p>
      </div>

      <p className="mt-4 text-xs leading-5 text-amber-100/65">{node.safeNote}</p>

      {node.evidencePreview.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-white/35">
            Evidence preview
          </p>
          {node.evidencePreview.slice(0, 3).map((item) => (
            <div key={item.evidence_id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
              <p className="line-clamp-2 text-xs leading-5 text-white/55">
                {item.audited_safe_website_wording || item.evidence_text_preview || item.file_name}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CinematicConnectedMap({
  ingredients,
  suppliers,
  graph,
  costBreakdown,
}: CinematicConnectedMapProps) {
  const [activeNodeId, setActiveNodeId] = useState<string>("hershey_factory");

  const nodes = useMemo<FlowNode[]>(() => {
    const sugarEvidence = countIngredientEvidence(ingredients, "sugar");
    const dairyEvidence = countIngredientEvidence(ingredients, "dairy_milk_skim_milk_milk_fat");
    const cocoaEvidence = countIngredientEvidence(ingredients, "cocoa_chocolate_cocoa_butter");
    const minorEvidence =
      countIngredientEvidence(ingredients, "soy_lecithin") +
      countIngredientEvidence(ingredients, "pgpr") +
      countIngredientEvidence(ingredients, "natural_flavor");
    const packagingEvidence = countIngredientEvidence(ingredients, "packaging_wrapper");
    const retailEvidence = graph.nodes
      .filter((node) =>
        String(node.label || node.id || "").toLowerCase().includes("retail")
      )
      .reduce((sum, node) => sum + (node.enrichedApprovedEvidenceCount ?? 0), 0);

    return [
      {
        id: "dairy_farm",
        title: "Cow / Dairy Farm",
        subtitle: "Dairy begins as farm-level milk context before supplier movement.",
        stage: "Dairy origin",
        x: 6,
        y: 12,
        icon: Milk,
        packet: "dairy_milk_skim_milk_milk_fat",
        evidenceCount: dairyEvidence,
        safeNote: "Dairy origin is modeled public-evidence context.",
        evidencePreview: evidenceForIngredientPacket(ingredients, "dairy_milk_skim_milk_milk_fat"),
        tone: "origin",
      },
      {
        id: "land_olakes",
        title: "Land O'Lakes",
        subtitle: "Company-level dairy supplier context.",
        stage: "Dairy supplier",
        x: 27,
        y: 12,
        icon: Boxes,
        evidenceCount: supplierEvidenceCount(suppliers, "Land"),
        safeNote: supplierSafeNote(suppliers, "Land"),
        evidencePreview: supplierEvidencePreview(suppliers, "Land"),
        tone: "supplier",
      },
      {
        id: "sugar_origin",
        title: "Sugarcane / Beet",
        subtitle: "Agricultural sugar origin and sourcing context.",
        stage: "Sugar origin",
        x: 6,
        y: 38,
        icon: Wheat,
        packet: "sugar",
        evidenceCount: sugarEvidence,
        safeNote: "Sugar origin is public-evidence sourcing context.",
        evidencePreview: evidenceForIngredientPacket(ingredients, "sugar"),
        tone: "origin",
      },
      {
        id: "asr_refiner",
        title: "ASR / Domino Context",
        subtitle: "Company-level sugar supplier / refiner context.",
        stage: "Sugar supplier",
        x: 27,
        y: 38,
        icon: Factory,
        evidenceCount: supplierEvidenceCount(suppliers, "ASR"),
        safeNote: supplierSafeNote(suppliers, "ASR"),
        evidencePreview: supplierEvidencePreview(suppliers, "ASR"),
        tone: "supplier",
      },
      {
        id: "cocoa_origin",
        title: "Cocoa Origin",
        subtitle: "Cocoa, chocolate, and cocoa butter evidence context.",
        stage: "Cocoa origin",
        x: 6,
        y: 64,
        icon: Sprout,
        packet: "cocoa_chocolate_cocoa_butter",
        evidenceCount: cocoaEvidence,
        safeNote: "Cocoa origin is modeled public-evidence context.",
        evidencePreview: evidenceForIngredientPacket(ingredients, "cocoa_chocolate_cocoa_butter"),
        tone: "origin",
      },
      {
        id: "barry_callebaut",
        title: "Barry Callebaut",
        subtitle: "Company-level cocoa/chocolate supplier context.",
        stage: "Cocoa supplier",
        x: 27,
        y: 64,
        icon: Boxes,
        evidenceCount: supplierEvidenceCount(suppliers, "Barry"),
        safeNote: supplierSafeNote(suppliers, "Barry"),
        evidencePreview: supplierEvidencePreview(suppliers, "Barry"),
        tone: "supplier",
      },
      {
        id: "minor_ingredients",
        title: "Minor Ingredients",
        subtitle: "Soy lecithin, PGPR, and natural flavor function evidence.",
        stage: "Ingredient function",
        x: 27,
        y: 82,
        icon: Waves,
        evidenceCount: minorEvidence,
        safeNote: "Minor ingredient suppliers remain unknown or benchmark-only unless direct supplier evidence exists.",
        evidencePreview: [
          ...evidenceForIngredientPacket(ingredients, "soy_lecithin"),
          ...evidenceForIngredientPacket(ingredients, "pgpr"),
          ...evidenceForIngredientPacket(ingredients, "natural_flavor"),
        ].slice(0, 5),
        tone: "supplier",
      },
      {
        id: "hershey_factory",
        title: "Hershey Factory Intake",
        subtitle: "Ingredient streams converge into the modeled Hershey process.",
        stage: "Convergence point",
        x: 52,
        y: 38,
        icon: Factory,
        evidenceCount: graph.nodes.length,
        safeNote: "Factory process is a modeled public-evidence visualization, not proprietary line data.",
        evidencePreview: [],
        tone: "factory",
      },
      {
        id: "mix_form_conveyor",
        title: "Mix → Form → Conveyor",
        subtitle: "Ingredients combine, chocolate forms, and bars move along a modeled conveyor.",
        stage: "Modeled process",
        x: 68,
        y: 38,
        icon: Waves,
        evidenceCount: graph.edges.length,
        safeNote: "Process animation is explanatory and does not claim proprietary Hershey line details.",
        evidencePreview: [],
        tone: "process",
      },
      {
        id: "wrapper_packaging",
        title: "Wrapper / Packaging",
        subtitle: "Bars are wrapped and packed into retail-ready flow.",
        stage: "Packaging",
        x: 82,
        y: 38,
        icon: PackageCheck,
        packet: "packaging_wrapper",
        evidenceCount: packagingEvidence,
        safeNote: "Packaging evidence is benchmark and sourcing context unless exact wrapper supplier proof exists.",
        evidencePreview: evidenceForIngredientPacket(ingredients, "packaging_wrapper"),
        tone: "process",
      },
      {
        id: "distribution",
        title: "Warehouse / Truck",
        subtitle: "Packed bars move through warehouse and distribution context.",
        stage: "Distribution",
        x: 68,
        y: 66,
        icon: Truck,
        evidenceCount: supplierEvidenceCount(suppliers, "McLane"),
        safeNote: supplierSafeNote(suppliers, "McLane"),
        evidencePreview: supplierEvidencePreview(suppliers, "McLane"),
        tone: "distribution",
      },
      {
        id: "retail_shelf",
        title: "Retail Shelf",
        subtitle: "Retailer visuals stay general until final retailer assets are added.",
        stage: "Retail",
        x: 82,
        y: 66,
        icon: Store,
        evidenceCount: retailEvidence,
        safeNote: "Retail price evidence is page/store/date dependent and not margin evidence.",
        evidencePreview: [],
        tone: "retail",
      },
      {
        id: "consumer_purchase",
        title: "Consumer Purchase",
        subtitle: `Observed retail base price from JSON: $${costBreakdown.retail_price?.base_usd_per_bar ?? "—"}.`,
        stage: "Consumer",
        x: 94,
        y: 66,
        icon: ShoppingBag,
        evidenceCount: retailEvidence,
        safeNote: "Consumer purchase is the end of the modeled commercial flow.",
        evidencePreview: [],
        tone: "retail",
      },
    ];
  }, [ingredients, suppliers, graph, costBreakdown]);

  const nodeById = useMemo(() => {
    return new Map(nodes.map((node) => [node.id, node]));
  }, [nodes]);

  const edges: FlowEdge[] = [
    { id: "dairy_to_land", from: "dairy_farm", to: "land_olakes", label: "milk stream" },
    { id: "land_to_hershey", from: "land_olakes", to: "hershey_factory", label: "refrigerated movement" },
    { id: "sugar_to_asr", from: "sugar_origin", to: "asr_refiner", label: "refining" },
    { id: "asr_to_hershey", from: "asr_refiner", to: "hershey_factory", label: "sugar input" },
    { id: "cocoa_to_barry", from: "cocoa_origin", to: "barry_callebaut", label: "processing" },
    { id: "barry_to_hershey", from: "barry_callebaut", to: "hershey_factory", label: "cocoa/chocolate input" },
    { id: "minor_to_hershey", from: "minor_ingredients", to: "hershey_factory", label: "functional ingredients" },
    { id: "hershey_to_process", from: "hershey_factory", to: "mix_form_conveyor", label: "combine" },
    { id: "process_to_pack", from: "mix_form_conveyor", to: "wrapper_packaging", label: "pack" },
    { id: "pack_to_distribution", from: "wrapper_packaging", to: "distribution", label: "cases/pallets" },
    { id: "distribution_to_shelf", from: "distribution", to: "retail_shelf", label: "retail delivery" },
    { id: "shelf_to_consumer", from: "retail_shelf", to: "consumer_purchase", label: "purchase" },
  ];

  const activeNode = nodeById.get(activeNodeId) || nodeById.get("hershey_factory") || nodes[0];

  return (
    <section className="relative overflow-hidden bg-[#080202] px-6 py-20">
      <style>{`
        @keyframes hersheyDash {
          from { stroke-dashoffset: 48; }
          to { stroke-dashoffset: 0; }
        }
        @keyframes hersheyPulse {
          0%, 100% { transform: scale(1); opacity: .7; }
          50% { transform: scale(1.08); opacity: 1; }
        }
        .hershey-flow-path {
          stroke-dasharray: 12 12;
          animation: hersheyDash 2.6s linear infinite;
        }
        .hershey-node-pulse {
          animation: hersheyPulse 3.4s ease-in-out infinite;
        }
      `}</style>

      <div className="absolute inset-0 opacity-60">
        <div className="absolute left-0 top-0 h-[32rem] w-[32rem] rounded-full bg-[#5c1e13] blur-3xl" />
        <div className="absolute bottom-20 right-0 h-[36rem] w-[36rem] rounded-full bg-amber-300/10 blur-3xl" />
        <div className="absolute left-1/2 top-1/3 h-[24rem] w-[24rem] rounded-full bg-red-900/30 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl">
        <div className="mb-10 grid gap-8 lg:grid-cols-[0.8fr_0.55fr] lg:items-end">
          <div>
            <p className="inline-flex rounded-full border border-amber-200/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
              Premium connected visual system
            </p>
            <h2 className="mt-5 text-4xl font-black leading-tight tracking-tight md:text-6xl">
              A cinematic supply-chain map with evidence-aware nodes
            </h2>
            <p className="mt-5 max-w-4xl text-lg leading-8 text-white/65">
              Hover or click each stage to reveal the evidence-backed context. This layout becomes
              the foundation for the final animated Hershey supply-chain experience.
            </p>
          </div>

          <div className="rounded-[2rem] border border-amber-100/15 bg-white/[0.06] p-5">
            <p className="text-xs font-black uppercase tracking-[0.25em] text-amber-100/50">
              Map summary
            </p>
            <div className="mt-4 grid grid-cols-3 gap-3 text-center">
              <div className="rounded-2xl bg-black/25 p-3">
                <p className="text-2xl font-black">{nodes.length}</p>
                <p className="text-xs text-white/45">visual nodes</p>
              </div>
              <div className="rounded-2xl bg-black/25 p-3">
                <p className="text-2xl font-black">{edges.length}</p>
                <p className="text-xs text-white/45">flow paths</p>
              </div>
              <div className="rounded-2xl bg-black/25 p-3">
                <p className="text-2xl font-black">{graph.nodes.length}</p>
                <p className="text-xs text-white/45">artifact nodes</p>
              </div>
            </div>
          </div>
        </div>

        <div className="hidden rounded-[2.5rem] border border-white/10 bg-white/[0.04] p-6 shadow-2xl xl:grid xl:grid-cols-[1fr_360px] xl:gap-6">
          <div className="relative h-[760px] overflow-hidden rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_center,#2b0c08_0%,#120504_60%,#070202_100%)]">
            <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <linearGradient id="flowGradient" x1="0" x2="1" y1="0" y2="0">
                  <stop offset="0%" stopColor="rgba(252, 211, 77, 0.15)" />
                  <stop offset="50%" stopColor="rgba(252, 211, 77, 0.75)" />
                  <stop offset="100%" stopColor="rgba(255, 255, 255, 0.2)" />
                </linearGradient>
              </defs>

              {edges.map((edge) => {
                const from = nodeById.get(edge.from);
                const to = nodeById.get(edge.to);
                if (!from || !to) return null;

                return (
                  <path
                    key={edge.id}
                    d={pathBetween(from, to)}
                    fill="none"
                    stroke="url(#flowGradient)"
                    strokeWidth="0.45"
                    strokeLinecap="round"
                    className="hershey-flow-path"
                  />
                );
              })}
            </svg>

            {nodes.map((node) => {
              const Icon = node.icon;
              const active = node.id === activeNode?.id;

              return (
                <button
                  key={node.id}
                  type="button"
                  onMouseEnter={() => setActiveNodeId(node.id)}
                  onClick={() => setActiveNodeId(node.id)}
                  className={`absolute w-[168px] -translate-x-1/2 -translate-y-1/2 rounded-[1.4rem] border p-4 text-left shadow-2xl backdrop-blur transition duration-500 hover:z-20 hover:scale-105 ${toneClasses(
                    node.tone
                  )} ${active ? "z-20 scale-105 ring-2 ring-amber-200/40" : "z-10"}`}
                  style={{
                    left: `${node.x}%`,
                    top: `${node.y}%`,
                  }}
                >
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <Icon className={active ? "text-amber-100 hershey-node-pulse" : "text-amber-200"} size={22} />
                    <span className="rounded-full bg-black/30 px-2 py-1 text-[10px] font-black text-amber-100/70">
                      {node.evidenceCount}
                    </span>
                  </div>
                  <p className="text-sm font-black leading-tight text-white">{node.title}</p>
                  <p className="mt-1 line-clamp-2 text-[11px] leading-4 text-white/55">{node.stage}</p>
                </button>
              );
            })}

            <div className="absolute left-1/2 top-[38%] -z-0 h-52 w-52 -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber-200/10 blur-3xl" />
          </div>

          <div className="space-y-4">
            {activeNode && <DetailPanel node={activeNode} />}

            <div className="rounded-[1.75rem] border border-white/10 bg-black/20 p-5">
              <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-100/50">
                Cost pulse
              </p>
              <p className="mt-3 text-2xl font-black">
                {costBreakdown.physical_cost?.base_cents_per_bar?.toFixed(2) ?? "—"}¢{" "}
                <span className="text-white/25">→</span>{" "}
                ${costBreakdown.retail_price?.base_usd_per_bar?.toFixed(2) ?? "—"}
              </p>
              <p className="mt-3 text-xs leading-5 text-white/50">
                Benchmark physical cost to observed retail price. This is not internal Hershey
                cost, margin, or profit.
              </p>
            </div>
          </div>
        </div>

        <div className="grid gap-4 xl:hidden">
          {nodes.map((node) => {
            const Icon = node.icon;
            return (
              <button
                key={node.id}
                type="button"
                onClick={() => setActiveNodeId(node.id)}
                className={`rounded-[1.5rem] border p-5 text-left ${toneClasses(node.tone)}`}
              >
                <Icon className="mb-3 text-amber-200" size={24} />
                <p className="text-lg font-black">{node.title}</p>
                <p className="mt-1 text-sm text-white/55">{node.subtitle}</p>
                <p className="mt-3 text-xs font-bold text-amber-100/60">
                  {node.evidenceCount} approved evidence links
                </p>
              </button>
            );
          })}
          {activeNode && <DetailPanel node={activeNode} />}
        </div>
      </div>
    </section>
  );
}