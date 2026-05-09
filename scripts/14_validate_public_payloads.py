from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_PUBLIC_FILES = {
    "frontend_public_manifest": "public/data/hershey/frontend_public_manifest.json",
    "display_ready_manifest": "public/data/hershey/display_ready/display_ready_manifest.json",
    "home_summary_cards": "public/data/hershey/display_ready/home_summary_cards.json",
    "interactive_graph_payload": "public/data/hershey/display_ready/interactive_graph_payload.json",
    "node_detail_panels": "public/data/hershey/display_ready/node_detail_panels.json",
    "cost_breakdown_display": "public/data/hershey/display_ready/cost_breakdown_display.json",
    "supplier_display_cards": "public/data/hershey/display_ready/supplier_display_cards.json",
    "ingredient_display_cards": "public/data/hershey/display_ready/ingredient_display_cards.json",
    "evidence_panel_lookup": "public/data/hershey/display_ready/evidence_panel_lookup.json",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "check_name",
        "status",
        "severity",
        "message",
        "path",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_check(
    rows: list[dict[str, Any]],
    check_name: str,
    status: str,
    severity: str,
    message: str,
    path: str = "",
) -> None:
    rows.append(
        {
            "check_name": check_name,
            "status": status,
            "severity": severity,
            "message": message,
            "path": path,
        }
    )


def contains_local_windows_path(payload: Any) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return "D:/" in text or "D:\\" in text or "C:/" in text or "C:\\" in text


def validate_required_files(root: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}

    for name, rel_path in REQUIRED_PUBLIC_FILES.items():
        path = root / rel_path

        if not path.exists():
            add_check(rows, f"required_file_{name}", "fail", "critical", "Required public file is missing.", str(path))
            continue

        try:
            payload = read_json(path)
            loaded[name] = payload
            add_check(rows, f"required_file_{name}", "pass", "info", "Required public file exists and JSON is valid.", str(path))

            if contains_local_windows_path(payload):
                add_check(rows, f"no_local_paths_{name}", "fail", "high", "Public JSON contains local Windows path.", str(path))
            else:
                add_check(rows, f"no_local_paths_{name}", "pass", "info", "No local Windows paths found.", str(path))

        except Exception as exc:
            add_check(rows, f"json_parse_{name}", "fail", "critical", f"JSON parse failed: {exc}", str(path))

    return loaded


def validate_manifest(root: Path, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    primary = manifest.get("primary_artifacts", {})
    artifacts = manifest.get("artifacts", {})
    asset_map = manifest.get("asset_map", {})

    expected_primary = ["home_cards", "graph", "node_panels", "cost_breakdown", "suppliers", "ingredients", "evidence"]

    for key in expected_primary:
        url = primary.get(key)
        if not url:
            add_check(rows, f"manifest_primary_{key}", "fail", "critical", f"Missing primary artifact URL for {key}.")
            continue

        local_path = root / "public" / url.lstrip("/")
        if local_path.exists():
            add_check(rows, f"manifest_primary_{key}", "pass", "info", f"Primary artifact exists: {url}", str(local_path))
        else:
            add_check(rows, f"manifest_primary_{key}", "fail", "critical", f"Primary artifact URL does not resolve locally: {url}", str(local_path))

    if len(artifacts) >= 8:
        add_check(rows, "manifest_artifact_count", "pass", "info", f"Manifest lists {len(artifacts)} artifacts.")
    else:
        add_check(rows, "manifest_artifact_count", "fail", "high", f"Manifest lists only {len(artifacts)} artifacts.")

    for original, public_url in asset_map.items():
        if not public_url:
            add_check(rows, "asset_map_unresolved", "fail", "medium", f"Asset unresolved: {original}")
            continue

        asset_path = root / "public" / public_url.lstrip("/")
        if asset_path.exists():
            add_check(rows, "asset_map_file_exists", "pass", "info", f"Asset mapped and exists: {public_url}", str(asset_path))
        else:
            add_check(rows, "asset_map_file_exists", "fail", "medium", f"Asset mapped but file not found: {public_url}", str(asset_path))


def validate_graph(graph: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if len(nodes) >= 30:
        add_check(rows, "graph_node_count", "pass", "info", f"Graph has {len(nodes)} nodes.")
    else:
        add_check(rows, "graph_node_count", "fail", "high", f"Graph has only {len(nodes)} nodes.")

    if len(edges) >= 30:
        add_check(rows, "graph_edge_count", "pass", "info", f"Graph has {len(edges)} edges.")
    else:
        add_check(rows, "graph_edge_count", "fail", "high", f"Graph has only {len(edges)} edges.")

    node_ids = set()

    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            add_check(rows, "graph_node_id", "fail", "critical", "Node missing id.")
            continue
        node_ids.add(node_id)

        if not node.get("label"):
            add_check(rows, "graph_node_label", "fail", "medium", f"Node missing label: {node_id}")

        if not node.get("relationshipStatus"):
            add_check(rows, "graph_node_relationship_status", "fail", "medium", f"Node missing relationshipStatus: {node_id}")

    bad_edges = []

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        edge_id = edge.get("id")

        if source not in node_ids or target not in node_ids:
            bad_edges.append(edge_id)

    if bad_edges:
        add_check(rows, "graph_edge_endpoints", "fail", "critical", f"Edges have missing endpoints: {bad_edges[:10]}")
    else:
        add_check(rows, "graph_edge_endpoints", "pass", "info", "All edge endpoints resolve to valid node ids.")


def validate_panels(graph: dict[str, Any], panels: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    node_ids = [node.get("id") for node in graph.get("nodes", []) if node.get("id")]

    missing_panels = []

    for node_id in node_ids:
        if node_id not in panels:
            missing_panels.append(node_id)

    if missing_panels:
        add_check(rows, "node_panels_complete", "fail", "high", f"Missing node panels: {missing_panels[:10]}")
    else:
        add_check(rows, "node_panels_complete", "pass", "info", "Every graph node has a detail panel.")


def validate_cards(suppliers: list[dict[str, Any]], ingredients: list[dict[str, Any]], home_cards: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    if len(suppliers) == 4:
        add_check(rows, "supplier_card_count", "pass", "info", "Supplier cards count is 4.")
    else:
        add_check(rows, "supplier_card_count", "fail", "medium", f"Supplier cards count is {len(suppliers)}.")

    if len(ingredients) == 10:
        add_check(rows, "ingredient_card_count", "pass", "info", "Ingredient cards count is 10.")
    else:
        add_check(rows, "ingredient_card_count", "fail", "medium", f"Ingredient cards count is {len(ingredients)}.")

    if len(home_cards) == 5:
        add_check(rows, "home_card_count", "pass", "info", "Home summary cards count is 5.")
    else:
        add_check(rows, "home_card_count", "fail", "medium", f"Home summary cards count is {len(home_cards)}.")

    supplier_levels = {card.get("relationship_level") for card in suppliers}
    if "company_level_confirmed" in supplier_levels:
        add_check(rows, "supplier_relationship_levels", "pass", "info", f"Supplier levels present: {sorted(supplier_levels)}")
    else:
        add_check(rows, "supplier_relationship_levels", "fail", "high", f"No company_level_confirmed supplier cards found: {sorted(supplier_levels)}")


def validate_cost(cost: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    physical = cost.get("physical_cost", {})
    retail = cost.get("retail_price", {})
    residual = cost.get("residual_channel_pool", {})
    records = cost.get("records", [])

    required_numeric = [
        ("physical_base", physical.get("base_cents_per_bar")),
        ("retail_base", retail.get("base_cents_per_bar")),
        ("residual_base", residual.get("base_cents_per_bar")),
    ]

    for name, value in required_numeric:
        try:
            val = float(value)
            if val > 0:
                add_check(rows, f"cost_{name}", "pass", "info", f"{name} is positive: {val}")
            else:
                add_check(rows, f"cost_{name}", "fail", "high", f"{name} is not positive: {val}")
        except Exception:
            add_check(rows, f"cost_{name}", "fail", "high", f"{name} is missing or not numeric.")

    if len(records) >= 10:
        add_check(rows, "cost_record_count", "pass", "info", f"Cost display has {len(records)} records.")
    else:
        add_check(rows, "cost_record_count", "fail", "medium", f"Cost display has only {len(records)} records.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    loaded = validate_required_files(root, rows)

    manifest = loaded.get("frontend_public_manifest", {})
    graph = loaded.get("interactive_graph_payload", {})
    panels = loaded.get("node_detail_panels", {})
    cost = loaded.get("cost_breakdown_display", {})
    suppliers = loaded.get("supplier_display_cards", [])
    ingredients = loaded.get("ingredient_display_cards", [])
    home_cards = loaded.get("home_summary_cards", [])

    if manifest:
        validate_manifest(root, manifest, rows)
    if graph:
        validate_graph(graph, rows)
    if graph and panels:
        validate_panels(graph, panels, rows)
    if suppliers and ingredients and home_cards:
        validate_cards(suppliers, ingredients, home_cards, rows)
    if cost:
        validate_cost(cost, rows)

    fail_rows = [row for row in rows if row["status"] == "fail"]
    critical_failures = [row for row in fail_rows if row["severity"] == "critical"]
    high_failures = [row for row in fail_rows if row["severity"] == "high"]

    validation_status = "pass"
    if critical_failures:
        validation_status = "fail"
    elif high_failures:
        validation_status = "pass_with_warnings"
    elif fail_rows:
        validation_status = "pass_with_minor_warnings"

    checks_csv = report_dir / "step16b_public_json_validation_checks.csv"
    write_csv(checks_csv, rows)

    report = {
        "run_name": "step16b_public_json_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "total_checks": len(rows),
        "failed_checks": len(fail_rows),
        "critical_failures": len(critical_failures),
        "high_failures": len(high_failures),
        "loaded_public_files": list(loaded.keys()),
        "frontend_graph_nodes": len(graph.get("nodes", [])) if isinstance(graph, dict) else 0,
        "frontend_graph_edges": len(graph.get("edges", [])) if isinstance(graph, dict) else 0,
        "node_detail_panels": len(panels) if isinstance(panels, dict) else 0,
        "supplier_cards": len(suppliers) if isinstance(suppliers, list) else 0,
        "ingredient_cards": len(ingredients) if isinstance(ingredients, list) else 0,
        "home_cards": len(home_cards) if isinstance(home_cards, list) else 0,
        "checks_csv": str(checks_csv).replace("\\", "/"),
        "next_step": (
            "Step 17: begin frontend page build from public JSON artifacts."
            if validation_status in ["pass", "pass_with_minor_warnings"]
            else "Fix validation failures before frontend build."
        ),
    }

    report_path = report_dir / "step16b_public_json_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16B PUBLIC JSON VALIDATION COMPLETE")
    print("----------------------------------------")
    print(f"Validation status: {validation_status}")
    print(f"Total checks: {len(rows)}")
    print(f"Failed checks: {len(fail_rows)}")
    print(f"Critical failures: {len(critical_failures)}")
    print(f"High failures: {len(high_failures)}")
    print("")
    print(f"Checks CSV:  {checks_csv}")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()