from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

required_files = [
    "src/app/page.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
]

required_home_terms = [
    "Hershey",
    "Supply Chain",
    "Intelligence.",
    "Praveen Rathee",
    "Dr. Rajendra Tibrewala",
    "MGMT 780",
    "Supply Chain Management",
    "JSON-first",
    "Three.js Supply Chain World",
    "Project Overview",
    "Intelligence Pipeline",
]

empty_route_files = []
missing_files = []

for rel_path in required_files:
    path = root / rel_path
    if not path.exists():
        missing_files.append(rel_path)
        continue
    if len(path.read_text(encoding="utf-8").strip()) == 0:
        empty_route_files.append(rel_path)

home_path = root / "src" / "app" / "page.tsx"
home_text = home_path.read_text(encoding="utf-8") if home_path.exists() else ""

missing_home_terms = [
    term for term in required_home_terms if term not in home_text
]

validation_status = "pass"
if missing_files or empty_route_files or missing_home_terms:
    validation_status = "fail"

report = {
    "run_name": "step17e3_validate_home_rebuild",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "missing_files": missing_files,
    "empty_route_files": empty_route_files,
    "missing_home_terms": missing_home_terms,
    "next_step": (
        "Step 17E-B3: build CinematicPageShell and Gold-style cinematic navbar."
        if validation_status == "pass"
        else "Fix home page or empty route files before continuing."
    ),
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / "step17e3_home_rebuild_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B2 HOME REBUILD VALIDATION COMPLETE")
print("--------------------------------------------")
print(f"Validation status:  {validation_status}")
print(f"Missing files:      {len(missing_files)}")
print(f"Empty route files:  {len(empty_route_files)}")
print(f"Missing home terms: {len(missing_home_terms)}")
print(f"Report JSON:        {report_path}")
print("")