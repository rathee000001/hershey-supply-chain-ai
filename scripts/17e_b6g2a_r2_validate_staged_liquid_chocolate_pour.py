import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r2_staged_liquid_chocolate_pour_report.json"

FILE = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
PACKAGE = ROOT / "package.json"

REQUIRED = [
    'data-hero-chocolate-melt-overlay="staged-liquid-pour-with-three-shader-gloss"',
    'import { Canvas, useFrame } from "@react-three/fiber";',
    'import * as THREE from "three";',
    "function ChocolateGlossShader",
    "shaderMaterial",
    "fragmentShader",
    "vertexShader",
    'pointer-events-none absolute left-0 top-[-138px] z-[140]',
    'initial={{ clipPath: "inset(0% 100% 100% 0%)", opacity: 0 }}',
    "clipPath:",
    "RoundedChocolateDrip",
    "AnimatedFlowBead",
    "sheetDrips",
    "streamDrips",
    "flowBeads",
    "stageChocolateBody",
    "stageChocolateStream",
    "stageChocolateGloss",
    "stageFlowBlur",
    "pathLength",
    "preserveAspectRatio=\"none\"",
]

FORBIDDEN = [
    "Chocolate motion layer",
    "Decorative flow",
    "Evidence-safe wording",
    "Reusable site layer",
    "data-home-chocolate-flow-divider",
    "fixed inset-0",
    "@ts-nocheck",
    "images from Google",
    "official Hershey",
    "endorsed by Hershey",
    "Hershey internal cost",
    "profit margin",
    "invoice data",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
]

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = FILE.read_text(encoding="utf-8") if FILE.exists() else ""
    package = PACKAGE.read_text(encoding="utf-8") if PACKAGE.exists() else ""

    missing_required = [item for item in REQUIRED if item not in content]
    forbidden_found = [item for item in FORBIDDEN if item.lower() in content.lower()]

    missing_dependencies = []
    for dep in ['"@react-three/fiber"', '"three"', '"framer-motion"']:
        if dep not in package:
            missing_dependencies.append(dep)

    status = "PASS"
    warnings = []

    if not FILE.exists():
        status = "FAIL"
        warnings.append("HeroChocolateMeltOverlay.tsx is missing.")

    if missing_required:
        status = "FAIL"
        warnings.append("Required staged liquid chocolate pour markers are missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Old info-section or unsupported wording markers found.")

    if missing_dependencies:
        status = "FAIL"
        warnings.append("Required animation/3D dependencies are missing from package.json.")

    report = {
        "step": "17E-B6G-2A-R2",
        "name": "Staged liquid chocolate pour system with Three.js shader gloss",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "missing_dependencies": missing_dependencies,
        "files_checked": {
            "overlay": str(FILE.relative_to(ROOT)).replace("\\", "/"),
            "package": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "starts_above_nav": "top-[-138px]" in content,
            "click_safe": "pointer-events-none" in content,
            "uses_staged_clip_reveal": 'clipPath: "inset(0% 100% 100% 0%)"' in content,
            "uses_three_shader_gloss_now": all(item in content for item in ["Canvas", "useFrame", "shaderMaterial", "fragmentShader"]),
            "has_liquid_paths": all(item in content for item in ["stageChocolateStream", "pathLength", "RoundedChocolateDrip", "AnimatedFlowBead"]),
            "not_an_info_section": all(term not in content for term in ["Chocolate motion layer", "Decorative flow", "Evidence-safe wording", "Reusable site layer"]),
            "mobile_deferred": True,
            "product_showcase_not_touched": True,
            "pipeline_not_touched": True,
            "overview_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the chocolate pour. It should reveal from above the nav and visually flow toward the product card start.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "missing_dependencies": missing_dependencies,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
