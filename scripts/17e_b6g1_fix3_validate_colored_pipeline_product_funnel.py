import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix3_colored_pipeline_product_funnel_report.json"

FILES = {
    "pipeline_map": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "page": ROOT / "src/app/page.tsx",
}

REQUIRED = {
    "pipeline_map": [
        "data-home-intelligence-pipeline=\"portfolio-style-interactive-map-colored-connections\"",
        "accent",
        "soft",
        "border",
        "routePaths",
        "pipelineRouteGlowStrong",
        "strokeWidth=\"6\"",
        "strokeDasharray=\"46 430\"",
        "activeIndex",
        "onMouseEnter",
        "onFocus",
        "onClick",
        "Decorative visuals do not create claims",
    ],
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-contained-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "Product Study Anchor",
        "max-h-[88%]",
        "w-[96%]",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[0.06, 0.08, 0]}",
        "scale={0.82}",
        "right-[2vw] w-[44vw] min-w-[560px]",
    ],
    "page": [
        "HomeIntelligencePipelineMap",
        "<HomeIntelligencePipelineMap />",
        "Spring 2026 - M01",
        "Operations Management Applications",
        "QANT_760-M01-2026SP-S",
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
    "w-[118%]",
    "scale: 1.18",
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
        warnings.append("One or more colored pipeline/product/funnel files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required colored pipeline/product/funnel markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old pipeline, oversized product, old course, unsupported claim, reveal/drip, or legacy marker found.")

    pipeline = read(FILES["pipeline_map"])
    showcase = read(FILES["showcase"])
    field = read(FILES["field"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6G-1-FIX-3",
        "name": "Colored interactive pipeline, contained product showcase, and right-balanced 3D funnel",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "pipeline_color_themes_present": all(term in pipeline for term in ["accent", "soft", "border"]),
            "pipeline_lines_stronger": "strokeWidth=\"6\"" in pipeline and "strokeDasharray=\"46 430\"" in pipeline,
            "pipeline_interactive_nodes_present": all(term in pipeline for term in ["onMouseEnter", "onFocus", "onClick"]),
            "pipeline_active_route_logic_present": "activeIndex" in pipeline,
            "product_showcase_recontained": "max-h-[88%]" in showcase and "w-[96%]" in showcase,
            "hover_back_wrapper_kept": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "oversized_product_removed": not any(term in showcase for term in ["w-[170%]", "scale: 2.08", "w-[118%]", "scale: 1.18"]),
            "funnel_right_balanced": "position={[0.06, 0.08, 0]}" in field and "right-[2vw] w-[44vw] min-w-[560px]" in field,
            "interactive_pipeline_still_on_home": "<HomeIntelligencePipelineMap />" in page,
            "course_text_still_correct": "Spring 2026 - M01" in page and "QANT_760-M01-2026SP-S" in page,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + pipeline + showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + pipeline + showcase + field,
        },
        "next_recommended_step": "Clear .next, run npm run build, then inspect pipeline motion and hero product/funnel balance.",
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
