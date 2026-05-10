from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

required_files = [
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/app/page.tsx",
]

required_terms = {
    "src/components/cinematic/CinematicNavbar.tsx": [
        "HERSHEY",
        "SUPPLY CHAIN",
        "EVIDENCE BRAIN",
        "COST MODEL",
        "METHODOLOGY",
        "hershey-navbar-active",
        "JSON-first",
    ],
    "src/components/cinematic/CinematicPageShell.tsx": [
        "CinematicNavbar",
        "footerMode",
        "Study project by Praveen Rathee",
        "Not affiliated with",
    ],
    "src/app/page.tsx": [
        "CinematicPageShell",
        "MotionSafeWrapper",
        "Hershey",
        "Supply Chain",
        "Intelligence.",
        "Praveen Rathee",
        "Dr. Rajendra Tibrewala",
        "MGMT 780",
        "Three.js Supply Chain World",
        "Intelligence Pipeline",
    ],
}

missing_files = []
missing_terms = {}

for rel_path in required_files:
    path = root / rel_path
    if not path.exists():
        missing_files.append(rel_path)
        continue

    text = path.read_text(encoding="utf-8")
    missing = [term for term in required_terms.get(rel_path, []) if term not in text]
    if missing:
        missing_terms[rel_path] = missing

validation_status = "pass"
if missing_files or missing_terms:
    validation_status = "fail"

report = {
    "run_name": "step17e4_validate_shell_nav_home",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "missing_files": missing_files,
    "missing_terms": missing_terms,
    "next_step": (
        "Step 17E-B4: create global chocolate loading and chocolate atmosphere layer."
        if validation_status == "pass"
        else "Fix navbar/shell/home files before Step 17E-B4."
    ),
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / "step17e4_shell_nav_home_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B3 SHELL / NAV / HOME VALIDATION COMPLETE")
print("--------------------------------------------------")
print(f"Validation status: {validation_status}")
print(f"Missing files:     {len(missing_files)}")
print(f"Missing term files:{len(missing_terms)}")
print(f"Report JSON:       {report_path}")
print("")