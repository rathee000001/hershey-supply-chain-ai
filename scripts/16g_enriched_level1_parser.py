from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


CLAIM_PATTERNS = {
    "supplier_relationship": [
        "supplier", "supplies", "supply", "sourcing", "sourced", "partner", "partnership",
        "agreement", "collaboration", "strategic partner", "relationship"
    ],
    "ingredient_confirmation": [
        "ingredients", "ingredient", "contains", "milk chocolate", "sugar", "milk",
        "chocolate", "cocoa", "lecithin", "pgpr", "natural flavor"
    ],
    "cost_or_price_benchmark": [
        "price", "cost", "market", "benchmark", "average", "per pound", "per kg",
        "per metric ton", "cents", "dollars", "$", "ppi", "diesel", "trucking"
    ],
    "retail_price": [
        "walmart", "target", "cvs", "walgreens", "retail", "price", "1.55 oz", "43 g"
    ],
    "logistics_distribution": [
        "distribution", "warehouse", "warehousing", "truck", "trucking", "freight",
        "carrier", "mclane", "transportation"
    ],
    "sustainability_context": [
        "sustainability", "sustainable", "responsible sourcing", "farmers", "farms",
        "environmental", "traceability", "ethical"
    ],
    "manufacturing_or_process": [
        "manufacturing", "processing", "process", "refining", "conching", "tempering",
        "packaging", "wrapper", "production"
    ],
}


SAFE_LIMITS = {
    "supplier_relationship": (
        "Supplier relationship candidates must remain company-level unless the text directly confirms the exact 1.55 oz SKU."
    ),
    "ingredient_confirmation": (
        "Ingredient candidates can confirm label/product ingredients, but not supplier allocation unless direct evidence says so."
    ),
    "cost_or_price_benchmark": (
        "Cost/price candidates are benchmark evidence, not Hershey internal invoice or SKU cost."
    ),
    "retail_price": (
        "Retail candidates may support observed shelf price only for the captured retailer/date/page context."
    ),
    "logistics_distribution": (
        "Logistics candidates support modeled downstream structure, not exact route confirmation unless directly stated."
    ),
    "sustainability_context": (
        "Sustainability context supports sourcing program discussion, not exact cost or SKU-level supply."
    ),
    "manufacturing_or_process": (
        "Manufacturing/process candidates are general modeled process evidence, not proprietary Hershey line data."
    ),
}


ENTITY_ALIASES = {
    "hershey": ["hershey", "hershey's", "the hershey company"],
    "asr": ["asr", "asr group", "american sugar refining", "domino"],
    "barry_callebaut": ["barry callebaut"],
    "land_olakes": ["land o'lakes", "land o’lakes", "land olakes"],
    "mclane": ["mclane"],
    "walmart": ["walmart"],
    "target": ["target"],
    "cvs": ["cvs"],
    "walgreens": ["walgreens"],
    "usda": ["usda"],
    "fda": ["fda"],
    "icco": ["icco"],
    "bls": ["bls"],
    "eia": ["eia"],
}

INGREDIENT_ALIASES = {
    "sugar": ["sugar", "cane", "beet"],
    "cocoa_chocolate": ["cocoa", "chocolate", "cocoa mass", "cocoa butter"],
    "milk_dairy": ["milk", "dairy", "skim milk", "milk fat", "butterfat"],
    "soy_lecithin": ["soy lecithin", "lecithin"],
    "pgpr": ["pgpr", "polyglycerol polyricinoleate"],
    "natural_flavor": ["natural flavor", "flavor"],
    "packaging": ["packaging", "wrapper", "paper", "pulp", "paperboard"],
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def clean_text(text: Any) -> str:
    text = str(text or "")
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def find_entities(text: str) -> list[str]:
    hits = []
    lower = text.lower()

    for entity, aliases in ENTITY_ALIASES.items():
        if any(alias.lower() in lower for alias in aliases):
            hits.append(entity)

    return sorted(set(hits))


def find_ingredients(text: str) -> list[str]:
    hits = []
    lower = text.lower()

    for ingredient, aliases in INGREDIENT_ALIASES.items():
        if any(alias.lower() in lower for alias in aliases):
            hits.append(ingredient)

    return sorted(set(hits))


def classify_claim_roles(text: str) -> list[str]:
    roles = []

    for role, terms in CLAIM_PATTERNS.items():
        if contains_any(text, terms):
            roles.append(role)

    return roles or ["general_context"]


def infer_claim_strength(text: str, roles: list[str], source_type: str, usefulness_class: str) -> str:
    lower = text.lower()

    strong_direct_terms = [
        "hershey", "supplier", "partner", "agreement", "ingredients", "nutrition facts",
        "1.55 oz", "43 g", "walmart", "target", "cvs", "walgreens"
    ]

    if "retail_price" in roles and any(x in lower for x in ["walmart", "target", "cvs", "walgreens"]):
        return "direct_visual_or_page_evidence"

    if "ingredient_confirmation" in roles and any(x in lower for x in ["ingredients", "nutrition facts", "1.55 oz", "43 g"]):
        return "direct_product_or_label_evidence"

    if "supplier_relationship" in roles and lower.count("hershey") >= 1 and any(x in lower for x in ["supplier", "partner", "sourcing"]):
        return "company_level_relationship_evidence"

    if "cost_or_price_benchmark" in roles:
        return "benchmark_context_evidence"

    if source_type == "visual_ocr" and usefulness_class.startswith("high"):
        return "visual_high_relevance_context"

    if any(term in lower for term in strong_direct_terms):
        return "medium_context_evidence"

    return "background_context"


def safe_scope_for_claim(roles: list[str], claim_strength: str) -> str:
    if claim_strength == "direct_product_or_label_evidence":
        return "sku_or_label_level"
    if claim_strength == "direct_visual_or_page_evidence":
        return "retail_page_level"
    if claim_strength == "company_level_relationship_evidence":
        return "company_level_only"
    if claim_strength == "benchmark_context_evidence":
        return "benchmark_only"
    if "logistics_distribution" in roles:
        return "modeled_route_context"
    return "context_only"


def build_candidate_claim(chunk: dict[str, Any], source_context: str, rank: int | None = None, test_id: str = "") -> dict[str, Any]:
    text = clean_text(chunk.get("text") or chunk.get("text_preview"))
    roles = classify_claim_roles(text)
    entities = find_entities(text)
    ingredients = find_ingredients(text)
    source_type = chunk.get("source_type", "")
    usefulness = chunk.get("usefulness_class", "")

    claim_strength = infer_claim_strength(text, roles, source_type, usefulness)
    safe_scope = safe_scope_for_claim(roles, claim_strength)

    claim_label = " / ".join(roles[:3])
    if entities or ingredients:
        claim_label = f"{claim_label}: {', '.join(entities + ingredients)}"

    return {
        "candidate_claim_id": f"CAND_{test_id or 'MEMORY'}_{chunk.get('vector_chunk_id') or chunk.get('unified_chunk_id') or rank}",
        "source_context": source_context,
        "rag_test_id": test_id,
        "rag_rank": rank,
        "doc_id": chunk.get("doc_id", ""),
        "file_name": chunk.get("file_name", ""),
        "packet": chunk.get("packet", ""),
        "source_type": source_type,
        "usefulness_class": usefulness,
        "claim_roles": roles,
        "claim_label": claim_label,
        "entities": entities,
        "ingredients": ingredients,
        "claim_strength": claim_strength,
        "safe_scope": safe_scope,
        "safe_limit": " | ".join(SAFE_LIMITS.get(role, "") for role in roles if role in SAFE_LIMITS),
        "text_preview": text[:1600],
        "needs_strict_audit": True,
        "frontend_display_allowed_now": False,
    }


def build_document_profiles(unified_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for chunk in unified_chunks:
        grouped[chunk.get("doc_id", "UNKNOWN")].append(chunk)

    profiles = []

    for doc_id, chunks in sorted(grouped.items()):
        all_text = "\n".join(clean_text(c.get("text", ""))[:3000] for c in chunks)
        entities = find_entities(all_text)
        ingredients = find_ingredients(all_text)

        role_counter = Counter()
        source_counter = Counter()
        packet_counter = Counter()
        usefulness_counter = Counter()

        for chunk in chunks:
            roles = classify_claim_roles(clean_text(chunk.get("text", "")))
            role_counter.update(roles)
            source_counter.update([chunk.get("source_type", "unknown")])
            packet_counter.update([chunk.get("packet", "unknown")])
            usefulness_counter.update([chunk.get("usefulness_class", "unknown")])

        file_names = sorted(set(c.get("file_name", "") for c in chunks if c.get("file_name")))

        profiles.append({
            "doc_id": doc_id,
            "primary_file_name": file_names[0] if file_names else "",
            "file_names": file_names,
            "chunk_count": len(chunks),
            "total_text_length": sum(int(c.get("text_length", len(clean_text(c.get("text", ""))))) for c in chunks),
            "source_type_counts": dict(sorted(source_counter.items())),
            "packet_counts": dict(sorted(packet_counter.items())),
            "usefulness_counts": dict(sorted(usefulness_counter.items())),
            "claim_role_counts": dict(sorted(role_counter.items())),
            "entities_detected": entities,
            "ingredients_detected": ingredients,
            "has_visual_ocr": "visual_ocr" in source_counter,
            "has_text_or_table": "text_or_table" in source_counter,
            "level1_priority": assign_level1_priority(role_counter, usefulness_counter, entities, ingredients),
        })

    return profiles


def assign_level1_priority(
    role_counter: Counter,
    usefulness_counter: Counter,
    entities: list[str],
    ingredients: list[str],
) -> str:
    high_useful = (
        usefulness_counter.get("high_sku_evidence", 0)
        + usefulness_counter.get("high_supplier_or_ingredient_evidence", 0)
        + usefulness_counter.get("high_cost_or_price_evidence", 0)
    )

    if high_useful > 0:
        return "high"

    if role_counter.get("supplier_relationship", 0) > 0 and entities and ingredients:
        return "high"

    if role_counter.get("cost_or_price_benchmark", 0) > 0:
        return "medium_high"

    if entities or ingredients:
        return "medium"

    return "low"


def build_rag_question_bundles(rag_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bundles = []

    for item in rag_results:
        test_id = item.get("test_id", "")
        retrieved = item.get("retrieved_chunks", [])
        evaluation = item.get("evaluation", {})

        claims = []
        for retrieved_chunk in retrieved:
            claims.append(
                build_candidate_claim(
                    chunk=retrieved_chunk,
                    source_context="rag_retrieval_result",
                    rank=retrieved_chunk.get("rank"),
                    test_id=test_id,
                )
            )

        bundles.append({
            "bundle_id": f"BUNDLE_{test_id}",
            "test_id": test_id,
            "question": item.get("question", ""),
            "purpose": item.get("purpose", ""),
            "retrieval_status": evaluation.get("status", ""),
            "top_score": evaluation.get("top_score", ""),
            "top_packets": evaluation.get("top_packets", []),
            "top_files": evaluation.get("top_files", []),
            "candidate_claim_count": len(claims),
            "candidate_claims": claims,
            "safe_usage_rule": "Level 1 enriched bundles are research support only. Claims must pass enriched strict audit before display.",
        })

    return bundles


def build_memory_candidate_claims(unified_chunks: list[dict[str, Any]], max_claims: int = 900) -> list[dict[str, Any]]:
    candidates = []

    priority_classes = {
        "high_sku_evidence",
        "high_supplier_or_ingredient_evidence",
        "high_cost_or_price_evidence",
        "medium_context_evidence",
    }

    for chunk in unified_chunks:
        usefulness = chunk.get("usefulness_class", "")
        text = clean_text(chunk.get("text", ""))

        if usefulness not in priority_classes and len(text) < 500:
            continue

        roles = classify_claim_roles(text)
        if roles == ["general_context"]:
            continue

        entities = find_entities(text)
        ingredients = find_ingredients(text)

        if not entities and not ingredients and "cost_or_price_benchmark" not in roles:
            continue

        candidate = build_candidate_claim(
            chunk={
                **chunk,
                "vector_chunk_id": chunk.get("unified_chunk_id"),
                "text_preview": text[:1600],
            },
            source_context="unified_memory_scan",
            rank=None,
            test_id="MEMORY",
        )
        candidates.append(candidate)

    # Sort useful/direct candidates first.
    strength_order = {
        "direct_product_or_label_evidence": 0,
        "direct_visual_or_page_evidence": 1,
        "company_level_relationship_evidence": 2,
        "benchmark_context_evidence": 3,
        "visual_high_relevance_context": 4,
        "medium_context_evidence": 5,
        "background_context": 6,
    }

    candidates = sorted(
        candidates,
        key=lambda x: (
            strength_order.get(x.get("claim_strength", ""), 99),
            x.get("packet", ""),
            x.get("file_name", ""),
        )
    )

    return candidates[:max_claims]


def write_summary_csv(path: Path, document_profiles: list[dict[str, Any]], bundles: list[dict[str, Any]], claims: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for profile in document_profiles:
        rows.append({
            "record_type": "document_profile",
            "id": profile.get("doc_id", ""),
            "label": profile.get("primary_file_name", ""),
            "packet": "; ".join(profile.get("packet_counts", {}).keys()),
            "priority_or_status": profile.get("level1_priority", ""),
            "claim_strength": "",
            "safe_scope": "",
            "claim_roles": "; ".join(profile.get("claim_role_counts", {}).keys()),
            "entities": "; ".join(profile.get("entities_detected", [])),
            "ingredients": "; ".join(profile.get("ingredients_detected", [])),
            "summary": f"chunks={profile.get('chunk_count')} text={profile.get('total_text_length')}",
        })

    for bundle in bundles:
        rows.append({
            "record_type": "rag_bundle",
            "id": bundle.get("bundle_id", ""),
            "label": bundle.get("question", ""),
            "packet": "; ".join(bundle.get("top_packets", [])),
            "priority_or_status": bundle.get("retrieval_status", ""),
            "claim_strength": "",
            "safe_scope": "",
            "claim_roles": "",
            "entities": "",
            "ingredients": "",
            "summary": f"candidate_claims={bundle.get('candidate_claim_count')}",
        })

    for claim in claims:
        rows.append({
            "record_type": "candidate_claim",
            "id": claim.get("candidate_claim_id", ""),
            "label": claim.get("claim_label", ""),
            "packet": claim.get("packet", ""),
            "priority_or_status": claim.get("source_context", ""),
            "claim_strength": claim.get("claim_strength", ""),
            "safe_scope": claim.get("safe_scope", ""),
            "claim_roles": "; ".join(claim.get("claim_roles", [])),
            "entities": "; ".join(claim.get("entities", [])),
            "ingredients": "; ".join(claim.get("ingredients", [])),
            "summary": claim.get("text_preview", "")[:300],
        })

    fieldnames = [
        "record_type",
        "id",
        "label",
        "packet",
        "priority_or_status",
        "claim_strength",
        "safe_scope",
        "claim_roles",
        "entities",
        "ingredients",
        "summary",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    unified_path = root / "artifacts" / "11_unified_memory" / "unified_chunks.jsonl"
    rag_results_path = root / "artifacts" / "13_rag_tests" / "rag_test_results.json"

    out_dir = root / "artifacts" / "14_enriched_level1"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not unified_path.exists():
        raise FileNotFoundError(f"Missing unified memory: {unified_path}")
    if not rag_results_path.exists():
        raise FileNotFoundError(f"Missing RAG test results: {rag_results_path}")

    unified_chunks = read_jsonl(unified_path)
    rag_results = read_json(rag_results_path)

    document_profiles = build_document_profiles(unified_chunks)
    rag_bundles = build_rag_question_bundles(rag_results)
    memory_claims = build_memory_candidate_claims(unified_chunks)

    rag_claims = []
    for bundle in rag_bundles:
        rag_claims.extend(bundle.get("candidate_claims", []))

    all_claims = rag_claims + memory_claims

    document_profiles_path = out_dir / "enriched_document_profiles.json"
    rag_bundles_path = out_dir / "enriched_rag_question_bundles.json"
    candidate_claims_path = out_dir / "enriched_candidate_claims.json"
    summary_csv_path = out_dir / "enriched_level1_summary.csv"

    write_json(document_profiles_path, document_profiles)
    write_json(rag_bundles_path, rag_bundles)
    write_json(candidate_claims_path, all_claims)
    write_summary_csv(summary_csv_path, document_profiles, rag_bundles, all_claims)

    claim_strength_counts = Counter(claim.get("claim_strength", "unknown") for claim in all_claims)
    safe_scope_counts = Counter(claim.get("safe_scope", "unknown") for claim in all_claims)
    role_counts = Counter(role for claim in all_claims for role in claim.get("claim_roles", []))
    priority_counts = Counter(profile.get("level1_priority", "unknown") for profile in document_profiles)

    report = {
        "run_name": "step16g_enriched_level1_parser",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "unified_chunks_seen": len(unified_chunks),
        "rag_question_bundles_created": len(rag_bundles),
        "document_profiles_created": len(document_profiles),
        "candidate_claims_created": len(all_claims),
        "rag_candidate_claims": len(rag_claims),
        "memory_scan_candidate_claims": len(memory_claims),
        "claim_strength_counts": dict(sorted(claim_strength_counts.items())),
        "safe_scope_counts": dict(sorted(safe_scope_counts.items())),
        "claim_role_counts": dict(sorted(role_counts.items())),
        "document_priority_counts": dict(sorted(priority_counts.items())),
        "enriched_document_profiles_json": str(document_profiles_path).replace("\\", "/"),
        "enriched_rag_question_bundles_json": str(rag_bundles_path).replace("\\", "/"),
        "enriched_candidate_claims_json": str(candidate_claims_path).replace("\\", "/"),
        "enriched_level1_summary_csv": str(summary_csv_path).replace("\\", "/"),
        "next_step": "Step 16H: build enriched evidence blobs from candidate claims, then Step 16I strict audit.",
    }

    report_path = report_dir / "step16g_enriched_level1_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16G ENRICHED LEVEL 1 PARSER COMPLETE")
    print("-----------------------------------------")
    print(f"Unified chunks seen:        {len(unified_chunks)}")
    print(f"Document profiles created:  {len(document_profiles)}")
    print(f"RAG bundles created:        {len(rag_bundles)}")
    print(f"Candidate claims created:   {len(all_claims)}")
    print(f"  - RAG candidate claims:   {len(rag_claims)}")
    print(f"  - Memory scan claims:     {len(memory_claims)}")
    print("")
    print(f"Document profiles: {document_profiles_path}")
    print(f"RAG bundles:       {rag_bundles_path}")
    print(f"Candidate claims:  {candidate_claims_path}")
    print(f"Summary CSV:       {summary_csv_path}")
    print(f"Report JSON:       {report_path}")
    print("")


if __name__ == "__main__":
    main()