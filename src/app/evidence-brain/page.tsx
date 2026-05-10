"use client";

import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function PlaceholderPage() {
  return (
    <main className="min-h-screen bg-[#080202] px-6 py-16 text-white">
      <section className="mx-auto max-w-5xl rounded-[2rem] border border-white/10 bg-white/[0.06] p-8 shadow-2xl backdrop-blur">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-amber-100/20 bg-black/25 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
          <ShieldCheck size={16} />
          Parser + audit intelligence
        </div>

        <h1 className="text-5xl font-black tracking-tight md:text-7xl">Evidence Brain</h1>

        <p className="mt-6 max-w-3xl text-lg leading-8 text-white/65">
          This page will display source inventory, OCR/RAG memory, evidence blobs, audit status, and searchable public-source evidence.
        </p>

        <p className="mt-6 rounded-2xl border border-amber-100/15 bg-black/25 p-4 text-sm leading-6 text-amber-100/70">
          This route is intentionally stabilized before the advanced cinematic system is built.
          Claims and final content will come from validated JSON artifacts.
        </p>

        <Link
          href="/"
          className="mt-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-5 py-3 text-sm font-black uppercase tracking-[0.18em] text-white transition hover:border-amber-100/30 hover:bg-amber-100/10"
        >
          <ArrowLeft size={16} />
          Back home
        </Link>
      </section>
    </main>
  );
}
