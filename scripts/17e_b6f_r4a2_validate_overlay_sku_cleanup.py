import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6f_r4a2_overlay_sku_cleanup_report.json"

FILES = {
    "readable_atmosphere": ROOT / "src/components/hershey3d/home/HersheyHomeReadableAtmosphere.tsx",
    "product_identity_badge": ROOT / "src/components/cinematic/ProductIdentityBadge.tsx",
}

REQUIRED = {
    "readable_atmosphere": [
        "data-hershey-home-background=\"right-only-readable-atmosphere-reset-v2\"",
        "motion",
        "useReducedMotion",
        "goldDust",
        "routeLines",
    ],
    "product_identity_badge": [
        "ProductIdentityBadgeProps",
        "return null",
        "proper right-side",
        "product showcase",
    ],
}

FORBIDDEN = [
    "Target SKU",
    "Hershey 1.55 oz Milk Chocolate",
    "hershey_wrapper_front",
    "bg-gradient-to-r from-[#fffaf2]",
    "bg-gradient-to-t from-[#f8f1e7]",
    "w-[68%]",
    "w-[64%]",
    "inset-y-0 left-0",
    "Canvas",
    "Line",
    "Stars",
    "boxGeometry",
    "sphereGeometry",
    "torusGeometry",
    "HomeProductRevealSequence",
    "WrapperPeelPanels",
    "UnwrappedBarPlane",
    "ProductWrapperPlane",
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
        forbidden_found[key] = [item for item in FORBIDDEN if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more overlay/SKU cleanup files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required cleanup markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden transparent wash, Target SKU badge, old 3D scene, product-covering code, or hardcoded claims found.")

    atmosphere = read(FILES["readable_atmosphere"])
    badge = read(FILES["product_identity_badge"])

    report = {
        "step": "17E-B6F-R4A-2",
        "name": "Remove transparent overlay and disable Target SKU hero badge",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "left_transparent_wash_removed": "inset-y-0 left-0" not in atmosphere and "bg-gradient-to-r from-[#fffaf2]" not in atmosphere,
            "bottom_transparent_wash_removed": "bg-gradient-to-t from-[#f8f1e7]" not in atmosphere,
            "right_only_subtle_motion_kept": "right-only-readable-atmosphere-reset-v2" in atmosphere,
            "target_sku_badge_disabled": "return null" in badge and "Target SKU" not in badge,
            "wrapper_thumbnail_removed_from_badge": "hershey_wrapper_front" not in badge,
            "no_canvas_or_bad_3d_scene_active": not any(term in atmosphere for term in ["Canvas", "Line", "Stars", "boxGeometry", "sphereGeometry", "torusGeometry"]),
            "chocolate_drip_not_integrated_until_b6g": "ChocolateDripHeader" not in atmosphere,
            "no_supplier_or_cost_claims_hardcoded": not any(term in atmosphere + badge for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot. Continue only if text/cards are readable and Target SKU badge is gone.",
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
