import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r4_fix4_portal_absolute_hero_scoped_melt_report.json"

FILES = {
    "overlay": ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
    "shell": ROOT / "src/components/cinematic/CinematicPageShell.tsx",
    "home": ROOT / "src/app/page.tsx",
    "video": ROOT / "public/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4",
    "package": ROOT / "package.json",
}

def read(path):
    if not path.exists() or path.suffix.lower() == ".mp4":
        return ""
    return path.read_text(encoding="utf-8")

overlay = read(FILES["overlay"])
shell = read(FILES["shell"])
home = read(FILES["home"])
package = read(FILES["package"])

required_overlay = [
    'data-hero-chocolate-melt-overlay="portal-absolute-hero-scoped-video-melt"',
    'data-hero-chocolate-anchor="first-container-scope"',
    'createPortal',
    'useHeroAnchoredPortalBox',
    'position: "absolute"',
    'top: `${box.top}px`',
    'height: `${box.height}px`',
    'zIndex: 2147483000',
    'pointerEvents: "none"',
    'contain: "layout paint style"',
    'const VIDEO_PLAYBACK_RATE = 0.68;',
    'const FINAL_IDLE_LOOP_SECONDS = 1.45;',
    'video.loop = false;',
    'video.currentTime = idleStart;',
    'new THREE.VideoTexture(video)',
    'function ChromaKeyChocolatePlane',
    'heroOnlyMask',
    'diagonalHeroCorridor',
    'chocolateRamp',
    'wetGloss',
    'greenDominance',
    'powerPreference: "high-performance"',
]

required_shell = [
    'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";',
    '<HeroChocolateMeltOverlay />',
]

forbidden_overlay = [
    'pointer-events-none fixed',
    'fixed inset-x-0',
    'position: "fixed"',
    'top-[-40px] h-[470px]',
    'duration: 18',
    'const VIDEO_PLAYBACK_RATE = 0.2;',
    'data-hero-chocolate-melt-overlay="smooth-hdr-video-melt-over-navbar-pills"',
    '<ChocolateFlowDivider />',
    '<ChocolateDripRibbon variant="heroTop" />',
    'Chocolate motion layer',
    'Decorative flow',
    'Evidence-safe wording',
    'Reusable site layer',
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
    "shell": [item for item in required_shell if item not in shell],
    "package": [
        dep for dep in ['"three"', '"@react-three/fiber"', '"framer-motion"']
        if dep not in package
    ],
}

forbidden_found = {
    "overlay": [item for item in forbidden_overlay if item.lower() in overlay.lower()],
    "shell": [item for item in forbidden_overlay if item.lower() in shell.lower()],
    "home": [item for item in ['<HeroChocolateMeltOverlay />'] if item in home],
}

status = "PASS"
warnings = []

if missing_files:
    status = "FAIL"
    warnings.append("Required file/video missing.")

if any(missing_required.values()):
    status = "FAIL"
    warnings.append("Required hero-scoped portal overlay markers missing.")

if any(forbidden_found.values()):
    status = "FAIL"
    warnings.append("Fixed/full-site overlay markers, duplicate homepage overlay, or unsupported wording found.")

video_size_mb = None
if FILES["video"].exists():
    video_size_mb = round(FILES["video"].stat().st_size / (1024 * 1024), 2)

report = {
    "step": "17E-B6G-2A-R4-FIX4",
    "name": "Anchor portal chocolate melt to first hero container across all pages",
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
        "portal_used_for_z_index": "createPortal" in overlay,
        "not_fixed_full_site": 'position: "fixed"' not in overlay and "fixed inset-x-0" not in overlay,
        "anchored_to_first_container": 'data-hero-chocolate-anchor="first-container-scope"' in overlay,
        "absolute_document_position": 'position: "absolute"' in overlay and 'top: `${box.top}px`' in overlay,
        "scrolls_away_with_hero": 'window.scrollY + rect.top' in overlay,
        "height_is_hero_scoped": 'Math.min(460, Math.max(350, window.innerHeight * 0.42))' in overlay,
        "nav_stays_clickable": 'pointerEvents: "none"' in overlay,
        "global_shell_layer": all(item in shell for item in required_shell),
        "homepage_duplicate_removed": "<HeroChocolateMeltOverlay />" not in home,
        "no_restart_from_zero": "video.loop = false;" in overlay and "video.currentTime = idleStart;" in overlay,
        "hdr_shader_present": all(item in overlay for item in ["uContrast", "uSaturation", "uGlossBoost", "chocolateRamp", "wetGloss"]),
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
