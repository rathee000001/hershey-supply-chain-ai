from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

pages = {
    "src/app/evidence-brain/page.tsx": {
        "title": "Evidence Brain",
        "kicker": "Parser + audit intelligence",
        "body": "This page will display source inventory, OCR/RAG memory, evidence blobs, audit status, and searchable public-source evidence.",
    },
    "src/app/cost-model/page.tsx": {
        "title": "Cost Model",
        "kicker": "Benchmark cost intelligence",
        "body": "This page will display benchmark physical cost, observed retail price, residual channel pool, and safe cost-model limitations.",
    },
    "src/app/sources/page.tsx": {
        "title": "Sources",
        "kicker": "Public evidence + visual asset notes",
        "body": "This page will list source packets, raw files, supplier evidence, retail evidence, visual asset notes, and project disclaimers.",
    },
    "src/app/methodology/page.tsx": {
        "title": "Methodology",
        "kicker": "How the intelligence system was built",
        "body": "This page will explain data collection, OCR, RAG/vector memory, evidence audit, supplier classification, cost modeling, and JSON-first frontend rules.",
    },
}

template = '''"use client";

import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function PlaceholderPage() {
  return (
    <main className="min-h-screen bg-[#080202] px-6 py-16 text-white">
      <section className="mx-auto max-w-5xl rounded-[2rem] border border-white/10 bg-white/[0.06] p-8 shadow-2xl backdrop-blur">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-amber-100/20 bg-black/25 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
          <ShieldCheck size={16} />
          __KICKER__
        </div>

        <h1 className="text-5xl font-black tracking-tight md:text-7xl">__TITLE__</h1>

        <p className="mt-6 max-w-3xl text-lg leading-8 text-white/65">
          __BODY__
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
'''

written = []

for rel_path, data in pages.items():
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        template
        .replace("__TITLE__", data["title"])
        .replace("__KICKER__", data["kicker"])
        .replace("__BODY__", data["body"])
    )
    path.write_text(content, encoding="utf-8")
    written.append(str(path).replace("\\", "/"))

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e3_create_placeholder_route_pages",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "routes_written": written,
    "next_step": "Replace main home page with full Gold-style Hershey portfolio page.",
}

report_path = report_dir / "step17e3_placeholder_routes_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B2-A PLACEHOLDER ROUTES COMPLETE")
print("------------------------------------------")
print(f"Routes written: {len(written)}")
print(f"Report JSON:    {report_path}")
print("")