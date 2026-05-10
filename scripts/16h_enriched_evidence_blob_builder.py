from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


DIRECT_STRENGTHS = {
    "direct_product_or_label_evidence",
    "direct_visual_or_page_evidence",
    "company_level_relationship_evidence",
}

BENCHMARK_STRENGTHS = {
    "benchmark_context_evidence",
}

LOWER_VALUE_STRENGTHS = {
    "visual_high_relevance_context",
    "medium_context_evidence",
    "background_context",
}


ROLE_TO_EVIDENCE_TYPE = {
    "supplier_relationship": "supplier_relationship_evidence",
    "ingredient_confirmation": "ingredient_or_label_evidence",
    "cost_or_price_benchmark": "benchmark_cost_or_price_evidence",
    "retail_price": "retail_price_evidence",
    "logistics_distribution": "logistics_distribution_evidence",
    "sustainability_context": "sustainability_context_evidence",
    "manufacturing_or_process": "manufacturing_process_evidence",
    "general_context": "general_context_evidence",
}


SAFE_DISPLAY_RULES = {
    "company_level_only": (
        "Use only as company-level relationship evidence. Do not claim exact 1.55 oz SKU allocation."
    ),
    "sku_or_label_level": (
        "Use for product label, wrapper, ingredient, or SKU identity evidence. Do not infer supplier allocation."
    ),
    "retail_page_level": (
        "Use for observed retailer page or price evidence only. Price may vary by store, date, and promotion."
    ),
    "benchmark_only": (
        "Use only as public benchmark or market context. Do not present as Hershey internal invoice or SKU cost."
    ),
    "modeled_route_context": (
        "Use only as modeled logistics/distribution context. Do not claim exact route unless direct evidence says so."
    ),
    "context_only": (
        "Use only as background context. Do not use as a direct website claim without audit approval."
    ),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean_text(text: Any) -> str:
    text = str(text or "")
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def infer_primary_role(claim_roles: list[str]) -> str:
    priority = [
        "retail_price",
        "ingredient_confirmation",
        "supplier_relationship",
        "cost_or_price_benchmark",
        "logistics_distribution",
        "manufacturing_or_process",
        "sustainability_context",
        "general_context",
    ]

    for role in priority:
        if role in claim_roles:
            return role

    return claim_roles[0] if claim_roles else "general_context"


def infer_evidence_type(claim_roles: list[str]) -> str:
    primary = infer_primary_role(claim_roles)
    return ROLE_TO_EVIDENCE_TYPE.get(primary, "general_context_evidence")


def infer_relationship_strength(claim_strength: str, safe_scope: str, claim_roles: list[str]) -> str:
    if claim_strength == "direct_product_or_label_evidence":
        return "direct_sku_or_label_evidence"

    if claim_strength == "direct_visual_or_page_evidence":
        return "direct_retail_or_visual_page_evidence"

    if claim_strength == "company_level_relationship_evidence":
        return "company_level_confirmed"

    if claim_strength == "benchmark_context_evidence":
        return "benchmark_proxy"

    if safe_scope == "modeled_route_context":
        return "modeled_context"

    if claim_strength == "visual_high_relevance_context":
        return "visual_context"

    if claim_strength == "medium_context_evidence":
        return "contextual_support"

    return "background_or_low_support"


def infer_confidence_level(claim_strength: str, safe_scope: str, source_type: str, text: str) -> str:
    text_len = len(clean_text(text))

    if claim_strength in {"direct_product_or_label_evidence", "direct_visual_or_page_evidence"} and text_len >= 100:
        return "medium_high"

    if claim_strength == "company_level_relationship_evidence":
        return "medium"

    if claim_strength == "benchmark_context_evidence":
        return "medium"

    if source_type == "visual_ocr" and text_len >= 300:
        return "medium_low"

    if claim_strength == "medium_context_evidence":
        return "low_medium"

    return "low"


def infer_audit_priority(claim_strength: str, safe_scope: str, claim_roles: list[str], source_context: str) -> str:
    if claim_strength in DIRECT_STRENGTHS:
        return "high"

    if claim_strength in BENCHMARK_STRENGTHS:
        return "high" if "cost_or_price_benchmark" in claim_roles else "medium_high"

    if safe_scope in {"company_level_only", "sku_or_label_level", "retail_page_level", "benchmark_only"}:
        return "medium_high"

    if source_context == "rag_retrieval_result":
        return "medium"

    return "medium_low"


def infer_display_candidate_status(claim_strength: str, safe_scope: str) -> str:
    if safe_scope in {"sku_or_label_level", "retail_page_level", "company_level_only", "benchmark_only"}:
        if claim_strength in DIRECT_STRENGTHS or claim_strength in BENCHMARK_STRENGTHS:
            return "candidate_for_strict_audit"

    if safe_scope == "modeled_route_context":
        return "candidate_for_context_audit"

    return "research_only"


def build_safe_website_wording(blob: dict[str, Any]) -> str:
    role = blob.get("primary_claim_role", "")
    entities = ", ".join(blob.get("entities", []))
    ingredients = ", ".join(blob.get("ingredients", []))
    packet = blob.get("packet", "")
    safe_scope = blob.get("safe_scope", "")
    relationship = blob.get("relationship_strength", "")

    subject_parts = [x for x in [entities, ingredients, packet] if x]
    subject = " / ".join(subject_parts) if subject_parts else "This source"

    if role == "supplier_relationship":
        return (
            f"{subject} may support a {relationship.replace('_', ' ')} relationship claim. "
            f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
        ).strip()

    if role == "ingredient_confirmation":
        return (
            f"{subject} may support ingredient, label, or product identity evidence. "
            f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
        ).strip()

    if role == "cost_or_price_benchmark":
        return (
            f"{subject} may support benchmark cost or market-price logic. "
            f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
        ).strip()

    if role == "retail_price":
        return (
            f"{subject} may support observed retail page or price evidence. "
            f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
        ).strip()

    if role == "logistics_distribution":
        return (
            f"{subject} may support modeled logistics or distribution context. "
            f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
        ).strip()

    return (
        f"{subject} may support background context only. "
        f"{SAFE_DISPLAY_RULES.get(safe_scope, '')}"
    ).strip()


def risk_flags_for_blob(blob: dict[str, Any]) -> list[str]:
    flags = []
    safe_scope = blob.get("safe_scope", "")
    roles = blob.get("claim_roles", [])
    text = clean_text(blob.get("evidence_text", "")).lower()
    source_type = blob.get("source_type", "")

    if safe_scope == "company_level_only":
        flags.append("do_not_claim_sku_level_supplier")

    if safe_scope == "benchmark_only":
        flags.append("do_not_claim_internal_hershey_cost")

    if safe_scope == "retail_page_level":
        flags.append("retail_price_varies_by_store_date_promotion")

    if safe_scope == "modeled_route_context":
        flags.append("do_not_claim_exact_distribution_route")

    if source_type == "visual_ocr":
        flags.append("ocr_text_requires_visual_confidence_review")

    if "supplier_relationship" in roles and "1.55" not in text and "43 g" not in text:
        flags.append("supplier_claim_not_sku_confirmed")

    if "cost_or_price_benchmark" in roles:
        flags.append("benchmark_not_invoice")

    if "retail_price" in roles:
        flags.append("retail_observation_not_margin")

    return sorted(set(flags))


def build_blob_from_claim(claim: dict[str, Any], duplicate_index: int) -> dict[str, Any]:
    text = clean_text(claim.get("text_preview", ""))
    roles = normalize_list(claim.get("claim_roles", []))
    entities = normalize_list(claim.get("entities", []))
    ingredients = normalize_list(claim.get("ingredients", []))
    claim_strength = str(claim.get("claim_strength", "background_context"))
    safe_scope = str(claim.get("safe_scope", "context_only"))
    source_type = str(claim.get("source_type", ""))

    primary_role = infer_primary_role(roles)
    evidence_type = infer_evidence_type(roles)
    relationship_strength = infer_relationship_strength(claim_strength, safe_scope, roles)
    confidence_level = infer_confidence_level(claim_strength, safe_scope, source_type, text)
    audit_priority = infer_audit_priority(claim_strength, safe_scope, roles, claim.get("source_context", ""))
    display_candidate_status = infer_display_candidate_status(claim_strength, safe_scope)

    base_key = "|".join(
        [
            str(claim.get("doc_id", "")),
            str(claim.get("packet", "")),
            primary_role,
            claim_strength,
            safe_scope,
            text[:500],
        ]
    )

    evidence_id = f"EEVID_{stable_hash(base_key)}"
    if duplicate_index > 1:
        evidence_id = f"{evidence_id}_{duplicate_index:03d}"

    blob = {
        "evidence_id": evidence_id,
        "source_candidate_claim_id": claim.get("candidate_claim_id", ""),
        "doc_id": claim.get("doc_id", ""),
        "file_name": claim.get("file_name", ""),
        "packet": claim.get("packet", ""),
        "source_type": source_type,
        "source_context": claim.get("source_context", ""),
        "rag_test_id": claim.get("rag_test_id", ""),
        "rag_rank": claim.get("rag_rank", ""),
        "primary_claim_role": primary_role,
        "claim_roles": roles,
        "evidence_type": evidence_type,
        "claim_strength": claim_strength,
        "relationship_strength": relationship_strength,
        "safe_scope": safe_scope,
        "confidence_level": confidence_level,
        "audit_priority": audit_priority,
        "display_candidate_status": display_candidate_status,
        "entities": entities,
        "ingredients": ingredients,
        "claim_label": claim.get("claim_label", ""),
        "evidence_text": text,
        "safe_limit": claim.get("safe_limit", ""),
        "safe_website_wording": "",
        "risk_flags": [],
        "frontend_display_allowed_now": False,
        "strict_audit_status": "pending_step16i",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    blob["safe_website_wording"] = build_safe_website_wording(blob)
    blob["risk_flags"] = risk_flags_for_blob(blob)

    return blob


def dedupe_and_build_blobs(candidate_claims: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen_exact = set()
    duplicate_id_counter = Counter()
    blobs = []
    exact_duplicates_removed = 0

    for claim in candidate_claims:
        text = clean_text(claim.get("text_preview", ""))
        if not text:
            continue

        exact_key = stable_hash(
            "|".join(
                [
                    str(claim.get("doc_id", "")),
                    str(claim.get("packet", "")),
                    str(claim.get("claim_strength", "")),
                    str(claim.get("safe_scope", "")),
                    text[:900],
                ]
            )
        )

        if exact_key in seen_exact:
            exact_duplicates_removed += 1
            continue

        seen_exact.add(exact_key)
        duplicate_id_counter[exact_key] += 1
        blob = build_blob_from_claim(claim, duplicate_id_counter[exact_key])
        blobs.append(blob)

    return blobs, exact_duplicates_removed


def build_by_packet(blobs: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for blob in blobs:
        grouped[blob.get("packet", "unknown")].append(blob)

    out = {}
    for packet, rows in sorted(grouped.items()):
        out[packet] = {
            "packet": packet,
            "evidence_count": len(rows),
            "role_counts": dict(sorted(Counter(r.get("primary_claim_role", "unknown") for r in rows).items())),
            "safe_scope_counts": dict(sorted(Counter(r.get("safe_scope", "unknown") for r in rows).items())),
            "claim_strength_counts": dict(sorted(Counter(r.get("claim_strength", "unknown") for r in rows).items())),
            "evidence_ids": [r.get("evidence_id") for r in rows],
        }

    return out


def build_review_queue(blobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_order = {
        "high": 0,
        "medium_high": 1,
        "medium": 2,
        "medium_low": 3,
        "low": 4,
    }

    queue = sorted(
        blobs,
        key=lambda b: (
            priority_order.get(b.get("audit_priority", "medium"), 99),
            b.get("packet", ""),
            b.get("primary_claim_role", ""),
            b.get("file_name", ""),
        ),
    )

    review_rows = []

    for blob in queue:
        if blob.get("display_candidate_status") == "research_only" and blob.get("audit_priority") not in {"high", "medium_high"}:
            continue

        review_rows.append(
            {
                "evidence_id": blob.get("evidence_id"),
                "audit_priority": blob.get("audit_priority"),
                "packet": blob.get("packet"),
                "file_name": blob.get("file_name"),
                "primary_claim_role": blob.get("primary_claim_role"),
                "claim_strength": blob.get("claim_strength"),
                "safe_scope": blob.get("safe_scope"),
                "relationship_strength": blob.get("relationship_strength"),
                "confidence_level": blob.get("confidence_level"),
                "display_candidate_status": blob.get("display_candidate_status"),
                "risk_flags": blob.get("risk_flags", []),
                "safe_website_wording": blob.get("safe_website_wording", ""),
                "evidence_text_preview": blob.get("evidence_text", "")[:900],
            }
        )

    return review_rows


def write_summary_csv(path: Path, blobs: list[dict[str, Any]]) -> None:
    fieldnames = [
        "evidence_id",
        "packet",
        "file_name",
        "source_type",
        "source_context",
        "primary_claim_role",
        "evidence_type",
        "claim_strength",
        "relationship_strength",
        "safe_scope",
        "confidence_level",
        "audit_priority",
        "display_candidate_status",
        "strict_audit_status",
        "entities",
        "ingredients",
        "risk_flags",
        "safe_website_wording",
        "evidence_text_preview",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for blob in blobs:
            writer.writerow(
                {
                    "evidence_id": blob.get("evidence_id", ""),
                    "packet": blob.get("packet", ""),
                    "file_name": blob.get("file_name", ""),
                    "source_type": blob.get("source_type", ""),
                    "source_context": blob.get("source_context", ""),
                    "primary_claim_role": blob.get("primary_claim_role", ""),
                    "evidence_type": blob.get("evidence_type", ""),
                    "claim_strength": blob.get("claim_strength", ""),
                    "relationship_strength": blob.get("relationship_strength", ""),
                    "safe_scope": blob.get("safe_scope", ""),
                    "confidence_level": blob.get("confidence_level", ""),
                    "audit_priority": blob.get("audit_priority", ""),
                    "display_candidate_status": blob.get("display_candidate_status", ""),
                    "strict_audit_status": blob.get("strict_audit_status", ""),
                    "entities": "; ".join(blob.get("entities", [])),
                    "ingredients": "; ".join(blob.get("ingredients", [])),
                    "risk_flags": "; ".join(blob.get("risk_flags", [])),
                    "safe_website_wording": blob.get("safe_website_wording", ""),
                    "evidence_text_preview": blob.get("evidence_text", "")[:350],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    claims_path = root / "artifacts" / "14_enriched_level1" / "enriched_candidate_claims.json"
    document_profiles_path = root / "artifacts" / "14_enriched_level1" / "enriched_document_profiles.json"
    rag_bundles_path = root / "artifacts" / "14_enriched_level1" / "enriched_rag_question_bundles.json"

    out_dir = root / "artifacts" / "15_enriched_evidence"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not claims_path.exists():
        raise FileNotFoundError(f"Missing enriched candidate claims: {claims_path}")

    candidate_claims = read_json(claims_path)
    document_profiles = read_json(document_profiles_path) if document_profiles_path.exists() else []
    rag_bundles = read_json(rag_bundles_path) if rag_bundles_path.exists() else []

    blobs, duplicates_removed = dedupe_and_build_blobs(candidate_claims)
    by_packet = build_by_packet(blobs)
    review_queue = build_review_queue(blobs)

    evidence_blobs_path = out_dir / "enriched_evidence_blobs.json"
    by_packet_path = out_dir / "enriched_evidence_by_packet.json"
    review_queue_path = out_dir / "enriched_evidence_review_queue.json"
    summary_csv_path = out_dir / "enriched_evidence_summary.csv"
    manifest_path = out_dir / "enriched_evidence_manifest.json"

    write_json(evidence_blobs_path, blobs)
    write_json(by_packet_path, by_packet)
    write_json(review_queue_path, review_queue)
    write_summary_csv(summary_csv_path, blobs)

    role_counts = Counter(blob.get("primary_claim_role", "unknown") for blob in blobs)
    evidence_type_counts = Counter(blob.get("evidence_type", "unknown") for blob in blobs)
    claim_strength_counts = Counter(blob.get("claim_strength", "unknown") for blob in blobs)
    safe_scope_counts = Counter(blob.get("safe_scope", "unknown") for blob in blobs)
    confidence_counts = Counter(blob.get("confidence_level", "unknown") for blob in blobs)
    audit_priority_counts = Counter(blob.get("audit_priority", "unknown") for blob in blobs)
    display_status_counts = Counter(blob.get("display_candidate_status", "unknown") for blob in blobs)
    packet_counts = Counter(blob.get("packet", "unknown") for blob in blobs)

    manifest = {
        "enriched_evidence_version": "v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "Structured evidence blobs generated from enriched Level 1 candidate claims. These require Step 16I strict audit before frontend use.",
        "input_artifacts": {
            "candidate_claims": str(claims_path).replace("\\", "/"),
            "document_profiles": str(document_profiles_path).replace("\\", "/"),
            "rag_bundles": str(rag_bundles_path).replace("\\", "/"),
        },
        "output_artifacts": {
            "enriched_evidence_blobs": str(evidence_blobs_path).replace("\\", "/"),
            "enriched_evidence_by_packet": str(by_packet_path).replace("\\", "/"),
            "enriched_evidence_review_queue": str(review_queue_path).replace("\\", "/"),
            "enriched_evidence_summary_csv": str(summary_csv_path).replace("\\", "/"),
        },
        "strict_rule": "Frontend must not display these blobs directly. Step 16I strict audit must approve display-safe claims first.",
    }

    write_json(manifest_path, manifest)

    report = {
        "run_name": "step16h_enriched_evidence_blob_builder",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "candidate_claims_seen": len(candidate_claims),
        "document_profiles_seen": len(document_profiles),
        "rag_bundles_seen": len(rag_bundles),
        "enriched_evidence_blobs_created": len(blobs),
        "exact_duplicates_removed": duplicates_removed,
        "review_queue_items": len(review_queue),
        "packet_counts": dict(sorted(packet_counts.items())),
        "primary_claim_role_counts": dict(sorted(role_counts.items())),
        "evidence_type_counts": dict(sorted(evidence_type_counts.items())),
        "claim_strength_counts": dict(sorted(claim_strength_counts.items())),
        "safe_scope_counts": dict(sorted(safe_scope_counts.items())),
        "confidence_level_counts": dict(sorted(confidence_counts.items())),
        "audit_priority_counts": dict(sorted(audit_priority_counts.items())),
        "display_candidate_status_counts": dict(sorted(display_status_counts.items())),
        "enriched_evidence_blobs_json": str(evidence_blobs_path).replace("\\", "/"),
        "enriched_evidence_by_packet_json": str(by_packet_path).replace("\\", "/"),
        "enriched_evidence_review_queue_json": str(review_queue_path).replace("\\", "/"),
        "enriched_evidence_summary_csv": str(summary_csv_path).replace("\\", "/"),
        "manifest_json": str(manifest_path).replace("\\", "/"),
        "next_step": "Step 16I: enriched strict audit to approve/reject/rewrite evidence for display-safe artifacts.",
    }

    report_path = report_dir / "step16h_enriched_evidence_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16H ENRICHED EVIDENCE BLOB BUILDER COMPLETE")
    print("------------------------------------------------")
    print(f"Candidate claims seen:        {len(candidate_claims)}")
    print(f"Evidence blobs created:       {len(blobs)}")
    print(f"Duplicates removed:           {duplicates_removed}")
    print(f"Review queue items:           {len(review_queue)}")
    print("")
    print(f"Evidence blobs: {evidence_blobs_path}")
    print(f"Review queue:   {review_queue_path}")
    print(f"Summary CSV:    {summary_csv_path}")
    print(f"Report JSON:    {report_path}")
    print("")


if __name__ == "__main__":
    main()