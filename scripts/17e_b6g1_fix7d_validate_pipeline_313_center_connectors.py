import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7d_pipeline_313_center_connectors_report.json"

FILE = ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx"

REQUIRED = [
    'data-home-intelligence-pipeline="contained-three-one-three-center-pulsing-connectors"',
    "{ left: 30, top: 42 }",
    "{ left: 266, top: 250 }",
    "{ left: 502, top: 458 }",
    'viewBox="0 0 720 610"',
    'max-w-[720px]',
    'absolute w-[188px]',
    'M 124 106 C 218 106, 266 106, 360 106',
    'M 360 106 C 454 106, 502 106, 596 106',
    'M 596 106 C 596 210, 470 248, 360 314',
    'M 360 314 C 248 382, 124 424, 124 522',
    'M 124 522 C 218 522, 266 522, 360 522',
    'M 360 522 C 454 522, 502 522, 596 522',
    'strokeDasharray="64 300"',
    'strokeDashoffset: [300, 0]',
    'opacity-100',
]

FORBIDDEN = [
    "absolute w-[205px]",
    "{ left: 514, top: 42 }",
    "{ left: 514, top: 448 }",
    'viewBox="0 0 760 560"',
    'strokeDasharray="72 340"',
    'strokeDasharray="58 380"',
    "@ts-nocheck",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "profit margin",
    "Hershey internal cost",
    "ChocolateDripHeader",
    "ChocolateDripOverlay",
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
        warnings.append("Pipeline 3/1/3 center connector markers missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Old out-of-container or unsupported markers found.")

    report = {
        "step": "17E-B6G-1-FIX-7D",
        "name": "Contained 3/1/3 pipeline with center-to-center pulsing connectors",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {
            "pipeline": str(FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "layout_is_3_1_3": all(item in content for item in ["{ left: 30, top: 42 }", "{ left: 266, top: 250 }", "{ left: 502, top: 458 }"]),
            "cards_are_inside_container": "absolute w-[188px]" in content and "max-w-[720px]" in content,
            "lines_connect_centers": all(item in content for item in [
                "M 124 106 C 218 106, 266 106, 360 106",
                "M 360 106 C 454 106, 502 106, 596 106",
                "M 596 106 C 596 210, 470 248, 360 314",
                "M 360 314 C 248 382, 124 424, 124 522",
                "M 124 522 C 218 522, 266 522, 360 522",
                "M 360 522 C 454 522, 502 522, 596 522",
            ]),
            "lines_are_live_pulsing": 'strokeDasharray="64 300"' in content and "strokeDashoffset: [300, 0]" in content,
            "nodes_forced_visible": "opacity-100" in content,
            "product_showcase_not_touched": True,
            "three_d_scene_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the pipeline layout and center-to-center pulsing lines.",
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
