import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6b_archive_validation_report.json"

ACTIVE_LEGACY_FILES = [
    "src/components/hershey/HersheyCinematicHero.tsx",
    "src/components/hershey/cost/CostPulsePanel.tsx",
    "src/components/hershey/cost/CostWaterfall.tsx",
    "src/components/hershey/evidence/EvidenceDrawer.tsx",
    "src/components/hershey/evidence/EvidenceMiniTooltip.tsx",
    "src/components/hershey/fallback/SupplyChainFallbackMap.tsx",
]

ARCHIVED_EXPECTED_FILES = [
    "src/components/archive/step17e_b6b_legacy_hershey/HersheyCinematicHero.tsx",
    "src/components/archive/step17e_b6b_legacy_hershey/cost/CostPulsePanel.tsx",
    "src/components/archive/step17e_b6b_legacy_hershey/cost/CostWaterfall.tsx",
    "src/components/archive/step17e_b6b_legacy_hershey/evidence/EvidenceDrawer.tsx",
    "src/components/archive/step17e_b6b_legacy_hershey/evidence/EvidenceMiniTooltip.tsx",
    "src/components/archive/step17e_b6b_legacy_hershey/fallback/SupplyChainFallbackMap.tsx",
]

ROUTES = [
    "src/app/page.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
]

def exists(path: str) -> bool:
    return (ROOT / path).exists()

def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    active_legacy_still_present = [path for path in ACTIVE_LEGACY_FILES if exists(path)]
    archived_missing = [path for path in ARCHIVED_EXPECTED_FILES if not exists(path)]
    route_missing = [path for path in ROUTES if not exists(path)]

    status = "PASS"
    warnings = []

    if active_legacy_still_present:
        status = "FAIL"
        warnings.append("Some old src/components/hershey legacy files are still active and may compile.")

    if archived_missing:
        warnings.append("Some expected archived files are missing. This may be okay only if they were already removed earlier.")

    if route_missing:
        status = "FAIL"
        warnings.append("One or more active route files are missing.")

    report = {
        "step": "17E-B6B-2-validation",
        "name": "Validate legacy Hershey archive cleanup",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "active_legacy_still_present": active_legacy_still_present,
        "archived_missing": archived_missing,
        "route_missing": route_missing,
        "next_recommended_action": "Run npm run build. If build fails, send the exact error output.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "active_legacy_still_present": active_legacy_still_present,
        "archived_missing": archived_missing,
        "route_missing": route_missing,
    }, indent=2))

    if status == "FAIL":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
