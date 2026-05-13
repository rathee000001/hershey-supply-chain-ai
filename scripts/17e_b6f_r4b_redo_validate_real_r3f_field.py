import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4b_redo_real_r3f_field_report.json"

FILES = {
    "field_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "atmosphere_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainAtmosphereScene.tsx",
    "readable_atmosphere": ROOT / "src/components/hershey3d/home/HersheyHomeReadableAtmosphere.tsx",
    "lab_scene": ROOT / "src/components/hershey3d/home/HersheyHomeLabScene.tsx",
    "home_scene": ROOT / "src/components/hershey3d/home/HomeHeroScene.tsx",
    "compat_hero": ROOT / "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "compat_slot": ROOT / "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
    "page": ROOT / "src/app/page.tsx",
}

REQUIRED = {
    "field_scene": [
        "data-hershey-home-background=\"real-r3f-supply-chain-field\"",
        "data-hershey-scene-world=\"supply-chain-field\"",
        "Canvas",
        "useFrame",
        "Float",
        "Line",
        "Stars",
        "StreamRoute",
        "StreamParticle",
        "getBezierPoint",
        "HersheySupplyChainFieldWorld",
        "cocoa",
        "milk",
        "sugar",
        "evidence",
        "cost",
        "absolute inset-y-0 right-0 w-[62vw]",
    ],
    "atmosphere_scene": [
        "HersheySupplyChainFieldScene",
    ],
    "readable_atmosphere": [
        "HersheySupplyChainFieldScene",
    ],
    "lab_scene": [
        "HersheySupplyChainFieldScene",
    ],
    "home_scene": [
        "HersheySupplyChainFieldScene",
    ],
    "compat_hero": [
        "HersheySupplyChainFieldScene",
    ],
    "compat_slot": [
        "dynamic(",
        "ssr: false",
    ],
    "page": [
        "HomeChocolateBarHeroSlot",
        "<HomeChocolateBarHeroSlot />",
        "relative z-20",
        "hidden lg:block",
        "bg-white/94",
    ],
}

FORBIDDEN_ACTIVE = [
    "@ts-nocheck",
    "Sources",
    "Parser",
    "Audit",
    "Frontend",
    "data-hershey-home-background=\"right-only-supply-chain-atmosphere\"",
    "data-hershey-home-background=\"portfolio-style-supply-chain-lab\"",
    "HersheyHomeLabWorld",
    "matrixCells",
    "dataParticles",
    "Product reveal sequence",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
    "ProductWrapperPlane",
    "hershey_wrapper_front.webp",
    "hershey_wrapper_back.webp",
    "hershey_unwrapped_bar.png",
    "Target SKU",
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
        forbidden_found[key] = [item for item in FORBIDDEN_ACTIVE if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more real R3F field files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required real R3F field markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden label/SVG/product-covering/drip/supplier/cost claim markers found.")

    field = read(FILES["field_scene"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6F-R4B-REDO",
        "name": "Real Hershey R3F supply-chain field background validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "real_r3f_scene_present": "Canvas" in field and "useFrame" in field and "Line" in field,
            "right_side_scene_region": "absolute inset-y-0 right-0 w-[62vw]" in field,
            "hershey_specific_streams_present": all(term in field for term in ["cocoa", "milk", "sugar", "evidence", "cost"]),
            "no_text_labels_inside_background": not any(term in field for term in ["Sources", "Parser", "Audit", "Frontend"]),
            "no_product_assets_in_background": not any(asset in field for asset in ["hershey_wrapper_front.webp", "hershey_wrapper_back.webp", "hershey_unwrapped_bar.png"]),
            "page_uses_portfolio_layering": "<HomeChocolateBarHeroSlot />" in page and "relative z-20" in page,
            "right_hero_column_left_open_for_scene": "hidden lg:block" in page,
            "cards_strengthened_above_background": "bg-white/94" in page,
            "target_sku_disabled": "Target SKU" not in page,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot/video. Do not push until the background looks like a real Hershey motion field and stays behind content.",
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
