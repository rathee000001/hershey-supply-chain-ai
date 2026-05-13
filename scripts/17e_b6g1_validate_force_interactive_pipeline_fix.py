import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_force_interactive_pipeline_fix_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "pipeline_map": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
}

REQUIRED = {
    "page": [
        "HomeIntelligencePipelineMap",
        "<HomeIntelligencePipelineMap />",
        "Spring 2026 - M01",
        "Operations Management Applications",
        "QANT_760-M01-2026SP-S",
        "HomeProductShowcase",
        "HomeChocolateBarHeroSlot",
    ],
    "pipeline_map": [
        "data-home-intelligence-pipeline=\"portfolio-style-interactive-map\"",
        "pipelineSteps",
        "activeId",
        "setActiveId",
        "routePaths",
        "PipelineNode",
        "onMouseEnter",
        "onFocus",
        "onClick",
        "Raw public sources",
        "Parser + OCR memory",
        "RAG/vector evidence index",
        "Evidence audit",
        "Supplier/ingredient packets",
        "Cost model artifacts",
        "3D cinematic frontend",
        "Decorative visuals do not create claims",
    ],
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-front-back-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "Product Study Anchor",
        "w-[170%]",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[-0.85, 0.08, 0]}",
        "scale={0.84}",
        "right-[14vw] w-[54vw] min-w-[700px]",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "MGMT 780",
    "pipelineItems",
    "Professor: Dr. Rajendra Tibrewala",
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
        warnings.append("One or more forced pipeline fix files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required forced pipeline fix markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old static pipeline, old course, old professor line, unsupported claim, reveal/drip, or legacy marker found.")

    page = read(FILES["page"])
    pipeline = read(FILES["pipeline_map"])
    showcase = read(FILES["showcase"])
    field = read(FILES["field"])

    report = {
        "step": "17E-B6G-1-FIX",
        "name": "Force interactive pipeline map, course cleanup, product scale, and left-shift 3D funnel",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "homepage_uses_interactive_pipeline": "<HomeIntelligencePipelineMap />" in page,
            "old_static_pipeline_removed": "pipelineItems" not in page,
            "interactive_pipeline_created": "PipelineNode" in pipeline and "onMouseEnter" in pipeline and "onClick" in pipeline,
            "course_text_clean": "Spring 2026 - M01" in page and "QANT_760-M01-2026SP-S" in page and "MGMT 780" not in page,
            "old_professor_line_removed_from_academic_framing": "Professor: Dr. Rajendra Tibrewala" not in page,
            "product_wrapper_scaled": "w-[170%]" in showcase,
            "hover_back_wrapper_kept": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "funnel_shifted_left": "position={[-0.85, 0.08, 0]}" in field and "right-[14vw] w-[54vw] min-w-[700px]" in field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + pipeline + showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + pipeline + showcase + field,
        },
        "next_recommended_step": "Clear .next, run npm run build, then inspect the homepage pipeline and hero.",
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
