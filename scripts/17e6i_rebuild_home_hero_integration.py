from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

shell_path = root / "src" / "components" / "cinematic" / "CinematicPageShell.tsx"
home_path = root / "src" / "app" / "page.tsx"
slot_path = root / "src" / "components" / "hershey3d" / "HomeChocolateBarHeroSlot.tsx"

shell_code = r'''"use client";

import { ReactNode } from "react";
import CinematicNavbar from "@/components/cinematic/CinematicNavbar";
import ChocolateAtmosphere from "@/components/cinematic/ChocolateAtmosphere";
import ProductIdentityBadge from "@/components/cinematic/ProductIdentityBadge";

type CinematicPageShellProps = {
  children: ReactNode;
  footerMode?: "light" | "dark";
  showFloatingProductBadge?: boolean;
};

export default function CinematicPageShell({
  children,
  footerMode = "light",
  showFloatingProductBadge = false,
}: CinematicPageShellProps) {
  const dark = footerMode === "dark";

  return (
    <main
      className={
        dark
          ? "relative min-h-screen overflow-hidden bg-[#080202] text-white"
          : "relative min-h-screen overflow-hidden bg-[#f8f4ed] text-[#110706]"
      }
    >
      <ChocolateAtmosphere mode={dark ? "dark" : "light"} />
      <CinematicNavbar />

      {showFloatingProductBadge && <ProductIdentityBadge variant="floating" />}

      <div className="relative z-10">{children}</div>

      <footer
        className={
          dark
            ? "relative z-10 border-t border-white/10 bg-black/30 px-6 py-8 text-white/55"
            : "relative z-10 border-t border-[#2a0805]/10 bg-[#fffaf3]/80 px-6 py-8 text-[#51433d] backdrop-blur"
        }
      >
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm lg:flex-row lg:items-center lg:justify-between">
          <p>© 2026 Hershey Supply Chain AI · Study project by Praveen Rathee</p>
          <p className="max-w-3xl text-xs leading-5">
            Academic/professional study project using public-source evidence and benchmark
            modeling. Not affiliated with, endorsed by, or sponsored by The Hershey Company.
          </p>
        </div>
      </footer>
    </main>
  );
}
'''

slot_code = r'''"use client";

import dynamic from "next/dynamic";

const HomeChocolateBarHero = dynamic(
  () => import("@/components/hershey3d/HomeChocolateBarHero"),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-[560px] rounded-[2.8rem] border border-[#2a0805]/10 bg-[#170504] p-8 text-white shadow-2xl">
        <p className="text-[10px] font-black uppercase tracking-[0.28em] text-amber-100/55">
          Loading 3D hero
        </p>
        <h2 className="mt-4 text-3xl font-black">Preparing Hershey product scene...</h2>
        <p className="mt-3 max-w-xl text-sm leading-6 text-white/60">
          The homepage hero uses the collected wrapper and unwrapped Hershey bar assets.
        </p>
      </div>
    ),
  }
);

export default function HomeChocolateBarHeroSlot() {
  return <HomeChocolateBarHero />;
}
'''

home_code = r'''"use client";

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
import ProductIdentityBadge from "@/components/cinematic/ProductIdentityBadge";
import HomeChocolateBarHeroSlot from "@/components/hershey3d/HomeChocolateBarHeroSlot";

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
    <CinematicPageShell showFloatingProductBadge={false}>
      <section className="relative overflow-hidden px-6 py-16 md:py-24">
        <div className="absolute inset-0">
          <div className="absolute right-[-10rem] top-[-8rem] h-[40rem] w-[40rem] rounded-full bg-[#7b2a15]/20 blur-3xl" />
          <div className="absolute bottom-[-10rem] left-[-10rem] h-[38rem] w-[38rem] rounded-full bg-[#d6a526]/25 blur-3xl" />
          <div className="absolute left-1/2 top-20 h-[20rem] w-[20rem] rounded-full bg-white/70 blur-3xl" />
        </div>

        <div className="relative mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <MotionSafeWrapper>
            <div>
              <div className="mb-5 inline-flex items-center gap-3 rounded-full border border-[#2a0805]/10 bg-white/70 px-5 py-3 shadow-sm backdrop-blur">
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

              <div className="mb-6">
                <ProductIdentityBadge variant="hero" />
              </div>

              <h1 className="max-w-5xl text-6xl font-black leading-[0.88] tracking-tight text-[#09040a] md:text-8xl">
                Hershey
                <span className="block text-[#7b2a15]">Supply Chain</span>
                <span className="block text-[#d6a526]">Intelligence.</span>
              </h1>

              <p className="mt-7 max-w-3xl text-lg font-medium leading-8 text-[#51433d]">
                A JSON-first, public-evidence study project centered on the 1.55 oz
                Hershey milk chocolate bar. The model connects product identity, supplier
                context, ingredient evidence, benchmark cost logic, and a cinematic
                product-first interface.
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
          </MotionSafeWrapper>

          <MotionSafeWrapper delay={0.12}>
            <HomeChocolateBarHeroSlot />
          </MotionSafeWrapper>
        </div>
      </section>

      <section className="px-6 pb-12">
        <div className="mx-auto grid max-w-7xl gap-5 lg:grid-cols-[1.1fr_1fr]">
          <MotionSafeWrapper>
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
          </MotionSafeWrapper>

          <div className="grid gap-5 sm:grid-cols-2">
            {overviewCards.map((card, index) => {
              const Icon = card.icon;
              return (
                <MotionSafeWrapper key={card.title} delay={index * 0.05}>
                  <div className="rounded-[2rem] border border-[#2a0805]/10 bg-white/75 p-6 shadow-sm">
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
                    Academic Framing
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
        </MotionSafeWrapper>
      </section>
    </CinematicPageShell>
  );
}
'''

shell_path.write_text(shell_code, encoding="utf-8")
slot_path.parent.mkdir(parents=True, exist_ok=True)
slot_path.write_text(slot_code, encoding="utf-8")
home_path.write_text(home_code, encoding="utf-8")

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

checks = {
    "home_has_ProductIdentityBadge": "ProductIdentityBadge" in home_code,
    "home_has_HomeChocolateBarHeroSlot": "HomeChocolateBarHeroSlot" in home_code,
    "shell_has_showFloatingProductBadge": "showFloatingProductBadge" in shell_code,
    "slot_exists": slot_path.exists(),
}

status = "pass" if all(checks.values()) else "fail"

report = {
    "run_name": "step17e6i_rebuild_home_hero_integration",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "checks": checks,
    "files_written": [
        str(shell_path).replace("\\", "/"),
        str(slot_path).replace("\\", "/"),
        str(home_path).replace("\\", "/"),
    ],
    "remembered_home_3d_hero_rule": "Homepage 3D hero is product-first: target SKU badge inside hero, wrapper asset, unwrapped bar asset, and cinematic Hershey product identity before full supply-chain world.",
    "next_step": "Run snapshot again. If pass, continue to Step 17F.",
}

report_path = report_dir / "step17e6i_rebuild_home_hero_integration_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5I HOME HERO INTEGRATION REBUILD COMPLETE")
print("---------------------------------------------------")
print(f"Status:                           {status}")
print(f"Home has ProductIdentityBadge:    {checks['home_has_ProductIdentityBadge']}")
print(f"Home has HomeChocolateBarHeroSlot:{checks['home_has_HomeChocolateBarHeroSlot']}")
print(f"Shell has showFloatingProductBadge:{checks['shell_has_showFloatingProductBadge']}")
print(f"Report JSON:                      {report_path}")
print("")