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
              __KICKER__
            </div>

            <h1 className="text-5xl font-black tracking-tight text-[#09040a] md:text-7xl">
              __TITLE__
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-[#51433d]">
              __BODY__
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
'''

written = []

for rel_path, data in pages.items():
    path = root / rel_path
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
    "run_name": "step17e5_rebuild_placeholder_pages_with_shell",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "pages_written": written,
    "next_step": "Validate global chocolate atmosphere and page shell.",
}

report_path = report_dir / "step17e5_placeholder_shell_pages_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B4 PLACEHOLDER SHELL PAGES COMPLETE")
print("---------------------------------------------")
print(f"Pages written: {len(written)}")
print(f"Report JSON:   {report_path}")
print("")