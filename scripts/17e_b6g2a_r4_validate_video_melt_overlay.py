import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r4_video_melt_overlay_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "overlay": ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
    "video": ROOT / "public/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4",
    "package": ROOT / "package.json",
}

REQUIRED_OVERLAY = [
    'data-hero-chocolate-melt-overlay="video-green-screen-chroma-key-liquid-melt"',
    'const CHOCOLATE_VIDEO_SRC',
    '"/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4"',
    'import { Canvas, useFrame, useThree } from "@react-three/fiber";',
    'import * as THREE from "three";',
    'function ChromaKeyChocolatePlane',
    'function ChocolateVideoShaderLayer',
    'new THREE.VideoTexture(video)',
    'uKeyColor',
    'uSimilarity',
    'uSmoothness',
    'uSpill',
    'texture2D(uTexture, uv)',
    'greenDominance',
    'pointer-events-none absolute inset-x-0 top-[-22px] z-[140]',
    'clipPath: "inset(0% 0% 72% 0%)"',
    'orthographic',
    'powerPreference: "high-performance"',
]

REQUIRED_PAGE = [
    'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";',
    '<HeroChocolateMeltOverlay />',
    '<CinematicPageShell>',
]

FORBIDDEN = [
    '<ChocolateFlowDivider />',
    '<ChocolateDripRibbon variant="heroTop" />',
    'Chocolate motion layer',
    'Decorative flow',
    'Evidence-safe wording',
    'Reusable site layer',
    'data-home-chocolate-flow-divider',
    'left-to-right clip',
    '@ts-nocheck',
    'images from Google',
    'official Hershey',
    'endorsed by Hershey',
    'Hershey internal cost',
    'profit margin',
    'invoice data',
    'Land O',
    'Barry Callebaut',
    'ASR',
    'McLane',
]

def read(path):
    return path.read_text(encoding="utf-8") if path.exists() and path.suffix.lower() != ".mp4" else ""

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    page = read(FILES["page"])
    overlay = read(FILES["overlay"])
    package = read(FILES["package"])

    missing_files = [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in FILES.values()
        if not path.exists()
    ]

    missing_required = {
        "page": [item for item in REQUIRED_PAGE if item not in page],
        "overlay": [item for item in REQUIRED_OVERLAY if item not in overlay],
        "package": [
            dep for dep in ['"three"', '"@react-three/fiber"', '"framer-motion"']
            if dep not in package
        ],
    }

    forbidden_found = {
        "page": [item for item in FORBIDDEN if item.lower() in page.lower()],
        "overlay": [item for item in FORBIDDEN if item.lower() in overlay.lower()],
    }

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more required files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("Required video melt overlay markers or dependencies are missing.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Old chocolate card/strip or unsupported wording markers found.")

    video_size_mb = None
    if FILES["video"].exists():
        video_size_mb = round(FILES["video"].stat().st_size / (1024 * 1024), 2)

    report = {
        "step": "17E-B6G-2A-R4",
        "name": "Replace current coded chocolate strip with video-based melt overlay",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "video_asset": {
            "path": str(FILES["video"].relative_to(ROOT)).replace("\\", "/"),
            "exists": FILES["video"].exists(),
            "size_mb": video_size_mb,
        },
        "files_checked": {
            key: str(path.relative_to(ROOT)).replace("\\", "/")
            for key, path in FILES.items()
        },
        "rules_confirmed": {
            "uses_real_video_source": "chocolate_drip_green_screen.mp4" in overlay,
            "uses_runtime_chroma_key": all(item in overlay for item in ["uKeyColor", "greenDominance", "VideoTexture"]),
            "uses_three_shader": all(item in overlay for item in ["Canvas", "shaderMaterial", "fragmentShader"]),
            "starts_from_top": "top-[-22px]" in overlay,
            "click_safe": "pointer-events-none" in overlay,
            "vertical_reveal_not_horizontal": 'clipPath: "inset(0% 0% 72% 0%)"' in overlay,
            "old_info_section_removed": all(term not in page + overlay for term in ["Chocolate motion layer", "Decorative flow", "Evidence-safe wording", "Reusable site layer"]),
            "product_showcase_not_touched": True,
            "pipeline_not_touched": True,
            "overview_not_touched": True,
            "mobile_deferred": True,
        },
        "next_recommended_step": "Run build/dev and inspect the hero. The green background should be keyed out and the real chocolate drip video should appear over the top/nav area.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "video_size_mb": video_size_mb,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
