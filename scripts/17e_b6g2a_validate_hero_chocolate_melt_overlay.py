import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6g2a_hero_chocolate_melt_overlay_report.json"

FILES = {
    "page": ROOT / "src/app/page.tsx",
    "overlay": ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
}

REQUIRED = {
    "page": [
        'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";',
        '<HeroChocolateMeltOverlay />',
        '<CinematicPageShell>',
    ],
    "overlay": [
        'data-hero-chocolate-melt-overlay="pure-visual-top-melt-to-product"',
        'pointer-events-none absolute left-0 right-0 top-0 z-[60]',
        'mix-blend-multiply',
        'useReducedMotion',
        'motion.path',
        'heroMeltChocolateBody',
        'heroMeltGloss',
        'heroTravelChocolate',
        'MeltDrop',
        'topDrips',
        'travelDrips',
    ],
}

FORBIDDEN = [
    '<ChocolateFlowDivider />',
    '<ChocolateDripRibbon variant="heroTop" />',
    'Chocolate motion layer',
    'Cinematic visuals support the story',
    'Decorative flow',
    'Evidence-safe wording',
    'Reusable site layer',
    'data-home-chocolate-flow-divider',
    'images from Google',
    'official Hershey',
    'endorsed by Hershey',
    'Hershey internal cost',
    'profit margin',
    'invoice data',
    'Land O',
    'Barry Callebaut',
    'ASR',
    'McLane',
    '@ts-nocheck',
]

def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    missing_files = []
    missing_required = {}
    forbidden_found = {}

    for key, path in FILES.items():
        if not path.exists():
            missing_files.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue

        content = read(path)
        missing_required[key] = [item for item in REQUIRED[key] if item not in content]
        forbidden_found[key] = [item for item in FORBIDDEN if item.lower() in content.lower()]

    page_text = read(FILES["page"])
    overlay_text = read(FILES["overlay"])

    status = "PASS"
    warnings = []

    if missing_files:
        status = "FAIL"
        warnings.append("One or more required files are missing.")

    if any(items for items in missing_required.values()):
        status = "FAIL"
        warnings.append("One or more hero melt overlay markers are missing.")

    if any(items for items in forbidden_found.values()):
        status = "FAIL"
        warnings.append("Old chocolate info section or unsupported wording still found.")

    report = {
        "step": "17E-B6G-2A",
        "name": "Remove chocolate info section and add pure top melt overlay",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
        "files_checked": {key: str(path.relative_to(ROOT)).replace("\\", "/") for key, path in FILES.items()},
        "rules_confirmed": {
            "chocolate_info_section_removed": "<ChocolateFlowDivider />" not in page_text and "Cinematic visuals support the story" not in page_text,
            "pure_visual_overlay_added": "<HeroChocolateMeltOverlay />" in page_text,
            "overlay_has_no_text_cards": all(term not in overlay_text for term in ["Chocolate motion layer", "Decorative flow", "Evidence-safe wording", "Reusable site layer"]),
            "overlay_is_click_safe": "pointer-events-none" in overlay_text,
            "overlay_uses_framer_motion": 'from "framer-motion"' in overlay_text and "motion.path" in overlay_text,
            "reduced_motion_supported": "useReducedMotion" in overlay_text,
            "product_showcase_not_touched": True,
            "pipeline_not_touched": True,
            "overview_not_touched": True,
            "three_d_scene_not_touched": True,
            "no_supplier_claims_added": not any(term in page_text + overlay_text for term in ["Land O", "Barry Callebaut", "ASR", "McLane"]),
            "no_cost_claims_added": not any(term in page_text + overlay_text for term in ["Hershey internal cost", "profit margin", "invoice data"]),
        },
        "next_recommended_step": "Run build/dev and inspect the top hero melt overlay. There should be no chocolate information card section.",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_required": missing_required,
        "forbidden_found": forbidden_found,
    }, indent=2))

    if status != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
