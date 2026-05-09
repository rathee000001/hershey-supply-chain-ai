"use client";

import Link from "next/link";
import { ArrowRight, Boxes, LineChart, Network } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-[#fff7ed] via-[#f8eadb] to-[#ead0bd] text-[#24100c]">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 py-16">
        <div className="max-w-4xl">
          <p className="mb-4 inline-flex rounded-full border border-[#4b1d16]/20 bg-white/60 px-4 py-2 text-sm font-semibold uppercase tracking-[0.25em] text-[#4b1d16]">
            Public-Evidence Benchmark Model
          </p>

          <h1 className="text-5xl font-black tracking-tight md:text-7xl">
            Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-[#5a3328]">
            Interactive artifact-driven supply chain model for ingredient sourcing,
            supplier confidence, manufacturing flow, logistics, verified retail price,
            and benchmark cost breakdown.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/supply-chain"
              className="inline-flex items-center gap-2 rounded-2xl bg-[#4b1d16] px-6 py-4 font-bold text-white shadow-xl transition hover:scale-[1.02]"
            >
              Open Supply Chain Model <ArrowRight size={20} />
            </Link>
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-3">
          {[
            ["JSON-First", "Frontend reads only public artifacts.", Boxes],
            ["Interactive Graph", "35 nodes and 36 edges prepared.", Network],
            ["Cost Intelligence", "Physical cost, retail price, and residual pool.", LineChart],
          ].map(([title, text, Icon]) => (
            <div key={String(title)} className="rounded-3xl border border-[#4b1d16]/10 bg-white/60 p-6 shadow-lg backdrop-blur">
              <Icon className="mb-4 text-[#4b1d16]" size={28} />
              <h2 className="text-xl font-black">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-[#6f4a3d]">{text}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
