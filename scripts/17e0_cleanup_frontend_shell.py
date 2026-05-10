from pathlib import Path
import shutil
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

legacy_dir = root / "src" / "components" / "archive" / "hershey_legacy_17d"
legacy_dir.mkdir(parents=True, exist_ok=True)

legacy_components = [
    root / "src" / "components" / "hershey" / "ChocolateDripOverlay.tsx",
    root / "src" / "components" / "hershey" / "HersheyCinematicHero.tsx",
    root / "src" / "components" / "hershey" / "CinematicAssetScene.tsx",
    root / "src" / "components" / "hershey" / "CinematicConnectedMap.tsx",
    root / "src" / "components" / "hershey" / "CinematicSupplyChainStoryboard.tsx",
]

moved = []
missing = []

for file_path in legacy_components:
    if file_path.exists():
        destination = legacy_dir / file_path.name
        shutil.copy2(file_path, destination)
        moved.append({
            "from": str(file_path).replace("\\", "/"),
            "archived_to": str(destination).replace("\\", "/")
        })
    else:
        missing.append(str(file_path).replace("\\", "/"))

page = root / "src" / "app" / "supply-chain" / "page.tsx"

clean_page = r'''"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Boxes, Factory, Network, ShieldCheck, Sparkles } from "lucide-react";
import {
  EnrichedArtifacts,
  loadEnrichedArtifacts,
} from "@/lib/hershey/enrichedArtifacts";

function formatNumber(value: number): string {
  return value.toLocaleString();
}

export default function SupplyChainPage() {
  const [data, setData] = useState<EnrichedArtifacts | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    loadEnrichedArtifacts()
      .then(setData)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Unknown artifact loading error");
      });
  }, []);

  const stats = useMemo(() => {
    if (!data) return null;

    return {
      evidenceCount: Object.keys(data.evidence || {}).length,
      packetCount: data.packetSummary?.length ?? 0,
      supplierCount: data.suppliers?.length ?? 0,
      ingredientCount: data.ingredients?.length ?? 0,
      nodeCount: data.graph?.nodes?.length ?? 0,
      edgeCount: data.graph?.edges?.length ?? 0,
      physicalCost: data.costBreakdown.physical_cost?.base_cents_per_bar,
      retailPrice: data.costBreakdown.retail_price?.base_usd_per_bar,
    };
  }, [data]);

  if (error) {
    return (
      <main className="min-h-screen bg-[#080202] px-6 py-10 text-white">
        <section className="mx-auto max-w-4xl rounded-3xl border border-red-400/30 bg-red-950/40 p-8">
          <h1 className="text-3xl font-black">Artifact loading error</h1>
          <p className="mt-4 text-red-100">{error}</p>
        </section>
      </main>
    );
  }

  if (!data || !stats) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#080202] text-white">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl">
          <Sparkles className="mb-4 animate-pulse text-amber-200" />
          <p className="text-lg font-bold">Loading Hershey supply-chain intelligence...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#080202] text-white">
      <section className="relative min-h-screen border-b border-white/10 bg-[radial-gradient(circle_at_72%_18%,#6f2a17_0%,#2a0806_42%,#080202_100%)] px-6 py-24">
        <div className="absolute inset-0 opacity-70">
          <div className="absolute left-[-8rem] top-24 h-[34rem] w-[34rem] rounded-full bg-[#4a130b] blur-3xl" />
          <div className="absolute right-[-8rem] top-16 h-[42rem] w-[42rem] rounded-full bg-amber-300/10 blur-3xl" />
        </div>

        <div className="relative mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1fr_0.85fr] lg:items-center">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-amber-100/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/80 backdrop-blur">
              <ShieldCheck size={16} />
              Validated public-evidence intelligence
            </div>

            <h1 className="max-w-5xl text-5xl font-black leading-[0.92] tracking-tight md:text-7xl">
              Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence
            </h1>

            <p className="mt-7 max-w-3xl text-lg leading-8 text-amber-50/78">
              This page is being rebuilt into an advanced cinematic Three.js supply-chain experience.
              Current evidence artifacts remain loaded and validated while the new visual engine is prepared.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Evidence items</p>
                <p className="mt-2 text-3xl font-black">{formatNumber(stats.evidenceCount)}</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Graph model</p>
                <p className="mt-2 text-3xl font-black">{stats.nodeCount} / {stats.edgeCount}</p>
                <p className="text-xs text-amber-100/60">nodes / edges</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm text-amber-100/70">Loaded cards</p>
                <p className="mt-2 text-3xl font-black">{stats.supplierCount + stats.ingredientCount}</p>
              </div>
            </div>
          </div>

          <div className="rounded-[3rem] border border-amber-100/20 bg-white/[0.06] p-8 shadow-2xl backdrop-blur">
            <p className="text-xs font-black uppercase tracking-[0.32em] text-amber-100/55">
              Next visual engine
            </p>
            <div className="mt-6 rounded-[2rem] border border-white/10 bg-black/30 p-8">
              <div className="grid gap-4">
                <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
                  <Factory className="mb-3 text-amber-200" />
                  <h2 className="text-2xl font-black">Three.js supply-chain scene</h2>
                  <p className="mt-2 text-sm leading-6 text-white/60">
                    Farm origins, supplier logos, factory process, conveyor, trucks, retail shelf, and consumer purchase.
                  </p>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
                  <Network className="mb-3 text-amber-200" />
                  <h2 className="text-2xl font-black">Evidence-aware nodes</h2>
                  <p className="mt-2 text-sm leading-6 text-white/60">
                    Hover and click states will open JSON-driven evidence panels.
                  </p>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-5">
                  <Boxes className="mb-3 text-amber-200" />
                  <h2 className="text-2xl font-black">Cinematic process animation</h2>
                  <p className="mt-2 text-sm leading-6 text-white/60">
                    Ingredient streams combine, chocolate is mixed, molded, wrapped, shipped, shelved, and purchased.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-white/10 bg-[#100403] px-6 py-16">
        <div className="mx-auto max-w-7xl">
          <p className="inline-flex rounded-full border border-amber-200/20 bg-white/10 px-4 py-2 text-xs font-black uppercase tracking-[0.25em] text-amber-100/70">
            Clean frontend shell
          </p>

          <h2 className="mt-5 text-4xl font-black tracking-tight md:text-5xl">
            Ready for the advanced cinematic engine
          </h2>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
              <h3 className="text-xl font-black">Benchmark cost</h3>
              <p className="mt-3 text-3xl font-black text-amber-100">
                {typeof stats.physicalCost === "number" ? `${stats.physicalCost.toFixed(2)}¢` : "—"}
              </p>
              <p className="mt-3 text-sm leading-6 text-white/55">
                Benchmark-only. Not Hershey internal cost, invoice data, margin, or profit.
              </p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
              <h3 className="text-xl font-black">Retail base</h3>
              <p className="mt-3 text-3xl font-black text-amber-100">
                {typeof stats.retailPrice === "number" ? `$${stats.retailPrice.toFixed(2)}` : "—"}
              </p>
              <p className="mt-3 text-sm leading-6 text-white/55">
                Retail price evidence is page/store/date dependent and not margin evidence.
              </p>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/[0.06] p-6">
              <h3 className="text-xl font-black">Safety rule</h3>
              <p className="mt-3 text-sm leading-6 text-white/65">
                The 3D scene may hardcode layout and animation, but supplier claims, cost values,
                evidence counts, and safety wording must come from JSON artifacts.
              </p>
            </div>
          </div>

          <div className="mt-10 rounded-3xl border border-amber-100/15 bg-black/25 p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.25em] text-amber-100/50">
                  Next step
                </p>
                <h3 className="mt-2 text-2xl font-black">Step 17E — Advanced cinematic engine foundation</h3>
              </div>
              <ArrowRight className="text-amber-200" />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
'''

page.parent.mkdir(parents=True, exist_ok=True)
page.write_text(clean_page, encoding="utf-8")

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e0_cleanup_frontend_shell",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "page_rewritten": str(page).replace("\\", "/"),
    "legacy_archive_dir": str(legacy_dir).replace("\\", "/"),
    "legacy_components_archived": moved,
    "missing_legacy_components": missing,
    "next_step": "Create cinematic roadmap scaffold folders and empty files."
}

report_path = report_dir / "step17e0_cleanup_frontend_shell_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-0 FRONTEND CLEANUP COMPLETE")
print("------------------------------------")
print(f"Legacy components archived: {len(moved)}")
print(f"Missing legacy components:  {len(missing)}")
print(f"Clean page written:         {page}")
print(f"Report JSON:                {report_path}")
print("")