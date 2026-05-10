from __future__ import annotations

import argparse
import csv
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PACKET_DISPLAY_NAMES = {
    "hershey_company": "The Hershey Company Evidence",
    "product_sku_1_55oz": "Target SKU / Wrapper Evidence",
    "sugar": "Sugar Evidence",
    "cocoa_chocolate_cocoa_butter": "Cocoa / Chocolate / Cocoa Butter Evidence",
    "dairy_milk_skim_milk_milk_fat": "Dairy / Milk / Skim Milk / Milk Fat Evidence",
    "soy_lecithin": "Soy Lecithin Evidence",
    "pgpr": "PGPR Evidence",
    "natural_flavor": "Natural Flavor Evidence",
    "packaging_wrapper": "Packaging / Wrapper Evidence",
    "logistics_distribution": "Logistics / Distribution Evidence",
    "retail_price_evidence": "Retail Price Evidence",
}

SUPPLIER_PACKET_MAP = {
    "sugar": ["ASR / American Sugar Refining"],
    "cocoa_chocolate_cocoa_butter": ["Barry Callebaut"],
    "dairy_milk_skim_milk_milk_fat": ["Land O'Lakes"],
    "logistics_distribution": ["McLane"],
}

INGREDIENT_PACKET_MAP = {
    "sugar": ["Sugar"],
    "cocoa_chocolate_cocoa_butter": ["Chocolate", "Cocoa", "Cocoa Butter"],
    "dairy_milk_skim_milk_milk_fat": ["Milk", "Skim Milk", "Milk Fat"],
    "soy_lecithin": ["Soy Lecithin"],
    "pgpr": ["PGPR"],
    "natural_flavor": ["Natural Flavor"],
    "packaging_wrapper": ["Packaging / Wrapper"],
    "product_sku_1_55oz": ["Target SKU / Product Label"],
}

SAFE_PROJECT_WORDING = {
    "project_title": "Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence",
    "unit": "one HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g",
    "model_scope": "Public-evidence benchmark supply-chain and cost intelligence model.",
    "primary_disclaimer": (
        "This is a public-evidence benchmark model. It is not Hershey internal SKU-level cost accounting, "
        "supplier invoice data, margin analysis, or proprietary distribution data."
    ),
    "audit_disclaimer": (
        "Only Step 16I approved display-safe evidence is used in the enriched v2 display artifacts."
    ),
}


def read_json(path: Path, fallback: Any = None) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def cents_to_usd(value: Any) -> float | None:
    val = safe_float(value)
    if val is None:
        return None
    return round(val / 100.0, 4)


def compact_evidence(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": row.get("evidence_id", ""),
        "file_name": row.get("file_name", ""),
        "packet": row.get("packet", ""),
        "source_type": row.get("source_type", ""),
        "primary_claim_role": row.get("primary_claim_role", ""),
        "claim_strength": row.get("claim_strength", ""),
        "safe_scope": row.get("safe_scope", ""),
        "relationship_strength": row.get("relationship_strength", ""),
        "confidence_level": row.get("confidence_level", ""),
        "strict_audit_status": row.get("strict_audit_status", ""),
        "public_display_allowed": row.get("public_display_allowed", False),
        "context_display_allowed": row.get("context_display_allowed", False),
        "audited_safe_website_wording": row.get("audited_safe_website_wording", ""),
        "evidence_text_preview": str(row.get("evidence_text", ""))[:700],
    }


def group_approved_by_packet(approved: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in approved:
        grouped[row.get("packet", "unknown")].append(row)
    return grouped


def build_evidence_lookup(approved: list[dict[str, Any]], context_only: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup = {}

    for row in approved + context_only:
        evidence_id = row.get("evidence_id")
        if not evidence_id:
            continue

        lookup[evidence_id] = {
            **compact_evidence(row),
            "entities": row.get("entities", []),
            "ingredients": row.get("ingredients", []),
            "risk_flags": row.get("risk_flags", []),
            "audit_reasons": row.get("audit_reasons", []),
            "required_rewrites": row.get("required_rewrites", []),
            "evidence_text": row.get("evidence_text", ""),
        }

    return lookup


def build_packet_summary(
    approved: list[dict[str, Any]],
    context_only: list[dict[str, Any]],
    rejected: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    all_rows = approved + context_only + rejected
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in all_rows:
        grouped[row.get("packet", "unknown")].append(row)

    packet_summary = []

    for packet, rows in sorted(grouped.items()):
        approved_rows = [r for r in rows if r.get("strict_audit_status") == "approved_display_safe"]
        context_rows = [r for r in rows if r.get("strict_audit_status") == "approved_context_only"]
        rejected_rows = [r for r in rows if str(r.get("strict_audit_status", "")).startswith("rejected")]

        role_counts = Counter(r.get("primary_claim_role", "unknown") for r in rows)
        scope_counts = Counter(r.get("safe_scope", "unknown") for r in rows)
        source_counts = Counter(r.get("source_type", "unknown") for r in rows)

        packet_summary.append(
            {
                "packet": packet,
                "display_name": PACKET_DISPLAY_NAMES.get(packet, packet.replace("_", " ").title()),
                "total_evidence_seen": len(rows),
                "approved_display_count": len(approved_rows),
                "context_only_count": len(context_rows),
                "rejected_count": len(rejected_rows),
                "role_counts": dict(sorted(role_counts.items())),
                "safe_scope_counts": dict(sorted(scope_counts.items())),
                "source_type_counts": dict(sorted(source_counts.items())),
                "approved_evidence_ids": [r.get("evidence_id") for r in approved_rows],
                "top_approved_evidence": [compact_evidence(r) for r in approved_rows[:10]],
            }
        )

    return packet_summary


def evidence_for_packet(packet: str, grouped: dict[str, list[dict[str, Any]]], limit: int = 8) -> list[dict[str, Any]]:
    return [compact_evidence(row) for row in grouped.get(packet, [])[:limit]]


def build_supplier_cards_v2(
    baseline_supplier_cards: list[dict[str, Any]],
    grouped: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    cards = []

    baseline_by_name = {
        str(card.get("safe_display_name") or card.get("company_name") or "").lower(): card
        for card in baseline_supplier_cards
    }

    supplier_specs = [
        {
            "supplier_id": "SUP_ASR_SUGAR",
            "safe_display_name": "ASR / American Sugar Refining",
            "packet": "sugar",
            "related_stage": "Sugar",
            "relationship_level": "company_level_only",
        },
        {
            "supplier_id": "SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE",
            "safe_display_name": "Barry Callebaut",
            "packet": "cocoa_chocolate_cocoa_butter",
            "related_stage": "Cocoa / Chocolate / Cocoa Butter",
            "relationship_level": "company_level_only",
        },
        {
            "supplier_id": "SUP_LAND_O_LAKES_DAIRY",
            "safe_display_name": "Land O'Lakes",
            "packet": "dairy_milk_skim_milk_milk_fat",
            "related_stage": "Dairy / Milk",
            "relationship_level": "company_level_only",
        },
        {
            "supplier_id": "SUP_MCLANE_DISTRIBUTION",
            "safe_display_name": "McLane",
            "packet": "logistics_distribution",
            "related_stage": "Distribution / Downstream Logistics",
            "relationship_level": "modeled_route_context",
        },
    ]

    for spec in supplier_specs:
        evidence_rows = grouped.get(spec["packet"], [])
        company_level = [
            row for row in evidence_rows
            if row.get("safe_scope") == "company_level_only"
            or row.get("primary_claim_role") in {"supplier_relationship", "logistics_distribution"}
        ]

        baseline = baseline_by_name.get(spec["safe_display_name"].lower(), {})

        cards.append(
            {
                "supplier_packet_id": spec["supplier_id"],
                "safe_display_name": spec["safe_display_name"],
                "related_ingredient_or_stage": spec["related_stage"],
                "relationship_level": spec["relationship_level"],
                "sku_level_confirmed": False,
                "confidence_level": "medium" if company_level else "low_medium",
                "logo_path": baseline.get("logo_path", ""),
                "logo_allowed": baseline.get("logo_allowed", False),
                "approved_evidence_count": len(company_level),
                "approved_evidence_preview": [compact_evidence(row) for row in company_level[:8]],
                "safe_website_wording": (
                    f"{spec['safe_display_name']} is displayed as company-level or modeled supply-chain context only. "
                    "This does not prove exact 1.55 oz SKU allocation."
                ),
                "limits": [
                    "No exact SKU-level supplier allocation is claimed.",
                    "Evidence is public-source and audited for safe display wording.",
                ],
                "display_allowed": True,
                "source_version": "enriched_v2_step16i_audited",
            }
        )

    return cards


def build_ingredient_cards_v2(
    baseline_ingredient_cards: list[dict[str, Any]],
    grouped: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    cards = []

    label_order = 1

    for packet, ingredient_names in INGREDIENT_PACKET_MAP.items():
        evidence_rows = grouped.get(packet, [])
        label_rows = [
            row for row in evidence_rows
            if row.get("safe_scope") in {"sku_or_label_level", "company_level_only", "benchmark_only"}
        ]

        for ingredient in ingredient_names:
            supplier_names = SUPPLIER_PACKET_MAP.get(packet, [])

            cards.append(
                {
                    "ingredient_id": f"ING_{ingredient.upper().replace(' ', '_').replace('/', '').replace('-', '_')}",
                    "ingredient_name": ingredient,
                    "packet": packet,
                    "label_order_position": label_order,
                    "label_status": "confirmed_or_contextual_from_audited_public_evidence",
                    "supplier_status": "company_level_context_only" if supplier_names else "supplier_unknown_or_benchmark_only",
                    "confirmed_supplier_names": supplier_names,
                    "sku_level_supplier_confirmed": False,
                    "confidence_level": "medium_high" if label_rows else "medium_low",
                    "origin_logic": "Built from enriched audited evidence. Exact SKU supplier allocation is not claimed.",
                    "processing_logic": "Used for public-evidence explanation and display-safe supply-chain modeling.",
                    "supplier_limitations": [
                        "Supplier relationship is company-level unless exact SKU evidence is separately available.",
                        "Ingredient presence does not prove supplier allocation.",
                    ],
                    "approved_evidence_count": len(label_rows),
                    "approved_evidence_preview": [compact_evidence(row) for row in label_rows[:8]],
                    "display_allowed": True,
                    "source_version": "enriched_v2_step16i_audited",
                }
            )
            label_order += 1

    return cards


def build_home_cards_v2(
    baseline_home_cards: list[dict[str, Any]],
    approved_count: int,
    context_count: int,
    rejected_count: int,
    cost_display: dict[str, Any],
    graph_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    physical = cost_display.get("physical_cost", {})
    retail = cost_display.get("retail_price", {})

    cards = [
        {
            "card_id": "CARD_AUDITED_EVIDENCE",
            "title": "Audited Evidence Brain",
            "value": f"{approved_count} approved",
            "subtitle": f"{context_count} context-only / {rejected_count} rejected",
            "display_type": "audit",
            "safe_note": "Only approved display-safe evidence is used in enriched v2 artifacts.",
        },
        {
            "card_id": "CARD_TARGET_SKU",
            "title": "Target SKU",
            "value": "1.55 oz / 43 g",
            "subtitle": "HERSHEY'S Milk Chocolate Candy Bar",
            "display_type": "product",
            "safe_note": "SKU identity is supported by audited product/wrapper evidence.",
        },
        {
            "card_id": "CARD_GRAPH_SIZE",
            "title": "Interactive Supply Chain",
            "value": f"{len(graph_payload.get('nodes', []))} nodes / {len(graph_payload.get('edges', []))} edges",
            "subtitle": "Ingredient, manufacturing, logistics, retail, and cost structure",
            "display_type": "graph",
            "safe_note": "Graph is a modeled public-evidence visualization.",
        },
        {
            "card_id": "CARD_PHYSICAL_COST",
            "title": "Estimated Physical Cost",
            "value": f"{physical.get('base_cents_per_bar')}¢",
            "subtitle": f"Range: {physical.get('low_cents_per_bar')}¢–{physical.get('high_cents_per_bar')}¢ per bar",
            "display_type": "cost",
            "safe_note": "Benchmark estimate only, not Hershey internal cost.",
        },
        {
            "card_id": "CARD_RETAIL_PRICE",
            "title": "Verified Retail Price",
            "value": f"${retail.get('base_usd_per_bar')}",
            "subtitle": f"Observed range: ${retail.get('low_usd_per_bar')}–${retail.get('high_usd_per_bar')}",
            "display_type": "retail",
            "safe_note": "Retail price is page/store/date dependent and not margin evidence.",
        },
    ]

    return cards


def add_evidence_counts_to_graph(
    graph_payload: dict[str, Any],
    grouped: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    graph = dict(graph_payload)
    nodes = []
    edges = []

    node_packet_rules = {
        "SUGAR": "sugar",
        "ASR": "sugar",
        "COCOA": "cocoa_chocolate_cocoa_butter",
        "BARRY": "cocoa_chocolate_cocoa_butter",
        "DAIRY": "dairy_milk_skim_milk_milk_fat",
        "LAND_O_LAKES": "dairy_milk_skim_milk_milk_fat",
        "LECITHIN": "soy_lecithin",
        "PGPR": "pgpr",
        "NATURAL_FLAVOR": "natural_flavor",
        "PACKAGING": "packaging_wrapper",
        "WRAPPER": "packaging_wrapper",
        "MCLANE": "logistics_distribution",
        "WAREHOUSE": "logistics_distribution",
        "DISTRIBUTION": "logistics_distribution",
        "RETAILER": "retail_price_evidence",
        "WALMART": "retail_price_evidence",
        "TARGET": "retail_price_evidence",
        "CVS": "retail_price_evidence",
        "WALGREENS": "retail_price_evidence",
        "PRODUCT": "product_sku_1_55oz",
        "HERSHEY": "hershey_company",
    }

    for node in graph_payload.get("nodes", []):
        node2 = dict(node)
        node_id = str(node.get("id", "")).upper()
        label = str(node.get("label", "")).upper()

        matched_packets = []
        for key, packet in node_packet_rules.items():
            if key in node_id or key in label:
                matched_packets.append(packet)

        matched_packets = sorted(set(matched_packets))
        evidence_rows = []
        for packet in matched_packets:
            evidence_rows.extend(grouped.get(packet, []))

        node2["enrichedEvidencePackets"] = matched_packets
        node2["enrichedApprovedEvidenceCount"] = len(evidence_rows)
        node2["enrichedEvidencePreview"] = [compact_evidence(row) for row in evidence_rows[:5]]
        node2["sourceVersion"] = "enriched_v2_step16i_audited"
        nodes.append(node2)

    for edge in graph_payload.get("edges", []):
        edge2 = dict(edge)
        edge2["sourceVersion"] = "enriched_v2_step16i_audited"
        edges.append(edge2)

    graph["payload_version"] = "v2_enriched_interactive_graph_payload"
    graph["nodes"] = nodes
    graph["edges"] = edges
    graph["safe_display_rules"] = list(graph.get("safe_display_rules", [])) + [
        "Enriched v2 graph evidence counts come only from Step 16I approved display-safe evidence.",
        "Graph routes remain modeled unless exact public evidence is available.",
    ]

    return graph


def enrich_cost_display(cost_display: dict[str, Any], grouped: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    cost = dict(cost_display)
    cost["display_version"] = "v2_enriched_cost_breakdown_display"
    cost["enriched_audit_note"] = (
        "Cost and price evidence is display-safe only when scoped as benchmark-only or retail page-level. "
        "Nothing here is Hershey internal SKU cost, invoice data, margin, or profit."
    )

    packet_cost_map = {
        "sugar": "Sugar",
        "cocoa_chocolate_cocoa_butter": "Cocoa / chocolate",
        "dairy_milk_skim_milk_milk_fat": "Dairy",
        "packaging_wrapper": "Packaging",
        "logistics_distribution": "Freight / warehousing / logistics",
        "retail_price_evidence": "Retail price",
    }

    evidence_by_cost_area = []

    for packet, label in packet_cost_map.items():
        rows = [
            row for row in grouped.get(packet, [])
            if row.get("safe_scope") in {"benchmark_only", "retail_page_level", "company_level_only", "sku_or_label_level"}
        ]

        evidence_by_cost_area.append(
            {
                "cost_area": label,
                "packet": packet,
                "approved_evidence_count": len(rows),
                "approved_evidence_preview": [compact_evidence(row) for row in rows[:8]],
            }
        )

    cost["enriched_evidence_by_cost_area"] = evidence_by_cost_area

    return cost


def write_summary_csv(path: Path, artifact_rows: list[dict[str, Any]]) -> None:
    fieldnames = ["artifact_name", "artifact_path", "record_count", "purpose"]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(artifact_rows)


def copy_to_public(source_path: Path, public_dir: Path) -> str:
    public_dir.mkdir(parents=True, exist_ok=True)
    dest = public_dir / source_path.name
    shutil.copy2(source_path, dest)
    return f"/data/hershey/enriched_display/{dest.name}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    approved_path = root / "artifacts" / "16_enriched_audit" / "enriched_approved_display_candidates.json"
    context_path = root / "artifacts" / "16_enriched_audit" / "enriched_context_only_evidence.json"
    rejected_path = root / "artifacts" / "16_enriched_audit" / "enriched_rejected_evidence.json"
    audit_report_path = root / "artifacts" / "10_run_reports" / "step16i_enriched_strict_audit_report.json"

    baseline_display_dir = root / "artifacts" / "09_display_ready"
    baseline_public_manifest_path = root / "public" / "data" / "hershey" / "frontend_public_manifest.json"

    out_dir = root / "artifacts" / "17_enriched_rebuild"
    public_dir = root / "public" / "data" / "hershey" / "enriched_display"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not approved_path.exists():
        raise FileNotFoundError(f"Missing Step 16I approved evidence: {approved_path}")

    approved = read_json(approved_path, [])
    context_only = read_json(context_path, [])
    rejected = read_json(rejected_path, [])
    audit_report = read_json(audit_report_path, {})

    baseline_supplier_cards = read_json(baseline_display_dir / "supplier_display_cards.json", [])
    baseline_ingredient_cards = read_json(baseline_display_dir / "ingredient_display_cards.json", [])
    baseline_home_cards = read_json(baseline_display_dir / "home_summary_cards.json", [])
    baseline_graph = read_json(baseline_display_dir / "interactive_graph_payload.json", {"nodes": [], "edges": []})
    baseline_cost = read_json(baseline_display_dir / "cost_breakdown_display.json", {})
    baseline_manifest = read_json(baseline_public_manifest_path, {})

    grouped = group_approved_by_packet(approved)

    evidence_lookup = build_evidence_lookup(approved, context_only)
    packet_summary = build_packet_summary(approved, context_only, rejected)
    supplier_cards = build_supplier_cards_v2(baseline_supplier_cards, grouped)
    ingredient_cards = build_ingredient_cards_v2(baseline_ingredient_cards, grouped)
    graph_v2 = add_evidence_counts_to_graph(baseline_graph, grouped)
    cost_v2 = enrich_cost_display(baseline_cost, grouped)
    home_cards_v2 = build_home_cards_v2(
        baseline_home_cards=baseline_home_cards,
        approved_count=len(approved),
        context_count=len(context_only),
        rejected_count=len(rejected),
        cost_display=cost_v2,
        graph_payload=graph_v2,
    )

    output_payloads = {
        "enriched_evidence_panel_lookup_v2.json": evidence_lookup,
        "enriched_packet_summary_v2.json": packet_summary,
        "enriched_supplier_cards_v2.json": supplier_cards,
        "enriched_ingredient_cards_v2.json": ingredient_cards,
        "enriched_cost_breakdown_display_v2.json": cost_v2,
        "enriched_interactive_graph_payload_v2.json": graph_v2,
        "enriched_home_summary_cards_v2.json": home_cards_v2,
    }

    artifact_rows = []
    public_urls = {}

    for file_name, payload in output_payloads.items():
        path = out_dir / file_name
        write_json(path, payload)
        public_url = copy_to_public(path, public_dir)
        public_urls[file_name.replace(".json", "")] = public_url

        if isinstance(payload, list):
            count = len(payload)
        elif isinstance(payload, dict):
            if "nodes" in payload and "edges" in payload:
                count = len(payload.get("nodes", [])) + len(payload.get("edges", []))
            else:
                count = len(payload)
        else:
            count = 1

        artifact_rows.append(
            {
                "artifact_name": file_name,
                "artifact_path": str(path).replace("\\", "/"),
                "record_count": count,
                "purpose": "enriched_v2_display_artifact",
            }
        )

    manifest = {
        "display_ready_version": "v2_enriched_step16j",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "project_wording": SAFE_PROJECT_WORDING,
        "input_artifacts": {
            "approved_display_candidates": str(approved_path).replace("\\", "/"),
            "context_only_evidence": str(context_path).replace("\\", "/"),
            "rejected_evidence": str(rejected_path).replace("\\", "/"),
            "step16i_report": str(audit_report_path).replace("\\", "/"),
            "baseline_public_manifest": str(baseline_public_manifest_path).replace("\\", "/"),
        },
        "display_artifacts": {
            name.replace(".json", ""): str((out_dir / name)).replace("\\", "/")
            for name in output_payloads.keys()
        },
        "public_urls": public_urls,
        "frontend_rule": "Frontend should prefer enriched_display v2 artifacts after Step 16K validation passes.",
        "safety_rule": "No frontend claim should bypass Step 16I approved display-safe evidence.",
        "audit_summary": {
            "approved_display_candidates": len(approved),
            "context_only_evidence": len(context_only),
            "rejected_evidence": len(rejected),
            "audit_status_counts": audit_report.get("audit_status_counts", {}),
        },
    }

    manifest_path = out_dir / "enriched_display_manifest_v2.json"
    write_json(manifest_path, manifest)
    public_manifest_url = copy_to_public(manifest_path, public_dir)

    summary_csv_path = out_dir / "enriched_rebuild_summary.csv"
    write_summary_csv(summary_csv_path, artifact_rows)

    report = {
        "run_name": "step16j_enriched_display_rebuild",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "approved_display_candidates_seen": len(approved),
        "context_only_evidence_seen": len(context_only),
        "rejected_evidence_seen": len(rejected),
        "enriched_evidence_lookup_items": len(evidence_lookup),
        "packet_summary_items": len(packet_summary),
        "supplier_cards_v2": len(supplier_cards),
        "ingredient_cards_v2": len(ingredient_cards),
        "graph_nodes_v2": len(graph_v2.get("nodes", [])),
        "graph_edges_v2": len(graph_v2.get("edges", [])),
        "home_cards_v2": len(home_cards_v2),
        "public_enriched_manifest_url": public_manifest_url,
        "artifact_outputs": {row["artifact_name"]: row["artifact_path"] for row in artifact_rows},
        "public_urls": public_urls,
        "enriched_display_manifest_v2": str(manifest_path).replace("\\", "/"),
        "enriched_rebuild_summary_csv": str(summary_csv_path).replace("\\", "/"),
        "next_step": "Step 16K: validate enriched public JSON v2 before frontend build.",
    }

    report_path = report_dir / "step16j_enriched_display_rebuild_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16J ENRICHED DISPLAY REBUILD COMPLETE")
    print("------------------------------------------")
    print(f"Approved display evidence seen: {len(approved)}")
    print(f"Context-only evidence seen:     {len(context_only)}")
    print(f"Rejected evidence seen:         {len(rejected)}")
    print(f"Evidence lookup items:          {len(evidence_lookup)}")
    print(f"Packet summary items:           {len(packet_summary)}")
    print(f"Supplier cards v2:              {len(supplier_cards)}")
    print(f"Ingredient cards v2:            {len(ingredient_cards)}")
    print(f"Graph nodes v2:                 {len(graph_v2.get('nodes', []))}")
    print(f"Graph edges v2:                 {len(graph_v2.get('edges', []))}")
    print("")
    print(f"Manifest:   {manifest_path}")
    print(f"Summary CSV:{summary_csv_path}")
    print(f"Report JSON:{report_path}")
    print("")


if __name__ == "__main__":
    main()