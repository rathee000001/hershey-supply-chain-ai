import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
NAVBAR_PATH = ROOT / "src" / "components" / "cinematic" / "CinematicNavbar.tsx"
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6c_r2_navbar_opacity_lab_report.json"

REQUIRED_TEXT = [
    '"use client";',
    'Hershey AI Lab',
    'Hershey Supply Chain AI',
    'bg-white/96',
    'bg-white/94',
    'portfolio-style-hershey-nav-active',
    'Decorative visuals do not create factual claims',
    '/supply-chain',
    '/evidence-brain',
    '/cost-model',
    '/sources',
    '/methodology',
]

FORBIDDEN_TEXT = [
    'Rathee Intelligence Lab',
    '@/components/hershey/',
    'ChocolateDripOverlay',
    'ChocolateDripHeader',
    'ChocolateMeltSystem',
    'Evidence count:',
    'profit margin',
    'Hershey internal',
    'Land O',
    'Barry Callebaut',
    'ASR',
    'McLane',
]

def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not NAVBAR_PATH.exists():
        report = {
            "step": "17E-B6C-R2",
            "name": "Navbar opacity and lab rename validation",
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
        warnings.append("Navbar is missing opacity/lab rename markers.")

    if forbidden_text_found:
        status = "FAIL"
        warnings.append("Navbar contains forbidden old labels/imports or hardcoded supplier/business claims.")

    report = {
        "step": "17E-B6C-R2",
        "name": "Navbar opacity and lab rename validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "status": status,
        "warnings": warnings,
        "navbar_path": str(NAVBAR_PATH.relative_to(ROOT)).replace("\\", "/"),
        "required_text_missing": missing_required_text,
        "forbidden_text_found": forbidden_text_found,
        "rules_confirmed": {
            "left_pill_renamed_to_hershey_ai_lab": "Hershey AI Lab" in content and "Rathee Intelligence Lab" not in content,
            "glass_opacity_increased": "bg-white/96" in content and "bg-white/94" in content,
            "portfolio_reference_layout_kept": "pointer-events-none fixed left-0 right-0 top-0 z-50 h-24" in content,
            "active_route_animation_present": "portfolio-style-hershey-nav-active" in content,
            "no_old_hershey_component_imports": "@/components/hershey/" not in content,
            "no_chocolate_drip_added_yet": "ChocolateDripHeader" not in content and "ChocolateDripOverlay" not in content,
            "no_supplier_cost_evidence_claims_hardcoded": not any(term in content for term in ["Land O", "Barry Callebaut", "ASR", "McLane"]),
        },
        "next_recommended_step": "Run npm run build. If clean, inspect screenshot before committing.",
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
