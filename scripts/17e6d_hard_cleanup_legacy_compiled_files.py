from pathlib import Path
import shutil
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

moved = []
renamed = []
deleted_cache = []

archive_dest = root / "project_archive" / "compiled_legacy_hershey_17d"
archive_dest.mkdir(parents=True, exist_ok=True)

# These are legacy 17D files that must not compile anymore.
legacy_names = {
    "CinematicAssetScene.tsx",
    "CinematicConnectedMap.tsx",
    "CinematicSupplyChainStoryboard.tsx",
    "HersheyCinematicHero.tsx",
    "ChocolateDripOverlay.tsx",
}

# 1. Move any matching root-level legacy file from src/components/hershey.
hershey_root = root / "src" / "components" / "hershey"

if hershey_root.exists():
    for path in hershey_root.glob("*.tsx"):
        if path.name in legacy_names:
            dest = archive_dest / path.name
            counter = 1
            while dest.exists():
                dest = archive_dest / f"{path.stem}_{counter}{path.suffix}"
                counter += 1

            shutil.move(str(path), str(dest))
            moved.append({
                "from": str(path).replace("\\", "/"),
                "to": str(dest).replace("\\", "/"),
            })

# 2. Rename ALL TypeScript/TSX files in project_archive so TypeScript cannot compile them.
project_archive = root / "project_archive"

if project_archive.exists():
    for path in list(project_archive.rglob("*.tsx")) + list(project_archive.rglob("*.ts")):
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

# 3. Remove Next build cache so it cannot reuse stale TS diagnostics.
next_dir = root / ".next"
if next_dir.exists():
    shutil.rmtree(next_dir)
    deleted_cache.append(str(next_dir).replace("\\", "/"))

# 4. Make sure tsconfig excludes archive folders.
tsconfig_path = root / "tsconfig.json"
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))

exclude = tsconfig.get("exclude", [])
if not isinstance(exclude, list):
    exclude = []

needed = [
    "node_modules",
    ".next",
    "project_archive",
    "project_archive/**/*",
    "src/components/archive",
    "src/components/archive/**/*",
]

for item in needed:
    if item not in exclude:
        exclude.append(item)

tsconfig["exclude"] = exclude
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")

# 5. Scan remaining dangerous files.
remaining_dangerous = []

if hershey_root.exists():
    for path in hershey_root.glob("*.tsx"):
        remaining_dangerous.append(str(path).replace("\\", "/"))

remaining_archive_ts = []

if project_archive.exists():
    for path in list(project_archive.rglob("*.tsx")) + list(project_archive.rglob("*.ts")):
        if not path.name.endswith(".d.ts"):
            remaining_archive_ts.append(str(path).replace("\\", "/"))

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

status = "pass"
if remaining_dangerous or remaining_archive_ts:
    status = "fail"

report = {
    "run_name": "step17e6d_hard_cleanup_legacy_compiled_files",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "legacy_src_hershey_files_moved": moved,
    "project_archive_ts_files_renamed": renamed,
    "deleted_cache": deleted_cache,
    "remaining_root_hershey_tsx_files": remaining_dangerous,
    "remaining_project_archive_ts_files": remaining_archive_ts,
    "tsconfig_exclude": tsconfig["exclude"],
    "next_step": (
        "Run npm build. If it passes, reload VS Code and continue Step 17E-B5 validation."
        if status == "pass"
        else "Remove remaining listed TS/TSX files before build."
    ),
}

report_path = report_dir / "step17e6d_hard_cleanup_legacy_compiled_files_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5D HARD CLEANUP COMPLETE")
print("----------------------------------")
print(f"Status:                              {status}")
print(f"Legacy src/components/hershey moved: {len(moved)}")
print(f"Archive TS/TSX renamed:              {len(renamed)}")
print(f"Next cache deleted:                   {len(deleted_cache)}")
print(f"Remaining root Hershey TSX:           {len(remaining_dangerous)}")
print(f"Remaining archive TS/TSX:             {len(remaining_archive_ts)}")
print(f"Report JSON:                          {report_path}")
print("")