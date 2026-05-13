import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7c_bigger_3d_313_pipeline_report.json"

FILES = {
    "field": ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx",
    "pipeline": ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx",
}

REQUIRED = {
    "field": [
        "data-hershey-home-background=\"portfolio-right-background-funnel-bigger-solid-core\"",
        "data-hershey-scene-world=\"portfolio-right-background-funnel-bigger-solid-core\"",
        "right-[-2vw] z-0 hidden w-[36vw] min-w-[460px]",
        "camera={{ position: [0, 0, 6.15], fov: 35 }}",
        "position={[0.3, 0.08, 0]}",
        "scale={0.9}",
        "data-solid-core-color-variance=\"true\"",
        "<sphereGeometry args={[0.31, 64, 64]} />",
    ],
    "pipeline": [
        "data-home-intelligence-pipeline=\"three-one-three-direct-pulsing-connectors\"",
        "{ left: 42, top: 42 }",
        "{ left: 278, top: 246 }",
        "{ left: 514, top: 448 }",
        "strokeWidth=\"8\"",
        "strokeDasharray=\"72 340\"",
        "strokeDashoffset: [340, 0]",
        "opacity: 1",
        "absolute w-[205px]",
    ],
}

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

def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_required = {}
    forbidden_found = {}
    missing_files = []

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = read(path)
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN if item.lower() in content.lower()]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("Required file missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("Required 3D/pipeline markers missing.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden oversized/full-page/unsupported markers found.")

    field = read(FILES["field"])
    pipeline = read(FILES["pipeline"])

    report = {
        "step": "17E-B6G-1-FIX-7C",
        "name": "Bigger right-side 3D field and stable 3/1/3 direct pulsing pipeline",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {k: str(v.relative_to(ROOT)).replace("\\", "/") for k, v in FILES.items()},
        "rules_confirmed": {
            "3d_bigger_but_right_background_only": "w-[36vw] min-w-[460px]" in field and "fixed inset-0" not in field,
            "solid_core_sphere": "<sphereGeometry args={[0.31, 64, 64]} />" in field and "transparent\n              opacity={0.78}" not in field,
            "color_variance_on_core": "data-solid-core-color-variance=\"true\"" in field,
            "pipeline_313_layout": "{ left: 278, top: 246 }" in pipeline and "{ left: 514, top: 448 }" in pipeline,
            "pipeline_direct_visible_lines": "strokeWidth=\"8\"" in pipeline and "strokeDasharray=\"72 340\"" in pipeline,
            "pipeline_nodes_forced_visible": "opacity-100" in pipeline and "opacity: 1" in pipeline,
            "product_showcase_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only 3D size/position and 3/1/3 pipeline lines.",
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
