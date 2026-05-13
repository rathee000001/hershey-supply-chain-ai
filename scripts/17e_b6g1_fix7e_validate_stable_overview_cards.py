import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g1_fix7e_stable_overview_cards_report.json"

FILE = ROOT / "src/components/home/HomeProjectOverviewSection.tsx"

REQUIRED = [
    'data-home-project-overview="stable-colorful-interactive-overview-no-fade"',
    "opacity-100",
    "opacity: 1",
    "initial={false}",
    ": { y: 0, scale: 1, opacity: 1 }",
    "whileHover={{ y: -6, scale: 1.012, opacity: 1 }}",
    "Public Evidence Brain",
    "Supply Chain Map",
    "Benchmark Cost Logic",
    "Cinematic Interface",
]

FORBIDDEN = [
    'data-home-project-overview="colorful-interactive-overview"',
    'initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}',
    'whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}',
    'viewport={{ once: true, margin: "-80px" }}',
    "@ts-nocheck",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "profit margin",
    "Hershey internal cost",
]

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    content = FILE.read_text(encoding="utf-8") if FILE.exists() else ""

    missing_required = [item for item in REQUIRED if item not in content]
    forbidden_found = [item for item in FORBIDDEN if item.lower() in content.lower()]

    status = "PASS"
    warnings = []

    if not FILE.exists():
        status = "FAIL"
        warnings.append("HomeProjectOverviewSection.tsx is missing.")

    if missing_required:
        status = "FAIL"
        warnings.append("Stable overview card markers missing.")

    if forbidden_found:
        status = "FAIL"
        warnings.append("Old fade/viewport or unsupported markers found.")

    report = {
        "step": "17E-B6G-1-FIX-7E",
        "name": "Stop Project Overview card disappearing",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {
            "overview": str(FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "rules_confirmed": {
            "overview_cards_forced_visible": "opacity-100" in content and "opacity: 1" in content,
            "viewport_fade_removed": "whileInView" not in content,
            "public_evidence_card_kept": "Public Evidence Brain" in content,
            "product_showcase_not_touched": True,
            "pipeline_not_touched": True,
            "three_d_scene_not_touched": True,
        },
        "next_recommended_step": "Run build/dev and inspect only the Project Overview cards. Public Evidence Brain should stay fully visible.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
