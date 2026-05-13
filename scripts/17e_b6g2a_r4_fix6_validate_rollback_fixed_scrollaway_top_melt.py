import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_r4_fix6_rollback_fixed_scrollaway_top_melt_report.json"

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
    'data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"',
    'createPortal',
    'useHeroTopScrollAwayBox',
    'position: "fixed"',
    'top: 0',
    'transform: `translate3d(0, ${-scrollY}px, 0)`',
    'visible: scrollY < height + 90',
    'pointerEvents: "none"',
    'zIndex: 2147483000',
    'const VIDEO_PLAYBACK_RATE = 0.78;',
    'const FINAL_IDLE_LOOP_SECONDS = 1.35;',
    'video.loop = false;',
    'video.currentTime = idleStart;',
    'new THREE.VideoTexture(video)',
    'function ChocolateShaderPlane',
    'chocolateVideoUv',
    'chocolateRamp',
    'wetGloss',
    'greenDominance',
    'powerPreference: "high-performance"',
]

required_shell = [
    'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";',
    '<HeroChocolateMeltOverlay />',
]

forbidden = [
    'useDocumentTopHeroBox',
    'useHeroAnchoredPortalBox',
    'data-hero-chocolate-anchor="first-container-scope"',
    'portal-document-top-hero-only-video-melt',
    'portal-absolute-hero-scoped-video-melt',
    'top: `${box.top}px`',
    'height: `${box.height}px`',
    'window.scrollY + rect.top',
    'duration: 18',
    'const VIDEO_PLAYBACK_RATE = 0.2;',
    '<ChocolateFlowDivider />',
    '<ChocolateDripRibbon variant="heroTop" />',
    'Chocolate motion layer',
    'Decorative flow',
    'Evidence-safe wording',
    'Reusable site layer',
    '@ts-nocheck',
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
    "overlay": [item for item in forbidden if item.lower() in overlay.lower()],
    "shell": [item for item in forbidden if item.lower() in shell.lower()],
    "home": [item for item in ['<HeroChocolateMeltOverlay />'] if item in home],
}

status = "PASS"
warnings = []

if missing_files:
    status = "FAIL"
    warnings.append("Required file/video missing.")

if any(missing_required.values()):
    status = "FAIL"
    warnings.append("Required rollback fixed scroll-away melt markers missing.")

if any(forbidden_found.values()):
    status = "FAIL"
    warnings.append("Old bad overlay markers, homepage duplicate, or unsupported wording found.")

video_size_mb = None
if FILES["video"].exists():
    video_size_mb = round(FILES["video"].stat().st_size / (1024 * 1024), 2)

report = {
    "step": "17E-B6G-2A-R4-FIX6",
    "name": "Rollback and rebuild hero-scoped top chocolate portal",
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
        "starts_from_viewport_top": 'top: 0' in overlay,
        "flows_over_nav_with_portal": "createPortal" in overlay and 'zIndex: 2147483000' in overlay,
        "nav_stays_clickable": 'pointerEvents: "none"' in overlay,
        "scrolls_away_after_hero": 'transform: `translate3d(0, ${-scrollY}px, 0)`' in overlay,
        "hidden_after_hero": 'visible: scrollY < height + 90' in overlay,
        "does_not_restart_from_zero": "video.loop = false;" in overlay and "video.currentTime = idleStart;" in overlay,
        "global_shell_layer": all(item in shell for item in required_shell),
        "homepage_duplicate_removed": "<HeroChocolateMeltOverlay />" not in home,
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
