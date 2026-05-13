from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

required_files = [
    "src/components/cinematic/ChocolateAtmosphere.tsx",
    "src/components/cinematic/ProductIdentityBadge.tsx",
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/app/page.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
]

required_terms = {
    "src/components/cinematic/ChocolateAtmosphere.tsx": [
        "ChocolateAtmosphere",
        "floatingDrops",
        "chocolate",
        "useReducedMotion",
    ],
    "src/components/cinematic/ProductIdentityBadge.tsx": [
        "ProductIdentityBadge",
        "hershey_wrapper_front",
        "Target SKU",
        "Hershey 1.55 oz Milk Chocolate",
    ],
    "src/components/cinematic/CinematicPageShell.tsx": [
        "ChocolateAtmosphere",
        "ProductIdentityBadge",
        "showProductBadge",
        "CinematicNavbar",
    ],
    "src/app/supply-chain/page.tsx": [
        "CinematicPageShell",
        "Hershey 1.55 oz Supply Chain World",
        "Step 17E-B5 next",
    ],
}

route_shell_pages = [
    "src/app/page.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
]

missing_files = []
missing_terms = {}
routes_missing_shell = []

for rel_path in required_files:
    path = root / rel_path
    if not path.exists():
        missing_files.append(rel_path)
        continue

    text = path.read_text(encoding="utf-8")
    missing = [term for term in required_terms.get(rel_path, []) if term not in text]
    if missing:
        missing_terms[rel_path] = missing

for rel_path in route_shell_pages:
    path = root / rel_path
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "CinematicPageShell" not in text:
            routes_missing_shell.append(rel_path)

validation_status = "pass"
if missing_files or missing_terms or routes_missing_shell:
    validation_status = "fail"

report = {
    "run_name": "step17e5_validate_global_chocolate_shell",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "missing_files": missing_files,
    "missing_terms": missing_terms,
    "routes_missing_shell": routes_missing_shell,
    "next_step": (
        "Step 17E-B5: Home page Three.js hero animation."
        if validation_status == "pass"
        else "Fix global chocolate shell integration before Step 17E-B5."
    ),
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / "step17e5_global_chocolate_shell_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B4 GLOBAL CHOCOLATE SHELL VALIDATION COMPLETE")
print("------------------------------------------------------")
print(f"Validation status:    {validation_status}")
print(f"Missing files:        {len(missing_files)}")
print(f"Files missing terms:  {len(missing_terms)}")
print(f"Routes missing shell: {len(routes_missing_shell)}")
print(f"Report JSON:          {report_path}")
print("")