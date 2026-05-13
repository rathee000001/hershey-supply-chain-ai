import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r1_page_level_product_reveal_report.json"

FILES = {
    "background": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackground.tsx",
    "background_slot": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackgroundSlot.tsx",
    "sequence": ROOT / "src/components/hershey3d/home/HomeProductRevealSequence.tsx",
    "atmosphere": ROOT / "src/components/hershey3d/home/HomeProductAtmosphere.tsx",
    "peel": ROOT / "src/components/hershey3d/home/WrapperPeelPanels.tsx",
    "wrapper_plane": ROOT / "src/components/hershey3d/home/ProductWrapperPlane.tsx",
    "bar_plane": ROOT / "src/components/hershey3d/home/UnwrappedBarPlane.tsx",
    "fallback": ROOT / "src/components/hershey3d/home/HomeHeroFallback.tsx",
    "compat_hero": ROOT / "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "compat_slot": ROOT / "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
}

ASSETS = {
    "wrapper_front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "wrapper_back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
    "unwrapped_bar": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_unwrapped_bar.png",
}

REQUIRED = {
    "background": [
        "data-home-product-background=\"page-level-front-back-peel-reveal\"",
        "pointer-events-none fixed inset-0 z-[1]",
        "HomeProductRevealSequence",
        "HomeProductAtmosphere",
        "motion.div",
        "Product reveal sequence",
    ],
    "background_slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
    ],
    "sequence": [
        "data-home-product-sequence=\"front-back-peel-unwrapped\"",
        "wrapperFront",
        "wrapperBack",
        "unwrappedBar",
        "hershey_wrapper_front.webp",
        "hershey_wrapper_back.webp",
        "hershey_unwrapped_bar.png",
        "WrapperPeelPanels",
        "UnwrappedBarPlane",
        "useFrame",
        "smoothstep",
    ],
    "atmosphere": [
        "Sparkles",
        "Stars",
        "HomeProductAtmosphere",
    ],
    "peel": [
        "data-home-product-sequence=\"wrapper-peel-panels\"",
        "ProductWrapperPlane",
        "frontUrl",
        "backUrl",
    ],
    "wrapper_plane": [
        "ProductWrapperPlaneProps",
        "data-product-plane",
        "THREE.SRGBColorSpace",
        "DoubleSide",
    ],
    "bar_plane": [
        "UnwrappedBarPlaneProps",
        "data-product-plane=\"unwrapped-bar\"",
        "THREE.SRGBColorSpace",
        "DoubleSide",
    ],
    "compat_hero": [
        "HomeProductCinematicBackground",
        "HomeChocolateBarHero",
    ],
    "compat_slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "ChocolateBlockGrid",
    "boxGeometry args={[0.56, 0.32, 0.16]}",
    "rounded-[2.6rem] border border-[#3a160d]/10 bg-[#170504]",
    "data-home-hero-scene=\"hershey-product-3d-foundation\"",
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
        warnings.append("One or more page-level product reveal component files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("One or more required product visual assets are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required page-level animation markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old boxed preview code, old imports, or hardcoded supplier/business claims found.")

    background_content = read(FILES["background"])
    sequence_content = read(FILES["sequence"])

    report = {
        "step": "17E-B6F-R1",
        "name": "Full-page homepage product reveal background validation",
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
            "page_level_background_not_boxed_card": "pointer-events-none fixed inset-0 z-[1]" in background_content,
            "front_wrapper_used": "hershey_wrapper_front.webp" in sequence_content,
            "back_wrapper_used": "hershey_wrapper_back.webp" in sequence_content,
            "unwrapped_bar_used": "hershey_unwrapped_bar.png" in sequence_content,
            "front_back_peel_unwrapped_sequence_present": "front-back-peel-unwrapped" in sequence_content,
            "wrapper_peel_panels_present": "WrapperPeelPanels" in sequence_content,
            "motion_layer_present": "motion.div" in background_content,
            "dynamic_import_slots_present": "ssr: false" in read(FILES["background_slot"]) and "ssr: false" in read(FILES["compat_slot"]),
            "no_generic_chocolate_block_grid": "ChocolateBlockGrid" not in sequence_content,
            "no_old_hershey_component_imports": "@/components/hershey/" not in background_content + sequence_content,
            "no_supplier_or_cost_claims_hardcoded": not any(term in background_content + sequence_content for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in background_content + sequence_content,
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot. Do not push until the page-level background direction is accepted.",
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
