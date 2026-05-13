import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4c4_course_product_funnel_correction_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
}

REQUIRED = {
    "page": [
        "Spring 2026 - M01",
        "Operations Management Applications",
        "QANT_760-M01-2026SP-S",
        "Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala",
        "HomeProductShowcase",
        "HomeChocolateBarHeroSlot",
        "relative z-20",
    ],
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-front-back-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "onMouseEnter",
        "onMouseLeave",
        "max-w-[860px]",
        "sm:h-[280px]",
        "scale: 2.08",
        "Product Study Anchor",
        "JSON-first",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[-0.18, 0.08, 0]}",
        "scale={0.86}",
        "right-[9vw] w-[50vw] min-w-[640px]",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "MGMT 780 — Supply Chain Management",
    "Course: MGMT 780",
    "Course: Operations Management Applications · Professor",
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
        warnings.append("One or more patched files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required patched markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old course text, Target SKU, reveal/drip, supplier/cost claim, or legacy import marker found.")

    page = read(FILES["page"])
    showcase = read(FILES["showcase"])
    field = read(FILES["field"])

    report = {
        "step": "17E-B6F-R4C-4",
        "name": "Course text, product hero scale, and vertical funnel position correction",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "course_updated_to_spring_2026": "Spring 2026 - M01" in page,
            "course_code_present": "QANT_760-M01-2026SP-S" in page,
            "old_mgmt_780_primary_badge_removed": "MGMT 780 — Supply Chain Management" not in page,
            "academic_framing_cleaned": "Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala" in page,
            "product_scaled_larger": "scale: 2.08" in showcase and "max-w-[860px]" in showcase,
            "hover_back_wrapper_still_present": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "vertical_funnel_shifted_left": "position={[-0.18, 0.08, 0]}" in field and "right-[9vw] w-[50vw] min-w-[640px]" in field,
            "unwrapped_reveal_still_deferred_to_r4d": "hershey_unwrapped_bar.png" not in showcase,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + showcase + field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build, then inspect homepage and hover state. Next step is the portfolio-style interactive pipeline map.",
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
