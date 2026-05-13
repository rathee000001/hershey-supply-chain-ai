import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4c_right_side_product_showcase_report.json"

FILES = {
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "page": ROOT / "src/app/page.tsx",
}

ASSETS = {
    "wrapper_front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
}

REQUIRED = {
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-front\"",
        "WRAPPER_FRONT",
        "hershey_wrapper_front.webp",
        "Product Visual Anchor",
        "Cinematic study UI",
        "Visual identity only",
        "JSON-first",
        "motion.div",
        "useReducedMotion",
    ],
    "page": [
        "HomeProductShowcase",
        "HomeChocolateBarHeroSlot",
        "<HomeChocolateBarHeroSlot />",
        "<HomeProductShowcase />",
        "relative z-20",
        "lg:grid-cols-[0.86fr_1.14fr]",
        "bg-white/94",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "Target SKU",
    "ProductIdentityBadge",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
    "hershey_wrapper_back.webp",
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
        warnings.append("One or more right-side product showcase files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("Required wrapper front asset is missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required product showcase markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden Target SKU badge, reveal motion, drip integration, or hardcoded supplier/business claims found.")

    showcase = read(FILES["showcase"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6F-R4C",
        "name": "Right-side hero product showcase validation",
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
            "wrapper_front_asset_used": "hershey_wrapper_front.webp" in showcase,
            "only_front_wrapper_used_this_step": "hershey_wrapper_back.webp" not in showcase and "hershey_unwrapped_bar.png" not in showcase,
            "right_side_showcase_component_present": "data-home-product-showcase=\"right-side-wrapper-front\"" in showcase,
            "page_integrates_showcase_in_hero": "<HomeProductShowcase />" in page,
            "background_scene_still_present": "<HomeChocolateBarHeroSlot />" in page,
            "portfolio_layering_kept": "relative z-20" in page,
            "target_sku_badge_not_restored": "Target SKU" not in page + showcase,
            "controlled_reveal_deferred_to_r4d": "HomeProductRevealSequence" not in page + showcase,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + showcase,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + showcase for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot. Do not push until the wrapper showcase looks right-side, contained, and readable.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_files": missing_files,
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
