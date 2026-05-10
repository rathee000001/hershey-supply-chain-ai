from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ENRICHED_PUBLIC_FILES = {
    "evidence": "enriched_evidence_panel_lookup_v2.json",
    "packet_summary": "enriched_packet_summary_v2.json",
    "suppliers": "enriched_supplier_cards_v2.json",
    "ingredients": "enriched_ingredient_cards_v2.json",
    "cost_breakdown": "enriched_cost_breakdown_display_v2.json",
    "graph": "enriched_interactive_graph_payload_v2.json",
    "home_cards": "enriched_home_summary_cards_v2.json",
    "source_manifest": "enriched_display_manifest_v2.json",
}

FRONTEND_MANIFEST_NAME = "enriched_frontend_manifest_v2.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = ["check_name", "status", "severity", "message", "path"]
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_check(rows: list[dict[str, Any]], check_name: str, status: str, severity: str, message: str, path: str = "") -> None:
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
    return bool(re.search(r"\b[A-Z]:[\\/]", text))


def count_records(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        if "nodes" in payload and "edges" in payload:
            return len(payload.get("nodes", [])) + len(payload.get("edges", []))
        return len(payload)
    return 1


def public_url_for(file_name: str) -> str:
    return f"/data/hershey/enriched_display/{file_name}"


def validate_required_files(public_dir: Path, checks: list[dict[str, Any]]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}

    for key, file_name in ENRICHED_PUBLIC_FILES.items():
        path = public_dir / file_name

        if not path.exists():
            add_check(checks, f"required_file_{key}", "fail", "critical", "Required enriched public JSON file is missing.", str(path))
            continue

        try:
            payload = read_json(path)
            loaded[key] = payload
            add_check(checks, f"required_file_{key}", "pass", "info", "Required enriched public JSON exists and parses.", str(path))
        except Exception as exc:
            add_check(checks, f"parse_file_{key}", "fail", "critical", f"JSON parse failed: {exc}", str(path))

    return loaded


def build_frontend_manifest(public_dir: Path, loaded: dict[str, Any]) -> dict[str, Any]:
    source_manifest = loaded.get("source_manifest", {})

    return {
        "manifest_version": "v2_enriched_frontend_manifest",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project": "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence",
        "unit": "one HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g",
        "base_public_path": "/data/hershey/enriched_display",
        "frontend_rule": "Frontend must read enriched v2 public JSON artifacts only. Do not hardcode supplier, cost, relationship, or evidence claims.",
        "primary_artifacts": {
            key: public_url_for(file_name)
            for key, file_name in ENRICHED_PUBLIC_FILES.items()
            if key != "source_manifest"
        },
        "source_manifest_archival": public_url_for(ENRICHED_PUBLIC_FILES["source_manifest"]),
        "audit_summary": source_manifest.get("audit_summary", {}),
        "safe_display_rules": [
            "Only Step 16I approved display-safe evidence is used for enriched v2 display artifacts.",
            "Company-level supplier evidence cannot be displayed as exact SKU supplier proof.",
            "Benchmark cost evidence cannot be displayed as Hershey internal cost.",
            "Retail price evidence cannot be displayed as margin or profit.",
            "Distribution context cannot be displayed as exact route proof.",
            "OCR evidence requires safe wording and should not be over-read.",
        ],
        "final_goal": "Hershey 1.55 oz Cinematic Supply Chain Intelligence Platform",
    }


def validate_frontend_manifest(root: Path, manifest: dict[str, Any], checks: list[dict[str, Any]], manifest_path: Path) -> None:
    if contains_local_windows_path(manifest):
        add_check(checks, "frontend_manifest_no_local_paths", "fail", "critical", "Frontend manifest contains local Windows paths.", str(manifest_path))
    else:
        add_check(checks, "frontend_manifest_no_local_paths", "pass", "info", "Frontend manifest contains no local Windows paths.", str(manifest_path))

    primary = manifest.get("primary_artifacts", {})
    expected = {"evidence", "packet_summary", "suppliers", "ingredients", "cost_breakdown", "graph", "home_cards"}

    missing_keys = sorted(expected - set(primary.keys()))
    if missing_keys:
        add_check(checks, "frontend_manifest_primary_keys", "fail", "critical", f"Missing primary artifact keys: {missing_keys}", str(manifest_path))
    else:
        add_check(checks, "frontend_manifest_primary_keys", "pass", "info", "All primary frontend artifact keys are present.", str(manifest_path))

    for key, url in primary.items():
        local_path = root / "public" / str(url).lstrip("/")
        if local_path.exists():
            add_check(checks, f"frontend_url_resolves_{key}", "pass", "info", f"Frontend URL resolves: {url}", str(local_path))
        else:
            add_check(checks, f"frontend_url_resolves_{key}", "fail", "critical", f"Frontend URL does not resolve: {url}", str(local_path))


def validate_graph(graph: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    if len(nodes) == 35:
        add_check(checks, "graph_node_count_v2", "pass", "info", "Graph has expected 35 nodes.")
    else:
        add_check(checks, "graph_node_count_v2", "fail", "high", f"Graph node count is {len(nodes)}, expected 35.")

    if len(edges) == 36:
        add_check(checks, "graph_edge_count_v2", "pass", "info", "Graph has expected 36 edges.")
    else:
        add_check(checks, "graph_edge_count_v2", "fail", "high", f"Graph edge count is {len(edges)}, expected 36.")

    node_ids = {node.get("id") for node in nodes if node.get("id")}
    bad_edges = []

    for edge in edges:
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            bad_edges.append(edge.get("id"))

    if bad_edges:
        add_check(checks, "graph_edge_endpoint_integrity", "fail", "critical", f"Edges have missing endpoints: {bad_edges[:10]}")
    else:
        add_check(checks, "graph_edge_endpoint_integrity", "pass", "info", "All graph edge endpoints resolve to node IDs.")

    evidence_counts = [node.get("enrichedApprovedEvidenceCount", 0) for node in nodes]
    if any(isinstance(x, int) and x > 0 for x in evidence_counts):
        add_check(checks, "graph_enriched_evidence_counts", "pass", "info", "Graph nodes include enriched evidence counts.")
    else:
        add_check(checks, "graph_enriched_evidence_counts", "fail", "medium", "No enriched evidence counts found on graph nodes.")


def validate_cards(suppliers: list[dict[str, Any]], ingredients: list[dict[str, Any]], home_cards: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    if len(suppliers) == 4:
        add_check(checks, "supplier_cards_v2_count", "pass", "info", "Supplier cards v2 count is 4.")
    else:
        add_check(checks, "supplier_cards_v2_count", "fail", "high", f"Supplier cards v2 count is {len(suppliers)}, expected 4.")

    if len(ingredients) >= 10:
        add_check(checks, "ingredient_cards_v2_count", "pass", "info", f"Ingredient cards v2 count is {len(ingredients)}.")
    else:
        add_check(checks, "ingredient_cards_v2_count", "fail", "high", f"Ingredient cards v2 count is {len(ingredients)}, expected at least 10.")

    if len(home_cards) == 5:
        add_check(checks, "home_cards_v2_count", "pass", "info", "Home cards v2 count is 5.")
    else:
        add_check(checks, "home_cards_v2_count", "fail", "medium", f"Home cards v2 count is {len(home_cards)}, expected 5.")

    bad_supplier_claims = []
    for card in suppliers:
        if card.get("sku_level_confirmed") is True:
            bad_supplier_claims.append(card.get("safe_display_name", ""))

    if bad_supplier_claims:
        add_check(checks, "supplier_no_sku_level_overclaim", "fail", "critical", f"Supplier cards claim SKU-level confirmation: {bad_supplier_claims}")
    else:
        add_check(checks, "supplier_no_sku_level_overclaim", "pass", "info", "Supplier cards do not claim SKU-level supplier confirmation.")


def validate_evidence(evidence: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    count = len(evidence)

    if count >= 850:
        add_check(checks, "evidence_lookup_count_v2", "pass", "info", f"Evidence lookup has {count} items.")
    else:
        add_check(checks, "evidence_lookup_count_v2", "fail", "high", f"Evidence lookup has only {count} items.")

    bad_public = []
    bad_status = []
    local_paths = []

    for evidence_id, row in evidence.items():
        if row.get("strict_audit_status") not in {"approved_display_safe", "approved_context_only"}:
            bad_status.append(evidence_id)

        if contains_local_windows_path(row):
            local_paths.append(evidence_id)

        wording = str(row.get("audited_safe_website_wording", "")).lower()
        if any(unsafe in wording for unsafe in ["internal sku cost", "exact sku supplier proof", "profit", "margin"]):
            # These phrases can appear safely as negations, so only warn if no protective wording exists.
            if "not" not in wording and "must not" not in wording and "cannot" not in wording:
                bad_public.append(evidence_id)

    if bad_status:
        add_check(checks, "evidence_status_approved_only", "fail", "critical", f"Evidence lookup contains non-approved statuses: {bad_status[:10]}")
    else:
        add_check(checks, "evidence_status_approved_only", "pass", "info", "Evidence lookup contains approved display/context statuses only.")

    if local_paths:
        add_check(checks, "evidence_no_local_paths", "fail", "high", f"Evidence lookup contains local paths: {local_paths[:10]}")
    else:
        add_check(checks, "evidence_no_local_paths", "pass", "info", "Evidence lookup has no local Windows paths.")

    if bad_public:
        add_check(checks, "evidence_unsafe_wording_guard", "fail", "high", f"Potential unsafe wording found: {bad_public[:10]}")
    else:
        add_check(checks, "evidence_unsafe_wording_guard", "pass", "info", "Evidence wording guard passed.")


def validate_cost(cost: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    physical = cost.get("physical_cost", {})
    retail = cost.get("retail_price", {})
    residual = cost.get("residual_channel_pool", {})

    numeric_checks = {
        "physical_base_cents": physical.get("base_cents_per_bar"),
        "retail_base_cents": retail.get("base_cents_per_bar"),
        "residual_base_cents": residual.get("base_cents_per_bar"),
    }

    for name, value in numeric_checks.items():
        try:
            val = float(value)
            if val > 0:
                add_check(checks, f"cost_{name}", "pass", "info", f"{name} is positive: {val}")
            else:
                add_check(checks, f"cost_{name}", "fail", "high", f"{name} is not positive: {val}")
        except Exception:
            add_check(checks, f"cost_{name}", "fail", "high", f"{name} is missing or not numeric.")

    note = str(cost.get("enriched_audit_note", "")).lower()
    if "not hershey internal" in note or "nothing here is hershey internal" in note:
        add_check(checks, "cost_safe_disclaimer_v2", "pass", "info", "Cost display includes internal-cost disclaimer.")
    else:
        add_check(checks, "cost_safe_disclaimer_v2", "fail", "high", "Cost display missing clear internal-cost disclaimer.")


def validate_no_local_paths_for_frontend_payloads(loaded: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    # source_manifest is archival and may include local artifact paths; frontend should use sanitized manifest instead.
    frontend_keys = ["evidence", "packet_summary", "suppliers", "ingredients", "cost_breakdown", "graph", "home_cards"]

    for key in frontend_keys:
        payload = loaded.get(key)
        if payload is None:
            continue

        if contains_local_windows_path(payload):
            add_check(checks, f"no_local_paths_payload_{key}", "fail", "high", f"Frontend payload {key} contains local Windows paths.")
        else:
            add_check(checks, f"no_local_paths_payload_{key}", "pass", "info", f"Frontend payload {key} contains no local Windows paths.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    public_dir = root / "public" / "data" / "hershey" / "enriched_display"
    out_dir = root / "artifacts" / "18_enriched_public_validation"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    loaded = validate_required_files(public_dir, checks)

    frontend_manifest = build_frontend_manifest(public_dir, loaded)
    frontend_manifest_public_path = public_dir / FRONTEND_MANIFEST_NAME
    frontend_manifest_artifact_path = out_dir / FRONTEND_MANIFEST_NAME

    write_json(frontend_manifest_public_path, frontend_manifest)
    write_json(frontend_manifest_artifact_path, frontend_manifest)

    validate_frontend_manifest(root, frontend_manifest, checks, frontend_manifest_public_path)
    validate_no_local_paths_for_frontend_payloads(loaded, checks)

    if "graph" in loaded:
        validate_graph(loaded["graph"], checks)

    if "suppliers" in loaded and "ingredients" in loaded and "home_cards" in loaded:
        validate_cards(loaded["suppliers"], loaded["ingredients"], loaded["home_cards"], checks)

    if "evidence" in loaded:
        validate_evidence(loaded["evidence"], checks)

    if "cost_breakdown" in loaded:
        validate_cost(loaded["cost_breakdown"], checks)

    fail_rows = [row for row in checks if row["status"] == "fail"]
    critical_failures = [row for row in fail_rows if row["severity"] == "critical"]
    high_failures = [row for row in fail_rows if row["severity"] == "high"]

    if critical_failures:
        validation_status = "fail"
    elif high_failures:
        validation_status = "pass_with_warnings"
    elif fail_rows:
        validation_status = "pass_with_minor_warnings"
    else:
        validation_status = "pass"

    checks_csv = out_dir / "enriched_public_validation_checks.csv"
    write_csv(checks_csv, checks)

    report = {
        "run_name": "step16k_enriched_public_json_validation",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "total_checks": len(checks),
        "failed_checks": len(fail_rows),
        "critical_failures": len(critical_failures),
        "high_failures": len(high_failures),
        "loaded_public_files": list(loaded.keys()),
        "frontend_manifest_public_path": str(frontend_manifest_public_path).replace("\\", "/"),
        "frontend_manifest_public_url": public_url_for(FRONTEND_MANIFEST_NAME),
        "frontend_manifest_artifact_path": str(frontend_manifest_artifact_path).replace("\\", "/"),
        "evidence_lookup_items": len(loaded.get("evidence", {})) if isinstance(loaded.get("evidence"), dict) else 0,
        "packet_summary_items": len(loaded.get("packet_summary", [])) if isinstance(loaded.get("packet_summary"), list) else 0,
        "supplier_cards_v2": len(loaded.get("suppliers", [])) if isinstance(loaded.get("suppliers"), list) else 0,
        "ingredient_cards_v2": len(loaded.get("ingredients", [])) if isinstance(loaded.get("ingredients"), list) else 0,
        "graph_nodes_v2": len(loaded.get("graph", {}).get("nodes", [])) if isinstance(loaded.get("graph"), dict) else 0,
        "graph_edges_v2": len(loaded.get("graph", {}).get("edges", [])) if isinstance(loaded.get("graph"), dict) else 0,
        "home_cards_v2": len(loaded.get("home_cards", [])) if isinstance(loaded.get("home_cards"), list) else 0,
        "checks_csv": str(checks_csv).replace("\\", "/"),
        "next_step": (
            "Step 17A: frontend stability check and enriched manifest loader."
            if validation_status in {"pass", "pass_with_minor_warnings"}
            else "Fix enriched public JSON validation failures before frontend build."
        ),
    }

    report_path = report_dir / "step16k_enriched_public_json_validation_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16K ENRICHED PUBLIC JSON VALIDATION COMPLETE")
    print("-------------------------------------------------")
    print(f"Validation status:    {validation_status}")
    print(f"Total checks:         {len(checks)}")
    print(f"Failed checks:        {len(fail_rows)}")
    print(f"Critical failures:    {len(critical_failures)}")
    print(f"High failures:        {len(high_failures)}")
    print("")
    print(f"Frontend manifest:    {frontend_manifest_public_path}")
    print(f"Checks CSV:           {checks_csv}")
    print(f"Report JSON:          {report_path}")
    print("")


if __name__ == "__main__":
    main()