"use client";

import Link from "next/link";
import {
  ArrowRight,
  Brain,
  Database,
  GitBranch,
  GraduationCap,
  Network,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import CinematicPageShell from "@/components/cinematic/CinematicPageShell";
import MotionSafeWrapper from "@/components/cinematic/MotionSafeWrapper";
import HomeChocolateBarHeroSlot from "@/components/hershey3d/HomeChocolateBarHeroSlot";
import HomeProductShowcase from "@/components/home/HomeProductShowcase";

const overviewCards = [
  {
    title: "Public Evidence Brain",
    body: "Raw files, PDF text, visual OCR, evidence blobs, and audit-safe website wording form the intelligence base.",
    icon: Brain,
  },
  {
    title: "Supply Chain Map",
    body: "Dairy, sugar, cocoa, minor ingredients, packaging, distribution, retail shelf, and consumer purchase are modeled as a visual flow.",
    icon: Network,
  },
  {
    title: "Benchmark Cost Logic",
    body: "Physical cost, observed retail price, and residual channel pool are treated as benchmark estimates, not internal Hershey data.",
    icon: Database,
  },
  {
    title: "Cinematic Interface",
    body: "The next build layer uses Three.js, React Three Fiber, Drei, Framer Motion, GSAP, and JSON-first evidence panels.",
    icon: Sparkles,
  },
];

const pipelineItems = [
  "Raw public sources",
  "Parser + OCR memory",
  "RAG/vector evidence index",
  "Evidence audit",
  "Supplier/ingredient packets",
  "Cost model artifacts",
  "3D cinematic frontend",
];

export default function HomePage() {
  return (
    <CinematicPageShell>
      <HomeChocolateBarHeroSlot />

      <div className="relative z-20">
        <section className="relative overflow-hidden px-6 pb-16 pt-24 md:pb-20 md:pt-32">
          <div className="relative mx-auto grid max-w-7xl gap-8 lg:min-h-[calc(100vh-132px)] lg:grid-cols-[0.82fr_1.18fr] lg:items-center">
            <MotionSafeWrapper>
              <div className="max-w-[650px]">
                <div className="mb-6 inline-flex items-center gap-3 rounded-full border border-[#2a0805]/10 bg-white/90 px-5 py-3 shadow-sm backdrop-blur">
                  <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[#2a0805] text-amber-100">
                    <GraduationCap size={18} />
                  </div>
                  <div>
                    <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                      Course Project
                    </p>
                    <p className="text-sm font-black text-[#2a0805]">
                      Spring 2026 - M01</p>
                    <p className="mt-1 text-xs font-black text-[#2a0805]/72">Operations Management Applications · QANT_760-M01-2026SP-S</p>
                  </div>
                </div>

                <h1 className="text-6xl font-black leading-[0.88] tracking-tight text-[#09040a] md:text-8xl">
                  Hershey
                  <span className="block text-[#7b2a15]">Supply Chain</span>
                  <span className="block text-[#d6a526]">Intelligence.</span>
                </h1>

                <p className="mt-7 max-w-2xl text-lg font-medium leading-8 text-[#51433d]">
                  A JSON-first, public-evidence study project that models the 1.55 oz
                  Hershey milk chocolate supply chain through supplier context, ingredient
                  evidence, benchmark cost logic, and a planned cinematic Three.js interface.
                </p>

                <div className="mt-8 flex flex-wrap gap-4">
                  <Link
                    href="/supply-chain"
                    className="inline-flex items-center gap-2 rounded-full bg-[#09040a] px-6 py-4 text-sm font-black uppercase tracking-[0.16em] text-white shadow-xl transition hover:-translate-y-0.5 hover:bg-[#2a0805]"
                  >
                    Open Supply Chain
                    <ArrowRight size={17} />
                  </Link>
                  <Link
                    href="/methodology"
                    className="inline-flex items-center gap-2 rounded-full border border-[#2a0805]/15 bg-white/88 px-6 py-4 text-sm font-black uppercase tracking-[0.16em] text-[#2a0805] shadow-sm transition hover:-translate-y-0.5 hover:bg-white"
                  >
                    View Methodology
                  </Link>
                </div>

                <div className="mt-8 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-3xl border border-[#2a0805]/10 bg-white/92 p-5 shadow-sm backdrop-blur">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                      Submitted by
                    </p>
                    <p className="mt-2 text-lg font-black text-[#2a0805]">
                      Praveen Rathee
                    </p>
                  </div>

                  <div className="rounded-3xl border border-[#2a0805]/10 bg-white/92 p-5 shadow-sm backdrop-blur">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                      Professor
                    </p>
                    <p className="10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                      Professor
                    </p>
                    <p className="mt-2 text-lg font-black text-[#2a0805]">
                      Dr. Rajendra Tibrewala
                    </p>
                  </div>

                  <div className="rounded-3xl border border-[#2a0805]/10 bg-white/92 p-5 shadow-sm backdrop-blur">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                      Course
                    </p>
                    <p className="mt-2 text-lg font-black text-[#2a0805]">
                      QANT 760
                    </p>
                  </div>
                </div>
              </div>
            </MotionSafeWrapper>

            <MotionSafeWrapper delay={0.08}>
              <HomeProductShowcase />
            </MotionSafeWrapper>
          </div>
        </section>

        <section className="px-6 pb-12">
          <div className="mx-auto grid max-w-7xl gap-5 lg:grid-cols-[1.1fr_1fr]">
            <MotionSafeWrapper>
              <div className="rounded-[2rem] border border-[#2a0805]/10 bg-white/94 p-8 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl">
                <p className="text-[11px] font-black uppercase tracking-[0.25em] text-[#1f62ff]">
                  Project Overview
                </p>
                <h2 className="mt-4 text-4xl font-black tracking-tight text-[#09040a]">
                  A study platform built from public evidence and audited artifacts.
                </h2>
                <p className="mt-5 text-base leading-8 text-[#51433d]">
                  This project is designed as a public-source supply-chain intelligence prototype.
                  It combines document parsing, OCR/RAG memory, evidence audit logic, ingredient
                  and supplier packet construction, benchmark cost modeling, and a planned
                  cinematic frontend.
                </p>
              </div>
            </MotionSafeWrapper>

            <div className="grid gap-5 sm:grid-cols-2">
              {overviewCards.map((card, index) => {
                const Icon = card.icon;
                return (
                  <MotionSafeWrapper key={card.title} delay={index * 0.05}>
                    <div className="rounded-[2rem] border border-[#2a0805]/10 bg-white/94 p-6 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl">
                      <Icon className="mb-4 text-[#d6a526]" />
                      <h3 className="text-xl font-black text-[#09040a]">{card.title}</h3>
                      <p className="mt-3 text-sm leading-6 text-[#51433d]">{card.body}</p>
                    </div>
                  </MotionSafeWrapper>
                );
              })}
            </div>
          </div>
        </section>

        <section className="px-6 pb-20">
          <MotionSafeWrapper>
            <div className="mx-auto max-w-7xl rounded-[2rem] border border-[#2a0805]/10 bg-white/94 p-8 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl">
              <p className="text-[11px] font-black uppercase tracking-[0.25em] text-[#1f62ff]">
                Intelligence Pipeline
              </p>

              <div className="mt-6 grid gap-3 md:grid-cols-7">
                {pipelineItems.map((item, index) => (
                  <div
                    key={item}
                    className="rounded-3xl border border-[#2a0805]/10 bg-[#fffaf3] p-4"
                  >
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                      {String(index + 1).padStart(2, "0")}
                    </p>
                    <p className="mt-2 text-sm font-black text-[#2a0805]">{item}</p>
                  </div>
                ))}
              </div>

              <div className="mt-8 rounded-3xl border border-[#2a0805]/10 bg-[#f8f4ed] p-6">
                <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <p className="text-[11px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                      Academic Framing
                    </p>
                    <p className="mt-2 text-lg font-black text-[#2a0805]">
                      Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <div className="inline-flex items-center gap-2 rounded-full bg-[#2a0805] px-4 py-3 text-xs font-black uppercase tracking-[0.16em] text-white">
                      <ShieldCheck size={15} />
                      Evidence-safe
                    </div>
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#2a0805]/10 bg-white px-4 py-3 text-xs font-black uppercase tracking-[0.16em] text-[#2a0805]">
                      <GitBranch size={15} />
                      Portfolio-ready
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </MotionSafeWrapper>
        </section>
      </div>
    </CinematicPageShell>
  );
}
