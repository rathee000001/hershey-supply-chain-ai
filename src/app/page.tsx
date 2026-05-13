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
import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";
import HomeProjectOverviewSection from "@/components/home/HomeProjectOverviewSection";
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

        <HomeProjectOverviewSection />

        <HomeIntelligencePipelineMap />
      </div>
    </CinematicPageShell>
  );
}
