from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

archive_roots = [
    root / "project_archive",
    root / "src" / "components" / "archive",
]

renamed = []

for archive_root in archive_roots:
    if not archive_root.exists():
        continue

    for path in list(archive_root.rglob("*.tsx")) + list(archive_root.rglob("*.ts")):
        if path.name.endswith(".d.ts"):
            continue

        new_path = path.with_name(path.name + ".archive.txt")

        counter = 1
        while new_path.exists():
            new_path = path.with_name(path.name + f".archive_{counter}.txt")
            counter += 1

        path.rename(new_path)
        renamed.append({
            "from": str(path).replace("\\", "/"),
            "to": str(new_path).replace("\\", "/"),
        })

# Add explicit TypeScript excludes.
tsconfig_path = root / "tsconfig.json"
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))

existing_exclude = tsconfig.get("exclude", [])
if not isinstance(existing_exclude, list):
    existing_exclude = []

needed_excludes = [
    "node_modules",
    "project_archive",
    "project_archive/**/*",
    "src/components/archive",
    "src/components/archive/**/*",
]

for item in needed_excludes:
    if item not in existing_exclude:
        existing_exclude.append(item)

tsconfig["exclude"] = existing_exclude
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e6c_deactivate_archived_tsx",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "archived_ts_files_renamed": renamed,
    "tsconfig_exclude": tsconfig["exclude"],
    "next_step": "Run Step 17E-B5 validation and npm build.",
}

report_path = report_dir / "step17e6c_deactivate_archived_tsx_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5C ARCHIVED TSX DEACTIVATION COMPLETE")
print("------------------------------------------------")
print(f"Archived TS/TSX files renamed: {len(renamed)}")
print(f"tsconfig updated:              {tsconfig_path}")
print(f"Report JSON:                   {report_path}")
print("")