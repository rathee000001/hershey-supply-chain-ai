"use client";

import Link from "next/link";
import {
  ArrowRight,
  Boxes,
  Brain,
  Database,
  Factory,
  GitBranch,
  GraduationCap,
  Network,
  PackageCheck,
  ShieldCheck,
  Sparkles,
  Truck,
} from "lucide-react";

const navItems = [
  { label: "HOME", href: "/" },
  { label: "SUPPLY CHAIN", href: "/supply-chain" },
  { label: "EVIDENCE BRAIN", href: "/evidence-brain" },
  { label: "COST MODEL", href: "/cost-model" },
  { label: "SOURCES", href: "/sources" },
  { label: "METHODOLOGY", href: "/methodology" },
];

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
    <main className="min-h-screen overflow-hidden bg-[#f8f4ed] text-[#110706]">
      <nav className="sticky top-0 z-50 border-b border-[#1d0b06]/10 bg-[#fffaf3]/85 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2a0805] text-amber-100 shadow-lg">
              <Factory size={21} />
            </div>
            <div>
              <p className="text-lg font-black leading-none tracking-tight text-[#2a0805]">
                HERSHEY
              </p>
              <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                Supply Chain AI
              </p>
            </div>
          </Link>

          <div className="hidden items-center gap-1 rounded-full border border-[#1d0b06]/10 bg-white/70 p-1 shadow-sm lg:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-full px-4 py-2 text-[11px] font-black uppercase tracking-[0.16em] text-[#4d3a31] transition hover:bg-[#2a0805] hover:text-amber-50"
              >
                {item.label}
              </Link>
            ))}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            <div className="rounded-full border border-emerald-500/20 bg-emerald-50 px-4 py-2 text-[11px] font-black uppercase tracking-[0.18em] text-emerald-700">
              JSON-first
            </div>
            <div className="rounded-full border border-[#1d0b06]/10 bg-[#2a0805] px-4 py-2 text-[11px] font-black uppercase tracking-[0.18em] text-amber-100">
              Study Project
            </div>
          </div>
        </div>
      </nav>

      <section className="relative overflow-hidden px-6 py-20 md:py-28">
        <div className="absolute inset-0">
          <div className="absolute right-[-10rem] top-[-8rem] h-[40rem] w-[40rem] rounded-full bg-[#7b2a15]/20 blur-3xl" />
          <div className="absolute bottom-[-10rem] left-[-10rem] h-[38rem] w-[38rem] rounded-full bg-[#d6a526]/25 blur-3xl" />
          <div className="absolute left-1/2 top-20 h-[20rem] w-[20rem] rounded-full bg-white/70 blur-3xl" />
        </div>

        <div className="relative mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.02fr_0.98fr] lg:items-center">
          <div>
            <div className="mb-6 inline-flex items-center gap-3 rounded-full border border-[#2a0805]/10 bg-white/70 px-5 py-3 shadow-sm backdrop-blur">
              <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[#2a0805] text-amber-100">
                <GraduationCap size={18} />
              </div>
              <div>
                <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                  Course Project
                </p>
                <p className="text-sm font-black text-[#2a0805]">
                  MGMT 780 — Supply Chain Management
                </p>
              </div>
            </div>

            <h1 className="max-w-5xl text-6xl font-black leading-[0.88] tracking-tight text-[#09040a] md:text-8xl">
              Hershey
              <span className="block text-[#7b2a15]">Supply Chain</span>
              <span className="block text-[#d6a526]">Intelligence.</span>
            </h1>

            <p className="mt-7 max-w-3xl text-lg font-medium leading-8 text-[#51433d]">
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
                className="inline-flex items-center gap-2 rounded-full border border-[#2a0805]/15 bg-white/70 px-6 py-4 text-sm font-black uppercase tracking-[0.16em] text-[#2a0805] shadow-sm transition hover:-translate-y-0.5 hover:bg-white"
              >
                View Methodology
              </Link>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <div className="rounded-3xl border border-[#2a0805]/10 bg-white/75 p-5 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                  Submitted by
                </p>
                <p className="mt-2 text-lg font-black text-[#2a0805]">
                  Praveen Rathee
                </p>
              </div>

              <div className="rounded-3xl border border-[#2a0805]/10 bg-white/75 p-5 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                  Professor
                </p>
                <p className="mt-2 text-lg font-black text-[#2a0805]">
                  Dr. Rajendra Tibrewala
                </p>
              </div>

              <div className="rounded-3xl border border-[#2a0805]/10 bg-white/75 p-5 shadow-sm">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">
                  Subject
                </p>
                <p className="mt-2 text-lg font-black text-[#2a0805]">
                  Supply Chain Management
                </p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-8 rounded-full bg-[#7b2a15]/20 blur-3xl" />

            <div className="relative overflow-hidden rounded-[2.8rem] border border-[#2a0805]/10 bg-white/80 p-6 shadow-2xl backdrop-blur">
              <div className="rounded-[2.2rem] border border-[#2a0805]/10 bg-[#170504] p-7 text-white">
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <p className="text-[10px] font-black uppercase tracking-[0.28em] text-amber-100/55">
                      Cinematic Engine
                    </p>
                    <p className="mt-2 text-2xl font-black">
                      Three.js Supply Chain World
                    </p>
                  </div>
                  <div className="rounded-full bg-emerald-400/10 px-4 py-2 text-[10px] font-black uppercase tracking-[0.2em] text-emerald-200">
                    Planned
                  </div>
                </div>

                <div className="rounded-[1.8rem] border border-white/10 bg-white/[0.05] p-5">
                  <div className="grid gap-4">
                    <div className="flex items-center gap-4 rounded-2xl bg-black/25 p-4">
                      <Boxes className="text-amber-200" />
                      <div>
                        <p className="font-black">Origins → Suppliers</p>
                        <p className="text-sm text-white/55">
                          Dairy, sugar, cocoa, minor ingredients
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 rounded-2xl bg-black/25 p-4">
                      <Factory className="text-amber-200" />
                      <div>
                        <p className="font-black">Hershey Factory Process</p>
                        <p className="text-sm text-white/55">
                          Combine, mix, heat, mold, conveyor, wrap
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 rounded-2xl bg-black/25 p-4">
                      <Truck className="text-amber-200" />
                      <div>
                        <p className="font-black">Distribution → Retail</p>
                        <p className="text-sm text-white/55">
                          Warehouse, truck route, shelf, consumer purchase
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-5 rounded-[1.5rem] border border-amber-100/15 bg-amber-100/10 p-4 text-sm leading-6 text-amber-50/75">
                  Evidence claims, cost values, supplier status, and safety notes remain
                  artifact-driven. The 3D layer controls visuals and interaction only.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-12">
        <div className="mx-auto grid max-w-7xl gap-5 lg:grid-cols-[1.1fr_1fr]">
          <div className="rounded-[2rem] border border-[#2a0805]/10 bg-white/75 p-8 shadow-sm">
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

          <div className="grid gap-5 sm:grid-cols-2">
            {overviewCards.map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.title}
                  className="rounded-[2rem] border border-[#2a0805]/10 bg-white/75 p-6 shadow-sm"
                >
                  <Icon className="mb-4 text-[#d6a526]" />
                  <h3 className="text-xl font-black text-[#09040a]">{card.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-[#51433d]">{card.body}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-6 pb-20">
        <div className="mx-auto max-w-7xl rounded-[2rem] border border-[#2a0805]/10 bg-white/75 p-8 shadow-sm">
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
                  Academic framing
                </p>
                <p className="mt-2 text-lg font-black text-[#2a0805]">
                  Course: MGMT 780 · Subject: Supply Chain Management · Professor: Dr. Rajendra Tibrewala
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
      </section>

      <footer className="border-t border-[#2a0805]/10 bg-[#fffaf3] px-6 py-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm text-[#51433d] lg:flex-row lg:items-center lg:justify-between">
          <p>
            © 2026 Hershey Supply Chain AI · Study project by Praveen Rathee
          </p>
          <p className="max-w-3xl text-xs leading-5">
            Academic/professional study project using public-source evidence and benchmark modeling.
            Not affiliated with, endorsed by, or sponsored by The Hershey Company.
          </p>
        </div>
      </footer>
    </main>
  );
}