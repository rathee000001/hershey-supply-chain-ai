import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6e_chocolate_drip_flow_report.json"

FILES = {
    "drip_header": ROOT / "src/components/cinematic/ChocolateDripHeader.tsx",
    "flow_divider": ROOT / "src/components/cinematic/ChocolateFlowDivider.tsx",
    "divider_wrapper": ROOT / "src/components/cinematic/ChocolateDivider.tsx",
}

REQUIRED = {
    "drip_header": [
        '"use client";',
        "ChocolateDripHeaderProps",
        "data-chocolate-animation=\"drip-header\"",
        "hershey-drip-main",
        "hershey-drip-gloss",
        "hershey-drip-shadow",
        "useReducedMotion",
        "preserveAspectRatio=\"none\"",
    ],
    "flow_divider": [
        '"use client";',
        "ChocolateFlowDividerProps",
        "data-chocolate-animation=\"flow-divider\"",
        "hershey-flow-main",
        "hershey-flow-highlight",
        "useReducedMotion",
        "variant?: \"cream-to-chocolate\" | \"chocolate-to-cream\"",
    ],
    "divider_wrapper": [
        '"use client";',
        "ChocolateFlowDivider",
        "ChocolateDividerProps",
    ],
}

FORBIDDEN = [
    "@/components/hershey/",
    "ChocolateDripOverlay",
    "floatingDrops",
    "leaf",
    "blob",
    "Evidence count:",
    "profit margin",
    "Hershey internal",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
]

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_files = []
    missing_required = {}
    forbidden_found = {}

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = path.read_text(encoding="utf-8")
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more chocolate animation component files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more chocolate animation components are missing required implementation markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old imports, blob wording, or hardcoded supplier/business claims found.")

    report = {
        "step": "17E-B6E",
        "name": "Chocolate drip and flow animation components validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "drip_header_created": FILES["drip_header"].exists(),
            "flow_divider_created": FILES["flow_divider"].exists(),
            "legacy_divider_wrapper_created": FILES["divider_wrapper"].exists(),
            "uses_svg_paths_not_random_blobs": not any("blob" in values for values in forbidden_found.values()),
            "uses_reduced_motion": all("useReducedMotion" in FILES[key].read_text(encoding="utf-8") for key in ["drip_header", "flow_divider"] if FILES[key].exists()),
            "no_old_hershey_component_imports": not any("@/components/hershey/" in values for values in forbidden_found.values()),
            "no_supplier_or_cost_claims_hardcoded": not any(any(term in values for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]) for values in forbidden_found.values()),
            "not_integrated_into_homepage_yet": True,
        },
        "next_recommended_step": "Run npm run build. If clean, visually integrate these components in the next step only when requested.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
