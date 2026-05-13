from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


REQUIRED_COMPONENT_TERMS = [
    "Premium connected visual system",
    "CinematicConnectedMap",
    "hershey-flow-path",
    "Cow / Dairy Farm",
    "Sugarcane / Beet",
    "Cocoa Origin",
    "Hershey Factory Intake",
    "Mix → Form → Conveyor",
    "Wrapper / Packaging",
    "Retail Shelf",
    "Consumer Purchase",
    "DetailPanel",
]


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    component_path = root / "src" / "components" / "hershey" / "CinematicConnectedMap.tsx"
    page_path = root / "src" / "app" / "supply-chain" / "page.tsx"
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    missing_files = []
    if not component_path.exists():
        missing_files.append(str(component_path))
    if not page_path.exists():
        missing_files.append(str(page_path))

    component_text = component_path.read_text(encoding="utf-8") if component_path.exists() else ""
    page_text = page_path.read_text(encoding="utf-8") if page_path.exists() else ""

    missing_component_terms = [
        term for term in REQUIRED_COMPONENT_TERMS if term not in component_text
    ]

    page_import_ok = "CinematicConnectedMap" in page_text
    page_component_ok = "<CinematicConnectedMap" in page_text
    page_json_props_ok = all(
        term in page_text
        for term in [
            "ingredients={data.ingredients}",
            "suppliers={data.suppliers}",
            "graph={data.graph}",
            "costBreakdown={data.costBreakdown}",
        ]
    )

    validation_status = "pass"
    if (
        missing_files
        or missing_component_terms
        or not page_import_ok
        or not page_component_ok
        or not page_json_props_ok
    ):
        validation_status = "fail"

    report = {
        "run_name": "step17c_connected_visual_system_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "missing_files": missing_files,
        "missing_component_terms": missing_component_terms,
        "page_import_ok": page_import_ok,
        "page_component_ok": page_component_ok,
        "page_json_props_ok": page_json_props_ok,
        "component_path": str(component_path).replace("\\", "/"),
        "page_path": str(page_path).replace("\\", "/"),
        "next_step": (
            "Step 17D: premium visual asset layer with Hershey wrapper, unwrapped chocolate, and supplier logos."
            if validation_status == "pass"
            else "Fix connected visual system integration before Step 17D."
        ),
    }

    report_path = report_dir / "step17c_connected_visual_system_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17C CONNECTED VISUAL SYSTEM VALIDATION COMPLETE")
    print("----------------------------------------------------")
    print(f"Validation status:       {validation_status}")
    print(f"Missing files:           {len(missing_files)}")
    print(f"Missing component terms: {len(missing_component_terms)}")
    print(f"Page import ok:          {page_import_ok}")
    print(f"Page component ok:       {page_component_ok}")
    print(f"Page JSON props ok:      {page_json_props_ok}")
    print("")
    print(f"Report JSON:             {report_path}")
    print("")


if __name__ == "__main__":
    main()