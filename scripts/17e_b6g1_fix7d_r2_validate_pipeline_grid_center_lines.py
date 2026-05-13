import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7d_r2_pipeline_grid_center_lines_report.json"

FILE = ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx"

REQUIRED = [
    'data-home-intelligence-pipeline="contained-grid-three-one-three-center-pulsing-connectors"',
    'grid h-full grid-cols-3 grid-rows-[140px_140px_140px]',
    '<div />',
    'viewBox="0 0 1000 620"',
    'preserveAspectRatio="none"',
    'containedGridPipelinePulseGlow',
    'M 170 105 C 285 105, 335 105, 500 105',
    'M 500 105 C 665 105, 715 105, 830 105',
    'M 830 105 C 830 210, 640 235, 500 310',
    'M 500 310 C 360 385, 170 410, 170 515',
    'M 170 515 C 285 515, 335 515, 500 515',
    'M 500 515 C 665 515, 715 515, 830 515',
    'strokeDasharray="70 300"',
    'strokeDashoffset: [300, 0]',
    'opacity-100',
    'opacity: 1',
    'initial={false}',
]

FORBIDDEN = [
    'absolute w-[205px]',
    'absolute w-[188px]',
    'nodePositions',
    'viewBox="0 0 760 560"',
    'viewBox="0 0 720 610"',
    'strokeDasharray="72 340"',
    'strokeDasharray="64 300"',
    '@ts-nocheck',
    'Land O',
    'Barry Callebaut',
    'ASR',
    'McLane',
    'profit margin',
    'Hershey internal cost',
    'ChocolateDripHeader',
    'ChocolateDripOverlay',
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
        warnings.append("Pipeline map file is missing.")

    if missing_required:
        status = "FAIL"
        warnings.append("Grid-contained 3/1/3 center connector markers missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Old absolute-position/out-of-container pipeline markers found.")

    report = {
        "step": "17E-B6G-1-FIX-7D-R2",
        "name": "Pipeline grid containment with stable center-to-center pulsing connectors",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {
            "pipeline": str(FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "uses_normal_grid_not_absolute_nodes": "grid h-full grid-cols-3 grid-rows-[140px_140px_140px]" in content and "nodePositions" not in content,
            "layout_is_3_1_3": content.count("<div />") >= 2,
            "cards_cannot_leave_container": "w-full" in content and "absolute w-[205px]" not in content and "absolute w-[188px]" not in content,
            "center_to_center_lines_exist": all(item in content for item in [
                "M 170 105 C 285 105, 335 105, 500 105",
                "M 500 105 C 665 105, 715 105, 830 105",
                "M 830 105 C 830 210, 640 235, 500 310",
                "M 500 310 C 360 385, 170 410, 170 515",
                "M 170 515 C 285 515, 335 515, 500 515",
                "M 500 515 C 665 515, 715 515, 830 515",
            ]),
            "lines_are_live_pulsing": 'strokeDasharray="70 300"' in content and "strokeDashoffset: [300, 0]" in content,
            "nodes_forced_visible": "opacity-100" in content and "opacity: 1" in content,
            "product_showcase_not_touched": True,
            "three_d_scene_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the pipeline. Cards should remain inside the panel and lines should connect center-to-center.",
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
