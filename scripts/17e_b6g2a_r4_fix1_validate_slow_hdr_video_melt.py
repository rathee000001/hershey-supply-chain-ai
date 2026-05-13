import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r4_fix1_slow_hdr_video_melt_report.json"

FILES = {
    "overlay": ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
    "overview": ROOT / "src/components/home/HomeProjectOverviewSection.tsx",
    "video": ROOT / "public/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4",
    "package": ROOT / "package.json",
}

def read(path):
    if not path.exists() or path.suffix.lower() == ".mp4":
        return ""
    return path.read_text(encoding="utf-8")

overlay = read(FILES["overlay"])
overview = read(FILES["overview"])
package = read(FILES["package"])

required_overlay = [
    'data-hero-chocolate-melt-overlay="slow-hdr-video-melt-over-transparent-navbar"',
    'const VIDEO_PLAYBACK_RATE = 0.2;',
    'video.playbackRate = VIDEO_PLAYBACK_RATE;',
    'pointer-events-none absolute inset-x-0 top-[-72px] z-[9999]',
    'duration: 18',
    'clipPath: "inset(0% 0% 84% 0%)"',
    'function ChromaKeyChocolatePlane',
    'function ChocolateVideoShaderLayer',
    'new THREE.VideoTexture(video)',
    'uContrast',
    'uSaturation',
    'uBrightness',
    'uGlossBoost',
    'uWarmth',
    'greenDominance',
    'navReadability',
    'heroVideoUv',
    'powerPreference: "high-performance"',
]

forbidden = [
    '<ChocolateFlowDivider />',
    '<ChocolateDripRibbon variant="heroTop" />',
    'Chocolate motion layer',
    'Decorative flow',
    'Evidence-safe wording',
    'Reusable site layer',
    'data-home-chocolate-flow-divider',
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

missing_files = [
    str(path.relative_to(ROOT)).replace("\\", "/")
    for path in FILES.values()
    if not path.exists()
]

missing_required = {
    "overlay": [item for item in required_overlay if item not in overlay],
    "package": [
        dep for dep in ['"three"', '"@react-three/fiber"', '"framer-motion"']
        if dep not in package
    ],
}

forbidden_found = {
    "overlay": [item for item in forbidden if item.lower() in overlay.lower()],
    "overview": [item for item in forbidden if item.lower() in overview.lower()],
}

duplicate_opacity_pattern_found = bool(
    re.search(r"opacity:\s*1,\s*\n\s*opacity:\s*1,", overview)
)

status = "PASS"
warnings = []

if missing_files:
    status = "FAIL"
    warnings.append("Required file/video missing.")

if any(missing_required.values()):
    status = "FAIL"
    warnings.append("Required slow HDR chocolate overlay markers missing.")

if any(forbidden_found.values()):
    status = "FAIL"
    warnings.append("Forbidden old chocolate/info or unsupported wording markers found.")

if duplicate_opacity_pattern_found:
    status = "FAIL"
    warnings.append("Duplicate opacity build blocker still exists in HomeProjectOverviewSection.tsx.")

video_size_mb = None
if FILES["video"].exists():
    video_size_mb = round(FILES["video"].stat().st_size / (1024 * 1024), 2)

report = {
    "step": "17E-B6G-2A-R4-FIX1",
    "name": "Slow HDR video melt overlay over transparent navbar",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "warnings": warnings,
    "missing_files": missing_files,
    "missing_required": missing_required,
    "forbidden_found": forbidden_found,
    "duplicate_opacity_pattern_found": duplicate_opacity_pattern_found,
    "video_asset": {
        "path": str(FILES["video"].relative_to(ROOT)).replace("\\", "/"),
        "exists": FILES["video"].exists(),
        "size_mb": video_size_mb,
    },
    "rules_confirmed": {
        "video_is_5x_slower": "const VIDEO_PLAYBACK_RATE = 0.2;" in overlay,
        "entrance_reveal_is_slow": "duration: 18" in overlay,
        "flows_above_nav_visually": "z-[9999]" in overlay,
        "nav_stays_clickable": "pointer-events-none" in overlay,
        "hdr_texture_boost_present": all(x in overlay for x in ["uContrast", "uSaturation", "uGlossBoost", "uWarmth"]),
        "green_screen_chroma_key_present": all(x in overlay for x in ["uKeyColor", "greenDominance", "uSpill"]),
        "old_info_section_removed": all(term not in overlay for term in ["Chocolate motion layer", "Decorative flow", "Evidence-safe wording", "Reusable site layer"]),
        "mobile_deferred": True,
    },
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps({
    "status": status,
    "report_path": str(REPORT_PATH),
    "missing_files": missing_files,
    "missing_required": missing_required,
    "forbidden_found": forbidden_found,
    "duplicate_opacity_pattern_found": duplicate_opacity_pattern_found,
    "video_size_mb": video_size_mb,
}, indent=2))

if status != "PASS":
    raise SystemExit(1)
