import json
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
report = ROOT / "artifacts/10_run_reports/step17e_b6g2a_r4_fix7_top_layer_host_report.json"

text = overlay.read_text(encoding="utf-8")

required = [
    "useChocolateTopLayerHost",
    'hero-chocolate-melt-top-layer-host',
    'data-hero-chocolate-top-layer-host',
    'node.style.zIndex = "2147483647"',
    'node.style.pointerEvents = "none"',
    'node.style.position = "fixed"',
    'data-hero-chocolate-melt-overlay="top-layer-host-scrollaway-video-melt"',
    'position: "absolute"',
    'transform: `translate3d(0, ${-scrollY}px, 0)`',
    'visible: scrollY < height + 90',
    'createPortal(',
    'host,',
]

forbidden = [
    "document.body,",
    'data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"',
    'data-hero-chocolate-melt-overlay="portal-document-top-hero-only-video-melt"',
    'data-hero-chocolate-melt-overlay="portal-absolute-hero-scoped-video-melt"',
]

missing = [x for x in required if x not in text]
found_forbidden = [x for x in forbidden if x in text]

status = "PASS" if not missing and not found_forbidden else "FAIL"

payload = {
    "step": "17E-B6G-2A-R4-FIX7",
    "name": "Force chocolate melt into top-layer portal above navbar",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "missing_required": missing,
    "forbidden_found": found_forbidden,
    "rules_confirmed": {
        "dedicated_top_layer_host": "useChocolateTopLayerHost" in text,
        "host_max_z_index": 'node.style.zIndex = "2147483647"' in text,
        "nav_remains_clickable": 'node.style.pointerEvents = "none"' in text,
        "portal_targets_host_not_body": "host," in text and "document.body," not in text,
        "hero_scrollaway_kept": 'transform: `translate3d(0, ${-scrollY}px, 0)`' in text,
        "not_full_site_after_scroll": "visible: scrollY < height + 90" in text,
    },
}

report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps({
    "status": status,
    "report_path": str(report),
    "missing_required": missing,
    "forbidden_found": found_forbidden,
}, indent=2))

if status != "PASS":
    raise SystemExit(1)
