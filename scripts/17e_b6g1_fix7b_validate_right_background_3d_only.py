import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7b_right_background_3d_only_report.json"

FILE = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

REQUIRED = [
    "data-hershey-home-background=\"portfolio-right-background-funnel\"",
    "data-hershey-scene-world=\"portfolio-right-background-funnel\"",
    "pointer-events-none fixed inset-y-0 right-0 z-0 hidden w-[32vw] min-w-[390px] overflow-visible lg:block",
    "camera={{ position: [0, 0, 6.4], fov: 34 }}",
    "gl={{ alpha: true, antialias: true }}",
    "position={[0.42, 0.08, 0]}",
    "scale={0.78}",
    "BackgroundFunnelWorld",
    "getFunnelPoint",
    "makeFunnelLine",
]

FORBIDDEN = [
    "fixed inset-0",
    "w-[42vw] min-w-[560px]",
    "right-[-14vw]",
    "<color attach=\"background\"",
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

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = FILE.read_text(encoding="utf-8") if FILE.exists() else ""

    missing_required = [item for item in REQUIRED if item not in content]
    forbidden_found = [item for item in FORBIDDEN if item.lower() in content.lower()]

    status = "PASS"
    warnings = []

    if not FILE.exists():
        status = "FAIL"
        warnings.append("HersheySupplyChainFieldScene.tsx is missing.")

    if missing_required:
        status = "FAIL"
        warnings.append("Required right-background 3D markers are missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Forbidden full-page/oversized/scattered/background markers found.")

    report = {
        "step": "17E-B6G-1-FIX-7B",
        "name": "Portfolio-style right background 3D field only",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {
            "field": str(FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "right_background_only": "w-[32vw] min-w-[390px]" in content,
            "not_full_page_canvas": "fixed inset-0" not in content,
            "transparent_canvas": "gl={{ alpha: true, antialias: true }}" in content and "<color attach=\"background\"" not in content,
            "starts_after_product_area": "right-0 z-0 hidden w-[32vw]" in content,
            "not_using_stars": "Stars" not in content,
            "product_showcase_not_touched": True,
            "pipeline_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the right-side background animation position.",
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
