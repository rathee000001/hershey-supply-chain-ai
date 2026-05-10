from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


APPROVABLE_SCOPES = {
    "company_level_only",
    "sku_or_label_level",
    "retail_page_level",
    "benchmark_only",
    "modeled_route_context",
}

DISPLAY_SCOPES = {
    "company_level_only",
    "sku_or_label_level",
    "retail_page_level",
    "benchmark_only",
}

CONTEXT_ONLY_SCOPES = {
    "modeled_route_context",
    "context_only",
}

HIGH_VALUE_STRENGTHS = {
    "direct_product_or_label_evidence",
    "direct_visual_or_page_evidence",
    "company_level_relationship_evidence",
    "benchmark_context_evidence",
}

SAFE_SCOPE_LABELS = {
    "company_level_only": "Company-level evidence only",
    "sku_or_label_level": "SKU/label-level evidence",
    "retail_page_level": "Retail page-level evidence",
    "benchmark_only": "Benchmark-only evidence",
    "modeled_route_context": "Modeled route/context evidence",
    "context_only": "Context-only evidence",
}

ABSOLUTE_OVERCLAIM_WORDS = [
    "proves hershey's internal cost",
    "proves internal cost",
    "exact supplier for this sku",
    "confirmed sku supplier",
    "hershey profit",
    "retailer profit",
    "exact margin",
    "guaranteed cost",
    "actual invoice",
    "internal invoice",
    "exact distribution route",
]

RISK_REWRITE_MAP = {
    "do_not_claim_sku_level_supplier": "Supplier relationship evidence is limited to company-level context unless exact SKU evidence is separately available.",
    "do_not_claim_internal_hershey_cost": "Cost evidence is benchmark-only and must not be presented as Hershey internal cost.",
    "retail_price_varies_by_store_date_promotion": "Retail price evidence is page/date/store-context dependent and may vary.",
    "do_not_claim_exact_distribution_route": "Distribution evidence supports modeled logistics context, not an exact route.",
    "ocr_text_requires_visual_confidence_review": "OCR-derived text should be treated as visual evidence support and not over-read.",
    "supplier_claim_not_sku_confirmed": "Supplier relationship is not confirmed for the exact 1.55 oz SKU.",
    "benchmark_not_invoice": "Benchmark evidence is not invoice evidence.",
    "retail_observation_not_margin": "Retail observation does not prove margin or profit.",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean_text(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def has_absolute_overclaim(text: str) -> bool:
    lower = clean_text(text).lower()
    return any(term in lower for term in ABSOLUTE_OVERCLAIM_WORDS)


def normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def audit_decision(blob: dict[str, Any]) -> dict[str, Any]:
    safe_scope = str(blob.get("safe_scope", "context_only"))
    claim_strength = str(blob.get("claim_strength", "background_context"))
    source_type = str(blob.get("source_type", ""))
    display_status = str(blob.get("display_candidate_status", "research_only"))
    evidence_text = clean_text(blob.get("evidence_text", ""))
    safe_wording = clean_text(blob.get("safe_website_wording", ""))
    risk_flags = normalize_list(blob.get("risk_flags", []))
    primary_role = str(blob.get("primary_claim_role", ""))
    relationship_strength = str(blob.get("relationship_strength", ""))
    confidence_level = str(blob.get("confidence_level", ""))

    reasons = []
    required_rewrites = []
    public_display_allowed = False
    audit_status = "review_locked"
    audit_class = "needs_review"

    if not evidence_text or len(evidence_text) < 40:
        return {
            "audit_status": "rejected_research_only",
            "audit_class": "too_little_text",
            "public_display_allowed": False,
            "context_display_allowed": False,
            "audit_reasons": ["Evidence text is too short for display-safe use."],
            "required_rewrites": ["Keep as research-only unless manually verified."],
        }

    if has_absolute_overclaim(evidence_text) or has_absolute_overclaim(safe_wording):
        return {
            "audit_status": "rejected_overclaim_risk",
            "audit_class": "unsafe_wording",
            "public_display_allowed": False,
            "context_display_allowed": False,
            "audit_reasons": ["Evidence or wording contains absolute overclaim language."],
            "required_rewrites": ["Remove internal-cost, exact-SKU, profit, margin, or exact-route language."],
        }

    if safe_scope not in APPROVABLE_SCOPES and safe_scope not in CONTEXT_ONLY_SCOPES:
        reasons.append(f"Safe scope {safe_scope} is not approvable for display.")
        audit_status = "rejected_research_only"
        audit_class = "unapproved_scope"

    elif display_status == "research_only":
        reasons.append("Evidence was marked research-only by enriched evidence builder.")
        audit_status = "rejected_research_only"
        audit_class = "research_only"

    elif safe_scope in DISPLAY_SCOPES and claim_strength in HIGH_VALUE_STRENGTHS:
        audit_status = "approved_display_safe"
        audit_class = "display_safe_evidence"
        public_display_allowed = True
        reasons.append("Evidence has an approved safe scope and high-value claim strength.")

    elif safe_scope == "modeled_route_context":
        audit_status = "approved_context_only"
        audit_class = "modeled_context"
        reasons.append("Evidence supports modeled logistics/context only, not exact route.")
        public_display_allowed = False

    elif safe_scope == "context_only":
        audit_status = "approved_context_only"
        audit_class = "background_context"
        reasons.append("Evidence supports background context only.")
        public_display_allowed = False

    else:
        audit_status = "review_locked"
        audit_class = "manual_review_needed"
        reasons.append("Evidence did not meet automatic strict-audit approval rules.")

    if source_type == "visual_ocr":
        required_rewrites.append("Display as visual/OCR-supported evidence; avoid over-reading screenshot text.")

    for flag in risk_flags:
        rewrite = RISK_REWRITE_MAP.get(flag)
        if rewrite:
            required_rewrites.append(rewrite)

    if primary_role == "supplier_relationship" and safe_scope == "company_level_only":
        required_rewrites.append("Use company-level language only; do not say this proves exact SKU sourcing.")

    if primary_role == "cost_or_price_benchmark" or safe_scope == "benchmark_only":
        required_rewrites.append("Use benchmark language only; do not present as Hershey internal SKU cost.")

    if primary_role == "retail_price" or safe_scope == "retail_page_level":
        required_rewrites.append("Use observed retail price language only; do not infer margin or profit.")

    if relationship_strength == "background_or_low_support" or confidence_level == "low":
        if audit_status == "approved_display_safe":
            audit_status = "review_locked"
            audit_class = "low_confidence_review"
            public_display_allowed = False
            reasons.append("Low confidence evidence requires manual review before public display.")

    return {
        "audit_status": audit_status,
        "audit_class": audit_class,
        "public_display_allowed": public_display_allowed,
        "context_display_allowed": audit_status in {"approved_display_safe", "approved_context_only"},
        "audit_reasons": sorted(set(reasons)),
        "required_rewrites": sorted(set(required_rewrites)),
    }


def build_audited_wording(blob: dict[str, Any], decision: dict[str, Any]) -> str:
    role = blob.get("primary_claim_role", "")
    safe_scope = blob.get("safe_scope", "")
    packet = blob.get("packet", "")
    entities = normalize_list(blob.get("entities", []))
    ingredients = normalize_list(blob.get("ingredients", []))
    file_name = blob.get("file_name", "")

    entity_text = ", ".join(entities) if entities else ""
    ingredient_text = ", ".join(ingredients) if ingredients else ""
    subject = " / ".join(x for x in [entity_text, ingredient_text, packet] if x) or file_name or "This evidence"

    scope_label = SAFE_SCOPE_LABELS.get(safe_scope, "Evidence")

    if decision["audit_status"] == "approved_display_safe":
        if safe_scope == "company_level_only":
            return (
                f"{subject} is approved for company-level relationship context only. "
                "It must not be displayed as proof of exact 1.55 oz SKU supplier allocation."
            )

        if safe_scope == "sku_or_label_level":
            return (
                f"{subject} is approved for SKU, wrapper, product identity, ingredient-label, or nutrition context. "
                "It must not be used to infer supplier allocation."
            )

        if safe_scope == "retail_page_level":
            return (
                f"{subject} is approved for observed retail page/price context. "
                "Retail price may vary by store, date, and promotion; it must not be used as margin/profit evidence."
            )

        if safe_scope == "benchmark_only":
            return (
                f"{subject} is approved for benchmark or market context only. "
                "It must not be displayed as Hershey internal SKU cost or invoice evidence."
            )

    if decision["audit_status"] == "approved_context_only":
        return (
            f"{subject} is approved for context-only use under scope: {scope_label}. "
            "It should support explanation, not direct factual display claims."
        )

    if decision["audit_status"].startswith("rejected"):
        return (
            f"{subject} is not approved for frontend display. "
            "Keep as research-only unless manually reviewed and rewritten."
        )

    return (
        f"{subject} is review-locked. "
        "Do not display publicly until manually verified or audited with stronger evidence."
    )


def audit_blobs(blobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    audited = []

    for blob in blobs:
        decision = audit_decision(blob)
        audited_wording = build_audited_wording(blob, decision)

        audited_blob = {
            **blob,
            "strict_audit_status": decision["audit_status"],
            "strict_audit_class": decision["audit_class"],
            "public_display_allowed": decision["public_display_allowed"],
            "context_display_allowed": decision["context_display_allowed"],
            "audit_reasons": decision["audit_reasons"],
            "required_rewrites": decision["required_rewrites"],
            "audited_safe_website_wording": audited_wording,
            "frontend_display_allowed_now": decision["public_display_allowed"],
            "audit_timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        audited.append(audited_blob)

    return audited


def split_audited(audited: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    approved_display = []
    context_only = []
    review_locked = []
    rejected = []

    for row in audited:
        status = row.get("strict_audit_status", "")

        if status == "approved_display_safe":
            approved_display.append(row)
        elif status == "approved_context_only":
            context_only.append(row)
        elif status == "review_locked":
            review_locked.append(row)
        else:
            rejected.append(row)

    return {
        "approved_display": approved_display,
        "context_only": context_only,
        "review_locked": review_locked,
        "rejected": rejected,
    }


def build_packet_summary(audited: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in audited:
        grouped[row.get("packet", "unknown")].append(row)

    packet_summary = {}

    for packet, rows in sorted(grouped.items()):
        packet_summary[packet] = {
            "packet": packet,
            "total_evidence": len(rows),
            "audit_status_counts": dict(sorted(Counter(r.get("strict_audit_status", "unknown") for r in rows).items())),
            "safe_scope_counts": dict(sorted(Counter(r.get("safe_scope", "unknown") for r in rows).items())),
            "primary_role_counts": dict(sorted(Counter(r.get("primary_claim_role", "unknown") for r in rows).items())),
            "public_display_allowed_count": sum(1 for r in rows if r.get("public_display_allowed")),
            "context_display_allowed_count": sum(1 for r in rows if r.get("context_display_allowed")),
            "approved_evidence_ids": [r.get("evidence_id") for r in rows if r.get("public_display_allowed")],
        }

    return packet_summary


def write_summary_csv(path: Path, audited: list[dict[str, Any]]) -> None:
    fieldnames = [
        "evidence_id",
        "packet",
        "file_name",
        "source_type",
        "primary_claim_role",
        "claim_strength",
        "safe_scope",
        "relationship_strength",
        "confidence_level",
        "strict_audit_status",
        "strict_audit_class",
        "public_display_allowed",
        "context_display_allowed",
        "risk_flags",
        "audit_reasons",
        "required_rewrites",
        "audited_safe_website_wording",
        "evidence_text_preview",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for row in audited:
            writer.writerow(
                {
                    "evidence_id": row.get("evidence_id", ""),
                    "packet": row.get("packet", ""),
                    "file_name": row.get("file_name", ""),
                    "source_type": row.get("source_type", ""),
                    "primary_claim_role": row.get("primary_claim_role", ""),
                    "claim_strength": row.get("claim_strength", ""),
                    "safe_scope": row.get("safe_scope", ""),
                    "relationship_strength": row.get("relationship_strength", ""),
                    "confidence_level": row.get("confidence_level", ""),
                    "strict_audit_status": row.get("strict_audit_status", ""),
                    "strict_audit_class": row.get("strict_audit_class", ""),
                    "public_display_allowed": row.get("public_display_allowed", False),
                    "context_display_allowed": row.get("context_display_allowed", False),
                    "risk_flags": "; ".join(row.get("risk_flags", [])),
                    "audit_reasons": "; ".join(row.get("audit_reasons", [])),
                    "required_rewrites": "; ".join(row.get("required_rewrites", [])),
                    "audited_safe_website_wording": row.get("audited_safe_website_wording", ""),
                    "evidence_text_preview": clean_text(row.get("evidence_text", ""))[:350],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    input_path = root / "artifacts" / "15_enriched_evidence" / "enriched_evidence_blobs.json"
    out_dir = root / "artifacts" / "16_enriched_audit"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing enriched evidence blobs: {input_path}")

    blobs = read_json(input_path)
    audited = audit_blobs(blobs)
    split = split_audited(audited)
    packet_summary = build_packet_summary(audited)

    audited_path = out_dir / "enriched_audited_evidence.json"
    approved_path = out_dir / "enriched_approved_display_candidates.json"
    context_path = out_dir / "enriched_context_only_evidence.json"
    locked_path = out_dir / "enriched_review_locked_evidence.json"
    rejected_path = out_dir / "enriched_rejected_evidence.json"
    packet_summary_path = out_dir / "enriched_audit_by_packet.json"
    summary_csv_path = out_dir / "enriched_audit_summary.csv"
    manifest_path = out_dir / "enriched_audit_manifest.json"

    write_json(audited_path, audited)
    write_json(approved_path, split["approved_display"])
    write_json(context_path, split["context_only"])
    write_json(locked_path, split["review_locked"])
    write_json(rejected_path, split["rejected"])
    write_json(packet_summary_path, packet_summary)
    write_summary_csv(summary_csv_path, audited)

    status_counts = Counter(row.get("strict_audit_status", "unknown") for row in audited)
    class_counts = Counter(row.get("strict_audit_class", "unknown") for row in audited)
    packet_counts = Counter(row.get("packet", "unknown") for row in audited)
    scope_counts = Counter(row.get("safe_scope", "unknown") for row in audited)
    role_counts = Counter(row.get("primary_claim_role", "unknown") for row in audited)
    source_counts = Counter(row.get("source_type", "unknown") for row in audited)

    manifest = {
        "enriched_strict_audit_version": "v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "Strict audited evidence layer for display-safe rebuilding of supplier, ingredient, cost, graph, and frontend artifacts.",
        "input_artifacts": {
            "enriched_evidence_blobs": str(input_path).replace("\\", "/"),
        },
        "output_artifacts": {
            "audited_evidence": str(audited_path).replace("\\", "/"),
            "approved_display_candidates": str(approved_path).replace("\\", "/"),
            "context_only_evidence": str(context_path).replace("\\", "/"),
            "review_locked_evidence": str(locked_path).replace("\\", "/"),
            "rejected_evidence": str(rejected_path).replace("\\", "/"),
            "audit_by_packet": str(packet_summary_path).replace("\\", "/"),
            "audit_summary_csv": str(summary_csv_path).replace("\\", "/"),
        },
        "display_rule": "Only enriched_approved_display_candidates.json should be used to rebuild public display claims. Context-only evidence may support explanatory panels but not hard claims.",
        "hard_limits": [
            "Company-level supplier evidence cannot be displayed as exact SKU supplier proof.",
            "Benchmark cost evidence cannot be displayed as Hershey internal cost.",
            "Retail price evidence cannot be displayed as margin or profit.",
            "Distribution context cannot be displayed as exact route proof.",
            "OCR evidence requires safe wording and should not be over-read."
        ],
    }

    write_json(manifest_path, manifest)

    report = {
        "run_name": "step16i_enriched_strict_audit",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "input_evidence_blobs_seen": len(blobs),
        "audited_evidence_created": len(audited),
        "approved_display_candidates": len(split["approved_display"]),
        "context_only_evidence": len(split["context_only"]),
        "review_locked_evidence": len(split["review_locked"]),
        "rejected_evidence": len(split["rejected"]),
        "audit_status_counts": dict(sorted(status_counts.items())),
        "audit_class_counts": dict(sorted(class_counts.items())),
        "packet_counts": dict(sorted(packet_counts.items())),
        "safe_scope_counts": dict(sorted(scope_counts.items())),
        "primary_role_counts": dict(sorted(role_counts.items())),
        "source_type_counts": dict(sorted(source_counts.items())),
        "enriched_audited_evidence_json": str(audited_path).replace("\\", "/"),
        "enriched_approved_display_candidates_json": str(approved_path).replace("\\", "/"),
        "enriched_context_only_evidence_json": str(context_path).replace("\\", "/"),
        "enriched_review_locked_evidence_json": str(locked_path).replace("\\", "/"),
        "enriched_rejected_evidence_json": str(rejected_path).replace("\\", "/"),
        "enriched_audit_by_packet_json": str(packet_summary_path).replace("\\", "/"),
        "enriched_audit_summary_csv": str(summary_csv_path).replace("\\", "/"),
        "manifest_json": str(manifest_path).replace("\\", "/"),
        "next_step": "Step 16J: rebuild supplier, ingredient, cost, graph, and display artifacts from enriched audited evidence.",
    }

    report_path = report_dir / "step16i_enriched_strict_audit_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16I ENRICHED STRICT AUDIT COMPLETE")
    print("---------------------------------------")
    print(f"Input evidence blobs seen:       {len(blobs)}")
    print(f"Audited evidence created:        {len(audited)}")
    print(f"Approved display candidates:     {len(split['approved_display'])}")
    print(f"Context-only evidence:           {len(split['context_only'])}")
    print(f"Review-locked evidence:          {len(split['review_locked'])}")
    print(f"Rejected evidence:               {len(split['rejected'])}")
    print("")
    print(f"Audited evidence: {audited_path}")
    print(f"Approved display: {approved_path}")
    print(f"Summary CSV:      {summary_csv_path}")
    print(f"Report JSON:      {report_path}")
    print("")


if __name__ == "__main__":
    main()