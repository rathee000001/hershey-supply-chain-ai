import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
NAVBAR_PATH = ROOT / "src" / "components" / "cinematic" / "CinematicNavbar.tsx"
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6c_r3_navbar_text_visibility_report.json"

content = NAVBAR_PATH.read_text(encoding="utf-8")

required = [
    "Hershey AI Lab",
    "text-[#fff1a8]",
    "text-[#9a6a28]",
    "text-[#2d0d06]",
    "bg-[#151820]/98",
    "portfolio-style-hershey-nav-active",
]

forbidden = [
    "Rathee Intelligence Lab",
    "@/components/hershey/",
    "ChocolateDripOverlay",
    "ChocolateDripHeader",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
    "profit margin",
    "Hershey internal",
]

missing = [item for item in required if item not in content]
found_forbidden = [item for item in forbidden if item in content]

status = "PASS" if not missing and not found_forbidden else "FAIL"

report = {
    "step": "17E-B6C-R3",
    "name": "Navbar text visibility patch validation",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "navbar_path": "src/components/cinematic/CinematicNavbar.tsx",
    "required_text_missing": missing,
    "forbidden_text_found": found_forbidden,
    "rules_confirmed": {
        "left_pill_label_is_hershey_ai_lab": "Hershey AI Lab" in content,
        "left_pill_text_brightened": "text-[#fff1a8]" in content,
        "center_pill_text_darkened": "text-[#2d0d06]" in content,
        "portfolio_label_visible": "text-[#9a6a28]" in content,
        "no_chocolate_drip_added_yet": "ChocolateDripHeader" not in content and "ChocolateDripOverlay" not in content,
        "no_supplier_cost_claims_hardcoded": not any(term in content for term in ["Land O", "Barry Callebaut", "ASR", "McLane"]),
    },
    "next_recommended_step": "Run npm run build. If clean, commit and push navbar step, then proceed to Step 17E-B6D.",
}

REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({
    "status": status,
    "report_path": str(REPORT_PATH),
    "required_text_missing": missing,
    "forbidden_text_found": found_forbidden,
}, indent=2))

if status != "PASS":
    raise SystemExit(1)
