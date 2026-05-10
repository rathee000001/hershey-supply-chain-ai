from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


ASSET_SPECS = {
    "hershey_wrapper_front": {
        "label": "Hershey wrapper front",
        "keywords": ["wrapper_front", "hershey front", "front.webp", "front.png", "hershey_front", "wrapper front"],
        "preferred": ["hershey", "front"],
        "asset_type": "product_visual",
    },
    "hershey_wrapper_back": {
        "label": "Hershey wrapper back",
        "keywords": ["wrapper_back", "hershey back", "back.webp", "back.png", "hershey_back", "wrapper back"],
        "preferred": ["hershey", "back"],
        "asset_type": "product_visual",
    },
    "hershey_unwrapped_bar": {
        "label": "Unwrapped Hershey chocolate bar",
        "keywords": ["unwrapped", "chocolate bar", "hershey unwrapped"],
        "preferred": ["hershey", "unwrapped"],
        "asset_type": "product_visual",
    },
    "hershey_logo": {
        "label": "Hershey logo",
        "keywords": ["hersheyco", "hershey logo", "hershey_company", "hersheyco.svg", "hersheyco.png"],
        "preferred": ["hershey"],
        "asset_type": "company_logo",
    },
    "asr_logo": {
        "label": "ASR logo",
        "keywords": ["asr_group_logo", "asr logo", "asr_group", "asr"],
        "preferred": ["asr", "logo"],
        "asset_type": "supplier_logo",
    },
    "barry_callebaut_logo": {
        "label": "Barry Callebaut logo",
        "keywords": ["barry_logo", "barry callebaut", "barry_callebaut", "barry"],
        "preferred": ["barry", "logo"],
        "asset_type": "supplier_logo",
    },
    "land_olakes_logo": {
        "label": "Land O'Lakes logo",
        "keywords": ["land_o_lakes_logo", "land o lakes logo", "land_o_lakes", "landolakes"],
        "preferred": ["land", "logo"],
        "asset_type": "supplier_logo",
    },
    "mclane_logo": {
        "label": "McLane logo",
        "keywords": ["mclane_logo", "mclane logo", "mclane"],
        "preferred": ["mclane", "logo"],
        "asset_type": "supplier_logo",
    },
    "dairy_origin": {
        "label": "Dairy farm / cow origin",
        "keywords": ["cow", "cattle", "dairy_farm", "dairy farm", "milk farm"],
        "preferred": ["cow"],
        "asset_type": "origin_visual",
    },
    "sugarcane_origin": {
        "label": "Sugarcane / beet origin",
        "keywords": ["sugarcane", "sugar_cane", "beet", "sugar origin"],
        "preferred": ["sugar"],
        "asset_type": "origin_visual",
    },
    "cocoa_origin": {
        "label": "Cocoa origin",
        "keywords": ["cocoa pod", "cocoa_origin", "cocoa farm", "cocoa"],
        "preferred": ["cocoa"],
        "asset_type": "origin_visual",
    },
    "factory_visual": {
        "label": "Factory / manufacturing visual",
        "keywords": ["factory", "manufacturing", "plant"],
        "preferred": ["factory"],
        "asset_type": "process_visual",
    },
    "truck_visual": {
        "label": "Truck / logistics visual",
        "keywords": ["truck", "freight", "transport", "carrier"],
        "preferred": ["truck"],
        "asset_type": "logistics_visual",
    },
    "retail_shelf_visual": {
        "label": "Retail shelf visual",
        "keywords": ["retail", "shelf", "store", "walmart", "target", "cvs", "walgreens"],
        "preferred": ["retail"],
        "asset_type": "retail_visual",
    },
}


PLACEHOLDER_SVG = {
    "dairy_origin": ("DAIRY FARM", "🐄", "#123d2b", "#d9ffe7"),
    "sugarcane_origin": ("SUGARCANE", "🌾", "#3c2f0d", "#fff1a8"),
    "cocoa_origin": ("COCOA ORIGIN", "🌱", "#3b1f13", "#ffd2a6"),
    "factory_visual": ("HERSHEY FACTORY", "🏭", "#3b120d", "#ffe1b5"),
    "truck_visual": ("TRUCK / DC", "🚚", "#11253b", "#c9e8ff"),
    "retail_shelf_visual": ("RETAIL SHELF", "🏬", "#34112d", "#ffd5f2"),
    "consumer_visual": ("CONSUMER", "🛍️", "#30143b", "#ead2ff"),
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sanitize_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def collect_images(root: Path) -> list[Path]:
    search_roots = [
        root / "data" / "raw_sources",
        root / "public",
        root / "artifacts",
    ]

    images: list[Path] = []

    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in search_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                images.append(path)

    return sorted(set(images))


def score_image(path: Path, spec: dict[str, Any]) -> int:
    full = str(path).replace("\\", "/").lower()
    name = path.name.lower()

    score = 0

    for keyword in spec.get("keywords", []):
        if keyword.lower() in full:
            score += 15

    for keyword in spec.get("preferred", []):
        if keyword.lower() in full:
            score += 8

    if "logo" in name:
        score += 4
    if "raw_sources" in full:
        score += 3
    if "wrapper" in full:
        score += 6
    if "product_visual" in full:
        score += 4

    # Avoid accidental unrelated thumbnails when a better name exists.
    if "screenshot" in name:
        score -= 2
    if "contact_sheet" in full:
        score -= 8

    return score


def select_best_assets(images: list[Path]) -> dict[str, Path | None]:
    selected: dict[str, Path | None] = {}

    for key, spec in ASSET_SPECS.items():
        scored = [(score_image(path, spec), path) for path in images]
        scored = sorted(scored, key=lambda item: item[0], reverse=True)

        if scored and scored[0][0] > 0:
            selected[key] = scored[0][1]
        else:
            selected[key] = None

    return selected


def create_placeholder_svg(path: Path, title: str, icon: str, bg: str, fg: str) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
  <defs>
    <radialGradient id="g" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="{fg}" stop-opacity="0.22"/>
      <stop offset="45%" stop-color="{bg}" stop-opacity="1"/>
      <stop offset="100%" stop-color="#080202"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="720" rx="64" fill="url(#g)"/>
  <circle cx="600" cy="300" r="150" fill="{fg}" opacity="0.12"/>
  <text x="600" y="330" text-anchor="middle" font-size="150">{icon}</text>
  <text x="600" y="515" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="52" font-weight="900" letter-spacing="10" fill="{fg}">{title}</text>
  <text x="600" y="585" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="24" letter-spacing="6" fill="{fg}" opacity="0.68">PUBLIC-EVIDENCE VISUAL PLACEHOLDER</text>
</svg>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def copy_or_create_asset(
    root: Path,
    key: str,
    source_path: Path | None,
    public_asset_dir: Path,
) -> dict[str, Any]:
    spec = ASSET_SPECS.get(key, {"label": key, "asset_type": "visual"})

    if source_path and source_path.exists():
        ext = source_path.suffix.lower()
        dest = public_asset_dir / "source_assets" / f"{key}{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest)

        return {
            "asset_key": key,
            "label": spec.get("label", key),
            "url": f"/data/hershey/visual_assets/source_assets/{dest.name}",
            "asset_type": spec.get("asset_type", "visual"),
            "source_kind": "actual_project_asset",
            "source_path": str(source_path).replace("\\", "/"),
            "display_allowed": True,
            "usage_note": "Actual collected project asset. Use for visual storytelling, not as standalone factual proof.",
        }

    placeholder = PLACEHOLDER_SVG.get(
        key,
        (spec.get("label", key).upper(), "●", "#2b0909", "#f5d08a"),
    )
    dest = public_asset_dir / "generated_placeholders" / f"{key}.svg"
    create_placeholder_svg(dest, *placeholder)

    return {
        "asset_key": key,
        "label": spec.get("label", key),
        "url": f"/data/hershey/visual_assets/generated_placeholders/{dest.name}",
        "asset_type": spec.get("asset_type", "visual"),
        "source_kind": "generated_placeholder",
        "source_path": "",
        "display_allowed": True,
        "usage_note": "Generated project placeholder. Replace with approved/owned visual asset when available.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    public_asset_dir = root / "public" / "data" / "hershey" / "visual_assets"
    artifact_dir = root / "artifacts" / "19_visual_asset_registry"
    report_dir = root / "artifacts" / "10_run_reports"

    public_asset_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    images = collect_images(root)
    selected = select_best_assets(images)

    assets = {}

    for key in ASSET_SPECS:
        assets[key] = copy_or_create_asset(root, key, selected.get(key), public_asset_dir)

    # Consumer visual is always created as a general placeholder for now.
    consumer_dest = public_asset_dir / "generated_placeholders" / "consumer_visual.svg"
    create_placeholder_svg(consumer_dest, *PLACEHOLDER_SVG["consumer_visual"])
    assets["consumer_visual"] = {
        "asset_key": "consumer_visual",
        "label": "Consumer purchase visual",
        "url": "/data/hershey/visual_assets/generated_placeholders/consumer_visual.svg",
        "asset_type": "consumer_visual",
        "source_kind": "generated_placeholder",
        "source_path": "",
        "display_allowed": True,
        "usage_note": "Generated project placeholder for consumer purchase endpoint.",
    }

    manifest = {
        "visual_assets_version": "step17d_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence",
        "base_public_path": "/data/hershey/visual_assets",
        "frontend_rule": "Use visual assets for cinematic storytelling only. Evidence claims still come from audited JSON artifacts.",
        "assets": assets,
        "asset_keys": sorted(assets.keys()),
        "next_step": "Step 17E can use these URLs as texture/image planes for Three.js.",
    }

    public_manifest = public_asset_dir / "hershey_visual_assets_manifest.json"
    artifact_manifest = artifact_dir / "hershey_visual_assets_manifest.json"

    write_json(public_manifest, manifest)
    write_json(artifact_manifest, manifest)

    actual_count = sum(1 for a in assets.values() if a["source_kind"] == "actual_project_asset")
    placeholder_count = sum(1 for a in assets.values() if a["source_kind"] == "generated_placeholder")

    report = {
        "run_name": "step17d_visual_asset_registry",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "images_scanned": len(images),
        "assets_registered": len(assets),
        "actual_project_assets": actual_count,
        "generated_placeholders": placeholder_count,
        "public_manifest": str(public_manifest).replace("\\", "/"),
        "public_manifest_url": "/data/hershey/visual_assets/hershey_visual_assets_manifest.json",
        "artifact_manifest": str(artifact_manifest).replace("\\", "/"),
        "selected_assets": {
            key: str(path).replace("\\", "/") if path else ""
            for key, path in selected.items()
        },
        "next_step": "Patch frontend to use visual asset manifest and display actual images/logos.",
    }

    report_path = report_dir / "step17d_visual_asset_registry_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17D VISUAL ASSET REGISTRY COMPLETE")
    print("---------------------------------------")
    print(f"Images scanned:          {len(images)}")
    print(f"Assets registered:       {len(assets)}")
    print(f"Actual project assets:   {actual_count}")
    print(f"Generated placeholders:  {placeholder_count}")
    print("")
    print(f"Public manifest: {public_manifest}")
    print(f"Report JSON:     {report_path}")
    print("")


if __name__ == "__main__":
    main()