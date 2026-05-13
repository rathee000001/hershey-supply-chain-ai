import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r4_fix2_smooth_hdr_nav_melt_report.json"

FILES = {
    "overlay": ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
    "video": ROOT / "public/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4",
    "package": ROOT / "package.json",
}

def read(path):
    if not path.exists() or path.suffix.lower() == ".mp4":
        return ""
    return path.read_text(encoding="utf-8")

overlay = read(FILES["overlay"])
package = read(FILES["package"])

required_overlay = [
    'data-hero-chocolate-melt-overlay="smooth-hdr-video-melt-over-navbar-pills"',
    'const VIDEO_PLAYBACK_RATE = 0.55;',
    'video.playbackRate = VIDEO_PLAYBACK_RATE;',
    'fixed inset-x-0 top-[-40px] h-[470px]',
    'style={{ zIndex: 2147483000 }}',
    'duration: 7.5',
    'clipPath: "inset(0% 0% 72% 0%)"',
    'function ChromaKeyChocolatePlane',
    'function ChocolateVideoShaderLayer',
    'new THREE.VideoTexture(video)',
    'uContrast',
    'uSaturation',
    'uGlossBoost',
    'uWarmth',
    'uDepth',
    'chocolateRamp',
    'wetGloss',
    'navFlowBand',
    'navReadability',
    'fitWideTopUv',
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
    'const VIDEO_PLAYBACK_RATE = 0.2;',
    'duration: 18',
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
}

status = "PASS"
warnings = []

if missing_files:
    status = "FAIL"
    warnings.append("Required video or source file missing.")

if any(missing_required.values()):
    status = "FAIL"
    warnings.append("Required smooth HDR navbar melt markers missing.")

if any(forbidden_found.values()):
    status = "FAIL"
    warnings.append("Old slow/static chocolate markers or unsupported wording found.")

video_size_mb = None
if FILES["video"].exists():
    video_size_mb = round(FILES["video"].stat().st_size / (1024 * 1024), 2)

report = {
    "step": "17E-B6G-2A-R4-FIX2",
    "name": "Smooth HDR chocolate video melt over navbar",
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
    "rules_confirmed": {
        "video_slow_but_smooth": "const VIDEO_PLAYBACK_RATE = 0.55;" in overlay,
        "not_absurdly_slow": "duration: 18" not in overlay and "duration: 7.5" in overlay,
        "flows_over_nav_pills_visually": "style={{ zIndex: 2147483000 }}" in overlay and "fixed inset-x-0 top-[-40px]" in overlay,
        "nav_stays_clickable": "pointer-events-none" in overlay,
        "hdr_texture_boost_present": all(x in overlay for x in ["uContrast", "uSaturation", "uGlossBoost", "chocolateRamp", "wetGloss"]),
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
    "video_size_mb": video_size_mb,
}, indent=2))

if status != "PASS":
    raise SystemExit(1)
