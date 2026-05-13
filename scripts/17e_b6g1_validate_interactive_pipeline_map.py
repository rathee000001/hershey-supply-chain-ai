import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_interactive_pipeline_map_report.json"

FILES = {
    "pipeline_map": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
    "page": ROOT / "src/app/page.tsx",
}

REQUIRED = {
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
        "JSON-first",
        "Decorative visuals do not create claims",
    ],
    "page": [
        "HomeIntelligencePipelineMap",
        "<HomeIntelligencePipelineMap />",
        "Spring 2026 - M01",
        "Operations Management Applications",
        "QANT_760-M01-2026SP-S",
        "HomeProductShowcase",
        "HomeChocolateBarHeroSlot",
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
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more interactive pipeline files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required interactive pipeline markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old pipeline, old course, unsupported claim, reveal/drip, or legacy marker found.")

    pipeline = read(FILES["pipeline_map"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6G-1",
        "name": "Portfolio-style interactive intelligence pipeline map",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "interactive_pipeline_component_created": "HomeIntelligencePipelineMap" in pipeline,
            "hover_focus_click_interaction_present": all(term in pipeline for term in ["onMouseEnter", "onFocus", "onClick"]),
            "connected_map_paths_present": "routePaths" in pipeline and "motion.path" in pipeline,
            "all_seven_pipeline_steps_present": all(term in pipeline for term in [
                "Raw public sources",
                "Parser + OCR memory",
                "RAG/vector evidence index",
                "Evidence audit",
                "Supplier/ingredient packets",
                "Cost model artifacts",
                "3D cinematic frontend",
            ]),
            "page_uses_pipeline_component": "<HomeIntelligencePipelineMap />" in page,
            "old_static_pipeline_items_removed": "pipelineItems" not in page,
            "course_kept_correct": "Spring 2026 - M01" in page and "QANT_760-M01-2026SP-S" in page,
            "no_supplier_or_cost_claims_hardcoded": not any(term in pipeline + page for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "no_evidence_counts_hardcoded": "evidence counts" not in (pipeline + page).lower() and "evidence count" not in (pipeline + page).lower(),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + pipeline,
        },
        "next_recommended_step": "Run npm run build. Then inspect the homepage pipeline interaction.",
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
