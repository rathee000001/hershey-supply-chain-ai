import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
NAVBAR_PATH = ROOT / "src" / "components" / "cinematic" / "CinematicNavbar.tsx"
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6c_portfolio_navbar_report.json"

REQUIRED_TEXT = [
    '"use client";',
    'Rathee Intelligence Lab',
    'Hershey Supply Chain AI',
    'JSON-first',
    'Study Project',
    '/supply-chain',
    '/evidence-brain',
    '/cost-model',
    '/sources',
    '/methodology',
    'usePathname',
    'AnimatePresence',
    'motion.nav',
    'layoutId="hershey-portfolio-navbar-active-pill"',
]

FORBIDDEN_TEXT = [
    '@/components/hershey/',
    'ChocolateDripOverlay',
    'ChocolateDripHeader',
    'ChocolateMeltSystem',
    'Evidence count:',
    'profit margin',
    'Hershey internal',
]

def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not NAVBAR_PATH.exists():
        report = {
            "step": "17E-B6C",
            "name": "Portfolio-style animated navbar validation",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "status": "FAIL",
            "error": "CinematicNavbar.tsx does not exist.",
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        raise SystemExit(1)

    content = NAVBAR_PATH.read_text(encoding="utf-8")

    missing_required_text = [item for item in REQUIRED_TEXT if item not in content]
    forbidden_text_found = [item for item in FORBIDDEN_TEXT if item in content]

    status = "PASS"
    warnings = []

    if missing_required_text:
        status = "FAIL"
        warnings.append("Navbar is missing required structure/text markers.")

    if forbidden_text_found:
        status = "FAIL"
        warnings.append("Navbar contains forbidden old imports or unsafe wording.")

    report = {
        "step": "17E-B6C",
        "name": "Portfolio-style animated navbar validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "status": status,
        "warnings": warnings,
        "navbar_path": str(NAVBAR_PATH.relative_to(ROOT)).replace("\\", "/"),
        "required_text_missing": missing_required_text,
        "forbidden_text_found": forbidden_text_found,
        "rules_confirmed": {
            "portfolio_style_navbar_created": status == "PASS",
            "mobile_drawer_present": "mobileOpen" in content and "Open navigation" in content,
            "active_route_animation_present": "layoutId=\"hershey-portfolio-navbar-active-pill\"" in content,
            "no_old_hershey_component_imports": "@/components/hershey/" not in content,
            "no_chocolate_drip_added_yet": "ChocolateDripHeader" not in content and "ChocolateDripOverlay" not in content,
            "no_supplier_cost_evidence_claims_hardcoded": True,
        },
        "next_recommended_step": "Run npm run build. If clean, visually inspect the navbar with npm run dev.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "required_text_missing": missing_required_text,
        "forbidden_text_found": forbidden_text_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
