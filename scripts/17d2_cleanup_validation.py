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

    page_path = root / "src" / "app" / "supply-chain" / "page.tsx"
    hero_path = root / "src" / "components" / "hershey" / "HersheyCinematicHero.tsx"
    drip_path = root / "src" / "components" / "hershey" / "ChocolateDripOverlay.tsx"
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    missing_files = [
        str(path)
        for path in [page_path, hero_path, drip_path]
        if not path.exists()
    ]

    page_text = page_path.read_text(encoding="utf-8") if page_path.exists() else ""
    hero_text = hero_path.read_text(encoding="utf-8") if hero_path.exists() else ""
    drip_text = drip_path.read_text(encoding="utf-8") if drip_path.exists() else ""

    required_page_terms = [
        "HersheyCinematicHero",
        "CinematicAssetScene",
        "CinematicConnectedMap",
        "Cost Intelligence",
        "Evidence Graph",
        "Safety Rules",
    ]

    forbidden_page_terms = [
        "Ingredient Cards from JSON",
        "Supplier / Stage Cards from JSON",
        "CinematicSupplyChainStoryboard",
    ]

    required_hero_terms = [
        "Actual collected product visual",
        "hershey_wrapper_front",
        "hershey_wrapper_back",
        "hershey_unwrapped_bar",
        "ChocolateDripOverlay",
    ]

    required_drip_terms = [
        "CHOCOLATE_MELT_URL",
        "real-chocolate-melt",
        "chocolateImageFloat",
        "chocolateGlossSweep",
        "chocolate_melt_drip.webp",
    ]

    missing_page_terms = [term for term in required_page_terms if term not in page_text]
    forbidden_terms_found = [term for term in forbidden_page_terms if term in page_text]
    missing_hero_terms = [term for term in required_hero_terms if term not in hero_text]
    missing_drip_terms = [term for term in required_drip_terms if term not in drip_text]

    validation_status = "pass"
    if (
        missing_files
        or missing_page_terms
        or forbidden_terms_found
        or missing_hero_terms
        or missing_drip_terms
    ):
        validation_status = "fail"

    report = {
        "run_name": "step17d2_cleanup_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "missing_files": missing_files,
        "missing_page_terms": missing_page_terms,
        "forbidden_duplicate_terms_found": forbidden_terms_found,
        "missing_hero_terms": missing_hero_terms,
        "missing_drip_terms": missing_drip_terms,
        "page_path": str(page_path).replace("\\", "/"),
        "hero_path": str(hero_path).replace("\\", "/"),
        "drip_path": str(drip_path).replace("\\", "/"),
        "next_step": (
            "Step 17E: Three.js scene foundation for animated supply-chain objects."
            if validation_status == "pass"
            else "Fix cleanup patch before Three.js."
        ),
    }

    report_path = report_dir / "step17d2_cleanup_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17D-2 CLEANUP VALIDATION COMPLETE")
    print("--------------------------------------")
    print(f"Validation status: {validation_status}")
    print(f"Missing files:     {len(missing_files)}")
    print(f"Missing page terms:{len(missing_page_terms)}")
    print(f"Forbidden terms:   {len(forbidden_terms_found)}")
    print(f"Missing hero terms:{len(missing_hero_terms)}")
    print(f"Missing drip terms:{len(missing_drip_terms)}")
    print("")
    print(f"Report JSON:       {report_path}")
    print("")


if __name__ == "__main__":
    main()