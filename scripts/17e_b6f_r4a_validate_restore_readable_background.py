import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4a_restore_readable_background_report.json"

FILES = {
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
    "readable_atmosphere": [
        '"use client";',
        "data-hershey-home-background=\"readable-soft-atmosphere-reset\"",
        "motion",
        "useReducedMotion",
        "goldDust",
        "routeLines",
        "bg-gradient-to-r from-[#fffaf2]",
    ],
    "lab_scene": [
        "HersheyHomeReadableAtmosphere",
        "HersheyHomeLabScene",
    ],
    "product_background": [
        "HersheyHomeReadableAtmosphere",
        "HomeProductCinematicBackground",
    ],
    "home_scene": [
        "HersheyHomeReadableAtmosphere",
        "HomeHeroScene",
    ],
    "compat_hero": [
        "HersheyHomeReadableAtmosphere",
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

FORBIDDEN_ACTIVE = [
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
    "data-home-product-background=\"right-side-page-level-product-reveal\"",
    "data-home-product-background=\"page-level-front-back-peel-reveal\"",
    "data-hershey-home-background=\"portfolio-style-supply-chain-lab\"",
    "Product reveal sequence",
    "@/components/hershey/",
    "ChocolateDripOverlay",
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
        warnings.append("One or more reset/readable background files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required reset markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden active 3D/product-covering code or hardcoded supplier/business claims found.")

    readable_content = read(FILES["readable_atmosphere"])

    report = {
        "step": "17E-B6F-R4A",
        "name": "Disable bad scene and restore readable Hershey background foundation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "bad_canvas_scene_disabled_from_active_path": not any("Canvas" in values for values in forbidden_found.values()),
            "product_covering_assets_disabled_from_active_path": not any(any(asset in values for asset in ["hershey_wrapper_front.webp", "hershey_wrapper_back.webp", "hershey_unwrapped_bar.png"]) for values in forbidden_found.values()),
            "readable_soft_background_present": "readable-soft-atmosphere-reset" in readable_content,
            "framer_motion_used_for_subtle_motion": "motion" in readable_content and "useReducedMotion" in readable_content,
            "no_dark_lab_rectangle": "boxGeometry" not in readable_content,
            "no_huge_nodes_or_portfolio_copy": "sphereGeometry" not in readable_content and "torusGeometry" not in readable_content,
            "left_readability_gradient_present": "bg-gradient-to-r from-[#fffaf2]" in readable_content,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in readable_content,
            "no_supplier_or_cost_claims_hardcoded": not any(term in readable_content for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot and confirm readability before moving to Step 17E-B6F-R4B.",
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
