"use client";

import Link from "next/link";
import { ArrowRight, ShieldCheck } from "lucide-react";
import CinematicPageShell from "@/components/cinematic/CinematicPageShell";
import MotionSafeWrapper from "@/components/cinematic/MotionSafeWrapper";

export default function PlaceholderPage() {
  return (
    <CinematicPageShell>
      <section className="px-6 py-20 md:py-28">
        <MotionSafeWrapper>
          <div className="mx-auto max-w-6xl rounded-[2.5rem] border border-[#2a0805]/10 bg-white/78 p-8 shadow-2xl backdrop-blur">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#2a0805]/10 bg-[#fffaf3] px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-[#9c6a27]">
              <ShieldCheck size={16} />
              Parser + audit intelligence
            </div>

            <h1 className="text-5xl font-black tracking-tight text-[#09040a] md:text-7xl">
              Evidence Brain
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-[#51433d]">
              This page will display source inventory, OCR/RAG memory, evidence blobs, audit status, and searchable public-source evidence.
            </p>

            <div className="mt-8 rounded-3xl border border-[#2a0805]/10 bg-[#f8f4ed] p-5 text-sm leading-6 text-[#51433d]">
              This route is stabilized inside the global cinematic shell. Final content will be
              rebuilt from validated JSON artifacts in its roadmap step.
            </div>

            <Link
              href="/supply-chain"
              className="mt-8 inline-flex items-center gap-2 rounded-full bg-[#2a0805] px-6 py-4 text-sm font-black uppercase tracking-[0.16em] text-white shadow-xl transition hover:-translate-y-0.5"
            >
              Continue to Supply Chain
              <ArrowRight size={17} />
            </Link>
          </div>
        </MotionSafeWrapper>
      </section>
    </CinematicPageShell>
  );
}
