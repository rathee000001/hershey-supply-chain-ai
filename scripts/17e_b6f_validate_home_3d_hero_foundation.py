import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_home_3d_hero_foundation_report.json"

FILES = {
    "scene": ROOT / "src/components/hershey3d/home/HomeHeroScene.tsx",
    "slot": ROOT / "src/components/hershey3d/home/HomeHeroSceneSlot.tsx",
    "wrapper_plane": ROOT / "src/components/hershey3d/home/ProductWrapperPlane.tsx",
    "bar_plane": ROOT / "src/components/hershey3d/home/UnwrappedBarPlane.tsx",
    "particles": ROOT / "src/components/hershey3d/home/HomeHeroParticles.tsx",
    "spotlight": ROOT / "src/components/hershey3d/home/ProductSpotlightRig.tsx",
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
    "scene": [
        "data-home-hero-scene=\"hershey-product-3d-foundation\"",
        "PRODUCT_ASSETS",
        "hershey_wrapper_front.webp",
        "hershey_wrapper_back.webp",
        "hershey_unwrapped_bar.png",
        "ProductWrapperPlane",
        "UnwrappedBarPlane",
        "HomeHeroParticles",
        "ProductSpotlightRig",
        "Target SKU product anchor",
        "Evidence claims come only from",
        "audited public JSON artifacts",
    ],
    "slot": [
        "dynamic(",
        "ssr: false",
        "HomeHeroFallback",
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
    "particles": [
        "Sparkles",
        "HomeHeroParticles",
    ],
    "spotlight": [
        "ambientLight",
        "spotLight",
        "ProductSpotlightRig",
    ],
    "fallback": [
        "Product hero fallback",
        "Hershey 1.55 oz Milk Chocolate Bar",
    ],
    "compat_hero": [
        "HomeHeroScene",
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
    "@/components/hershey/",
    "ChocolateDripOverlay",
    "ChocolateMeltSystem",
    "profit margin",
    "Hershey internal cost",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
]

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

        content = path.read_text(encoding="utf-8")
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    for key, path in ASSETS.items():
        if not path.exists():
            missing_assets.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more homepage 3D hero component files are missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("One or more required product visual assets are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more 3D hero files are missing required implementation markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old generic 3D code, imports, or hardcoded supplier/business claims found.")

    report = {
        "step": "17E-B6F",
        "name": "Homepage 3D background hero foundation validation",
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
            "actual_wrapper_front_used": not missing_assets and "hershey_wrapper_front.webp" in FILES["scene"].read_text(encoding="utf-8") if FILES["scene"].exists() else False,
            "actual_wrapper_back_used": not missing_assets and "hershey_wrapper_back.webp" in FILES["scene"].read_text(encoding="utf-8") if FILES["scene"].exists() else False,
            "actual_unwrapped_bar_used": not missing_assets and "hershey_unwrapped_bar.png" in FILES["scene"].read_text(encoding="utf-8") if FILES["scene"].exists() else False,
            "dynamic_import_slot_present": "ssr: false" in FILES["slot"].read_text(encoding="utf-8") if FILES["slot"].exists() else False,
            "compatibility_slot_preserved": "HomeChocolateBarHeroSlot" in FILES["compat_slot"].read_text(encoding="utf-8") if FILES["compat_slot"].exists() else False,
            "no_generic_chocolate_block_grid": not any("ChocolateBlockGrid" in values for values in forbidden_found.values()),
            "no_old_hershey_component_imports": not any("@/components/hershey/" in values for values in forbidden_found.values()),
            "no_supplier_or_cost_claims_hardcoded": not any(any(term in values for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]) for values in forbidden_found.values()),
            "not_full_homepage_remake_yet": True,
        },
        "next_recommended_step": "Run npm run build. If clean, visually inspect the homepage hero, then proceed to Step 17E-B6G.",
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
