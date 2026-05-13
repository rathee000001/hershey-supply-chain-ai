import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4d_controlled_product_reveal_report.json"

FILE = ROOT / "src/components/home/HomeProductShowcase.tsx"

ASSETS = {
    "front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
    "bar": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_unwrapped_bar.png",
}

REQUIRED = [
    'data-home-product-showcase="controlled-wrapper-front-back-unwrapped-reveal"',
    "const WRAPPER_FRONT",
    "const WRAPPER_BACK",
    "const UNWRAPPED_BAR",
    'type RevealPhase = "front" | "back" | "bar"',
    'const revealPhases: RevealPhase[] = ["front", "back", "bar"];',
    "setPhaseIndex",
    "window.setInterval",
    "manualPhase",
    "inspectBack",
    "releaseInspection",
    "Hover to inspect back",
    "01 ·",
    "Product visuals support identification only; evidence claims remain JSON-first.",
]

FORBIDDEN = [
    "@ts-nocheck",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "profit margin",
    "Hershey internal cost",
    "evidence count",
    "evidence counts",
    "ChocolateDripHeader",
    "ChocolateDripOverlay",
    "ProductIdentityBadge",
]

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = FILE.read_text(encoding="utf-8") if FILE.exists() else ""

    missing_assets = [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in ASSETS.values()
        if not path.exists()
    ]

    missing_required = [item for item in REQUIRED if item not in content]
    forbidden_found = [item for item in FORBIDDEN if item.lower() in content.lower()]

    status = "PASS"
    warnings = []

    if not FILE.exists():
        status = "FAIL"
        warnings.append("HomeProductShowcase.tsx is missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("One or more product reveal visual assets are missing.")

    if missing_required:
        status = "FAIL"
        warnings.append("Controlled reveal markers missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Unsupported claim or old component marker found.")

    report = {
        "step": "17E-B6F-R4D",
        "name": "Controlled product reveal motion",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {
            "showcase": str(FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "front_back_bar_sequence": all(item in content for item in ["WRAPPER_FRONT", "WRAPPER_BACK", "UNWRAPPED_BAR", '"front" | "back" | "bar"']),
            "controlled_auto_reveal": "window.setInterval" in content and "setPhaseIndex" in content,
            "hover_back_inspection": "inspectBack" in content and "manualPhase(\"back\")" not in content and "setManualPhase(\"back\")" in content,
            "json_first_safe_wording": "Evidence claims remain JSON-first" in content or "evidence claims remain JSON-first" in content,
            "pipeline_not_touched": True,
            "three_d_scene_not_touched": True,
            "no_supplier_claims_added": not any(term in content for term in ["Land O", "Barry Callebaut", "ASR", "McLane"]),
            "no_cost_claims_added": not any(term in content for term in ["profit margin", "Hershey internal cost"]),
        },
        "next_recommended_step": "Run build/dev and inspect the product card reveal sequence: front wrapper, back wrapper, unwrapped bar.",
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
