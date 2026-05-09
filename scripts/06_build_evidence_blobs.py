from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


CONFIRMED_COMPANY_LEVEL_SUPPLIER_RULES = [
    {
        "packet": "sugar",
        "company": "American Sugar Refining / ASR",
        "ingredient": "Sugar",
        "safe_wording": "ASR is treated as a confirmed Hershey company-level sugar sourcing partner when supported by Hershey/ASR evidence. Exact 1.55 oz SKU allocation is not publicly confirmed.",
        "unsafe_wording": "ASR supplies the exact sugar in every 1.55 oz Hershey bar."
    },
    {
        "packet": "cocoa_chocolate_cocoa_butter",
        "company": "Barry Callebaut",
        "ingredient": "Cocoa / Chocolate / Cocoa Butter",
        "safe_wording": "Barry Callebaut is treated as a confirmed Hershey company-level cocoa/chocolate supply partner when supported by supply-agreement evidence. Exact 1.55 oz SKU allocation is not publicly confirmed.",
        "unsafe_wording": "Barry Callebaut supplies the exact cocoa or cocoa butter in every 1.55 oz Hershey bar."
    },
    {
        "packet": "dairy_milk_skim_milk_milk_fat",
        "company": "Land O'Lakes",
        "ingredient": "Milk / Skim Milk / Milk Fat",
        "safe_wording": "Land O'Lakes is treated as a confirmed Hershey company-level dairy supplier/partner when supported by Hershey/Land O'Lakes evidence. Exact 1.55 oz SKU allocation is not publicly confirmed.",
        "unsafe_wording": "Land O'Lakes supplies the exact milk, skim milk, or milk fat in every 1.55 oz Hershey bar."
    },
    {
        "packet": "logistics_distribution",
        "company": "McLane",
        "ingredient": "Distribution / Downstream Channel",
        "safe_wording": "McLane is treated as a confirmed Hershey company-level downstream/customer/distribution-related entity when supported by Hershey/McLane evidence. Exact route for this 1.55 oz bar is not publicly confirmed.",
        "unsafe_wording": "McLane distributes every 1.55 oz Hershey bar to every retailer."
    },
]


UNKNOWN_SUPPLIER_INGREDIENTS = {
    "soy_lecithin": {
        "ingredient": "Soy Lecithin",
        "safe_wording": "Soy lecithin is listed as an ingredient/function input, but the supplier is not publicly confirmed for the 1.55 oz bar.",
        "unsafe_wording": "A specific soy lecithin company supplies Hershey's soy lecithin for this exact bar."
    },
    "pgpr": {
        "ingredient": "PGPR",
        "safe_wording": "PGPR is listed as an ingredient/function input, but the supplier is not publicly confirmed for the 1.55 oz bar.",
        "unsafe_wording": "A specific PGPR company supplies Hershey's PGPR for this exact bar."
    },
    "natural_flavor": {
        "ingredient": "Natural Flavor",
        "safe_wording": "Natural flavor is listed as an ingredient/function input, but its exact composition and supplier are not publicly confirmed for the 1.55 oz bar.",
        "unsafe_wording": "A specific flavor company supplies the natural flavor for this exact bar."
    },
    "packaging_wrapper": {
        "ingredient": "Packaging / Wrapper",
        "safe_wording": "Packaging and wrapper materials are modeled as an input stream. Exact wrapper supplier for the 1.55 oz bar is not publicly confirmed unless later evidence proves it.",
        "unsafe_wording": "A specific packaging company supplies the exact wrapper for every 1.55 oz Hershey bar."
    },
}


CATEGORY_BY_PACKET = {
    "product_sku_1_55oz": "product_sku",
    "sugar": "ingredient",
    "cocoa_chocolate_cocoa_butter": "ingredient",
    "dairy_milk_skim_milk_milk_fat": "ingredient",
    "soy_lecithin": "ingredient",
    "pgpr": "ingredient",
    "natural_flavor": "ingredient",
    "packaging_wrapper": "packaging",
    "logistics_distribution": "logistics",
    "retail_price_evidence": "retail",
    "hershey_company": "raw_material",
    "brand_logo_assets": "visual_asset",
    "reference_only": "reference_only",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean_text(value: str) -> str:
    value = value or ""
    value = value.replace("\x00", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def make_evidence_id(packet: str, doc_index: int, item_index: int) -> str:
    packet_code = re.sub(r"[^A-Za-z0-9]+", "_", packet).strip("_").upper()
    return f"EV_{packet_code}_{doc_index:04d}_{item_index:03d}"


def infer_category(parsed: dict[str, Any], fallback: str = "process") -> str:
    packet = parsed.get("packet", "unknown")
    return CATEGORY_BY_PACKET.get(packet, fallback)


def infer_evidence_type(parsed: dict[str, Any], category: str) -> str:
    packet = parsed.get("packet", "")
    file_name = parsed.get("file_name", "").lower()
    summary = parsed.get("summary", "").lower()
    source_owner = parsed.get("source_owner", "").lower()

    text = " ".join([packet.lower(), file_name, summary, source_owner, category.lower()])

    if packet == "reference_only" or category == "reference_only":
        return "reference_only"

    if category == "visual_asset":
        return "reference_only"

    if any(x in text for x in ["benchmark", "usda", "bls", "eia", "icco", "ppi", "market", "futures", "price index"]):
        return "benchmark_proxy"

    if any(x in text for x in ["fda", "efsa", "gras", "cfr", "regulatory", "food additive"]):
        return "direct"

    if any(x in text for x in ["hershey", "barry", "asr", "land o", "mclane", "walmart", "target", "cvs", "walgreens"]):
        return "direct"

    return "benchmark_proxy"


def infer_relationship_strength(
    parsed: dict[str, Any],
    category: str,
    evidence_text: str,
    related_company: str,
) -> str:
    packet = parsed.get("packet", "")
    lower = f"{parsed.get('file_name', '')} {parsed.get('summary', '')} {evidence_text}".lower()

    if packet == "reference_only" or category == "visual_asset":
        return "illustrative_only"

    if category == "retail":
        return "sku_level_confirmed"

    if any(x in lower for x in ["usda", "bls", "eia", "icco", "ppi", "benchmark", "market", "futures"]):
        return "benchmark_only"

    for rule in CONFIRMED_COMPANY_LEVEL_SUPPLIER_RULES:
        if packet == rule["packet"] and rule["company"].lower() in related_company.lower():
            return "company_level_confirmed"

    if packet in UNKNOWN_SUPPLIER_INGREDIENTS:
        return "unknown"

    if "supplier" in lower or "partner" in lower or "agreement" in lower or "customer" in lower:
        return "probable"

    return "unknown"


def infer_confidence(
    parsed: dict[str, Any],
    evidence_type: str,
    relationship_strength: str,
    evidence_text: str,
) -> str:
    if evidence_type == "reference_only":
        return "low"

    if relationship_strength in ["sku_level_confirmed", "company_level_confirmed"]:
        if len(evidence_text) > 60:
            return "high"
        return "medium"

    if relationship_strength == "benchmark_only":
        return "medium"

    if relationship_strength == "probable":
        return "medium"

    return "low"


def needs_human_review(parsed: dict[str, Any], evidence_type: str, relationship_strength: str) -> bool:
    meta = parsed.get("local_parser_meta", {})
    if meta.get("requires_future_ai_or_visual_review"):
        return True

    if evidence_type == "reference_only":
        return True

    if relationship_strength in ["probable", "unknown", "illustrative_only"]:
        return True

    return False


def find_related_company(parsed: dict[str, Any], evidence_text: str) -> str:
    candidates = []

    for entity in parsed.get("extracted_entities", []):
        if entity.get("entity_type") == "company_or_institution":
            candidates.append(entity.get("entity_name", ""))

    lower = evidence_text.lower()

    priority = [
        "The Hershey Company",
        "American Sugar Refining / ASR",
        "Barry Callebaut",
        "Land O'Lakes",
        "McLane",
        "Walmart",
        "Target",
        "CVS",
        "Walgreens",
        "USDA",
        "FDA",
        "EFSA",
        "ICCO",
        "BLS",
        "EIA",
        "FEMA",
    ]

    for company in priority:
        if company.lower().replace("'", "") in lower.replace("'", ""):
            return company

    for candidate in candidates:
        if candidate:
            return candidate

    return parsed.get("source_owner", "")


def find_related_ingredient(parsed: dict[str, Any], evidence_text: str) -> str:
    packet = parsed.get("packet", "")

    packet_default = {
        "sugar": "Sugar",
        "cocoa_chocolate_cocoa_butter": "Cocoa / Chocolate / Cocoa Butter",
        "dairy_milk_skim_milk_milk_fat": "Milk / Skim Milk / Milk Fat",
        "soy_lecithin": "Soy Lecithin",
        "pgpr": "PGPR",
        "natural_flavor": "Natural Flavor",
        "packaging_wrapper": "Packaging / Wrapper",
    }

    lower = evidence_text.lower()

    ingredient_terms = [
        ("Cocoa Butter", ["cocoa butter"]),
        ("Cocoa / Chocolate", ["cocoa", "chocolate"]),
        ("Milk / Dairy", ["milk", "skim milk", "milk fat", "dairy", "butterfat"]),
        ("Sugar", ["sugar", "cane", "beet"]),
        ("Soy Lecithin", ["soy lecithin", "lecithin"]),
        ("PGPR", ["pgpr", "polyglycerol"]),
        ("Natural Flavor", ["natural flavor", "flavor"]),
        ("Packaging / Wrapper", ["packaging", "wrapper", "paperboard", "pulp", "paper"]),
    ]

    for name, patterns in ingredient_terms:
        if any(p in lower for p in patterns):
            return name

    return packet_default.get(packet, "")


def safe_wording_for_blob(
    parsed: dict[str, Any],
    claim: str,
    relationship_strength: str,
    related_company: str,
    related_ingredient: str,
) -> tuple[str, str]:
    packet = parsed.get("packet", "")

    for rule in CONFIRMED_COMPANY_LEVEL_SUPPLIER_RULES:
        if packet == rule["packet"] and rule["company"].lower() in related_company.lower():
            return rule["safe_wording"], rule["unsafe_wording"]

    if packet in UNKNOWN_SUPPLIER_INGREDIENTS:
        item = UNKNOWN_SUPPLIER_INGREDIENTS[packet]
        return item["safe_wording"], item["unsafe_wording"]

    if relationship_strength == "sku_level_confirmed" and packet == "retail_price_evidence":
        return (
            "This retailer evidence is treated as SKU-level price evidence for the 1.55 oz product page/screenshot, pending final visual audit.",
            "This retail price proves Hershey's manufacturing cost or supplier invoice cost."
        )

    if relationship_strength == "benchmark_only":
        return (
            f"This source can support benchmark or market context for {related_ingredient or parsed.get('packet')}, not Hershey's exact invoice cost.",
            "This benchmark equals Hershey's actual SKU-level cost."
        )

    if relationship_strength == "illustrative_only":
        return (
            "This source may be used only as a visual/reference asset and not as factual supplier or cost evidence.",
            "This visual/reference file proves a supplier, route, or cost."
        )

    return (
        claim,
        "Do not expand this claim beyond the evidence text or imply SKU-level confirmation without explicit support."
    )


def build_blob(
    evidence_id: str,
    parsed: dict[str, Any],
    claim: str,
    evidence_text: str,
    category: str,
    page_or_section: str = "",
    related_cost_bucket: str = "",
) -> dict[str, Any]:
    related_company = find_related_company(parsed, evidence_text)
    related_ingredient = find_related_ingredient(parsed, evidence_text)

    evidence_type = infer_evidence_type(parsed, category)
    relationship_strength = infer_relationship_strength(parsed, category, evidence_text, related_company)
    confidence = infer_confidence(parsed, evidence_type, relationship_strength, evidence_text)
    human_review = needs_human_review(parsed, evidence_type, relationship_strength)

    safe_wording, unsafe_wording = safe_wording_for_blob(
        parsed=parsed,
        claim=claim,
        relationship_strength=relationship_strength,
        related_company=related_company,
        related_ingredient=related_ingredient,
    )

    return {
        "evidence_id": evidence_id,
        "doc_id": parsed.get("doc_id", ""),
        "source_file": parsed.get("file_name", ""),
        "claim": clean_text(claim),
        "evidence_text": clean_text(evidence_text)[:1500],
        "page_or_section": page_or_section,
        "packet": parsed.get("packet", ""),
        "category": category,
        "evidence_type": evidence_type,
        "relationship_strength": relationship_strength,
        "related_company": related_company,
        "related_ingredient": related_ingredient,
        "related_supply_chain_stage": infer_stage_from_category(category, parsed.get("packet", "")),
        "related_cost_bucket": related_cost_bucket,
        "confidence_level": confidence,
        "display_allowed": False,
        "reason_display_allowed": "Display must wait for Level 2 audit.",
        "requires_human_review": human_review,
        "safe_website_wording": safe_wording,
        "unsafe_wording_to_avoid": unsafe_wording,
        "local_builder_meta": {
            "created_by": "step09_evidence_blob_builder",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "source_usefulness_score": parsed.get("usefulness_score"),
            "source_requires_future_ai_or_visual_review": parsed.get("local_parser_meta", {}).get("requires_future_ai_or_visual_review"),
        },
    }


def infer_stage_from_category(category: str, packet: str) -> str:
    if category == "product_sku":
        return "product definition"
    if category == "supplier":
        return "supplier relationship"
    if category == "ingredient":
        return "ingredient input"
    if category == "packaging":
        return "packaging input"
    if category == "logistics":
        return "warehousing / logistics / distribution"
    if category == "retail":
        return "retail price evidence"
    if category == "cost":
        return "cost benchmark / cost model"
    if category == "regulatory":
        return "regulatory definition"
    if category == "process":
        return "process explanation"
    if category == "visual_asset":
        return "visual asset"
    if category == "reference_only":
        return "reference only"

    return packet


def build_document_summary_blob(parsed: dict[str, Any], evidence_id: str) -> dict[str, Any]:
    packet = parsed.get("packet", "")
    category = infer_category(parsed)

    if parsed.get("document_type") == "image_or_logo":
        category = "visual_asset"

    if parsed.get("packet") == "reference_only":
        category = "reference_only"

    claim = f"Source document available for packet: {packet}."
    evidence_text = parsed.get("summary", "")

    return build_blob(
        evidence_id=evidence_id,
        parsed=parsed,
        claim=claim,
        evidence_text=evidence_text,
        category=category,
        page_or_section="document summary",
    )


def blobs_from_relationships(parsed: dict[str, Any], doc_index: int, start_item_index: int) -> list[dict[str, Any]]:
    blobs = []
    item_index = start_item_index

    for rel in parsed.get("explicit_relationships", []):
        item_index += 1
        from_entity = rel.get("from_entity", "")
        to_entity = rel.get("to_entity", "")
        relationship = rel.get("relationship", "")
        evidence_text = rel.get("evidence_text", "")

        claim = f"{from_entity} has relationship language connected to {to_entity}: {relationship}."

        blob = build_blob(
            evidence_id=make_evidence_id(parsed.get("packet", "unknown"), doc_index, item_index),
            parsed=parsed,
            claim=claim,
            evidence_text=evidence_text,
            category="supplier",
            page_or_section=rel.get("page_or_location", ""),
        )
        blobs.append(blob)

    return blobs


def blobs_from_cost_mentions(parsed: dict[str, Any], doc_index: int, start_item_index: int) -> list[dict[str, Any]]:
    blobs = []
    item_index = start_item_index

    for cost in parsed.get("cost_bucket_mentions", []):
        item_index += 1
        bucket = cost.get("cost_bucket", "")
        evidence_text = cost.get("evidence_text", "")

        claim = f"Source contains cost, price, market, benchmark, or index language for cost bucket: {bucket}."

        blob = build_blob(
            evidence_id=make_evidence_id(parsed.get("packet", "unknown"), doc_index, item_index),
            parsed=parsed,
            claim=claim,
            evidence_text=evidence_text,
            category="cost",
            page_or_section=cost.get("page_or_location", ""),
            related_cost_bucket=bucket,
        )
        blobs.append(blob)

    return blobs


def build_packet_classification_blob(parsed: dict[str, Any], evidence_id: str) -> dict[str, Any] | None:
    packet = parsed.get("packet", "")

    for rule in CONFIRMED_COMPANY_LEVEL_SUPPLIER_RULES:
        if packet == rule["packet"]:
            text = " ".join([
                parsed.get("summary", ""),
                " ".join([r.get("evidence_text", "") for r in parsed.get("explicit_relationships", [])]),
            ])
            if rule["company"].lower().split("/")[0].strip() in text.lower() or rule["company"].lower() in text.lower():
                return build_blob(
                    evidence_id=evidence_id,
                    parsed=parsed,
                    claim=f"{rule['company']} is candidate company-level evidence for the {rule['ingredient']} stream.",
                    evidence_text=text[:1500],
                    category="supplier",
                    page_or_section="packet classification",
                )

    if packet in UNKNOWN_SUPPLIER_INGREDIENTS:
        item = UNKNOWN_SUPPLIER_INGREDIENTS[packet]
        return build_blob(
            evidence_id=evidence_id,
            parsed=parsed,
            claim=f"{item['ingredient']} packet is ingredient/function evidence with supplier currently unknown.",
            evidence_text=parsed.get("summary", ""),
            category="ingredient",
            page_or_section="packet classification",
        )

    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    parsed_path = root / "artifacts" / "02_document_artifacts" / "level1_parsed" / "_all_level1_parsed_documents.json"
    out_dir = root / "artifacts" / "03_evidence_blobs"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not parsed_path.exists():
        raise FileNotFoundError(f"Missing Level 1 parsed documents: {parsed_path}")

    parsed_docs = read_json(parsed_path)

    evidence_blobs = []
    summary_rows = []

    for doc_index, parsed_doc in enumerate(parsed_docs, start=1):
        packet = parsed_doc.get("packet", "unknown")

        # 1. Always create one document-summary evidence blob.
        summary_blob = build_document_summary_blob(
            parsed=parsed_doc,
            evidence_id=make_evidence_id(packet, doc_index, 1),
        )
        evidence_blobs.append(summary_blob)

        # 2. Relationship blobs.
        relationship_blobs = blobs_from_relationships(parsed_doc, doc_index, 100)
        evidence_blobs.extend(relationship_blobs)

        # 3. Cost / benchmark blobs.
        cost_blobs = blobs_from_cost_mentions(parsed_doc, doc_index, 300)
        evidence_blobs.extend(cost_blobs)

        # 4. Packet classification blob if applicable.
        classification_blob = build_packet_classification_blob(
            parsed=parsed_doc,
            evidence_id=make_evidence_id(packet, doc_index, 900),
        )
        if classification_blob:
            evidence_blobs.append(classification_blob)

    for blob in evidence_blobs:
        summary_rows.append({
            "evidence_id": blob["evidence_id"],
            "doc_id": blob["doc_id"],
            "source_file": blob["source_file"],
            "packet": blob["packet"],
            "category": blob["category"],
            "evidence_type": blob["evidence_type"],
            "relationship_strength": blob["relationship_strength"],
            "related_company": blob["related_company"],
            "related_ingredient": blob["related_ingredient"],
            "related_cost_bucket": blob["related_cost_bucket"],
            "confidence_level": blob["confidence_level"],
            "display_allowed": blob["display_allowed"],
            "requires_human_review": blob["requires_human_review"],
            "claim": blob["claim"],
        })

    evidence_json_path = out_dir / "evidence_blobs.json"
    evidence_csv_path = out_dir / "evidence_blobs_summary.csv"

    write_json(evidence_json_path, evidence_blobs)

    with evidence_csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "evidence_id",
            "doc_id",
            "source_file",
            "packet",
            "category",
            "evidence_type",
            "relationship_strength",
            "related_company",
            "related_ingredient",
            "related_cost_bucket",
            "confidence_level",
            "display_allowed",
            "requires_human_review",
            "claim",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    packet_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    relationship_counts: dict[str, int] = {}

    for blob in evidence_blobs:
        packet_counts[blob["packet"]] = packet_counts.get(blob["packet"], 0) + 1
        type_counts[blob["evidence_type"]] = type_counts.get(blob["evidence_type"], 0) + 1
        relationship_counts[blob["relationship_strength"]] = relationship_counts.get(blob["relationship_strength"], 0) + 1

    report = {
        "run_name": "step09_build_evidence_blobs",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "level1_parsed_documents_seen": len(parsed_docs),
        "evidence_blobs_created": len(evidence_blobs),
        "packet_counts": packet_counts,
        "evidence_type_counts": type_counts,
        "relationship_strength_counts": relationship_counts,
        "display_allowed_count": sum(1 for b in evidence_blobs if b["display_allowed"]),
        "requires_human_review_count": sum(1 for b in evidence_blobs if b["requires_human_review"]),
        "evidence_blobs_json": str(evidence_json_path).replace("\\", "/"),
        "evidence_blobs_summary_csv": str(evidence_csv_path).replace("\\", "/"),
        "next_step": "Step 10: Level 2 evidence audit and display-safety classification.",
    }

    report_path = report_dir / "step09_evidence_blob_builder_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 09 EVIDENCE BLOB BUILDER COMPLETE")
    print("--------------------------------------")
    print(f"Level 1 parsed docs seen: {len(parsed_docs)}")
    print(f"Evidence blobs created: {len(evidence_blobs)}")
    print(f"Requires human review: {report['requires_human_review_count']}")
    print(f"Display allowed before audit: {report['display_allowed_count']}")
    print("")
    print(f"Evidence JSON: {evidence_json_path}")
    print(f"Summary CSV:   {evidence_csv_path}")
    print(f"Report JSON:   {report_path}")
    print("")


if __name__ == "__main__":
    main()