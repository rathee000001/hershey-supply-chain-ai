import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix5_overview_product_pipeline_funnel_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "overview": ROOT / "src/components/home/HomeProjectOverviewSection.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "pipeline": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
}

REQUIRED = {
    "page": [
        "HomeProjectOverviewSection",
        "<HomeProjectOverviewSection />",
        "HomeIntelligencePipelineMap",
        "<HomeIntelligencePipelineMap />",
    ],
    "overview": [
        "data-home-project-overview=\"colorful-interactive-overview\"",
        "activeId",
        "setActiveId",
        "Public Evidence Brain",
        "Supply Chain Map",
        "Benchmark Cost Logic",
        "Cinematic Interface",
        "accent",
        "soft",
        "border",
    ],
    "showcase": [
        "data-home-product-showcase=\"contained-large-wrapper-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "w-[168%]",
        "sm:h-[340px]",
        "Product Study Anchor",
    ],
    "pipeline": [
        "data-home-intelligence-pipeline=\"icon-first-colored-flow-map\"",
        "pipelineRouteGlowIconFirst",
        "strokeWidth=\"5\"",
        "strokeDasharray=\"52 390\"",
        "h-16 w-16",
        "Icon size={30}",
        "onMouseEnter",
        "onFocus",
        "onClick",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[0.42, 0.08, 0]}",
        "scale={0.78}",
        "right-[-6vw] w-[42vw] min-w-[520px]",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "MGMT 780",
    "pipelineItems",
    "Target SKU",
    "ProductIdentityBadge",
    "hershey_unwrapped_bar.png",
    "ChocolateDripHeader",
    "ChocolateDripOverlay",
    "@/components/hershey/",
    "profit margin",
    "Hershey internal cost",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "evidence count",
    "evidence counts",
    "w-[170%]",
    "scale: 2.08",
]

def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_files = []
    missing_required = {}
    forbidden_found = {}

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = read(path)
        missing_required[key] = [item for item in REQUIRED.get(key, []) if item not in content]
        lower_content = content.lower()
        forbidden_found[key] = [item for item in FORBIDDEN if item.lower() in lower_content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more fix-5 files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required fix-5 markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old pipeline, old course, unsupported claim, reveal/drip, oversized product, or legacy marker found.")

    page = read(FILES["page"])
    overview = read(FILES["overview"])
    showcase = read(FILES["showcase"])
    pipeline = read(FILES["pipeline"])
    field = read(FILES["field"])

    report = {
        "step": "17E-B6G-1-FIX-5",
        "name": "Bigger product visual, right-edge 3D funnel, colorful overview, icon-first pipeline",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "page_uses_colorful_overview": "<HomeProjectOverviewSection />" in page,
            "overview_is_interactive_and_colored": "activeId" in overview and "accent" in overview and "setActiveId" in overview,
            "product_image_bigger_but_contained": "w-[168%]" in showcase and "overflow-hidden" in showcase,
            "hover_back_wrapper_kept": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "pipeline_small_descriptions_removed_from_nodes": "{step.summary}" not in pipeline and "summary:" not in pipeline,
            "pipeline_icons_larger": "h-16 w-16" in pipeline and "Icon size={30}" in pipeline,
            "pipeline_connections_colored": "pipelineRouteGlowIconFirst" in pipeline and "strokeDasharray=\"52 390\"" in pipeline,
            "funnel_starts_after_product_card_edge": "position={[0.42, 0.08, 0]}" in field and "right-[-6vw] w-[42vw] min-w-[520px]" in field,
            "course_text_still_correct": "Spring 2026 - M01" in page and "QANT_760-M01-2026SP-S" in page,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + overview + showcase + pipeline + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + overview + showcase + pipeline + field,
        },
        "next_recommended_step": "Clear .next, run npm run build, then inspect hero product/funnel layout, overview cards, and pipeline interaction.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
