import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix2_animated_pipeline_balance_report.json"

FILES = {
    "pipeline_map": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "page": ROOT / "src/app/page.tsx",
}

REQUIRED = {
    "pipeline_map": [
        "data-home-intelligence-pipeline=\"portfolio-style-interactive-map-animated-connections\"",
        "routePaths",
        "strokeWidth=\"4\"",
        "strokeDasharray=\"42 420\"",
        "pipelineRouteGlow",
        "PipelineNode",
        "whileHover={{ y: -6, scale: 1.015 }}",
        "animate=",
        "onMouseEnter",
        "onFocus",
        "onClick",
        "Decorative visuals do not create claims",
    ],
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-front-back-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "w-[118%]",
        "scale: 1.18",
        "Product Study Anchor",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[-0.42, 0.08, 0]}",
        "scale={0.84}",
        "right-[7vw] w-[50vw] min-w-[660px]",
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
        warnings.append("One or more animated pipeline balance files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required animated pipeline/product/funnel markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old pipeline, oversized product, old course, unsupported claim, reveal/drip, or legacy marker found.")

    pipeline = read(FILES["pipeline_map"])
    showcase = read(FILES["showcase"])
    field = read(FILES["field"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6G-1-FIX-2",
        "name": "Animated pipeline connections, balanced 3D funnel, and product scale correction",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "pipeline_lines_stronger": "strokeWidth=\"4\"" in pipeline and "strokeDasharray=\"42 420\"" in pipeline,
            "pipeline_flow_animation_present": "pipelineRouteGlow" in pipeline and "strokeDashoffset" in pipeline,
            "pipeline_cards_animated": "whileHover={{ y: -6, scale: 1.015 }}" in pipeline and "animate=" in pipeline,
            "interactive_pipeline_still_on_home": "<HomeIntelligencePipelineMap />" in page,
            "product_scale_rebalanced": "w-[118%]" in showcase and "scale: 1.18" in showcase,
            "oversized_product_removed": "w-[170%]" not in showcase and "scale: 2.08" not in showcase,
            "funnel_position_rebalanced": "position={[-0.42, 0.08, 0]}" in field and "right-[7vw] w-[50vw] min-w-[660px]" in field,
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
