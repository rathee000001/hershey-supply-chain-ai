import json
from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
report = ROOT / "artifacts/10_run_reports/step17e_b6g2a_r4_fix8_nav_spill_above_navbar_report.json"

text = overlay.read_text(encoding="utf-8")

required = [
    "function ChocolateNavSpillLayer",
    'data-hero-chocolate-nav-spill="above-navbar-pills"',
    '<ChocolateNavSpillLayer scrollY={scrollY} visible={visible} />',
    'node.style.zIndex = "2147483647"',
    'data-hero-chocolate-melt-overlay="top-layer-video-plus-nav-spill-melt"',
    'pointer-events-none',
    'transform: `translate3d(0, ${-scrollY}px, 0)`',
    'visible: scrollY < height + 90',
    'mixBlendMode: "multiply"',
    'mixBlendMode: "screen"',
]

forbidden = [
    'data-hero-chocolate-melt-overlay="portal-document-top-hero-only-video-melt"',
    'data-hero-chocolate-melt-overlay="portal-absolute-hero-scoped-video-melt"',
    'data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"',
    'document.body,',
    '@ts-nocheck',
]

missing = [x for x in required if x not in text]
found_forbidden = [x for x in forbidden if x in text]
status = "PASS" if not missing and not found_forbidden else "FAIL"

payload = {
    "step": "17E-B6G-2A-R4-FIX8",
    "name": "Add explicit nav-spill chocolate layer above navbar",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "missing_required": missing,
    "forbidden_found": found_forbidden,
    "rules_confirmed": {
        "nav_spill_layer_present": "function ChocolateNavSpillLayer" in text,
        "nav_spill_above_navbar_marker": 'data-hero-chocolate-nav-spill="above-navbar-pills"' in text,
        "top_host_max_z": 'node.style.zIndex = "2147483647"' in text,
        "nav_clicks_not_blocked": "pointer-events-none" in text,
        "hero_scrollaway_kept": 'transform: `translate3d(0, ${-scrollY}px, 0)`' in text,
        "hidden_after_hero": "visible: scrollY < height + 90" in text,
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
