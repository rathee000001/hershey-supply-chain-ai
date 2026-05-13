import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4c3_course_product_funnel_patch_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
}

ASSETS = {
    "wrapper_front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "wrapper_back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
}

REQUIRED = {
    "page": [
        "Spring 2026 - M01",
        "Operations Management Applications",
        "QANT_760-M01-2026SP-S",
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
        "max-w-[820px]",
        "h-[250px]",
        "sm:h-[285px]",
        "inset-[-18%]",
        "h-[136%]",
        "w-[136%]",
        "Product Study Anchor",
    ],
    "field": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "position={[0.62, 0.08, 0]}",
        "scale={0.9}",
        "right-[2vw] w-[48vw] min-w-[620px]",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "MGMT 780 — Supply Chain Management",
    "Course: MGMT 780",
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
    missing_assets = []
    missing_required = {}
    forbidden_found = {}

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = read(path)
        missing_required[key] = [item for item in REQUIRED.get(key, []) if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    for key, path in ASSETS.items():
        if not path.exists():
            missing_assets.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more patched files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("Wrapper front/back asset missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required patched markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old course, badge, unwrapped reveal, drip, or hardcoded claim marker found.")

    page = read(FILES["page"])
    showcase = read(FILES["showcase"])
    field = read(FILES["field"])

    report = {
        "step": "17E-B6F-R4C-3",
        "name": "Course, product scale, and vertical funnel position patch",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "assets_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in ASSETS.items()},
        "rules_confirmed": {
            "course_updated": "QANT_760-M01-2026SP-S" in page and "Operations Management Applications" in page,
            "old_mgmt_course_removed_from_home": "MGMT 780 — Supply Chain Management" not in page,
            "product_showcase_larger": "max-w-[820px]" in showcase and "h-[136%]" in showcase,
            "hover_back_wrapper_still_present": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "vertical_funnel_shifted_left": "position={[0.62, 0.08, 0]}" in field,
            "funnel_canvas_more_visible": "right-[2vw] w-[48vw] min-w-[620px]" in field,
            "unwrapped_reveal_still_deferred_to_r4d": "hershey_unwrapped_bar.png" not in showcase,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + showcase + field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build, then inspect homepage and hover state.",
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
