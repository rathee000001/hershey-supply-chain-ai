import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r3_hershey_home_lab_scene_report.json"

FILES = {
    "lab_scene": ROOT / "src/components/hershey3d/home/HersheyHomeLabScene.tsx",
    "lab_slot": ROOT / "src/components/hershey3d/home/HersheyHomeLabSceneSlot.tsx",
    "home_fallback": ROOT / "src/components/hershey3d/home/HomeHeroFallback.tsx",
    "compat_product_background": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackground.tsx",
    "compat_product_background_slot": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackgroundSlot.tsx",
    "compat_home_scene": ROOT / "src/components/hershey3d/home/HomeHeroScene.tsx",
    "compat_home_scene_slot": ROOT / "src/components/hershey3d/home/HomeHeroSceneSlot.tsx",
    "compat_hero": ROOT / "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "compat_slot": ROOT / "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
}

REQUIRED = {
    "lab_scene": [
        "data-hershey-home-background=\"portfolio-style-supply-chain-lab\"",
        "data-hershey-home-lab-scene=\"portfolio-style-background\"",
        "pointer-events-none fixed inset-0 z-[1]",
        "Canvas",
        "Line",
        "Stars",
        "Float",
        "HersheyHomeLabWorld",
        "matrixCells",
        "dataParticles",
        "nodes",
        "links",
        "bg-gradient-to-r from-[#fffaf2]",
    ],
    "lab_slot": [
        "dynamic(",
        "ssr: false",
        "HersheyHomeLabScene",
    ],
    "home_fallback": [
        "pointer-events-none fixed inset-0 z-[1]",
        "bg-gradient-to-r from-[#fffaf2]",
    ],
    "compat_product_background": [
        "HersheyHomeLabScene",
        "HomeProductCinematicBackground",
    ],
    "compat_product_background_slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
    ],
    "compat_home_scene": [
        "HersheyHomeLabScene",
        "HomeHeroScene",
    ],
    "compat_home_scene_slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
    ],
    "compat_hero": [
        "HersheyHomeLabScene",
        "HomeChocolateBarHero",
    ],
    "compat_slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
    ],
}

FORBIDDEN_ACTIVE = [
    "@ts-nocheck",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
    "ProductWrapperPlane",
    "hershey_wrapper_front.webp",
    "hershey_wrapper_back.webp",
    "hershey_unwrapped_bar.png",
    "data-home-product-background=\"right-side-page-level-product-reveal\"",
    "data-home-product-background=\"page-level-front-back-peel-reveal\"",
    "Product reveal sequence",
    "ChocolateBlockGrid",
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
        warnings.append("One or more Hershey home lab scene files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required portfolio-style scene markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden product-covering animation code, old imports, or hardcoded supplier/business claims found in active compatibility path.")

    lab_content = read(FILES["lab_scene"])

    report = {
        "step": "17E-B6F-R3",
        "name": "Portfolio-style Hershey background scene validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "portfolio_style_fixed_background_scene": "pointer-events-none fixed inset-0 z-[1]" in lab_content,
            "abstract_scene_not_product_covering": not any(asset in lab_content for asset in ["hershey_wrapper_front.webp", "hershey_wrapper_back.webp", "hershey_unwrapped_bar.png"]),
            "right_weighted_lab_composition": "position={[1.08, 0.02, 0]}" in lab_content,
            "nodes_and_links_present": "nodes" in lab_content and "links" in lab_content and "Line" in lab_content,
            "matrix_and_particles_present": "matrixCells" in lab_content and "dataParticles" in lab_content,
            "left_readability_gradient_present": "bg-gradient-to-r from-[#fffaf2]" in lab_content,
            "compatibility_paths_redirected_to_lab_scene": "HersheyHomeLabScene" in read(FILES["compat_hero"]) and "HersheyHomeLabScene" in read(FILES["compat_product_background"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in lab_content,
            "no_supplier_or_cost_claims_hardcoded": not any(term in lab_content for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect the homepage screenshot. Do not push until the background scene is visually accepted.",
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
