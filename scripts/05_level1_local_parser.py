from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


COMPANY_PATTERNS = {
    "The Hershey Company": ["the hershey company", "hershey"],
    "American Sugar Refining / ASR": ["american sugar refining", "asr group", "asr"],
    "Barry Callebaut": ["barry callebaut"],
    "Land O'Lakes": ["land o'lakes", "land o lakes"],
    "McLane": ["mclane"],
    "Walmart": ["walmart"],
    "Target": ["target"],
    "CVS": ["cvs"],
    "Walgreens": ["walgreens"],
    "USDA": ["usda"],
    "USDA ERS": ["economic research service", "ers"],
    "USDA AMS": ["agricultural marketing service", "ams"],
    "FDA": ["food and drug administration", "fda"],
    "EFSA": ["efsa", "european food safety authority"],
    "BLS": ["bureau of labor statistics", "bls"],
    "EIA": ["energy information administration", "eia"],
    "ICCO": ["international cocoa organization", "icco"],
    "FEMA": ["flavor and extract manufacturers association", "fema"],
    "EPA": ["environmental protection agency", "epa"],
}

INGREDIENT_PATTERNS = {
    "Sugar": ["sugar", "cane sugar", "beet sugar"],
    "Chocolate": ["chocolate", "milk chocolate"],
    "Cocoa": ["cocoa", "cocoa beans", "cocoa products"],
    "Cocoa Butter": ["cocoa butter"],
    "Milk": ["milk"],
    "Skim Milk": ["skim milk", "nonfat milk", "nonfat dry milk"],
    "Milk Fat": ["milk fat", "butterfat", "butter fat"],
    "Soy Lecithin": ["soy lecithin", "lecithin"],
    "PGPR": ["pgpr", "polyglycerol polyricinoleate"],
    "Natural Flavor": ["natural flavor", "natural flavors"],
    "Packaging": ["packaging", "wrapper", "paperboard", "pulp", "paper", "corrugated"],
}

STAGE_PATTERNS = {
    "ingredient sourcing": ["sourcing", "sourced", "supplier", "suppliers", "partner"],
    "processing": ["processing", "refining", "separation", "milling", "extraction"],
    "manufacturing": ["manufacturing", "plant", "factory", "production", "molding", "wrapping"],
    "packaging": ["packaging", "wrapper", "paperboard", "carton", "corrugated"],
    "warehousing": ["warehouse", "warehousing", "storage", "distribution center"],
    "freight": ["freight", "trucking", "truck", "diesel", "transport", "common carrier"],
    "retail": ["retail", "retailer", "store", "price", "pickup", "delivery"],
    "regulatory": ["fda", "efsa", "gras", "cfr", "food additive"],
}

RELATIONSHIP_WORDS = [
    "supplier",
    "supplies",
    "sourcing",
    "sourced",
    "partner",
    "partnership",
    "agreement",
    "supply agreement",
    "customer",
    "distributor",
    "distribution",
]

COST_WORDS = [
    "price",
    "prices",
    "cost",
    "costs",
    "benchmark",
    "market",
    "ppi",
    "index",
    "futures",
    "per lb",
    "per pound",
    "cents",
    "$",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_level1_inputs(input_dir: Path) -> list[Path]:
    return sorted([
        p for p in input_dir.glob("DOC_*.level1_input.json")
        if p.is_file()
    ])


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sentence_split(text: str) -> list[str]:
    text = clean_text(text)
    rough = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in rough if len(s.strip()) > 20]


def find_entities(text: str) -> list[dict[str, str]]:
    lower = text.lower()
    entities = []

    for company, patterns in COMPANY_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                entities.append({
                    "entity_name": company,
                    "entity_type": "company_or_institution",
                    "context": f"Matched term: {pattern}",
                })
                break

    for ingredient, patterns in INGREDIENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                entities.append({
                    "entity_name": ingredient,
                    "entity_type": "ingredient_or_input",
                    "context": f"Matched term: {pattern}",
                })
                break

    for stage, patterns in STAGE_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                entities.append({
                    "entity_name": stage,
                    "entity_type": "supply_chain_stage",
                    "context": f"Matched term: {pattern}",
                })
                break

    seen = set()
    unique = []
    for item in entities:
        key = (item["entity_name"], item["entity_type"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


def find_prices(text: str) -> list[dict[str, str]]:
    patterns = [
        r"\$[\d,]+(?:\.\d+)?",
        r"\b\d+(?:\.\d+)?\s?¢",
        r"\b\d+(?:\.\d+)?\s?cents\b",
        r"\b\d+(?:\.\d+)?\s?(?:per lb|/lb|per pound)\b",
        r"\b\d+(?:\.\d+)?\s?(?:dollars per pound|cents per pound)\b",
    ]

    results = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 120)
            context = clean_text(text[start:end])
            results.append({
                "metric_name": "price_or_cost_mention",
                "metric_value": match.group(0),
                "unit": "",
                "page_or_location": "",
                "context": context,
            })

    return results[:50]


def find_units_and_metrics(text: str) -> list[dict[str, str]]:
    patterns = [
        (r"\b\d+(?:\.\d+)?\s?(?:g|gram|grams)\b", "weight"),
        (r"\b\d+(?:\.\d+)?\s?(?:oz|ounce|ounces)\b", "weight"),
        (r"\b\d+(?:\.\d+)?\s?(?:lb|lbs|pound|pounds)\b", "weight"),
        (r"\b\d+(?:\.\d+)?\s?%\b", "percentage"),
        (r"\b(?:19|20)\d{2}\b", "year"),
    ]

    results = []
    for pattern, metric_name in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            results.append({
                "metric_name": metric_name,
                "metric_value": match.group(0),
                "unit": "",
                "page_or_location": "",
                "context": clean_text(text[start:end]),
            })

    return results[:80]


def find_relevant_sections(chunks: list[dict[str, Any]]) -> list[dict[str, str]]:
    sections = []

    for chunk in chunks:
        text = chunk.get("text", "")
        lower = text.lower()
        score = int(chunk.get("signal_score", 0))

        if score < 5 and not any(word in lower for word in RELATIONSHIP_WORDS + COST_WORDS):
            continue

        sections.append({
            "section_title": f"Selected chunk {chunk.get('chunk_number')}",
            "page_or_location": chunk.get("page_or_section_hint", ""),
            "why_relevant": (
                "Contains supply-chain, ingredient, supplier, cost, regulatory, or benchmark signals."
            ),
        })

    return sections[:12]


def find_explicit_relationships(text: str) -> list[dict[str, str]]:
    relationships = []
    sentences = sentence_split(text)

    for sentence in sentences:
        lower = sentence.lower()

        if not any(word in lower for word in RELATIONSHIP_WORDS):
            continue

        mentioned_companies = []
        for company, patterns in COMPANY_PATTERNS.items():
            if any(pattern in lower for pattern in patterns):
                mentioned_companies.append(company)

        mentioned_ingredients = []
        for ingredient, patterns in INGREDIENT_PATTERNS.items():
            if any(pattern in lower for pattern in patterns):
                mentioned_ingredients.append(ingredient)

        if len(mentioned_companies) >= 2:
            relationships.append({
                "from_entity": mentioned_companies[0],
                "to_entity": mentioned_companies[1],
                "relationship": "relationship language detected",
                "evidence_text": sentence[:700],
                "page_or_location": "",
            })
        elif mentioned_companies and mentioned_ingredients:
            relationships.append({
                "from_entity": mentioned_companies[0],
                "to_entity": mentioned_ingredients[0],
                "relationship": "company-to-ingredient/stage relationship language detected",
                "evidence_text": sentence[:700],
                "page_or_location": "",
            })

    return relationships[:20]


def find_cost_bucket_mentions(text: str) -> list[dict[str, str]]:
    sentences = sentence_split(text)
    mentions = []

    for sentence in sentences:
        lower = sentence.lower()
        if any(word in lower for word in COST_WORDS):
            mentions.append({
                "cost_bucket": infer_cost_bucket(sentence),
                "evidence_text": sentence[:700],
                "page_or_location": "",
            })

    return mentions[:40]


def infer_cost_bucket(sentence: str) -> str:
    lower = sentence.lower()

    if any(x in lower for x in ["sugar", "cane", "beet"]):
        return "sugar"
    if any(x in lower for x in ["cocoa", "chocolate", "cocoa butter"]):
        return "cocoa_chocolate_cocoa_butter"
    if any(x in lower for x in ["milk", "butter", "nonfat", "dairy"]):
        return "dairy"
    if any(x in lower for x in ["soy", "lecithin"]):
        return "soy_lecithin"
    if "pgpr" in lower:
        return "pgpr"
    if any(x in lower for x in ["natural flavor", "flavor"]):
        return "natural_flavor"
    if any(x in lower for x in ["packaging", "paper", "wrapper", "carton"]):
        return "packaging"
    if any(x in lower for x in ["freight", "truck", "diesel", "transport"]):
        return "freight"
    if any(x in lower for x in ["warehouse", "storage"]):
        return "warehousing"
    if any(x in lower for x in ["retail", "walmart", "target", "cvs", "walgreens"]):
        return "retail_price"

    return "general_cost_or_market_context"


def build_summary(doc_input: dict[str, Any], combined_text: str) -> str:
    metadata = doc_input.get("doc_metadata", {})
    file_name = metadata.get("file_name", "")
    packet = metadata.get("packet", "")
    evidence_role = metadata.get("evidence_role", "")
    ai_mode = doc_input.get("ai_input_mode", "")

    entities = find_entities(combined_text)
    entity_names = [x["entity_name"] for x in entities[:8]]

    if combined_text.strip():
        return (
            f"Local Level 1 parse for {file_name}. Packet: {packet}. "
            f"Evidence role: {evidence_role}. Input mode: {ai_mode}. "
            f"Detected entities/stages include: {', '.join(entity_names) if entity_names else 'none detected'}."
        )

    return (
        f"Local Level 1 parse for {file_name}. Packet: {packet}. "
        f"No extracted text available; likely image/logo or visual-priority source."
    )


def get_combined_selected_text(doc_input: dict[str, Any]) -> str:
    parts = []
    for chunk in doc_input.get("selected_chunks", []):
        chunk_id = chunk.get("chunk_id", "")
        location = chunk.get("page_or_section_hint", "")
        text = chunk.get("text", "")
        parts.append(f"\n--- {chunk_id} {location} ---\n{text}")
    return clean_text("\n".join(parts))


def detect_usefulness(doc_input: dict[str, Any], text: str) -> tuple[bool, float, list[str]]:
    metadata = doc_input.get("doc_metadata", {})
    role = metadata.get("evidence_role", "")
    packet = metadata.get("packet", "")
    ai_mode = doc_input.get("ai_input_mode", "")

    score = 0
    notes = []

    if role in ["direct_company_evidence", "supplier_relationship_context", "retail_price_evidence"]:
        score += 4
    if role in ["benchmark_proxy", "process_or_function_context", "regulatory_definition"]:
        score += 3
    if role == "visual_asset":
        score += 1
        notes.append("Visual asset useful for display but not factual proof by itself.")
    if role == "reference_only":
        score -= 4
        notes.append("Reference-only file must not be used as factual evidence.")

    if packet == "product_sku_1_55oz":
        score += 4
    if packet in ["sugar", "cocoa_chocolate_cocoa_butter", "dairy_milk_skim_milk_milk_fat"]:
        score += 3
    if packet in ["retail_price_evidence", "logistics_distribution"]:
        score += 3

    if len(text) > 500:
        score += 2
    elif len(text) > 50:
        score += 1
    else:
        notes.append("Extracted text is weak; visual/page image review may be needed.")

    if ai_mode in ["visual_priority", "visual_asset_only"]:
        notes.append("This document should be reviewed with page images or manual inspection before final claims.")

    usefulness = max(0, min(10, score))
    useful = usefulness >= 2 and role != "reference_only"

    return useful, float(usefulness), notes


def build_parsed_document(doc_input: dict[str, Any]) -> dict[str, Any]:
    metadata = doc_input.get("doc_metadata", {})
    text = get_combined_selected_text(doc_input)

    useful, usefulness_score, confidence_notes = detect_usefulness(doc_input, text)

    entities = find_entities(text)
    price_metrics = find_prices(text)
    unit_metrics = find_units_and_metrics(text)

    parsed = {
        "doc_id": metadata.get("doc_id", ""),
        "file_name": metadata.get("file_name", ""),
        "source_owner": infer_source_owner(metadata.get("file_name", ""), metadata.get("packet", "")),
        "document_title": infer_document_title(metadata.get("file_name", "")),
        "packet": metadata.get("packet", ""),
        "document_type": metadata.get("document_type", ""),
        "summary": build_summary(doc_input, text),
        "useful_for_project": useful,
        "usefulness_score": usefulness_score,
        "relevant_sections": find_relevant_sections(doc_input.get("selected_chunks", [])),
        "extracted_entities": entities,
        "extracted_metrics": unit_metrics[:50],
        "extracted_prices": price_metrics,
        "extracted_dates": extract_dates(unit_metrics),
        "extracted_locations": [],
        "explicit_relationships": find_explicit_relationships(text),
        "cost_bucket_mentions": find_cost_bucket_mentions(text),
        "confidence_notes": confidence_notes,
        "excluded_content": [],
        "level1_status": "complete",
        "local_parser_meta": {
            "parser_name": "step08_level1_local_parser",
            "parser_type": "deterministic_local_baseline",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "ai_input_mode": doc_input.get("ai_input_mode"),
            "priority_score": doc_input.get("priority_score"),
            "selected_chunk_count": len(doc_input.get("selected_chunks", [])),
            "requires_future_ai_or_visual_review": doc_input.get("ai_input_mode") in [
                "visual_priority",
                "visual_asset_only",
                "text_plus_page_images",
            ],
        },
    }

    if metadata.get("evidence_role") == "reference_only":
        parsed["excluded_content"].append(
            "Reference-only file. Do not use as evidence for supplier, cost, or product claims."
        )

    if metadata.get("evidence_role") == "visual_asset":
        parsed["excluded_content"].append(
            "Logo/image is a display asset. It does not prove supplier relationship."
        )

    return parsed


def extract_dates(metrics: list[dict[str, str]]) -> list[str]:
    years = []
    for metric in metrics:
        if metric.get("metric_name") == "year":
            years.append(metric.get("metric_value", ""))
    return list(dict.fromkeys([y for y in years if y]))[:30]


def infer_source_owner(file_name: str, packet: str) -> str:
    lower = file_name.lower()

    if "hershey" in lower:
        return "The Hershey Company"
    if "asr" in lower or "domino" in lower:
        return "American Sugar Refining / ASR"
    if "barry" in lower:
        return "Barry Callebaut"
    if "land_o_lakes" in lower:
        return "Land O'Lakes"
    if "mclane" in lower:
        return "McLane"
    if "walmart" in lower:
        return "Walmart"
    if "target" in lower:
        return "Target"
    if "cvs" in lower:
        return "CVS"
    if "walgreens" in lower:
        return "Walgreens"
    if "usda" in lower:
        return "USDA"
    if "fda" in lower:
        return "FDA"
    if "efsa" in lower:
        return "EFSA"
    if "bls" in lower or "ppi" in lower:
        return "BLS"
    if "eia" in lower:
        return "EIA"
    if "icco" in lower:
        return "ICCO"
    if "fema" in lower:
        return "FEMA"

    return packet


def infer_document_title(file_name: str) -> str:
    title = Path(file_name).stem
    title = title.replace("_", " ").replace("-", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title.title()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    input_dir = root / "artifacts" / "02_document_artifacts" / "level1_inputs"
    output_dir = root / "artifacts" / "02_document_artifacts" / "level1_parsed"
    report_dir = root / "artifacts" / "10_run_reports"

    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    input_paths = load_level1_inputs(input_dir)

    parsed_docs = []
    summary_rows = []

    for path in input_paths:
        doc_input = read_json(path)
        parsed = build_parsed_document(doc_input)

        out_path = output_dir / f"{parsed['doc_id']}.level1_parsed.json"
        write_json(out_path, parsed)

        parsed_docs.append(parsed)

        summary_rows.append({
            "doc_id": parsed["doc_id"],
            "file_name": parsed["file_name"],
            "packet": parsed["packet"],
            "document_type": parsed["document_type"],
            "source_owner": parsed["source_owner"],
            "useful_for_project": parsed["useful_for_project"],
            "usefulness_score": parsed["usefulness_score"],
            "entity_count": len(parsed["extracted_entities"]),
            "price_count": len(parsed["extracted_prices"]),
            "relationship_count": len(parsed["explicit_relationships"]),
            "cost_bucket_count": len(parsed["cost_bucket_mentions"]),
            "requires_future_ai_or_visual_review": parsed["local_parser_meta"]["requires_future_ai_or_visual_review"],
            "parsed_path": str(out_path).replace("\\", "/"),
        })

    write_json(output_dir / "_all_level1_parsed_documents.json", parsed_docs)

    summary_csv = output_dir / "_level1_parsed_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "doc_id",
            "file_name",
            "packet",
            "document_type",
            "source_owner",
            "useful_for_project",
            "usefulness_score",
            "entity_count",
            "price_count",
            "relationship_count",
            "cost_bucket_count",
            "requires_future_ai_or_visual_review",
            "parsed_path",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    useful_count = sum(1 for row in summary_rows if row["useful_for_project"])
    visual_review_count = sum(1 for row in summary_rows if row["requires_future_ai_or_visual_review"])

    report = {
        "run_name": "step08_level1_local_parser",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "level1_inputs_seen": len(input_paths),
        "parsed_documents_created": len(parsed_docs),
        "useful_documents": useful_count,
        "future_ai_or_visual_review_documents": visual_review_count,
        "level1_parsed_folder": str(output_dir).replace("\\", "/"),
        "all_level1_parsed_json": str(output_dir / "_all_level1_parsed_documents.json").replace("\\", "/"),
        "summary_csv": str(summary_csv).replace("\\", "/"),
        "next_step": "Step 09: build claim-level evidence blobs from Level 1 parsed documents."
    }

    report_path = report_dir / "step08_level1_local_parser_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 08 LEVEL 1 LOCAL PARSER COMPLETE")
    print("-------------------------------------")
    print(f"Inputs seen: {len(input_paths)}")
    print(f"Parsed documents created: {len(parsed_docs)}")
    print(f"Useful documents: {useful_count}")
    print(f"Future AI/visual review docs: {visual_review_count}")
    print("")
    print(f"Summary CSV: {summary_csv}")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()