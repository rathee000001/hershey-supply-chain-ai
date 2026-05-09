from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SAFE_PROJECT_WORDING = {
    "project_title": "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence",
    "unit": "one HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g",
    "model_scope": "Public-evidence benchmark model for ingredient, supplier, logistics, retail, and cost visualization.",
    "primary_disclaimer": (
        "This project estimates a public-evidence benchmark supply-chain and cost model. "
        "It is not Hershey's internal SKU-level cost accounting, bill of materials, supplier invoice, or margin model."
    ),
    "supplier_disclaimer": (
        "Supplier relationships are displayed at company level unless explicitly marked SKU-level. "
        "Exact ingredient allocation for the 1.55 oz bar is not publicly confirmed."
    ),
    "residual_disclaimer": (
        "Residual channel/commercial pool is the gap between observed retail price and modeled physical cost. "
        "It is not profit and may include retailer margin, distributor margin, trade promotions, taxes/fees, SG&A allocation, brand economics, and estimation error."
    ),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: Any) -> str:
    return str(value or "").strip()


def round2(value: Any) -> Any:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except Exception:
        return value


def cents_to_usd(value: Any) -> Any:
    if value is None:
        return None
    try:
        return round(float(value) / 100.0, 4)
    except Exception:
        return value


def percent(value: Any) -> Any:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except Exception:
        return value


def load_optional_json(path: Path, fallback: Any) -> Any:
    if path.exists():
        return read_json(path)
    return fallback


def evidence_lookup(audited_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup = {}

    for row in audited_rows:
        evidence_id = row.get("evidence_id")
        if not evidence_id:
            continue

        lookup[evidence_id] = {
            "evidence_id": evidence_id,
            "source_file": row.get("source_file", ""),
            "packet": row.get("packet", ""),
            "category": row.get("category", ""),
            "audit_status": row.get("audit_status", ""),
            "relationship_strength": row.get("corrected_relationship_strength", row.get("relationship_strength", "")),
            "evidence_type": row.get("corrected_evidence_type", row.get("evidence_type", "")),
            "related_company": row.get("corrected_related_company", row.get("related_company", "")),
            "related_ingredient": row.get("corrected_related_ingredient", row.get("related_ingredient", "")),
            "claim_scope": row.get("claim_scope", ""),
            "display_allowed": row.get("display_allowed", False),
            "safe_website_wording": row.get("safe_website_wording", ""),
            "evidence_text": row.get("evidence_text", ""),
            "confidence_level": row.get("confidence_level", ""),
        }

    return lookup


def compact_evidence_list(evidence_ids: list[str], lookup: dict[str, dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    compact = []

    for evidence_id in evidence_ids[:limit]:
        item = lookup.get(evidence_id)
        if not item:
            compact.append({
                "evidence_id": evidence_id,
                "source_file": "",
                "safe_website_wording": "",
                "available": False,
            })
            continue

        compact.append({
            "evidence_id": evidence_id,
            "source_file": item.get("source_file", ""),
            "packet": item.get("packet", ""),
            "relationship_strength": item.get("relationship_strength", ""),
            "claim_scope": item.get("claim_scope", ""),
            "safe_website_wording": item.get("safe_website_wording", ""),
            "available": True,
        })

    return compact


def build_home_summary_cards(cost_stack: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, Any]]:
    totals = cost_stack.get("totals", {})
    retail = cost_stack.get("retail_price_summary", {})
    residual = cost_stack.get("residual_channel_commercial_pool", {})

    return [
        {
            "card_id": "CARD_TARGET_SKU",
            "title": "Target SKU",
            "value": "1.55 oz / 43 g",
            "subtitle": "HERSHEY'S Milk Chocolate Candy Bar",
            "display_type": "product",
            "safe_note": "SKU identity is visually verified from product evidence."
        },
        {
            "card_id": "CARD_GRAPH_SIZE",
            "title": "Interactive Supply Chain",
            "value": f"{len(graph.get('nodes', []))} nodes / {len(graph.get('edges', []))} edges",
            "subtitle": "Ingredient, manufacturing, logistics, retail, and cost structure",
            "display_type": "graph",
            "safe_note": "Modeled graph for public-evidence visualization."
        },
        {
            "card_id": "CARD_PHYSICAL_COST",
            "title": "Estimated Physical Cost",
            "value": f"{round2(totals.get('base_cents_per_bar'))}¢",
            "subtitle": f"Range: {round2(totals.get('low_cents_per_bar'))}¢–{round2(totals.get('high_cents_per_bar'))}¢ per bar",
            "display_type": "cost",
            "safe_note": "Benchmark estimate, not Hershey internal cost."
        },
        {
            "card_id": "CARD_RETAIL_PRICE",
            "title": "Verified Retail Price",
            "value": f"${round(cents_to_usd(retail.get('base_retail_price_cents')), 2)}",
            "subtitle": f"Observed range: ${round(cents_to_usd(retail.get('low_retail_price_cents')), 2)}–${round(cents_to_usd(retail.get('high_retail_price_cents')), 2)}",
            "display_type": "retail",
            "safe_note": "Retail prices are visually verified from collected retailer pages."
        },
        {
            "card_id": "CARD_RESIDUAL_POOL",
            "title": "Residual Channel / Commercial Pool",
            "value": f"{round2(residual.get('base_cents_per_bar'))}¢",
            "subtitle": "Retail price minus modeled physical cost",
            "display_type": "residual",
            "safe_note": "Residual is not profit."
        },
    ]


def build_cost_breakdown_display(cost_stack: dict[str, Any], cost_records: list[dict[str, Any]]) -> dict[str, Any]:
    totals = cost_stack.get("totals", {})
    retail = cost_stack.get("retail_price_summary", {})
    residual = cost_stack.get("residual_channel_commercial_pool", {})

    display_records = []

    for row in cost_records:
        cost_type = row.get("cost_type", "")

        if cost_type == "retail_price" and row.get("cost_bucket_id") != "COST_RETAIL_PRICE_VERIFIED":
            continue

        display_records.append({
            "cost_bucket_id": row.get("cost_bucket_id", ""),
            "label": row.get("cost_bucket", ""),
            "cost_type": cost_type,
            "low_cents_per_bar": row.get("low_cents_per_bar"),
            "base_cents_per_bar": row.get("base_cents_per_bar"),
            "high_cents_per_bar": row.get("high_cents_per_bar"),
            "low_usd_per_bar": cents_to_usd(row.get("low_cents_per_bar")),
            "base_usd_per_bar": cents_to_usd(row.get("base_cents_per_bar")),
            "high_usd_per_bar": cents_to_usd(row.get("high_cents_per_bar")),
            "confidence_level": row.get("confidence_level", ""),
            "evidence_type": row.get("evidence_type", ""),
            "notes": row.get("notes", ""),
            "cost_logic": row.get("cost_logic", ""),
            "safe_display": True,
        })

    return {
        "display_version": "v1_cost_breakdown_display",
        "unit": SAFE_PROJECT_WORDING["unit"],
        "physical_cost": {
            "low_cents_per_bar": totals.get("low_cents_per_bar"),
            "base_cents_per_bar": totals.get("base_cents_per_bar"),
            "high_cents_per_bar": totals.get("high_cents_per_bar"),
            "low_usd_per_bar": cents_to_usd(totals.get("low_cents_per_bar")),
            "base_usd_per_bar": cents_to_usd(totals.get("base_cents_per_bar")),
            "high_usd_per_bar": cents_to_usd(totals.get("high_cents_per_bar")),
        },
        "retail_price": {
            "low_cents_per_bar": retail.get("low_retail_price_cents"),
            "base_cents_per_bar": retail.get("base_retail_price_cents"),
            "high_cents_per_bar": retail.get("high_retail_price_cents"),
            "low_usd_per_bar": retail.get("low_retail_price_usd"),
            "base_usd_per_bar": retail.get("base_retail_price_usd"),
            "high_usd_per_bar": retail.get("high_retail_price_usd"),
            "retailers_verified": retail.get("retailers_verified"),
        },
        "residual_channel_pool": {
            "low_cents_per_bar": residual.get("low_cents_per_bar"),
            "base_cents_per_bar": residual.get("base_cents_per_bar"),
            "high_cents_per_bar": residual.get("high_cents_per_bar"),
            "physical_cost_share_of_retail_base_case": percent(residual.get("physical_cost_share_of_retail_base_case")),
            "safe_display_wording": residual.get("safe_display_wording", SAFE_PROJECT_WORDING["residual_disclaimer"]),
        },
        "records": display_records,
        "safe_display_wording": cost_stack.get("safe_display_wording", SAFE_PROJECT_WORDING["primary_disclaimer"]),
    }


def build_supplier_display_cards(supplier_packets: list[dict[str, Any]], ev_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    cards = []

    for supplier in supplier_packets:
        cards.append({
            "supplier_packet_id": supplier.get("supplier_packet_id", ""),
            "company_name": supplier.get("company_name", ""),
            "safe_display_name": supplier.get("safe_display_name", supplier.get("company_name", "")),
            "related_ingredient_or_stage": supplier.get("related_ingredient_or_stage", ""),
            "relationship_level": supplier.get("relationship_level", ""),
            "sku_level_confirmed": supplier.get("sku_level_confirmed", False),
            "confidence_level": supplier.get("confidence_level", ""),
            "logo_path": supplier.get("logo_path", ""),
            "logo_allowed": supplier.get("logo_allowed", False),
            "safe_website_wording": supplier.get("safe_website_wording", ""),
            "limits": supplier.get("limits", []),
            "evidence_count": len(supplier.get("evidence_ids", [])),
            "evidence_preview": compact_evidence_list(supplier.get("evidence_ids", []), ev_lookup, limit=5),
            "display_allowed": True,
        })

    return cards


def build_ingredient_display_cards(ingredient_packets: list[dict[str, Any]], ev_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    cards = []

    for item in ingredient_packets:
        cards.append({
            "ingredient_id": item.get("ingredient_id", ""),
            "ingredient_name": item.get("ingredient_name", ""),
            "label_order_position": item.get("label_order_position"),
            "label_status": item.get("label_status", ""),
            "supplier_status": item.get("supplier_status", ""),
            "confirmed_supplier_names": item.get("confirmed_supplier_names", []),
            "confidence_level": item.get("confidence_level", ""),
            "origin_logic": item.get("origin_logic", ""),
            "processing_logic": item.get("processing_logic", ""),
            "supplier_limitations": item.get("supplier_limitations", []),
            "estimated_grams_base": item.get("estimated_grams_base"),
            "estimated_cost_base_cents": item.get("estimated_cost_base_cents"),
            "estimated_cost_low_cents": item.get("estimated_cost_low_cents"),
            "estimated_cost_high_cents": item.get("estimated_cost_high_cents"),
            "estimated_cost_status": item.get("estimated_cost_status", ""),
            "evidence_count": len(item.get("source_evidence_ids", [])),
            "evidence_preview": compact_evidence_list(item.get("source_evidence_ids", []), ev_lookup, limit=5),
            "display_allowed": True,
        })

    return sorted(cards, key=lambda x: x.get("label_order_position") or 999)


def build_node_detail_panels(graph: dict[str, Any], ev_lookup: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    panels = {}

    for node in graph.get("nodes", []):
        node_id = node.get("node_id")
        if not node_id:
            continue

        panels[node_id] = {
            "panel_id": f"PANEL_{node_id}",
            "node_id": node_id,
            "title": node.get("label", ""),
            "node_type": node.get("node_type", ""),
            "description": node.get("description", ""),
            "company_name": node.get("company_name", ""),
            "product_or_material": node.get("product_or_material", ""),
            "relationship_status": node.get("relationship_status", ""),
            "confidence_level": node.get("confidence_level", ""),
            "safe_summary": node.get("hover_summary", ""),
            "cost_fields": {
                "low_cents_per_bar": node.get("low_cents_per_bar", node.get("cost_total_low_cents")),
                "base_cents_per_bar": node.get("base_cents_per_bar", node.get("cost_total_base_cents")),
                "high_cents_per_bar": node.get("high_cents_per_bar", node.get("cost_total_high_cents")),
                "retail_low_cents": node.get("retail_low_cents"),
                "retail_base_cents": node.get("retail_base_cents"),
                "retail_high_cents": node.get("retail_high_cents"),
            },
            "logo_path": node.get("logo_path", ""),
            "image_path": node.get("image_path", ""),
            "evidence_ids": node.get("evidence_ids", []),
            "evidence_preview": compact_evidence_list(node.get("evidence_ids", []), ev_lookup, limit=8),
            "display_allowed": node.get("display_allowed", True),
        }

    return panels


def build_interactive_graph_payload(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = []
    edges = []

    for node in graph.get("nodes", []):
        if not node.get("display_allowed", True):
            continue

        nodes.append({
            "id": node.get("node_id"),
            "type": node.get("node_type"),
            "label": node.get("label"),
            "description": node.get("description"),
            "relationshipStatus": node.get("relationship_status"),
            "confidenceLevel": node.get("confidence_level"),
            "companyName": node.get("company_name", ""),
            "material": node.get("product_or_material", ""),
            "logoPath": node.get("logo_path", ""),
            "imagePath": node.get("image_path", ""),
            "hoverSummary": node.get("hover_summary", ""),
            "detailPanelId": f"PANEL_{node.get('node_id')}",
            "cost": {
                "low": node.get("low_cents_per_bar", node.get("cost_total_low_cents")),
                "base": node.get("base_cents_per_bar", node.get("cost_total_base_cents")),
                "high": node.get("high_cents_per_bar", node.get("cost_total_high_cents")),
            },
            "retail": {
                "low": node.get("retail_low_cents"),
                "base": node.get("retail_base_cents"),
                "high": node.get("retail_high_cents"),
            },
        })

    for edge in graph.get("edges", []):
        if not edge.get("display_allowed", True):
            continue

        edges.append({
            "id": edge.get("edge_id"),
            "source": edge.get("from_node_id"),
            "target": edge.get("to_node_id"),
            "flowType": edge.get("flow_type"),
            "materialFlow": edge.get("material_flow"),
            "relationshipStatus": edge.get("relationship_status"),
            "confidenceLevel": edge.get("confidence_level"),
            "animationType": edge.get("animation_type"),
            "tooltipText": edge.get("tooltip_text"),
        })

    return {
        "payload_version": "v1_interactive_graph_payload",
        "project": graph.get("project", SAFE_PROJECT_WORDING["project_title"]),
        "unit": graph.get("unit", SAFE_PROJECT_WORDING["unit"]),
        "safe_display_rules": graph.get("safe_display_rules", []),
        "nodes": nodes,
        "edges": edges,
    }


def build_evidence_panel_lookup(audited_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    panels = {}

    for row in audited_rows:
        evidence_id = row.get("evidence_id")
        if not evidence_id:
            continue

        panels[evidence_id] = {
            "evidence_id": evidence_id,
            "source_file": row.get("source_file", ""),
            "packet": row.get("packet", ""),
            "category": row.get("category", ""),
            "audit_status": row.get("audit_status", ""),
            "display_allowed": row.get("display_allowed", False),
            "relationship_strength": row.get("corrected_relationship_strength", row.get("relationship_strength", "")),
            "claim_scope": row.get("claim_scope", ""),
            "safe_website_wording": row.get("safe_website_wording", ""),
            "evidence_text_preview": clean(row.get("evidence_text", ""))[:600],
            "unsafe_wording_to_avoid": row.get("unsafe_wording_to_avoid", ""),
        }

    return panels


def write_payload_summary_csv(path: Path, outputs: dict[str, Any]) -> None:
    rows = []

    for name, payload in outputs.items():
        if isinstance(payload, list):
            count = len(payload)
        elif isinstance(payload, dict):
            if "nodes" in payload and "edges" in payload:
                count = len(payload.get("nodes", [])) + len(payload.get("edges", []))
            else:
                count = len(payload)
        else:
            count = 1

        rows.append({
            "artifact_name": name,
            "record_count": count,
            "artifact_type": type(payload).__name__,
        })

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["artifact_name", "record_count", "artifact_type"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    graph_path = root / "artifacts" / "08_node_edge_architecture" / "supply_chain_graph.json"
    cost_stack_path = root / "artifacts" / "07_cost_model_blobs" / "cost_stack_with_retail_summary.json"
    cost_records_path = root / "artifacts" / "07_cost_model_blobs" / "cost_model_records_with_retail.json"
    supplier_path = root / "artifacts" / "05_supplier_blobs" / "supplier_packets.json"
    ingredient_costed_path = root / "artifacts" / "07_cost_model_blobs" / "ingredient_packets_costed.json"
    ingredient_fallback_path = root / "artifacts" / "06_ingredient_blobs" / "ingredient_packets.json"
    audited_path = root / "artifacts" / "04_level2_audited_blobs_strict" / "audited_evidence_blobs_strict.json"

    out_dir = root / "artifacts" / "09_display_ready"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    for required in [graph_path, cost_stack_path, cost_records_path, supplier_path, audited_path]:
        if not required.exists():
            raise FileNotFoundError(f"Missing required Step 15 input: {required}")

    graph = read_json(graph_path)
    cost_stack = read_json(cost_stack_path)
    cost_records = read_json(cost_records_path)
    supplier_packets = read_json(supplier_path)
    ingredient_packets = read_json(ingredient_costed_path if ingredient_costed_path.exists() else ingredient_fallback_path)
    audited_rows = read_json(audited_path)

    ev_lookup = evidence_lookup(audited_rows)

    outputs = {
        "home_summary_cards": build_home_summary_cards(cost_stack, graph),
        "interactive_graph_payload": build_interactive_graph_payload(graph),
        "node_detail_panels": build_node_detail_panels(graph, ev_lookup),
        "cost_breakdown_display": build_cost_breakdown_display(cost_stack, cost_records),
        "supplier_display_cards": build_supplier_display_cards(supplier_packets, ev_lookup),
        "ingredient_display_cards": build_ingredient_display_cards(ingredient_packets, ev_lookup),
        "evidence_panel_lookup": build_evidence_panel_lookup(audited_rows),
    }

    output_paths = {
        "home_summary_cards": out_dir / "home_summary_cards.json",
        "interactive_graph_payload": out_dir / "interactive_graph_payload.json",
        "node_detail_panels": out_dir / "node_detail_panels.json",
        "cost_breakdown_display": out_dir / "cost_breakdown_display.json",
        "supplier_display_cards": out_dir / "supplier_display_cards.json",
        "ingredient_display_cards": out_dir / "ingredient_display_cards.json",
        "evidence_panel_lookup": out_dir / "evidence_panel_lookup.json",
    }

    for key, path in output_paths.items():
        write_json(path, outputs[key])

    manifest = {
        "display_ready_version": "v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project_wording": SAFE_PROJECT_WORDING,
        "input_artifacts": {
            "graph": str(graph_path).replace("\\", "/"),
            "cost_stack": str(cost_stack_path).replace("\\", "/"),
            "cost_records": str(cost_records_path).replace("\\", "/"),
            "supplier_packets": str(supplier_path).replace("\\", "/"),
            "ingredient_packets": str((ingredient_costed_path if ingredient_costed_path.exists() else ingredient_fallback_path)).replace("\\", "/"),
            "audited_evidence": str(audited_path).replace("\\", "/"),
        },
        "display_artifacts": {key: str(path).replace("\\", "/") for key, path in output_paths.items()},
        "frontend_rule": "Frontend should read these artifacts only. Hardcode layout labels only; do not hardcode supplier/cost claims.",
        "safe_display_rules": graph.get("safe_display_rules", []),
    }

    manifest_path = out_dir / "display_ready_manifest.json"
    summary_csv = out_dir / "frontend_payload_summary.csv"

    write_json(manifest_path, manifest)
    write_payload_summary_csv(summary_csv, outputs)

    graph_payload = outputs["interactive_graph_payload"]
    report = {
        "run_name": "step15_display_ready_artifacts",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "display_artifacts_created": len(output_paths) + 1,
        "graph_nodes_for_frontend": len(graph_payload["nodes"]),
        "graph_edges_for_frontend": len(graph_payload["edges"]),
        "node_detail_panels": len(outputs["node_detail_panels"]),
        "supplier_cards": len(outputs["supplier_display_cards"]),
        "ingredient_cards": len(outputs["ingredient_display_cards"]),
        "home_summary_cards": len(outputs["home_summary_cards"]),
        "evidence_panel_items": len(outputs["evidence_panel_lookup"]),
        "display_ready_folder": str(out_dir).replace("\\", "/"),
        "display_ready_manifest_json": str(manifest_path).replace("\\", "/"),
        "frontend_payload_summary_csv": str(summary_csv).replace("\\", "/"),
        "next_step": "Step 16: copy display-ready artifacts to public/data or build frontend pages that read from artifacts."
    }

    report_path = report_dir / "step15_display_ready_artifacts_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 15 DISPLAY-READY ARTIFACT BUILDER COMPLETE")
    print("-----------------------------------------------")
    print(f"Display artifacts created: {report['display_artifacts_created']}")
    print(f"Frontend graph nodes: {report['graph_nodes_for_frontend']}")
    print(f"Frontend graph edges: {report['graph_edges_for_frontend']}")
    print(f"Node detail panels: {report['node_detail_panels']}")
    print(f"Supplier cards: {report['supplier_cards']}")
    print(f"Ingredient cards: {report['ingredient_cards']}")
    print(f"Evidence panel items: {report['evidence_panel_items']}")
    print("")
    print(f"Manifest JSON: {manifest_path}")
    print(f"Summary CSV:   {summary_csv}")
    print(f"Report JSON:   {report_path}")
    print("")


if __name__ == "__main__":
    main()