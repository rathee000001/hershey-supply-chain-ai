from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


REQUIRED_ASSET_KEYS = [
    "hershey_wrapper_front",
    "hershey_wrapper_back",
    "hershey_unwrapped_bar",
    "hershey_logo",
    "asr_logo",
    "barry_callebaut_logo",
    "land_olakes_logo",
    "mclane_logo",
    "dairy_origin",
    "sugarcane_origin",
    "cocoa_origin",
    "factory_visual",
    "truck_visual",
    "retail_shelf_visual",
    "consumer_visual",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    manifest_path = root / "public" / "data" / "hershey" / "visual_assets" / "hershey_visual_assets_manifest.json"
    component_path = root / "src" / "components" / "hershey" / "CinematicAssetScene.tsx"
    page_path = root / "src" / "app" / "supply-chain" / "page.tsx"
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    missing_files = []
    for path in [manifest_path, component_path, page_path]:
        if not path.exists():
            missing_files.append(str(path))

    manifest = read_json(manifest_path) if manifest_path.exists() else {"assets": {}}
    assets = manifest.get("assets", {})

    missing_asset_keys = [key for key in REQUIRED_ASSET_KEYS if key not in assets]

    unresolved_asset_urls = []
    for key, item in assets.items():
        url = item.get("url", "")
        if not url:
            unresolved_asset_urls.append({"key": key, "url": url})
            continue

        local_path = root / "public" / url.lstrip("/")
        if not local_path.exists():
            unresolved_asset_urls.append({"key": key, "url": url})

    component_text = component_path.read_text(encoding="utf-8") if component_path.exists() else ""
    page_text = page_path.read_text(encoding="utf-8") if page_path.exists() else ""

    required_component_terms = [
        "Actual asset-driven scene layer",
        "CinematicAssetScene",
        "hershey_wrapper_front",
        "land_olakes_logo",
        "asr_logo",
        "barry_callebaut_logo",
        "mclane_logo",
        "Three.js ready",
    ]

    missing_component_terms = [
        term for term in required_component_terms if term not in component_text
    ]

    page_import_ok = "CinematicAssetScene" in page_text
    page_component_ok = "<CinematicAssetScene" in page_text

    actual_project_assets = sum(
        1 for item in assets.values() if item.get("source_kind") == "actual_project_asset"
    )
    generated_placeholders = sum(
        1 for item in assets.values() if item.get("source_kind") == "generated_placeholder"
    )

    validation_status = "pass"
    if (
        missing_files
        or missing_asset_keys
        or unresolved_asset_urls
        or missing_component_terms
        or not page_import_ok
        or not page_component_ok
    ):
        validation_status = "fail"

    report = {
        "run_name": "step17d_visual_asset_layer_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "missing_files": missing_files,
        "required_asset_keys": REQUIRED_ASSET_KEYS,
        "missing_asset_keys": missing_asset_keys,
        "unresolved_asset_urls": unresolved_asset_urls,
        "assets_registered": len(assets),
        "actual_project_assets": actual_project_assets,
        "generated_placeholders": generated_placeholders,
        "missing_component_terms": missing_component_terms,
        "page_import_ok": page_import_ok,
        "page_component_ok": page_component_ok,
        "visual_asset_manifest_url": "/data/hershey/visual_assets/hershey_visual_assets_manifest.json",
        "next_step": (
            "Step 17E: install/use Three.js and React Three Fiber to convert visual assets into 3D scene objects."
            if validation_status == "pass"
            else "Fix asset registry or frontend integration before Step 17E."
        ),
    }

    report_path = report_dir / "step17d_visual_asset_layer_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17D VISUAL ASSET LAYER VALIDATION COMPLETE")
    print("-----------------------------------------------")
    print(f"Validation status:       {validation_status}")
    print(f"Assets registered:       {len(assets)}")
    print(f"Actual project assets:   {actual_project_assets}")
    print(f"Generated placeholders:  {generated_placeholders}")
    print(f"Missing files:           {len(missing_files)}")
    print(f"Missing asset keys:      {len(missing_asset_keys)}")
    print(f"Unresolved asset URLs:   {len(unresolved_asset_urls)}")
    print(f"Page import ok:          {page_import_ok}")
    print(f"Page component ok:       {page_component_ok}")
    print("")
    print(f"Report JSON:             {report_path}")
    print("")


if __name__ == "__main__":
    main()