from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def round2(value: Any) -> Any:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except Exception:
        return value


def evidence_for_supplier(supplier_packets: list[dict[str, Any]], supplier_packet_id: str) -> list[str]:
    for supplier in supplier_packets:
        if supplier.get("supplier_packet_id") == supplier_packet_id:
            return supplier.get("evidence_ids", [])
    return []


def evidence_for_ingredient(ingredient_packets: list[dict[str, Any]], ingredient_id: str) -> list[str]:
    for item in ingredient_packets:
        if item.get("ingredient_id") == ingredient_id:
            return item.get("source_evidence_ids", [])
    return []


def logo_for_supplier(supplier_packets: list[dict[str, Any]], supplier_packet_id: str) -> str:
    for supplier in supplier_packets:
        if supplier.get("supplier_packet_id") == supplier_packet_id:
            return supplier.get("logo_path", "")
    return ""


def cost_record_by_id(cost_records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row.get("cost_bucket_id"): row for row in cost_records}


def make_node(
    node_id: str,
    node_type: str,
    label: str,
    description: str,
    relationship_status: str,
    confidence_level: str,
    evidence_ids: list[str] | None = None,
    company_name: str = "",
    product_or_material: str = "",
    location: str = "",
    logo_path: str = "",
    image_path: str = "",
    hover_summary: str = "",
    detail_panel_blob_id: str = "",
    display_allowed: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node = {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "description": description,
        "company_name": company_name,
        "product_or_material": product_or_material,
        "location": location,
        "confidence_level": confidence_level,
        "relationship_status": relationship_status,
        "evidence_ids": evidence_ids or [],
        "display_allowed": display_allowed,
        "logo_path": logo_path,
        "image_path": image_path,
        "hover_summary": hover_summary or description,
        "detail_panel_blob_id": detail_panel_blob_id,
    }

    if extra:
        node.update(extra)

    return node


def make_edge(
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
    flow_type: str,
    material_flow: str,
    relationship_status: str,
    confidence_level: str,
    evidence_ids: list[str] | None = None,
    animation_type: str = "moving_particles",
    tooltip_text: str = "",
    display_allowed: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    edge = {
        "edge_id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "flow_type": flow_type,
        "material_flow": material_flow,
        "relationship_status": relationship_status,
        "evidence_ids": evidence_ids or [],
        "confidence_level": confidence_level,
        "display_allowed": display_allowed,
        "animation_type": animation_type,
        "tooltip_text": tooltip_text,
    }

    if extra:
        edge.update(extra)

    return edge


def build_nodes(
    supplier_packets: list[dict[str, Any]],
    ingredient_packets: list[dict[str, Any]],
    cost_records: list[dict[str, Any]],
    cost_stack: dict[str, Any],
) -> list[dict[str, Any]]:
    cost_by_id = cost_record_by_id(cost_records)
    totals = cost_stack.get("totals", {})
    retail = cost_stack.get("retail_price_summary", {})
    residual = cost_stack.get("residual_channel_commercial_pool", {})

    nodes: list[dict[str, Any]] = []

    # Product / center nodes
    nodes.append(make_node(
        node_id="NODE_PRODUCT_HERSHEY_155OZ",
        node_type="visual_reference",
        label="HERSHEY'S 1.55 oz Bar",
        description="Target SKU: HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g, U.S. market.",
        relationship_status="sku_level_confirmed",
        confidence_level="medium",
        product_or_material="HERSHEY'S Milk Chocolate Candy Bar 1.55 oz / 43 g",
        hover_summary="Target SKU for the supply-chain and cost model.",
        extra={
            "cost_total_low_cents": totals.get("low_cents_per_bar"),
            "cost_total_base_cents": totals.get("base_cents_per_bar"),
            "cost_total_high_cents": totals.get("high_cents_per_bar"),
            "retail_low_cents": retail.get("low_retail_price_cents"),
            "retail_base_cents": retail.get("base_retail_price_cents"),
            "retail_high_cents": retail.get("high_retail_price_cents"),
        }
    ))

    nodes.append(make_node(
        node_id="NODE_HERSHEY_MANUFACTURING",
        node_type="hershey_facility",
        label="Hershey Manufacturing",
        description="Modeled Hershey manufacturing center where raw materials, minor ingredients, and packaging converge.",
        company_name="The Hershey Company",
        relationship_status="company_level_confirmed",
        confidence_level="medium",
        hover_summary="Central manufacturing node. Internal process is modeled generally, not proprietary line data."
    ))

    # Ingredient origins and suppliers
    supplier_map = {
        "NODE_SUPPLIER_ASR": ("SUP_ASR_SUGAR", "ASR / American Sugar Refining", "Sugar supplier stream", "Sugar"),
        "NODE_SUPPLIER_BARRY": ("SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE", "Barry Callebaut", "Cocoa/chocolate supplier stream", "Cocoa / Chocolate / Cocoa Butter"),
        "NODE_SUPPLIER_LAND_O_LAKES": ("SUP_LAND_O_LAKES_DAIRY", "Land O'Lakes", "Dairy supplier stream", "Milk / Skim Milk / Milk Fat"),
        "NODE_DISTRIBUTOR_MCLANE": ("SUP_MCLANE_DISTRIBUTION", "McLane", "Downstream/distribution context", "Distribution"),
    }

    nodes.extend([
        make_node(
            node_id="NODE_ORIGIN_SUGAR",
            node_type="ingredient_origin",
            label="Sugar Cane / Beet Stream",
            description="Modeled sugar origin stream before refining and Hershey sourcing.",
            relationship_status="benchmark_only",
            confidence_level="medium",
            product_or_material="Sugar",
            evidence_ids=evidence_for_ingredient(ingredient_packets, "ING_SUGAR"),
            hover_summary="Sugar origin is modeled from public sourcing and benchmark context."
        ),
        make_node(
            node_id="NODE_ORIGIN_COCOA",
            node_type="ingredient_origin",
            label="Cocoa Origin Stream",
            description="Modeled cocoa origin stream before cocoa/chocolate processing.",
            relationship_status="benchmark_only",
            confidence_level="medium",
            product_or_material="Cocoa / Chocolate",
            evidence_ids=evidence_for_ingredient(ingredient_packets, "ING_COCOA_CHOCOLATE"),
            hover_summary="Cocoa origin and chocolate input stream."
        ),
        make_node(
            node_id="NODE_ORIGIN_DAIRY",
            node_type="ingredient_origin",
            label="Dairy Farm Stream",
            description="Modeled dairy origin stream before cooperative/processor stage.",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            product_or_material="Milk / Dairy",
            evidence_ids=evidence_for_ingredient(ingredient_packets, "ING_MILK"),
            hover_summary="Dairy farm/cooperative stream feeding dairy ingredients."
        ),
    ])

    for node_id, (supplier_id, label, desc, material) in supplier_map.items():
        if supplier_id == "SUP_MCLANE_DISTRIBUTION":
            continue

        ev = evidence_for_supplier(supplier_packets, supplier_id)
        nodes.append(make_node(
            node_id=node_id,
            node_type="supplier",
            label=label,
            description=desc + ". Company-level relationship only; exact SKU allocation is not publicly confirmed.",
            company_name=label,
            product_or_material=material,
            relationship_status="company_level_confirmed" if ev else "unknown",
            confidence_level="medium" if ev else "low",
            evidence_ids=ev,
            logo_path=logo_for_supplier(supplier_packets, supplier_id),
            hover_summary=f"{label}: company-level supplier context, not SKU-level allocation."
        ))

    # Minor ingredient nodes
    minor_ingredients = [
        ("NODE_ING_SOY_LECITHIN", "Soy Lecithin", "ING_SOY_LECITHIN", "Emulsifier input; supplier unknown."),
        ("NODE_ING_PGPR", "PGPR", "ING_PGPR", "Specialty emulsifier/flow modifier input; supplier unknown."),
        ("NODE_ING_NATURAL_FLAVOR", "Natural Flavor", "ING_NATURAL_FLAVOR", "Flavor input; exact composition and supplier unknown."),
    ]

    for node_id, label, ingredient_id, desc in minor_ingredients:
        nodes.append(make_node(
            node_id=node_id,
            node_type="processor",
            label=label,
            description=desc,
            product_or_material=label,
            relationship_status="unknown",
            confidence_level="low",
            evidence_ids=evidence_for_ingredient(ingredient_packets, ingredient_id),
            hover_summary=desc
        ))

    nodes.append(make_node(
        node_id="NODE_PACKAGING_STREAM",
        node_type="processor",
        label="Packaging / Wrapper Stream",
        description="Modeled packaging stream for wrapper, paperboard, and secondary packaging. Exact wrapper supplier is not confirmed.",
        product_or_material="Packaging / Wrapper",
        relationship_status="benchmark_only",
        confidence_level="medium",
        evidence_ids=evidence_for_ingredient(ingredient_packets, "ING_PACKAGING_WRAPPER"),
        hover_summary="Packaging input stream with benchmark-backed cost allocation."
    ))

    # Hershey process nodes
    process_nodes = [
        ("NODE_PROCESS_RECEIVING", "Raw Material Receiving", "Raw materials and packaging arrive at Hershey manufacturing."),
        ("NODE_PROCESS_STORAGE", "Ingredient Storage", "Inputs are stored before production; modeled general process node."),
        ("NODE_PROCESS_MIXING_REFINING", "Mixing / Refining", "Chocolate ingredients are mixed/refined in modeled manufacturing flow."),
        ("NODE_PROCESS_CONCHING", "Conching / Chocolate Processing", "Modeled chocolate processing step; not proprietary Hershey line data."),
        ("NODE_PROCESS_TEMPERING_MOLDING", "Tempering / Molding", "Chocolate is tempered and molded into bar form."),
        ("NODE_PROCESS_COOLING", "Cooling", "Molded chocolate cools and stabilizes."),
        ("NODE_PROCESS_WRAPPING", "Wrapping / Packaging", "Finished bar is wrapped and prepared for distribution."),
        ("NODE_PROCESS_FINISHED_GOODS", "Finished Goods", "Packaged bars enter finished-goods inventory before distribution."),
    ]

    for node_id, label, desc in process_nodes:
        nodes.append(make_node(
            node_id=node_id,
            node_type="manufacturing_process",
            label=label,
            description=desc,
            company_name="The Hershey Company",
            relationship_status="illustrative_only",
            confidence_level="medium",
            hover_summary=desc
        ))

    # Downstream nodes
    nodes.extend([
        make_node(
            node_id="NODE_WAREHOUSE_DISTRIBUTION_CENTER",
            node_type="warehouse",
            label="Warehouse / Distribution Center",
            description="Modeled storage/distribution node between Hershey finished goods and downstream movement.",
            relationship_status="benchmark_only",
            confidence_level="medium",
            hover_summary="Storage and distribution allocation node."
        ),
        make_node(
            node_id="NODE_COMMON_CARRIER_TRUCKING",
            node_type="distributor",
            label="Common Carrier / Trucking",
            description="Modeled outbound freight/trucking movement using public logistics benchmark context.",
            relationship_status="benchmark_only",
            confidence_level="medium",
            hover_summary="Outbound freight and diesel/trucking benchmark node."
        ),
        make_node(
            node_id="NODE_DISTRIBUTOR_MCLANE",
            node_type="distributor",
            label="McLane",
            description="Company-level downstream/distribution context. Exact route for this SKU is not confirmed.",
            company_name="McLane",
            product_or_material="Distribution",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_MCLANE_DISTRIBUTION"),
            logo_path=logo_for_supplier(supplier_packets, "SUP_MCLANE_DISTRIBUTION"),
            hover_summary="McLane downstream context; not an exact route claim."
        ),
    ])

    retailer_nodes = [
        ("NODE_RETAILER_WALMART", "Walmart"),
        ("NODE_RETAILER_TARGET", "Target"),
        ("NODE_RETAILER_CVS", "CVS"),
        ("NODE_RETAILER_WALGREENS", "Walgreens"),
    ]

    for node_id, label in retailer_nodes:
        nodes.append(make_node(
            node_id=node_id,
            node_type="retailer",
            label=label,
            description=f"{label} retail price evidence for the 1.55 oz bar was manually verified.",
            company_name=label,
            product_or_material="Retail shelf price",
            relationship_status="sku_level_confirmed",
            confidence_level="medium",
            hover_summary=f"{label}: verified retail price evidence."
        ))

    nodes.append(make_node(
        node_id="NODE_CONSUMER",
        node_type="consumer",
        label="Consumer",
        description="Final consumer purchase point in the modeled supply chain.",
        relationship_status="illustrative_only",
        confidence_level="medium",
        hover_summary="End consumer node."
    ))

    # Cost nodes
    cost_node_map = [
        ("NODE_COST_INGREDIENTS", "Ingredient Cost", "ingredient"),
        ("NODE_COST_PACKAGING", "Packaging Cost", "packaging"),
        ("NODE_COST_MANUFACTURING", "Manufacturing Conversion", "manufacturing_conversion"),
        ("NODE_COST_STORAGE", "Storage / Warehousing Cost", "storage"),
        ("NODE_COST_FREIGHT", "Freight Cost", "freight"),
        ("NODE_COST_RETAIL", "Observed Retail Price", "retail_price"),
        ("NODE_COST_RESIDUAL", "Residual Channel / Commercial Pool", "residual_channel_pool"),
    ]

    totals_by_type = cost_stack.get("totals_by_type", {})

    for node_id, label, cost_type in cost_node_map:
        if cost_type in totals_by_type:
            cost_data = totals_by_type[cost_type]
        elif cost_type == "retail_price":
            cost_data = {
                "low_cents_per_bar": retail.get("low_retail_price_cents"),
                "base_cents_per_bar": retail.get("base_retail_price_cents"),
                "high_cents_per_bar": retail.get("high_retail_price_cents"),
            }
        elif cost_type == "residual_channel_pool":
            cost_data = {
                "low_cents_per_bar": residual.get("low_cents_per_bar"),
                "base_cents_per_bar": residual.get("base_cents_per_bar"),
                "high_cents_per_bar": residual.get("high_cents_per_bar"),
            }
        else:
            cost_data = {}

        nodes.append(make_node(
            node_id=node_id,
            node_type="cost_bucket",
            label=label,
            description=f"{label} low/base/high cents per bar from the benchmark model.",
            product_or_material=cost_type,
            relationship_status="benchmark_only" if cost_type not in ["retail_price", "residual_channel_pool"] else "sku_level_confirmed",
            confidence_level="low" if cost_type == "residual_channel_pool" else "medium",
            hover_summary=f"{label}: base {round2(cost_data.get('base_cents_per_bar'))}¢ per bar.",
            extra={
                "low_cents_per_bar": cost_data.get("low_cents_per_bar"),
                "base_cents_per_bar": cost_data.get("base_cents_per_bar"),
                "high_cents_per_bar": cost_data.get("high_cents_per_bar"),
            }
        ))

    return nodes


def build_edges(
    supplier_packets: list[dict[str, Any]],
    ingredient_packets: list[dict[str, Any]],
    cost_stack: dict[str, Any],
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []

    # Upstream ingredient flows
    edges.extend([
        make_edge(
            edge_id="EDGE_SUGAR_ORIGIN_TO_ASR",
            from_node_id="NODE_ORIGIN_SUGAR",
            to_node_id="NODE_SUPPLIER_ASR",
            flow_type="ingredient",
            material_flow="Sugar cane/beet stream to sugar refiner/supplier context",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_ASR_SUGAR"),
            tooltip_text="Company-level sugar sourcing context; not SKU-level proof."
        ),
        make_edge(
            edge_id="EDGE_ASR_TO_HERSHEY_RECEIVING",
            from_node_id="NODE_SUPPLIER_ASR",
            to_node_id="NODE_PROCESS_RECEIVING",
            flow_type="ingredient",
            material_flow="Refined sugar input stream",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_ASR_SUGAR"),
            tooltip_text="ASR → Hershey is company-level supplier context only."
        ),
        make_edge(
            edge_id="EDGE_COCOA_ORIGIN_TO_BARRY",
            from_node_id="NODE_ORIGIN_COCOA",
            to_node_id="NODE_SUPPLIER_BARRY",
            flow_type="ingredient",
            material_flow="Cocoa/chocolate input stream",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE"),
            tooltip_text="Barry Callebaut company-level cocoa/chocolate context."
        ),
        make_edge(
            edge_id="EDGE_BARRY_TO_HERSHEY_RECEIVING",
            from_node_id="NODE_SUPPLIER_BARRY",
            to_node_id="NODE_PROCESS_RECEIVING",
            flow_type="ingredient",
            material_flow="Cocoa/chocolate/cocoa butter input stream",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE"),
            tooltip_text="Not exact SKU-level cocoa allocation."
        ),
        make_edge(
            edge_id="EDGE_DAIRY_ORIGIN_TO_LAND_O_LAKES",
            from_node_id="NODE_ORIGIN_DAIRY",
            to_node_id="NODE_SUPPLIER_LAND_O_LAKES",
            flow_type="ingredient",
            material_flow="Dairy farm/cooperative stream",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_LAND_O_LAKES_DAIRY"),
            tooltip_text="Land O'Lakes company-level dairy context."
        ),
        make_edge(
            edge_id="EDGE_LAND_O_LAKES_TO_HERSHEY_RECEIVING",
            from_node_id="NODE_SUPPLIER_LAND_O_LAKES",
            to_node_id="NODE_PROCESS_RECEIVING",
            flow_type="ingredient",
            material_flow="Milk / skim milk / milk fat input stream",
            relationship_status="company_level_confirmed",
            confidence_level="medium",
            evidence_ids=evidence_for_supplier(supplier_packets, "SUP_LAND_O_LAKES_DAIRY"),
            tooltip_text="Not exact SKU-level dairy allocation."
        ),
    ])

    minor_edges = [
        ("EDGE_SOY_LECITHIN_TO_HERSHEY", "NODE_ING_SOY_LECITHIN", "Soy lecithin emulsifier input", "ING_SOY_LECITHIN"),
        ("EDGE_PGPR_TO_HERSHEY", "NODE_ING_PGPR", "PGPR emulsifier/flow modifier input", "ING_PGPR"),
        ("EDGE_NATURAL_FLAVOR_TO_HERSHEY", "NODE_ING_NATURAL_FLAVOR", "Natural flavor input", "ING_NATURAL_FLAVOR"),
        ("EDGE_PACKAGING_TO_HERSHEY", "NODE_PACKAGING_STREAM", "Wrapper and packaging input", "ING_PACKAGING_WRAPPER"),
    ]

    for edge_id, from_node, flow, ingredient_id in minor_edges:
        edges.append(make_edge(
            edge_id=edge_id,
            from_node_id=from_node,
            to_node_id="NODE_PROCESS_RECEIVING",
            flow_type="ingredient" if "PACKAGING" not in edge_id else "packaging",
            material_flow=flow,
            relationship_status="unknown" if "PACKAGING" not in edge_id else "benchmark_only",
            confidence_level="low" if "PACKAGING" not in edge_id else "medium",
            evidence_ids=evidence_for_ingredient(ingredient_packets, ingredient_id),
            tooltip_text="Supplier unknown or benchmark-only; no exact supplier claim."
        ))

    # Manufacturing process flow
    process_sequence = [
        ("NODE_PROCESS_RECEIVING", "NODE_PROCESS_STORAGE"),
        ("NODE_PROCESS_STORAGE", "NODE_PROCESS_MIXING_REFINING"),
        ("NODE_PROCESS_MIXING_REFINING", "NODE_PROCESS_CONCHING"),
        ("NODE_PROCESS_CONCHING", "NODE_PROCESS_TEMPERING_MOLDING"),
        ("NODE_PROCESS_TEMPERING_MOLDING", "NODE_PROCESS_COOLING"),
        ("NODE_PROCESS_COOLING", "NODE_PROCESS_WRAPPING"),
        ("NODE_PROCESS_WRAPPING", "NODE_PROCESS_FINISHED_GOODS"),
        ("NODE_PROCESS_FINISHED_GOODS", "NODE_PRODUCT_HERSHEY_155OZ"),
    ]

    for idx, (src, dst) in enumerate(process_sequence, start=1):
        edges.append(make_edge(
            edge_id=f"EDGE_PROCESS_{idx:02d}",
            from_node_id=src,
            to_node_id=dst,
            flow_type="finished_goods" if dst == "NODE_PRODUCT_HERSHEY_155OZ" else "ingredient",
            material_flow="Modeled manufacturing process flow",
            relationship_status="illustrative_only",
            confidence_level="medium",
            animation_type="moving_particles",
            tooltip_text="General chocolate manufacturing process model, not proprietary Hershey line data."
        ))

    # Downstream flow
    downstream = [
        ("NODE_PRODUCT_HERSHEY_155OZ", "NODE_WAREHOUSE_DISTRIBUTION_CENTER", "finished_goods", "Finished bars to warehouse/DC", "benchmark_only"),
        ("NODE_WAREHOUSE_DISTRIBUTION_CENTER", "NODE_COMMON_CARRIER_TRUCKING", "logistics", "Outbound movement", "benchmark_only"),
        ("NODE_COMMON_CARRIER_TRUCKING", "NODE_DISTRIBUTOR_MCLANE", "logistics", "Distribution / downstream channel movement", "company_level_confirmed"),
    ]

    for idx, (src, dst, flow_type, material_flow, status) in enumerate(downstream, start=1):
        ev = evidence_for_supplier(supplier_packets, "SUP_MCLANE_DISTRIBUTION") if dst == "NODE_DISTRIBUTOR_MCLANE" else []
        edges.append(make_edge(
            edge_id=f"EDGE_DOWNSTREAM_{idx:02d}",
            from_node_id=src,
            to_node_id=dst,
            flow_type=flow_type,
            material_flow=material_flow,
            relationship_status=status,
            confidence_level="medium",
            evidence_ids=ev,
            animation_type="truck" if flow_type == "logistics" else "moving_particles",
            tooltip_text="Downstream logistics are modeled; exact SKU route is not confirmed."
        ))

    retailers = [
        ("NODE_RETAILER_WALMART", "Walmart"),
        ("NODE_RETAILER_TARGET", "Target"),
        ("NODE_RETAILER_CVS", "CVS"),
        ("NODE_RETAILER_WALGREENS", "Walgreens"),
    ]

    for retailer_node, label in retailers:
        edges.append(make_edge(
            edge_id=f"EDGE_MCLANE_TO_{label.upper()}",
            from_node_id="NODE_DISTRIBUTOR_MCLANE",
            to_node_id=retailer_node,
            flow_type="logistics",
            material_flow=f"Modeled downstream path to {label}",
            relationship_status="illustrative_only",
            confidence_level="medium",
            animation_type="truck",
            tooltip_text=f"{label} has verified retail price evidence; exact distribution path is modeled."
        ))
        edges.append(make_edge(
            edge_id=f"EDGE_{label.upper()}_TO_CONSUMER",
            from_node_id=retailer_node,
            to_node_id="NODE_CONSUMER",
            flow_type="finished_goods",
            material_flow="Retail sale to consumer",
            relationship_status="sku_level_confirmed",
            confidence_level="medium",
            animation_type="moving_particles",
            tooltip_text=f"{label} price evidence supports retail sale context."
        ))

    # Cost edges
    cost_edges = [
        ("NODE_COST_INGREDIENTS", "NODE_PRODUCT_HERSHEY_155OZ", "ingredient cost contribution"),
        ("NODE_COST_PACKAGING", "NODE_PRODUCT_HERSHEY_155OZ", "packaging cost contribution"),
        ("NODE_COST_MANUFACTURING", "NODE_PRODUCT_HERSHEY_155OZ", "manufacturing conversion allocation"),
        ("NODE_COST_STORAGE", "NODE_PRODUCT_HERSHEY_155OZ", "storage cost allocation"),
        ("NODE_COST_FREIGHT", "NODE_PRODUCT_HERSHEY_155OZ", "freight cost allocation"),
        ("NODE_COST_RETAIL", "NODE_PRODUCT_HERSHEY_155OZ", "verified retail shelf price"),
        ("NODE_COST_RESIDUAL", "NODE_PRODUCT_HERSHEY_155OZ", "retail minus physical cost residual"),
    ]

    for idx, (src, dst, flow) in enumerate(cost_edges, start=1):
        edges.append(make_edge(
            edge_id=f"EDGE_COST_{idx:02d}",
            from_node_id=src,
            to_node_id=dst,
            flow_type="cost",
            material_flow=flow,
            relationship_status="benchmark_only" if "RETAIL" not in src else "sku_level_confirmed",
            confidence_level="low" if "RESIDUAL" in src else "medium",
            animation_type="cost_pulse",
            tooltip_text="Cost model value is benchmark/verified-retail based, not Hershey internal cost."
        ))

    return edges


def write_summary_csv(path: Path, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
    rows = []

    for node in nodes:
        rows.append({
            "record_type": "node",
            "id": node["node_id"],
            "label": node["label"],
            "type_or_flow": node["node_type"],
            "relationship_status": node["relationship_status"],
            "confidence_level": node["confidence_level"],
            "display_allowed": node["display_allowed"],
            "from_node": "",
            "to_node": "",
            "evidence_count": len(node.get("evidence_ids", [])),
            "summary": node.get("hover_summary", ""),
        })

    for edge in edges:
        rows.append({
            "record_type": "edge",
            "id": edge["edge_id"],
            "label": edge["material_flow"],
            "type_or_flow": edge["flow_type"],
            "relationship_status": edge["relationship_status"],
            "confidence_level": edge["confidence_level"],
            "display_allowed": edge["display_allowed"],
            "from_node": edge["from_node_id"],
            "to_node": edge["to_node_id"],
            "evidence_count": len(edge.get("evidence_ids", [])),
            "summary": edge.get("tooltip_text", ""),
        })

    fieldnames = [
        "record_type",
        "id",
        "label",
        "type_or_flow",
        "relationship_status",
        "confidence_level",
        "display_allowed",
        "from_node",
        "to_node",
        "evidence_count",
        "summary",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda item: item[0]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    supplier_path = root / "artifacts" / "05_supplier_blobs" / "supplier_packets.json"
    ingredient_costed_path = root / "artifacts" / "07_cost_model_blobs" / "ingredient_packets_costed.json"
    ingredient_fallback_path = root / "artifacts" / "06_ingredient_blobs" / "ingredient_packets.json"
    cost_records_path = root / "artifacts" / "07_cost_model_blobs" / "cost_model_records_with_retail.json"
    cost_stack_path = root / "artifacts" / "07_cost_model_blobs" / "cost_stack_with_retail_summary.json"

    out_dir = root / "artifacts" / "08_node_edge_architecture"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    supplier_packets = read_json(supplier_path)

    if ingredient_costed_path.exists():
        ingredient_packets = read_json(ingredient_costed_path)
    else:
        ingredient_packets = read_json(ingredient_fallback_path)

    cost_records = read_json(cost_records_path)
    cost_stack = read_json(cost_stack_path)

    nodes = build_nodes(supplier_packets, ingredient_packets, cost_records, cost_stack)
    edges = build_edges(supplier_packets, ingredient_packets, cost_stack)

    graph = {
        "graph_version": "v1_node_edge_architecture",
        "project": "Hershey Supply Chain AI",
        "unit": "one HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "safe_display_rules": [
            "Supplier relationships are company-level unless explicitly marked SKU-level.",
            "Minor ingredient suppliers are unknown unless direct evidence proves otherwise.",
            "Manufacturing process nodes are general modeled process nodes, not proprietary Hershey line claims.",
            "Cost values are public-evidence benchmark estimates, not Hershey internal SKU costs.",
            "Residual channel/commercial pool is not profit."
        ],
        "nodes": nodes,
        "edges": edges,
    }

    nodes_path = out_dir / "nodes.json"
    edges_path = out_dir / "edges.json"
    graph_path = out_dir / "supply_chain_graph.json"
    summary_csv = out_dir / "node_edge_summary.csv"

    write_json(nodes_path, nodes)
    write_json(edges_path, edges)
    write_json(graph_path, graph)
    write_summary_csv(summary_csv, nodes, edges)

    report = {
        "run_name": "step14_node_edge_architecture",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "nodes_created": len(nodes),
        "edges_created": len(edges),
        "node_type_counts": count_by(nodes, "node_type"),
        "edge_flow_type_counts": count_by(edges, "flow_type"),
        "node_relationship_counts": count_by(nodes, "relationship_status"),
        "edge_relationship_counts": count_by(edges, "relationship_status"),
        "nodes_json": str(nodes_path).replace("\\", "/"),
        "edges_json": str(edges_path).replace("\\", "/"),
        "supply_chain_graph_json": str(graph_path).replace("\\", "/"),
        "node_edge_summary_csv": str(summary_csv).replace("\\", "/"),
        "next_step": "Step 15: build display-ready artifacts for frontend and evidence panels."
    }

    report_path = report_dir / "step14_node_edge_architecture_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 14 NODE / EDGE ARCHITECTURE COMPLETE")
    print("-----------------------------------------")
    print(f"Nodes created: {len(nodes)}")
    print(f"Edges created: {len(edges)}")
    print(f"Node types: {report['node_type_counts']}")
    print(f"Edge flow types: {report['edge_flow_type_counts']}")
    print("")
    print(f"Graph JSON:  {graph_path}")
    print(f"Summary CSV: {summary_csv}")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()