import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6d_shell_global_theme_report.json"

FILES = {
    "shell": ROOT / "src/components/cinematic/CinematicPageShell.tsx",
    "atmosphere": ROOT / "src/components/cinematic/ChocolateAtmosphere.tsx",
    "globals": ROOT / "src/app/globals.css",
}

REQUIRED = {
    "shell": [
        "type PageMood",
        "pageMood?: PageMood",
        "showFloatingProductBadge?: boolean",
        "CinematicNavbar",
        "ChocolateAtmosphere",
        "ProductIdentityBadge",
        "Skip to main content",
        "Hershey AI Lab",
        "Evidence claims are not made from decorative visuals",
        "audited JSON evidence artifacts",
    ],
    "atmosphere": [
        "goldParticles",
        "chocolateDust",
        "useReducedMotion",
        "ChocolateAtmosphereProps",
        "mode?: \"light\" | \"dark\"",
    ],
    "globals": [
        "--hershey-dark",
        "--hershey-gold",
        "--hershey-cream-soft",
        "prefers-reduced-motion",
        "scroll-behavior",
    ],
}

FORBIDDEN_ALL = [
    "@/components/hershey/",
    "ChocolateDripOverlay",
    "ChocolateDripHeader",
    "ChocolateFlowDivider",
    "floatingDrops",
    "profit margin",
    "Hershey internal cost",
    "Land O",
    "Barry Callebaut",
    "ASR",
    "McLane",
]

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_files = []
    missing_required = {}
    forbidden_found = {}

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = path.read_text(encoding="utf-8")
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN_ALL if item in content]

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more required files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more files are missing required shell/global theme markers.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Forbidden old imports, drip components, or hardcoded claims found.")

    report = {
        "step": "17E-B6D",
        "name": "CinematicPageShell and global theme polish validation",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "shell_keeps_existing_props": not missing_required.get("shell"),
            "global_theme_variables_present": not missing_required.get("globals"),
            "atmosphere_has_no_blob_drip_layer": "floatingDrops" not in FILES["atmosphere"].read_text(encoding="utf-8") if FILES["atmosphere"].exists() else False,
            "no_chocolate_drip_built_yet": not any("ChocolateDripHeader" in items or "ChocolateFlowDivider" in items for items in forbidden_found.values()),
            "no_old_hershey_component_imports": not any("@/components/hershey/" in items for items in forbidden_found.values()),
            "no_supplier_or_cost_claims_hardcoded": not any(any(term in items for term in ["Land O", "Barry Callebaut", "ASR", "McLane", "profit margin"]) for items in forbidden_found.values()),
        },
        "next_recommended_step": "Run npm run build. If clean and screenshot is acceptable, commit/push Step 17E-B6D and continue to Step 17E-B6E.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
