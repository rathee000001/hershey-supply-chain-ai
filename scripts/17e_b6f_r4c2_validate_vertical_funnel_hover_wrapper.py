import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4c2_vertical_funnel_hover_wrapper_report.json"

FILES = {
    "field_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "page": ROOT / "src/app/page.tsx",
}

ASSETS = {
    "wrapper_front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "wrapper_back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
}

REQUIRED = {
    "field_scene": [
        "data-hershey-home-background=\"vertical-evidence-funnel-intelligence-field\"",
        "data-hershey-scene-world=\"vertical-evidence-funnel-intelligence-field\"",
        "getVerticalFunnelPoint",
        "Canvas",
        "useFrame",
        "Float",
        "Line",
        "Stars",
        "absolute inset-y-0 right-0 w-[42vw]",
        "position={[1.52, 0.08, 0]}",
    ],
    "showcase": [
        "data-home-product-showcase=\"right-side-wrapper-front-back-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "hershey_wrapper_front.webp",
        "hershey_wrapper_back.webp",
        "showBack",
        "onMouseEnter",
        "onMouseLeave",
        "AnimatePresence",
        "Hover to inspect back",
        "Visual identity",
        "JSON-first",
    ],
    "page": [
        "HomeProductShowcase",
        "HomeChocolateBarHeroSlot",
        "<HomeChocolateBarHeroSlot />",
        "<HomeProductShowcase />",
        "relative z-20",
        "lg:grid-cols-[0.82fr_1.18fr]",
        "max-w-[650px]",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "Target SKU",
    "ProductIdentityBadge",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
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
        warnings.append("One or more vertical funnel / hover wrapper files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("Wrapper front/back asset missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required vertical funnel / hover wrapper markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old badge, reveal, drip, unwrapped bar, or hardcoded supplier/business claim markers found.")

    field = read(FILES["field_scene"])
    showcase = read(FILES["showcase"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6F-R4C-2",
        "name": "Vertical background funnel and hover back-wrapper showcase validation",
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
            "vertical_funnel_background_present": "getVerticalFunnelPoint" in field and "vertical-evidence-funnel-intelligence-field" in field,
            "background_region_narrowed_right": "absolute inset-y-0 right-0 w-[42vw]" in field,
            "wrapper_front_and_back_hover_present": "WRAPPER_FRONT" in showcase and "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "front_asset_used": "hershey_wrapper_front.webp" in showcase,
            "back_asset_used": "hershey_wrapper_back.webp" in showcase,
            "unwrapped_bar_deferred_to_r4d": "hershey_unwrapped_bar.png" not in showcase,
            "page_layout_adjusted_for_visibility": "lg:grid-cols-[0.82fr_1.18fr]" in page and "max-w-[650px]" in page,
            "background_scene_still_behind_content": "<HomeChocolateBarHeroSlot />" in page and "relative z-20" in page,
            "target_sku_badge_not_restored": "Target SKU" not in page + showcase,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + showcase + field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot and hover behavior. Do not push until layout and hover swap are accepted.",
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
