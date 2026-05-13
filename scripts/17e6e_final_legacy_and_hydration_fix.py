from pathlib import Path
import shutil
import json
import re
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

legacy_names = {
    "CinematicAssetScene.tsx",
    "CinematicConnectedMap.tsx",
    "CinematicSupplyChainStoryboard.tsx",
    "HersheyCinematicHero.tsx",
    "ChocolateDripOverlay.tsx",
}

moved_src_legacy = []
renamed_archive_ts = []
deleted_cache = []
layout_patch_notes = []

archive_dest = root / "project_archive" / "final_legacy_compiled_cleanup_17e"
archive_dest.mkdir(parents=True, exist_ok=True)

# 1. Move exact legacy files from src/components/hershey if they still exist.
hershey_root = root / "src" / "components" / "hershey"

if hershey_root.exists():
    for name in legacy_names:
        path = hershey_root / name
        if path.exists():
            dest = archive_dest / f"{name}.archive.txt"
            counter = 1
            while dest.exists():
                dest = archive_dest / f"{name}.archive_{counter}.txt"
                counter += 1

            shutil.move(str(path), str(dest))
            moved_src_legacy.append({
                "from": str(path).replace("\\", "/"),
                "to": str(dest).replace("\\", "/"),
            })

# 2. Rename all archived TypeScript files so TypeScript cannot compile them.
archive_roots = [
    root / "project_archive",
    root / "src" / "components" / "archive",
]

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
        renamed_archive_ts.append({
            "from": str(path).replace("\\", "/"),
            "to": str(new_path).replace("\\", "/"),
        })

# 3. Update tsconfig excludes.
tsconfig_path = root / "tsconfig.json"
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))

exclude = tsconfig.get("exclude", [])
if not isinstance(exclude, list):
    exclude = []

needed_excludes = [
    "node_modules",
    ".next",
    "project_archive",
    "project_archive/**/*",
    "src/components/archive",
    "src/components/archive/**/*",
]

for item in needed_excludes:
    if item not in exclude:
        exclude.append(item)

tsconfig["exclude"] = exclude
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")

# 4. Patch layout.tsx for browser-extension hydration attributes.
layout_path = root / "src" / "app" / "layout.tsx"

if layout_path.exists():
    text = layout_path.read_text(encoding="utf-8")

    if "<html" in text and "suppressHydrationWarning" not in text.split("<body")[0]:
        text = re.sub(
            r"<html([^>]*)>",
            lambda m: "<html" + m.group(1) + " suppressHydrationWarning>",
            text,
            count=1,
        )
        layout_patch_notes.append("Added suppressHydrationWarning to html.")

    if "<body" in text:
        body_match = re.search(r"<body([^>]*)>", text)
        if body_match and "suppressHydrationWarning" not in body_match.group(0):
            text = re.sub(
                r"<body([^>]*)>",
                lambda m: "<body" + m.group(1) + " suppressHydrationWarning>",
                text,
                count=1,
            )
            layout_patch_notes.append("Added suppressHydrationWarning to body.")

    layout_path.write_text(text, encoding="utf-8")

# 5. Delete Next cache.
next_dir = root / ".next"
if next_dir.exists():
    shutil.rmtree(next_dir)
    deleted_cache.append(str(next_dir).replace("\\", "/"))

# 6. Scan remaining problems.
remaining_src_legacy = []
if hershey_root.exists():
    for name in legacy_names:
        path = hershey_root / name
        if path.exists():
            remaining_src_legacy.append(str(path).replace("\\", "/"))

remaining_archive_ts = []
for archive_root in archive_roots:
    if archive_root.exists():
        for path in list(archive_root.rglob("*.tsx")) + list(archive_root.rglob("*.ts")):
            if not path.name.endswith(".d.ts"):
                remaining_archive_ts.append(str(path).replace("\\", "/"))

layout_text = layout_path.read_text(encoding="utf-8") if layout_path.exists() else ""
layout_has_html_suppress = "<html" in layout_text and "suppressHydrationWarning" in layout_text.split("<body")[0]
layout_has_body_suppress = bool(re.search(r"<body[^>]*suppressHydrationWarning", layout_text))

status = "pass"
if remaining_src_legacy or remaining_archive_ts or not layout_has_html_suppress or not layout_has_body_suppress:
    status = "fail"

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e6e_final_legacy_and_hydration_fix",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "moved_src_legacy": moved_src_legacy,
    "renamed_archive_ts": renamed_archive_ts,
    "deleted_cache": deleted_cache,
    "layout_patch_notes": layout_patch_notes,
    "remaining_src_legacy": remaining_src_legacy,
    "remaining_archive_ts": remaining_archive_ts,
    "layout_has_html_suppress": layout_has_html_suppress,
    "layout_has_body_suppress": layout_has_body_suppress,
    "tsconfig_exclude": tsconfig["exclude"],
    "important_note": "If the hydration overlay still appears, test in Incognito or disable Grammarly/browser extensions. The shown data-gr attributes come from a browser extension.",
    "next_step": "Run npm build, reload VS Code if Problems panel is stale, then continue to Step 17F.",
}

report_path = report_dir / "step17e6e_final_legacy_and_hydration_fix_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5E FINAL LEGACY + HYDRATION FIX COMPLETE")
print("--------------------------------------------------")
print(f"Status:                  {status}")
print(f"Moved src legacy files:  {len(moved_src_legacy)}")
print(f"Renamed archive TS/TSX:  {len(renamed_archive_ts)}")
print(f"Deleted .next cache:     {len(deleted_cache)}")
print(f"Remaining src legacy:    {len(remaining_src_legacy)}")
print(f"Remaining archive TS:    {len(remaining_archive_ts)}")
print(f"HTML suppress:           {layout_has_html_suppress}")
print(f"Body suppress:           {layout_has_body_suppress}")
print(f"Report JSON:             {report_path}")
print("")