import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4b_r2_evidence_funnel_field_report.json"

FILES = {
    "field_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "atmosphere_scene": ROOT / "src/components/hershey3d/home/HersheySupplyChainAtmosphereScene.tsx",
    "readable_atmosphere": ROOT / "src/components/hershey3d/home/HersheyHomeReadableAtmosphere.tsx",
    "lab_scene": ROOT / "src/components/hershey3d/home/HersheyHomeLabScene.tsx",
    "product_background": ROOT / "src/components/hershey3d/home/HomeProductCinematicBackground.tsx",
    "home_scene": ROOT / "src/components/hershey3d/home/HomeHeroScene.tsx",
    "compat_hero": ROOT / "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "page": ROOT / "src/app/page.tsx",
}

REQUIRED = {
    "field_scene": [
        "data-hershey-home-background=\"evidence-funnel-intelligence-field\"",
        "data-hershey-scene-world=\"evidence-funnel-intelligence-field\"",
        "Canvas",
        "useFrame",
        "Float",
        "Line",
        "Stars",
        "StreamParticle",
        "InputCard",
        "OutputCard",
        "getFunnelPoint",
        "getOutputPoint",
        "HersheyEvidenceFunnelWorld",
        "RawInputCard",
        "CleanOutputCard",
        "torusGeometry",
        "sphereGeometry",
        "absolute inset-y-0 right-0 w-[62vw]",
    ],
    "atmosphere_scene": ["HersheySupplyChainFieldScene"],
    "readable_atmosphere": ["HersheySupplyChainFieldScene"],
    "lab_scene": ["HersheySupplyChainFieldScene"],
    "product_background": ["HersheySupplyChainFieldScene"],
    "home_scene": ["HersheySupplyChainFieldScene"],
    "compat_hero": ["HersheySupplyChainFieldScene"],
    "page": [
        "HomeChocolateBarHeroSlot",
        "relative z-20",
        "hidden lg:block",
        "bg-white/94",
    ],
}

FORBIDDEN = [
    "@ts-nocheck",
    "Sources",
    "Parser",
    "Audit",
    "Frontend",
    "PDF",
    "Excel",
    "DOC",
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
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more evidence funnel field files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required evidence funnel markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden visible labels/product assets/drip/supplier or cost claim markers found.")

    field = read(FILES["field_scene"])
    page = read(FILES["page"])

    report = {
        "step": "17E-B6F-R4B-R2",
        "name": "3D Evidence Funnel Intelligence Field validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "real_r3f_scene_present": "Canvas" in field and "useFrame" in field and "Line" in field,
            "evidence_funnel_concept_present": "getFunnelPoint" in field and "RawInputCard" in field and "CleanOutputCard" in field,
            "right_side_background_region": "absolute inset-y-0 right-0 w-[62vw]" in field,
            "central_3d_sphere_and_revolving_rings": "sphereGeometry" in field and "torusGeometry" in field,
            "no_visible_text_labels_inside_scene": not any(term in field for term in ["Sources", "Parser", "Audit", "Frontend", "PDF", "Excel", "DOC"]),
            "no_product_assets_in_background": not any(asset in field for asset in ["hershey_wrapper_front.webp", "hershey_wrapper_back.webp", "hershey_unwrapped_bar.png"]),
            "page_keeps_portfolio_layering": "HomeChocolateBarHeroSlot" in page and "relative z-20" in page,
            "hero_right_column_left_open_for_scene": "hidden lg:block" in page,
            "cards_strengthened_above_background": "bg-white/94" in page,
            "target_sku_disabled": "Target SKU" not in page,
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in page + field,
            "no_supplier_or_cost_claims_hardcoded": not any(term in page + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot/video. Do not push until the funnel scene looks visible, creative, and stays behind content.",
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
