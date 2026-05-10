from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    component_path = root / "src" / "components" / "hershey" / "CinematicSupplyChainStoryboard.tsx"
    page_path = root / "src" / "app" / "supply-chain" / "page.tsx"
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    missing = []
    if not component_path.exists():
        missing.append(str(component_path))
    if not page_path.exists():
        missing.append(str(page_path))

    page_text = page_path.read_text(encoding="utf-8") if page_path.exists() else ""
    component_text = component_path.read_text(encoding="utf-8") if component_path.exists() else ""

    required_story_terms = [
        "Dairy Flow",
        "Sugar Flow",
        "Cocoa / Chocolate Flow",
        "Inside Hershey: Combine",
        "Distribution → Retail → Consumer",
        "Cost pulse foundation",
    ]

    missing_terms = [term for term in required_story_terms if term not in component_text]

    page_import_ok = "CinematicSupplyChainStoryboard" in page_text
    page_component_ok = "<CinematicSupplyChainStoryboard" in page_text

    validation_status = "pass"
    if missing or missing_terms or not page_import_ok or not page_component_ok:
        validation_status = "fail"

    report = {
        "run_name": "step17b_cinematic_storyboard_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "missing_files": missing,
        "missing_story_terms": missing_terms,
        "page_import_ok": page_import_ok,
        "page_component_ok": page_component_ok,
        "storyboard_component": str(component_path).replace("\\", "/"),
        "supply_chain_page": str(page_path).replace("\\", "/"),
        "next_step": (
            "Step 17C: add premium visual asset layer and cinematic animation polish."
            if validation_status == "pass"
            else "Fix storyboard integration before moving forward."
        ),
    }

    report_path = report_dir / "step17b_cinematic_storyboard_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17B CINEMATIC STORYBOARD VALIDATION COMPLETE")
    print("------------------------------------------------")
    print(f"Validation status: {validation_status}")
    print(f"Missing files:     {len(missing)}")
    print(f"Missing terms:     {len(missing_terms)}")
    print(f"Page import ok:    {page_import_ok}")
    print(f"Page component ok: {page_component_ok}")
    print("")
    print(f"Report JSON:       {report_path}")
    print("")


if __name__ == "__main__":
    main()