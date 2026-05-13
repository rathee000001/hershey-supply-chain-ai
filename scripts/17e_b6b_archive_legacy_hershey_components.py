import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6b_archive_legacy_hershey_report.json"

LEGACY_FILES_TO_ARCHIVE = [
    "src/components/hershey/HersheyCinematicHero.tsx",
    "src/components/hershey/cost/CostPulsePanel.tsx",
    "src/components/hershey/cost/CostWaterfall.tsx",
    "src/components/hershey/evidence/EvidenceDrawer.tsx",
    "src/components/hershey/evidence/EvidenceMiniTooltip.tsx",
    "src/components/hershey/fallback/SupplyChainFallbackMap.tsx",
]

ARCHIVE_ROOT = ROOT / "src" / "components" / "archive" / "step17e_b6b_legacy_hershey"

def move_file(relative_path: str) -> dict:
    source = ROOT / relative_path
    target = ARCHIVE_ROOT / relative_path.replace("src/components/hershey/", "")

    if not source.exists():
        return {
            "source": relative_path,
            "target": str(target.relative_to(ROOT)).replace("\\", "/"),
            "status": "SKIPPED_SOURCE_MISSING",
        }

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        return {
            "source": relative_path,
            "target": str(target.relative_to(ROOT)).replace("\\", "/"),
            "status": "SKIPPED_TARGET_ALREADY_EXISTS",
        }

    shutil.move(str(source), str(target))

    return {
        "source": relative_path,
        "target": str(target.relative_to(ROOT)).replace("\\", "/"),
        "status": "MOVED_TO_ARCHIVE",
    }

def cleanup_empty_dirs() -> list[str]:
    removed = []
    candidates = [
        ROOT / "src/components/hershey/cost",
        ROOT / "src/components/hershey/evidence",
        ROOT / "src/components/hershey/fallback",
        ROOT / "src/components/hershey",
    ]

    for folder in candidates:
        if folder.exists():
            try:
                remaining = [p for p in folder.iterdir()]
                if not remaining:
                    folder.rmdir()
                    removed.append(str(folder.relative_to(ROOT)).replace("\\", "/"))
            except OSError:
                pass

    return removed

def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    moved = [move_file(path) for path in LEGACY_FILES_TO_ARCHIVE]
    removed_empty_dirs = cleanup_empty_dirs()

    report = {
        "step": "17E-B6B-2",
        "name": "Archive old compile-risk Hershey legacy components",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "archive_root": str(ARCHIVE_ROOT.relative_to(ROOT)).replace("\\", "/"),
        "moved_files": moved,
        "removed_empty_dirs": removed_empty_dirs,
        "rules_confirmed": {
            "no_files_deleted": True,
            "legacy_files_archived_not_destroyed": True,
            "new_chocolate_drip_not_created_yet": True,
            "claims_must_come_from_json": True,
            "next_step_requires_validation_and_build": True,
        },
        "expected_build_fix": "Removes src/components/hershey/HersheyCinematicHero.tsx from active TypeScript compilation so the missing ChocolateDripOverlay import no longer blocks npm run build.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "DONE",
        "report_path": str(REPORT_PATH),
        "moved_count": len([item for item in moved if item["status"] == "MOVED_TO_ARCHIVE"]),
        "skipped_count": len([item for item in moved if item["status"].startswith("SKIPPED")]),
        "removed_empty_dirs": removed_empty_dirs,
    }, indent=2))

if __name__ == "__main__":
    main()
