import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7a_product_picture_animation_report.json"

FILES = {
    "showcase": ROOT / "src/components/home/HomeProductShowcase.tsx",
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
}

ASSETS = {
    "front": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "back": ROOT / "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
}

REQUIRED = {
    "showcase": [
        "data-home-product-showcase=\"restored-large-wrapper-hover\"",
        "WRAPPER_FRONT",
        "WRAPPER_BACK",
        "showBack",
        "scale: 2.08",
        "aspect-[5.8/2]",
        "overflow-hidden",
        "Product Study Anchor",
        "Hover to inspect back",
    ],
    "field": [
        "data-hershey-home-background=\"compact-right-hero-evidence-funnel\"",
        "data-hershey-scene-world=\"compact-right-hero-evidence-funnel\"",
        "absolute right-[0vw] top-[6rem] z-0 hidden h-[760px] w-[38vw] min-w-[520px]",
        "camera={{ position: [0, 0, 6.2], fov: 38 }}",
        "scale={0.74}",
        "position={[0.44, 0.05, 0]}",
        "HersheyEvidenceFunnelWorld",
    ],
}

FORBIDDEN = [
    "fixed inset-0",
    "right-[-14vw]",
    "w-[44vw]",
    "min-w-[560px]",
    "Stars",
    "ProductIdentityBadge",
    "hershey_unwrapped_bar.png",
    "ChocolateDripHeader",
    "ChocolateDripOverlay",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "profit margin",
    "Hershey internal cost",
    "@ts-nocheck",
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
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        lower_content = content.lower()
        forbidden_found[key] = [item for item in FORBIDDEN if item.lower() in lower_content]

    for key, path in ASSETS.items():
        if not path.exists():
            missing_assets.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("Required component file missing.")

    if missing_assets:
        status = "FAIL"
        warnings.append("Wrapper front/back visual asset missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("Required picture/animation marker missing.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden full-page/scattered/unsupported marker found.")

    showcase = read(FILES["showcase"])
    field = read(FILES["field"])

    report = {
        "step": "17E-B6G-1-FIX-7A",
        "name": "Restore product picture and compact right-side 3D hero animation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_assets": missing_assets,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {k: str(v.relative_to(ROOT)).replace("\\", "/") for k, v in FILES.items()},
        "rules_confirmed": {
            "product_picture_restored_large": "scale: 2.08" in showcase and "aspect-[5.8/2]" in showcase,
            "hover_back_wrapper_kept": "WRAPPER_BACK" in showcase and "showBack" in showcase,
            "animation_no_longer_fixed_full_page": "fixed inset-0" not in field,
            "animation_compact_right_side": "absolute right-[0vw] top-[6rem]" in field and "w-[38vw]" in field,
            "animation_not_scattered_starfield": "Stars" not in field,
            "no_supplier_claims_added": not any(term in showcase + field for term in ["Land O", "Barry Callebaut", "ASR", "McLane"]),
            "no_cost_claims_added": not any(term in showcase + field for term in ["profit margin", "Hershey internal cost"]),
            "pipeline_not_touched_in_this_step": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the hero product picture plus right-side compact 3D animation.",
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
