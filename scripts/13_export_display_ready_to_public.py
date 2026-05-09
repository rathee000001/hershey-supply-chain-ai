from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


DISPLAY_FILES = [
    "display_ready_manifest.json",
    "home_summary_cards.json",
    "interactive_graph_payload.json",
    "node_detail_panels.json",
    "cost_breakdown_display.json",
    "supplier_display_cards.json",
    "ingredient_display_cards.json",
    "evidence_panel_lookup.json",
]

PATH_KEYS = {
    "logo_path",
    "image_path",
    "contact_sheet_path",
    "copied_review_asset_path",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_file_name(value: str) -> str:
    clean = []
    for ch in value:
        if ch.isalnum() or ch in [".", "_", "-"]:
            clean.append(ch)
        else:
            clean.append("_")
    out = "".join(clean).strip("_")
    while "__" in out:
        out = out.replace("__", "_")
    return out or "asset"


def resolve_local_asset(root: Path, value: str) -> Path | None:
    if not value:
        return None

    raw = value.replace("\\", "/").strip()

    candidates = []

    path_obj = Path(raw)
    if path_obj.is_absolute():
        candidates.append(path_obj)

    candidates.extend(
        [
            root / raw,
            root / "data" / "raw_sources" / raw,
            root / "artifacts" / raw,
            root / "public" / raw.lstrip("/"),
        ]
    )

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def copy_asset(root: Path, public_asset_dir: Path, value: str, asset_map: dict[str, str]) -> str:
    if not value:
        return ""

    if value.startswith("/data/"):
        return value

    local = resolve_local_asset(root, value)

    if not local:
        asset_map[value] = ""
        return value

    safe_name = safe_file_name(local.name)
    dest = public_asset_dir / safe_name

    counter = 2
    while dest.exists() and dest.read_bytes() != local.read_bytes():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        dest = public_asset_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(local, dest)

    public_url = f"/data/hershey/assets/{dest.name}"
    asset_map[value] = public_url
    return public_url


def transform_for_public(obj: Any, root: Path, public_asset_dir: Path, asset_map: dict[str, str]) -> Any:
    if isinstance(obj, list):
        return [transform_for_public(x, root, public_asset_dir, asset_map) for x in obj]

    if isinstance(obj, dict):
        transformed = {}

        for key, value in obj.items():
            if key in PATH_KEYS and isinstance(value, str):
                transformed[key] = copy_asset(root, public_asset_dir, value, asset_map)
            elif key in ["input_artifacts", "display_artifacts"] and isinstance(value, dict):
                # Replace local absolute paths with frontend public URLs where possible.
                transformed[key] = {
                    k: (
                        f"/data/hershey/display_ready/{Path(str(v)).name}"
                        if str(v).endswith(".json")
                        else str(v)
                    )
                    for k, v in value.items()
                }
            elif isinstance(value, (dict, list)):
                transformed[key] = transform_for_public(value, root, public_asset_dir, asset_map)
            else:
                transformed[key] = value

        return transformed

    return obj


def write_export_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "artifact_name",
        "source_path",
        "public_path",
        "public_url",
        "record_count",
        "status",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count_records(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        if "nodes" in payload and "edges" in payload:
            return len(payload.get("nodes", [])) + len(payload.get("edges", []))
        return len(payload)
    return 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    source_dir = root / "artifacts" / "09_display_ready"
    public_root = root / "public" / "data" / "hershey"
    public_display_dir = public_root / "display_ready"
    public_asset_dir = public_root / "assets"
    report_dir = root / "artifacts" / "10_run_reports"

    public_display_dir.mkdir(parents=True, exist_ok=True)
    public_asset_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    asset_map: dict[str, str] = {}
    export_rows: list[dict[str, Any]] = []

    missing_files = []

    for file_name in DISPLAY_FILES:
        src = source_dir / file_name

        if not src.exists():
            missing_files.append(file_name)
            continue

        payload = read_json(src)
        public_payload = transform_for_public(
            obj=payload,
            root=root,
            public_asset_dir=public_asset_dir,
            asset_map=asset_map,
        )

        dest = public_display_dir / file_name
        write_json(dest, public_payload)

        export_rows.append(
            {
                "artifact_name": file_name,
                "source_path": str(src).replace("\\", "/"),
                "public_path": str(dest).replace("\\", "/"),
                "public_url": f"/data/hershey/display_ready/{file_name}",
                "record_count": count_records(public_payload),
                "status": "exported",
            }
        )

    frontend_manifest = {
        "public_export_version": "v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence",
        "base_public_path": "/data/hershey",
        "display_ready_base": "/data/hershey/display_ready",
        "asset_base": "/data/hershey/assets",
        "frontend_rule": "Frontend should read these artifacts only. Hardcode layout labels only; do not hardcode supplier/cost claims.",
        "artifacts": {
            Path(row["artifact_name"]).stem: row["public_url"]
            for row in export_rows
        },
        "primary_artifacts": {
            "home_cards": "/data/hershey/display_ready/home_summary_cards.json",
            "graph": "/data/hershey/display_ready/interactive_graph_payload.json",
            "node_panels": "/data/hershey/display_ready/node_detail_panels.json",
            "cost_breakdown": "/data/hershey/display_ready/cost_breakdown_display.json",
            "suppliers": "/data/hershey/display_ready/supplier_display_cards.json",
            "ingredients": "/data/hershey/display_ready/ingredient_display_cards.json",
            "evidence": "/data/hershey/display_ready/evidence_panel_lookup.json",
        },
        "asset_map": asset_map,
        "safe_display_rules": [
            "Supplier relationships are company-level unless explicitly marked SKU-level.",
            "Minor ingredient suppliers are unknown unless direct evidence proves otherwise.",
            "Manufacturing process nodes are general modeled process nodes, not proprietary Hershey line claims.",
            "Cost values are public-evidence benchmark estimates, not Hershey internal SKU costs.",
            "Residual channel/commercial pool is not profit."
        ],
    }

    public_manifest_path = public_root / "frontend_public_manifest.json"
    write_json(public_manifest_path, frontend_manifest)

    export_summary_csv = public_root / "public_export_summary.csv"
    write_export_summary_csv(export_summary_csv, export_rows)

    report = {
        "run_name": "step16a_export_display_ready_to_public",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "source_display_ready_folder": str(source_dir).replace("\\", "/"),
        "public_display_ready_folder": str(public_display_dir).replace("\\", "/"),
        "public_asset_folder": str(public_asset_dir).replace("\\", "/"),
        "display_files_expected": len(DISPLAY_FILES),
        "display_files_exported": len(export_rows),
        "missing_files": missing_files,
        "assets_mapped": len([v for v in asset_map.values() if v]),
        "assets_unresolved": len([v for v in asset_map.values() if not v]),
        "frontend_public_manifest": str(public_manifest_path).replace("\\", "/"),
        "public_export_summary_csv": str(export_summary_csv).replace("\\", "/"),
        "frontend_public_urls": frontend_manifest["primary_artifacts"],
        "next_step": "Step 16B: validate public JSON payloads, then Step 17 can begin frontend page build.",
    }

    report_path = report_dir / "step16a_public_data_export_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16A PUBLIC DATA EXPORT COMPLETE")
    print("------------------------------------")
    print(f"Display files exported: {len(export_rows)} / {len(DISPLAY_FILES)}")
    print(f"Missing files: {len(missing_files)}")
    print(f"Assets mapped: {report['assets_mapped']}")
    print(f"Assets unresolved: {report['assets_unresolved']}")
    print("")
    print(f"Public manifest: {public_manifest_path}")
    print(f"Export summary:  {export_summary_csv}")
    print(f"Report JSON:     {report_path}")
    print("")


if __name__ == "__main__":
    main()