import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix6_product_funnel_pipeline_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "pipeline": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "overview": ROOT / "src/components/home/HomeProjectOverviewSection.tsx",
}

ASSETS = {
    "front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
}

REQUIRED = {
    "page": [
        "HomeProjectOverviewSection",
        "<HomeProjectOverviewSection />",
        "HomeIntelligencePipelineMap",
        "<HomeIntelligencePipelineMap />",
    ],
    "showcase": [
        "data-home-product-showcase=\"visible-large-wrapper-hover-fixed-transform\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "w-[154%]",
        "sm:h-[345px]",
        "flex h-full w-full items-center justify-center",
        "Product Study Anchor",
    ],
    "pipeline": [
        "data-home-intelligence-pipeline=\"absolute-card-map-direct-pulsing-connectors\"",
        "nodePositions",
        "directPipelinePulseGlow",
        "strokeWidth=\"7\"",
        "strokeDasharray=\"58 380\"",
        "absolute w-[205px]",
        "onMouseEnter",
        "onFocus",
        "onClick",
    ],
    "field": [
        "data-hershey-home-background=\"right-edge-vertical-evidence-funnel-intelligence-field\"",
        "right-[-14vw] z-0 hidden w-[44vw] min-w-[560px]",
        "EvidenceFunnel",
        "makeHelix",
    ],
    "overview": [
        "data-home-project-overview=\"colorful-interactive-overview\"",
        "activeId",
        "setActiveId",
        "accent",
        "soft",
        "border",
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
    missing_assets = []
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

    for key, path in ASSETS.items():
        if not path.exists():
            missing_assets.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more fix-6 files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("Wrapper front/back asset missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required fix-6 markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old pipeline, old course, unsupported claim, reveal/drip, oversized product, or legacy marker found.")

    page = read(FILES["page"])
    showcase = read(FILES["showcase"])
    pipeline = read(FILES["pipeline"])
    field = read(FILES["field"])
    overview = read(FILES["overview"])

    report = {
        "step": "17E-B6G-1-FIX-6",
        "name": "Restore product image, shift right-edge 3D funnel, and direct pulsing pipeline connectors",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "product_image_transform_conflict_removed": "flex h-full w-full items-center justify-center" in showcase and "className=\"h-auto w-[154%]" in showcase,
            "product_hover_back_kept": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "right_edge_3d_funnel_applied": "right-[-14vw] z-0 hidden w-[44vw] min-w-[560px]" in field,
            "pipeline_direct_connectors_present": "nodePositions" in pipeline and "directPipelinePulseGlow" in pipeline,
            "pipeline_live_pulsing_line_present": "strokeDasharray=\"58 380\"" in pipeline and "strokeDashoffset" in pipeline,
            "pipeline_nodes_absolute_for_clean_lines": "absolute w-[205px]" in pipeline,
            "overview_section_on_home": "<HomeProjectOverviewSection />" in page,
            "overview_interactive_colored": "activeId" in overview and "setActiveId" in overview and "accent" in overview,
            "course_text_still_correct": "Spring 2026 - M01" in page and "QANT_760-M01-2026SP-S" in page,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + overview + showcase + pipeline + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + overview + showcase + pipeline + field,
        },
        "next_recommended_step": "Clear .next, run npm run build, then inspect hero product image, right-edge 3D funnel, and pipeline pulsing connectors.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
