"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Brain, Database, Network, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useMemo, useState } from "react";

type OverviewCard = {
  id: string;
  title: string;
  body: string;
  icon: LucideIcon;
  accent: string;
  soft: string;
  border: string;
};

const overviewCards: OverviewCard[] = [
  {
    id: "brain",
    title: "Public Evidence Brain",
    body: "Parser/OCR memory and approved public artifacts shape the study interface.",
    icon: Brain,
    accent: "#1f62ff",
    soft: "rgba(31,98,255,0.10)",
    border: "rgba(31,98,255,0.35)",
  },
  {
    id: "map",
    title: "Supply Chain Map",
    body: "Ingredient, packaging, distribution, retail, and consumer flow become visual stages.",
    icon: Network,
    accent: "#0f9f6e",
    soft: "rgba(15,159,110,0.11)",
    border: "rgba(15,159,110,0.35)",
  },
  {
    id: "cost",
    title: "Benchmark Cost Logic",
    body: "Cost logic remains a benchmark study model, not internal cost or margin data.",
    icon: Database,
    accent: "#d6a526",
    soft: "rgba(216,165,38,0.13)",
    border: "rgba(216,165,38,0.42)",
  },
  {
    id: "cinema",
    title: "Cinematic Interface",
    body: "Three.js and Framer Motion turn approved outputs into a premium interface.",
    icon: Sparkles,
    accent: "#7b2a15",
    soft: "rgba(123,42,21,0.10)",
    border: "rgba(123,42,21,0.35)",
  },
];

export default function HomeProjectOverviewSection() {
  const prefersReducedMotion = useReducedMotion();
  const [activeId, setActiveId] = useState(overviewCards[0].id);

  const activeCard = useMemo(
    () => overviewCards.find((card) => card.id === activeId) ?? overviewCards[0],
    [activeId],
  );

  return (
    <section className="px-6 pb-12" data-home-project-overview="stable-colorful-interactive-overview-no-fade">
      <div className="mx-auto grid max-w-7xl gap-5 lg:grid-cols-[1.08fr_1fr]">
        <motion.div
          className="rounded-[2.35rem] border border-[#2a0805]/10 bg-white/94 p-8 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl"
          initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
          whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="text-[11px] font-black uppercase tracking-[0.25em] text-[#1f62ff]">
            Project Overview
          </p>
          <h2 className="mt-4 text-4xl font-black tracking-tight text-[#09040a] md:text-5xl">
            A study platform built from public evidence and audited artifacts.
          </h2>
          <p className="mt-5 text-base leading-8 text-[#51433d]">
            This project is designed as a public-source supply-chain intelligence prototype.
            It combines document parsing, OCR/RAG memory, evidence audit logic, ingredient
            and supplier packet construction, benchmark cost modeling, and a planned
            cinematic frontend.
          </p>

          <motion.div
            key={activeCard.id}
            className="mt-7 rounded-[1.75rem] border p-5"
            style={{
              borderColor: activeCard.border,
              background: `linear-gradient(135deg, ${activeCard.soft}, rgba(255,250,243,0.92))`,
            }}
            initial={prefersReducedMotion ? false : { opacity: 0, y: 10 }}
            animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          >
            <p className="text-[10px] font-black uppercase tracking-[0.24em] text-[#9c6a27]">
              Active module
            </p>
            <p className="mt-2 text-xl font-black text-[#2d0d06]">{activeCard.title}</p>
            <p className="mt-2 text-sm font-semibold leading-6 text-[#51433d]">{activeCard.body}</p>
          </motion.div>
        </motion.div>

        <div className="grid gap-5 sm:grid-cols-2">
          {overviewCards.map((card, index) => {
            const Icon = card.icon;
            const active = activeId === card.id;

            return (
              <motion.button
                key={card.id}
                type="button"
                onMouseEnter={() => setActiveId(card.id)}
                onFocus={() => setActiveId(card.id)}
                onClick={() => setActiveId(card.id)}
                className="group min-h-[210px] rounded-[2.2rem] border p-6 text-left opacity-100 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl transition"
                style={{
                  borderColor: active ? card.border : "rgba(42,8,5,0.10)",
                  opacity: 1,
                  opacity: 1,
                  background: active
                    ? `linear-gradient(135deg, ${card.soft}, rgba(255,255,255,0.96))`
                    : "rgba(255,255,255,0.94)",
                }}
                initial={false}
                animate={
                  prefersReducedMotion
                    ? undefined
                    : active
                      ? { y: [0, -5, 0], scale: [1, 1.012, 1], opacity: 1 }
                      : { y: 0, scale: 1, opacity: 1 }
                }
                whileHover={{ y: -6, scale: 1.012, opacity: 1 }}
                transition={{
                  duration: active ? 3.4 : 0.45,
                  delay: active ? 0 : index * 0.05,
                  repeat: active ? Infinity : 0,
                  ease: "easeInOut",
                }}
              >
                <div
                  className="grid h-16 w-16 place-items-center rounded-3xl border bg-white shadow-sm"
                  style={{ borderColor: card.border, color: card.accent }}
                >
                  <Icon size={30} />
                </div>

                <h3 className="mt-5 text-2xl font-black leading-tight text-[#09040a]">
                  {card.title}
                </h3>
                <p className="mt-3 text-sm font-semibold leading-6 text-[#51433d]">
                  {card.body}
                </p>
              </motion.button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
