import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4b_subtle_supply_chain_atmosphere_report.json"

FILES = {
    "atmosphere_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainAtmosphereScene.tsx",
    "readable_atmosphere": ROOT / "src/components/hershey3d/home/HersheyHomeReadableAtmosphere.tsx",
    "lab_scene": ROOT / "src/components/hershey3d/home/HersheyHomeLabScene.tsx",
    "lab_slot": ROOT / "src/components/hershey3d/home/HersheyHomeLabSceneSlot.tsx",
    "product_background": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackground.tsx",
    "product_background_slot": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackgroundSlot.tsx",
    "home_scene": ROOT / "src/components/hershey3d/home/HomeHeroScene.tsx",
    "home_scene_slot": ROOT / "src/components/hershey3d/home/HomeHeroSceneSlot.tsx",
    "fallback": ROOT / "src/components/hershey3d/home/HomeHeroFallback.tsx",
    "compat_hero": ROOT / "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "compat_slot": ROOT / "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
}

REQUIRED = {
    "atmosphere_scene": [
        "data-hershey-home-background=\"right-only-supply-chain-atmosphere\"",
        "motion.svg",
        "routeArcs",
        "particles",
        "pulseNodes",
        "viewBox=\"0 0 700 560\"",
        "absolute inset-y-0 right-0 w-[58vw]",
        "useReducedMotion",
        "Sources",
        "Parser",
        "Audit",
        "Cost",
        "Frontend",
    ],
    "readable_atmosphere": [
        "HersheySupplyChainAtmosphereScene",
        "HersheyHomeReadableAtmosphere",
    ],
    "lab_scene": [
        "HersheySupplyChainAtmosphereScene",
        "HersheyHomeLabScene",
    ],
    "product_background": [
        "HersheySupplyChainAtmosphereScene",
        "HomeProductCinematicBackground",
    ],
    "home_scene": [
        "HersheySupplyChainAtmosphereScene",
        "HomeHeroScene",
    ],
    "compat_hero": [
        "HersheySupplyChainAtmosphereScene",
        "HomeChocolateBarHero",
    ],
    "lab_slot": [
        "dynamic(",
        "ssr: false",
    ],
    "product_background_slot": [
        "dynamic(",
        "ssr: false",
    ],
    "home_scene_slot": [
        "dynamic(",
        "ssr: false",
    ],
    "compat_slot": [
        "dynamic(",
        "ssr: false",
    ],
    "fallback": [
        "return null",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "Canvas",
    "Line",
    "Stars",
    "HersheyHomeLabWorld",
    "matrixCells",
    "dataParticles",
    "boxGeometry",
    "sphereGeometry",
    "torusGeometry",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
    "ProductWrapperPlane",
    "hershey_wrapper_front.webp",
    "hershey_wrapper_back.webp",
    "hershey_unwrapped_bar.png",
    "Target SKU",
    "Hershey 1.55 oz Milk Chocolate",
    "bg-gradient-to-r from-[#fffaf2]",
    "bg-gradient-to-t from-[#f8f1e7]",
    "inset-y-0 left-0",
    "data-home-product-background=\"right-side-page-level-product-reveal\"",
    "data-home-product-background=\"page-level-front-back-peel-reveal\"",
    "data-hershey-home-background=\"portfolio-style-supply-chain-lab\"",
    "ChocolateDripOverlay",
    "ChocolateDripHeader",
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
        warnings.append("One or more supply-chain atmosphere files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required atmosphere markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden canvas/product-covering overlay/transparent wash/claims found.")

    atmosphere = read(FILES["atmosphere_scene"])

    report = {
        "step": "17E-B6F-R4B",
        "name": "Subtle Hershey supply-chain atmosphere scene validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "right_only_scene_region": "absolute inset-y-0 right-0 w-[58vw]" in atmosphere,
            "framer_motion_svg_scene": "motion.svg" in atmosphere and "routeArcs" in atmosphere,
            "no_left_transparent_wash": "inset-y-0 left-0" not in atmosphere and "bg-gradient-to-r from-[#fffaf2]" not in atmosphere,
            "no_bottom_transparent_wash": "bg-gradient-to-t from-[#f8f1e7]" not in atmosphere,
            "no_canvas_or_copied_portfolio_nodes": not any(term in atmosphere for term in ["Canvas", "Line", "Stars", "boxGeometry", "sphereGeometry", "torusGeometry"]),
            "no_product_assets_in_background": not any(asset in atmosphere for asset in ["hershey_wrapper_front.webp", "hershey_wrapper_back.webp", "hershey_unwrapped_bar.png"]),
            "target_sku_still_disabled": "Target SKU" not in atmosphere,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in atmosphere,
            "no_supplier_or_cost_claims_hardcoded": not any(term in atmosphere for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot. Continue only if the atmosphere is subtle and does not wash over text/cards.",
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
