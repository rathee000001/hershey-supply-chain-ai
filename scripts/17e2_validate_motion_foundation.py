from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

required_files = [
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/components/cinematic/PremiumLoadingScene.tsx",
    "src/app/supply-chain/page.tsx",
]

required_terms = {
    "src/components/cinematic/MotionSafeWrapper.tsx": [
        "useReducedMotion",
        "motion.div",
        "whileInView",
        "prefersReducedMotion",
    ],
    "src/components/cinematic/PremiumLoadingScene.tsx": [
        "PremiumLoadingScene",
        "useReducedMotion",
        "motion.div",
        "Hershey Supply Chain AI",
    ],
    "src/app/supply-chain/page.tsx": [
        "PremiumLoadingScene",
        "Loading Hershey cinematic supply-chain intelligence",
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
    "run_name": "step17e2_validate_motion_foundation",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "missing_files": missing_files,
    "missing_terms": missing_terms,
    "next_step": (
        "Step 17E-B2: build CinematicPageShell and CinematicNavbar."
        if validation_status == "pass"
        else "Fix motion foundation files before continuing."
    ),
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / "step17e2_motion_foundation_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B1 MOTION FOUNDATION VALIDATION COMPLETE")
print("-------------------------------------------------")
print(f"Validation status: {validation_status}")
print(f"Missing files:     {len(missing_files)}")
print(f"Files with missing terms: {len(missing_terms)}")
print(f"Report JSON:       {report_path}")
print("")