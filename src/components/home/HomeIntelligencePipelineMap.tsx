"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Brain,
  Calculator,
  CheckCircle2,
  FileText,
  GitBranch,
  MousePointer2,
  Package,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useMemo, useState } from "react";

type PipelineStep = {
  id: string;
  number: string;
  eyebrow: string;
  title: string;
  shortTitle: string;
  detail: string;
  icon: LucideIcon;
  accent: string;
  soft: string;
  border: string;
};

type RoutePath = {
  id: string;
  d: string;
  accent: string;
  soft: string;
};

const pipelineSteps: PipelineStep[] = [
  {
    id: "sources",
    number: "01",
    eyebrow: "RAW INPUT",
    title: "Raw public sources",
    shortTitle: "Sources",
    detail:
      "The platform begins with public materials and study references. Decorative visuals do not create claims; approved display artifacts control what the interface can say.",
    icon: FileText,
    accent: "#1f62ff",
    soft: "rgba(31,98,255,0.10)",
    border: "rgba(31,98,255,0.38)",
  },
  {
    id: "parser",
    number: "02",
    eyebrow: "MEMORY",
    title: "Parser + OCR memory",
    shortTitle: "Parser",
    detail:
      "Parser and OCR memory organize extracted text and visual notes. This layer supports the research workflow without directly publishing website claims.",
    icon: Search,
    accent: "#d6a526",
    soft: "rgba(216,165,38,0.12)",
    border: "rgba(216,165,38,0.42)",
  },
  {
    id: "rag",
    number: "03",
    eyebrow: "INDEX",
    title: "RAG/vector evidence index",
    shortTitle: "RAG Index",
    detail:
      "The retrieval layer helps reason across source fragments. Frontend language remains gated by approved public artifacts rather than raw retrieval output.",
    icon: Brain,
    accent: "#9b5cf6",
    soft: "rgba(155,92,246,0.11)",
    border: "rgba(155,92,246,0.38)",
  },
  {
    id: "audit",
    number: "04",
    eyebrow: "CONTROL",
    title: "Evidence audit",
    shortTitle: "Audit",
    detail:
      "The audit layer keeps the project professor-safe and Hershey-safe by separating public evidence, methodology statements, and decorative interface elements.",
    icon: ShieldCheck,
    accent: "#0f9f6e",
    soft: "rgba(15,159,110,0.11)",
    border: "rgba(15,159,110,0.38)",
  },
  {
    id: "packets",
    number: "05",
    eyebrow: "STRUCTURE",
    title: "Supplier/ingredient packets",
    shortTitle: "Packets",
    detail:
      "Supplier and ingredient packets are structured for display from approved artifacts. This component does not hardcode supplier facts or claim values.",
    icon: Package,
    accent: "#7b2a15",
    soft: "rgba(123,42,21,0.10)",
    border: "rgba(123,42,21,0.38)",
  },
  {
    id: "cost",
    number: "06",
    eyebrow: "BENCHMARK",
    title: "Cost model artifacts",
    shortTitle: "Cost",
    detail:
      "Cost artifacts are treated as benchmark study outputs. They are not Hershey internal costs, invoices, margins, or profit calculations.",
    icon: Calculator,
    accent: "#f59e0b",
    soft: "rgba(245,158,11,0.12)",
    border: "rgba(245,158,11,0.40)",
  },
  {
    id: "frontend",
    number: "07",
    eyebrow: "INTERFACE",
    title: "3D cinematic frontend",
    shortTitle: "Frontend",
    detail:
      "The final layer converts approved study outputs into interactive pages, cinematic motion, and evidence-safe interface components.",
    icon: Sparkles,
    accent: "#38bdf8",
    soft: "rgba(56,189,248,0.12)",
    border: "rgba(56,189,248,0.42)",
  },
];

const routePaths: RoutePath[] = [
  {
    id: "sources-parser",
    d: "M 170 105 C 285 105, 335 105, 500 105",
    accent: "#1f62ff",
    soft: "rgba(31,98,255,0.48)",
  },
  {
    id: "parser-rag",
    d: "M 500 105 C 665 105, 715 105, 830 105",
    accent: "#d6a526",
    soft: "rgba(216,165,38,0.52)",
  },
  {
    id: "rag-audit",
    d: "M 830 105 C 830 210, 640 235, 500 310",
    accent: "#9b5cf6",
    soft: "rgba(155,92,246,0.48)",
  },
  {
    id: "audit-packets",
    d: "M 500 310 C 360 385, 170 410, 170 515",
    accent: "#0f9f6e",
    soft: "rgba(15,159,110,0.48)",
  },
  {
    id: "packets-cost",
    d: "M 170 515 C 285 515, 335 515, 500 515",
    accent: "#7b2a15",
    soft: "rgba(123,42,21,0.46)",
  },
  {
    id: "cost-frontend",
    d: "M 500 515 C 665 515, 715 515, 830 515",
    accent: "#38bdf8",
    soft: "rgba(56,189,248,0.52)",
  },
];

export default function HomeIntelligencePipelineMap() {
  const prefersReducedMotion = useReducedMotion();
  const [activeId, setActiveId] = useState(pipelineSteps[0].id);

  const activeStep = useMemo(
    () => pipelineSteps.find((step) => step.id === activeId) ?? pipelineSteps[0],
    [activeId],
  );

  const activeIndex = Math.max(0, pipelineSteps.findIndex((step) => step.id === activeStep.id));
  const ActiveIcon = activeStep.icon;

  const getStep = (id: string) => pipelineSteps.find((step) => step.id === id) ?? pipelineSteps[0];

  return (
    <section
      className="px-6 pb-20"
      data-home-intelligence-pipeline="contained-grid-three-one-three-center-pulsing-connectors"
    >
      <div className="mx-auto max-w-7xl overflow-hidden rounded-[2.5rem] border border-[#2a0805]/10 bg-white/94 p-6 shadow-2xl shadow-[#3a160d]/8 backdrop-blur-xl md:p-8">
        <div className="grid gap-8 lg:grid-cols-[0.82fr_1.18fr] lg:items-start">
          <motion.div
            initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
            whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          >
            <p className="text-[11px] font-black uppercase tracking-[0.28em] text-[#1f62ff]">
              Intelligence Pipeline
            </p>

            <h2 className="mt-5 text-5xl font-black leading-[0.95] tracking-tight text-[#09040a] md:text-6xl">
              From raw public inputs to evidence-safe interface.
            </h2>

            <p className="mt-6 max-w-2xl text-base font-medium leading-8 text-[#51433d]">
              Hover through the connected pipeline map. Each node stays clean and visual;
              the active explanation appears here.
            </p>

            <motion.div
              key={activeStep.id}
              className="mt-8 rounded-[2rem] border p-6 shadow-xl shadow-[#3a160d]/5"
              style={{
                borderColor: activeStep.border,
                background: `linear-gradient(135deg, ${activeStep.soft}, rgba(255,250,243,0.92))`,
              }}
              initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
              animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
              transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="flex items-start gap-4">
                <motion.div
                  className="grid h-16 w-16 shrink-0 place-items-center rounded-3xl border bg-white shadow-sm"
                  style={{ borderColor: activeStep.border, color: activeStep.accent }}
                  animate={
                    prefersReducedMotion
                      ? undefined
                      : { y: [0, -4, 0], rotate: [0, -2, 2, 0] }
                  }
                  transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}
                >
                  <ActiveIcon size={30} />
                </motion.div>

                <div>
                  <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                    {activeStep.eyebrow} · {activeStep.number}
                  </p>
                  <h3 className="mt-2 text-2xl font-black leading-tight text-[#09040a]">
                    {activeStep.title}
                  </h3>
                  <p className="mt-3 text-sm font-semibold leading-7 text-[#51433d]">
                    {activeStep.detail}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                <span className="inline-flex items-center gap-2 rounded-full bg-[#2a0805] px-4 py-3 text-xs font-black uppercase tracking-[0.16em] text-white">
                  <CheckCircle2 size={15} />
                  JSON-first
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-[#2a0805]/10 bg-white px-4 py-3 text-xs font-black uppercase tracking-[0.16em] text-[#2a0805]">
                  <GitBranch size={15} />
                  Audited flow
                </span>
              </div>
            </motion.div>
          </motion.div>

          <motion.div
            className="relative min-h-[720px] overflow-hidden rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/88 p-5 shadow-inner shadow-slate-200/60"
            initial={prefersReducedMotion ? false : { opacity: 0, x: 24 }}
            whileInView={prefersReducedMotion ? undefined : { opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.58, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="pointer-events-none absolute inset-0 rounded-[2.25rem] bg-[radial-gradient(circle_at_28%_18%,rgba(31,98,255,0.08),transparent_24%),radial-gradient(circle_at_76%_72%,rgba(216,165,51,0.14),transparent_26%)]" />

            <div className="relative z-10 mx-auto hidden h-[620px] w-full max-w-[760px] sm:block">
              <svg
                className="pointer-events-none absolute inset-0 z-0 h-full w-full"
                viewBox="0 0 1000 620"
                fill="none"
                aria-hidden="true"
                preserveAspectRatio="none"
              >
                <defs>
                  <filter id="containedGridPipelinePulseGlow" x="-16%" y="-30%" width="132%" height="160%">
                    <feGaussianBlur stdDeviation="3.4" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>

                {routePaths.map((route, index) => {
                  const routeIsActive = index <= Math.max(0, activeIndex - 1);

                  return (
                    <g key={route.id}>
                      <path
                        d={route.d}
                        stroke={route.soft}
                        strokeWidth="7"
                        strokeLinecap="round"
                        opacity="0.82"
                      />

                      <motion.path
                        d={route.d}
                        stroke={route.accent}
                        strokeWidth={routeIsActive ? "7" : "5.5"}
                        strokeLinecap="round"
                        strokeDasharray="70 300"
                        filter="url(#containedGridPipelinePulseGlow)"
                        initial={false}
                        animate={
                          prefersReducedMotion
                            ? undefined
                            : {
                                strokeDashoffset: [300, 0],
                                opacity: routeIsActive ? [0.48, 1, 0.48] : [0.32, 0.72, 0.32],
                              }
                        }
                        transition={{
                          duration: 2.65 + index * 0.12,
                          delay: index * 0.1,
                          repeat: Infinity,
                          ease: "easeInOut",
                        }}
                      />
                    </g>
                  );
                })}
              </svg>

              <div className="relative z-10 grid h-full grid-cols-3 grid-rows-[140px_140px_140px] items-center gap-x-8 gap-y-[66px]">
                <PipelineNode
                  step={getStep("sources")}
                  index={0}
                  active={activeStep.id === "sources"}
                  onActivate={() => setActiveId("sources")}
                />
                <PipelineNode
                  step={getStep("parser")}
                  index={1}
                  active={activeStep.id === "parser"}
                  onActivate={() => setActiveId("parser")}
                />
                <PipelineNode
                  step={getStep("rag")}
                  index={2}
                  active={activeStep.id === "rag"}
                  onActivate={() => setActiveId("rag")}
                />

                <div />
                <PipelineNode
                  step={getStep("audit")}
                  index={3}
                  active={activeStep.id === "audit"}
                  onActivate={() => setActiveId("audit")}
                />
                <div />

                <PipelineNode
                  step={getStep("packets")}
                  index={4}
                  active={activeStep.id === "packets"}
                  onActivate={() => setActiveId("packets")}
                />
                <PipelineNode
                  step={getStep("cost")}
                  index={5}
                  active={activeStep.id === "cost"}
                  onActivate={() => setActiveId("cost")}
                />
                <PipelineNode
                  step={getStep("frontend")}
                  index={6}
                  active={activeStep.id === "frontend"}
                  onActivate={() => setActiveId("frontend")}
                />
              </div>
            </div>

            <div className="relative z-10 grid gap-4 sm:hidden">
              {pipelineSteps.map((step, index) => (
                <PipelineNode
                  key={step.id}
                  step={step}
                  index={index}
                  active={activeStep.id === step.id}
                  onActivate={() => setActiveId(step.id)}
                />
              ))}
            </div>

            <div className="relative z-10 mt-6 rounded-[1.75rem] border border-[#2a0805]/10 bg-white/86 p-5 shadow-lg shadow-slate-200/50 backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-[#eef4ff] text-[#1f62ff]">
                  <MousePointer2 size={22} />
                </div>
                <div>
                  <p className="text-[10px] font-black uppercase tracking-[0.24em] text-[#1f62ff]">
                    Interactive study map
                  </p>
                  <p className="mt-1 text-sm font-bold leading-6 text-[#51433d]">
                    Use hover, focus, or click to inspect each pipeline step.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function PipelineNode({
  step,
  index,
  active,
  onActivate,
}: {
  step: PipelineStep;
  index: number;
  active: boolean;
  onActivate: () => void;
}) {
  const prefersReducedMotion = useReducedMotion();
  const Icon = step.icon;

  return (
    <motion.button
      type="button"
      onMouseEnter={onActivate}
      onFocus={onActivate}
      onClick={onActivate}
      className="group relative z-20 min-h-[132px] w-full rounded-[1.6rem] border p-4 text-left opacity-100 shadow-lg shadow-slate-200/50 ring-1 ring-transparent transition duration-300 hover:bg-[#fffaf3] hover:shadow-xl hover:ring-[#d6a526]/25"
      style={{
        borderColor: active ? step.border : "rgba(42,8,5,0.10)",
        background: active
          ? `linear-gradient(135deg, ${step.soft}, rgba(255,255,255,0.96))`
          : "rgba(255,255,255,0.96)",
        boxShadow: active ? `0 22px 48px ${step.soft}` : undefined,
        opacity: 1,
      }}
      initial={false}
      animate={
        prefersReducedMotion
          ? undefined
          : active
            ? { y: [0, -5, 0], scale: [1, 1.012, 1], opacity: 1 }
            : { y: 0, scale: 1, opacity: 1 }
      }
      transition={{
        duration: active ? 3.4 : 0.3,
        delay: 0,
        repeat: active ? Infinity : 0,
        ease: "easeInOut",
      }}
      whileHover={{ y: -6, scale: 1.012, opacity: 1 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex items-center gap-4">
        <motion.div
          className="grid h-16 w-16 shrink-0 place-items-center rounded-3xl border bg-white transition"
          style={{
            borderColor: active ? step.border : "rgba(42,8,5,0.10)",
            color: step.accent,
          }}
          animate={
            prefersReducedMotion
              ? undefined
              : active
                ? { rotate: [0, -4, 4, 0] }
                : undefined
          }
          transition={{ duration: 2.6, repeat: active ? Infinity : 0, ease: "easeInOut" }}
        >
          <Icon size={30} />
        </motion.div>

        <div>
          <p className="text-[10px] font-black uppercase tracking-[0.18em] text-[#9aa8bd]">
            {step.number}
          </p>
          <h3 className="mt-1 text-xl font-black leading-tight text-[#09040a]">
            {step.shortTitle}
          </h3>
        </div>
      </div>

      {active ? (
        <motion.span
          layoutId="home-pipeline-active-glow"
          className="absolute inset-0 -z-10 rounded-[1.6rem]"
          style={{ background: step.soft }}
          transition={{ type: "spring", stiffness: 360, damping: 32 }}
        />
      ) : null}
    </motion.button>
  );
}
