from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


DIRECT_SUPPLIER_RELATIONSHIP_FILES = {
    "sugar": [
        "hershey_sugar_sourcing_page",
        "asr_hershey_learn_to_grow_belize",
        "hershey_sustainable_sugar_sourcing_policy"
    ],
    "cocoa_chocolate_cocoa_butter": [
        "barry_callebaut_hershey_supply_agreement_news_release",
        "hershey_cocoa_sustainability_page"
    ],
    "dairy_milk_skim_milk_milk_fat": [
        "hershey_dairy_sourcing_page",
        "hershey_sustainable_dairy_pa_2021_press_release",
        "epa_hershey_land_o_lakes_pa_dairy_farms_2m_commitment",
        "land_o_lakes_hershey_chesapeake_bay_page",
        "alliance_sustainable_dairy_pa_page"
    ],
    "logistics_distribution": [
        "hershey_10k_mclane_customer_section",
        "hershey_10k_distribution_common_carriers_section",
        "hershey_distribution_center_logistics_reference"
    ]
}


SUPPLIER_COMPANY_BY_PACKET = {
    "sugar": "American Sugar Refining / ASR",
    "cocoa_chocolate_cocoa_butter": "Barry Callebaut",
    "dairy_milk_skim_milk_milk_fat": "Land O'Lakes",
    "logistics_distribution": "McLane"
}


INGREDIENT_BY_PACKET = {
    "sugar": "Sugar",
    "cocoa_chocolate_cocoa_butter": "Cocoa / Chocolate / Cocoa Butter",
    "dairy_milk_skim_milk_milk_fat": "Milk / Skim Milk / Milk Fat",
    "soy_lecithin": "Soy Lecithin",
    "pgpr": "PGPR",
    "natural_flavor": "Natural Flavor",
    "packaging_wrapper": "Packaging / Wrapper",
    "retail_price_evidence": "Retail Price",
    "product_sku_1_55oz": "Product SKU"
}


BENCHMARK_SOURCE_HINTS = [
    "usda",
    "bls",
    "ppi",
    "fred",
    "eia",
    "icco",
    "ice",
    "futures",
    "market",
    "price",
    "benchmark",
    "monthly",
    "weekly",
    "national dairy products",
    "dairy market news",
    "sugar and sweeteners",
    "producer price index"
]


REGULATORY_SOURCE_HINTS = [
    "fda",
    "efsa",
    "gras",
    "cfr",
    "food additive",
    "regulation",
    "regulatory",
    "fema"
]


WEAK_EVIDENCE_PHRASES = [
    "local level 1 parse",
    "source document available for packet",
    "detected entities/stages include: none detected",
    "no extracted text available",
    "likely image/logo",
]


GENERIC_COST_PHRASES = [
    "marketing opportunities",
    "marketing for our beloved brands",
    "share price",
    "market capitalization",
    "price-earnings",
    "export markets include",
    "gdp",
    "efficient and cost-effective manner",
    "source contains cost, price, market, benchmark, or index language"
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def lower_blob_text(blob: dict[str, Any]) -> str:
    return " ".join([
        blob.get("source_file", ""),
        blob.get("claim", ""),
        blob.get("evidence_text", ""),
        blob.get("safe_website_wording", ""),
        blob.get("related_company", ""),
        blob.get("related_ingredient", ""),
        blob.get("related_cost_bucket", ""),
    ]).lower()


def source_name(blob: dict[str, Any]) -> str:
    return Path(blob.get("source_file", "")).stem.lower()


def has_any(text: str, hints: list[str]) -> bool:
    return any(h.lower() in text for h in hints)


def is_weak_summary_blob(blob: dict[str, Any]) -> bool:
    text = lower_blob_text(blob)
    evidence_text = blob.get("evidence_text", "").lower()

    if blob.get("page_or_section") == "document summary" and "local level 1 parse" in evidence_text:
        return True

    if has_any(evidence_text, WEAK_EVIDENCE_PHRASES):
        return True

    return False


def is_generic_or_bad_cost_blob(blob: dict[str, Any]) -> bool:
    text = lower_blob_text(blob)
    evidence_text = blob.get("evidence_text", "").lower()

    if blob.get("category") != "cost":
        return False

    if has_any(evidence_text, GENERIC_COST_PHRASES):
        return True

    if len(evidence_text.strip()) < 35:
        return True

    # Keep cost blobs with actual numeric/price/index signal.
    has_number = bool(re.search(r"\d", evidence_text))
    has_price_language = has_any(text, BENCHMARK_SOURCE_HINTS)

    if not has_number and not has_price_language:
        return True

    return False


def is_direct_supplier_relationship_source(blob: dict[str, Any]) -> bool:
    packet = blob.get("packet", "")
    name = source_name(blob)
    text = lower_blob_text(blob)

    allowed_names = DIRECT_SUPPLIER_RELATIONSHIP_FILES.get(packet, [])

    if any(allowed in name for allowed in allowed_names):
        return True

    supplier_company = SUPPLIER_COMPANY_BY_PACKET.get(packet, "")
    if supplier_company and supplier_company.lower().split("/")[0].strip() in text and "hershey" in text:
        if any(word in text for word in ["agreement", "partner", "partnership", "supplier", "sourcing", "customer", "distribution"]):
            return True

    return False


def is_company_profile_only(blob: dict[str, Any]) -> bool:
    name = source_name(blob)
    text = lower_blob_text(blob)

    profile_terms = [
        "company_profile",
        "home_page",
        "about_page",
        "who_we_are_page",
        "company_facts",
        "annual_report"
    ]

    if any(term in name for term in profile_terms):
        # Company profile can support context, but not supplier edge unless Hershey relationship is explicit.
        if "hershey" not in text:
            return True

    return False


def is_retail_price_candidate(blob: dict[str, Any]) -> bool:
    if blob.get("packet") != "retail_price_evidence":
        return False

    name = source_name(blob)
    return any(retailer in name for retailer in ["walmart", "target", "cvs", "walgreens"])


def is_product_sku_visual_or_label(blob: dict[str, Any]) -> bool:
    if blob.get("packet") != "product_sku_1_55oz":
        return False

    name = source_name(blob)
    text = lower_blob_text(blob)

    return any(x in name or x in text for x in [
        "hershey",
        "1_55",
        "1.55",
        "front",
        "back",
        "wrapper",
        "label",
        "sku",
        "milk_chocolate"
    ])


def corrected_evidence_type(blob: dict[str, Any]) -> str:
    text = lower_blob_text(blob)
    category = blob.get("category", "")
    packet = blob.get("packet", "")

    if blob.get("evidence_type") == "reference_only" or category == "visual_asset" or packet == "reference_only":
        return "reference_only"

    if is_direct_supplier_relationship_source(blob):
        return "direct"

    if is_retail_price_candidate(blob):
        return "direct"

    if is_product_sku_visual_or_label(blob):
        return "direct"

    if has_any(text, REGULATORY_SOURCE_HINTS):
        return "direct"

    if has_any(text, BENCHMARK_SOURCE_HINTS):
        return "benchmark_proxy"

    if category in ["supplier", "ingredient", "packaging", "logistics", "retail", "product_sku"]:
        if "hershey" in text:
            return "direct"

    return blob.get("evidence_type", "benchmark_proxy")


def corrected_relationship_strength(blob: dict[str, Any], evidence_type: str) -> str:
    packet = blob.get("packet", "")
    category = blob.get("category", "")

    if evidence_type == "reference_only":
        return "illustrative_only"

    if is_retail_price_candidate(blob):
        return "sku_level_confirmed"

    if packet == "product_sku_1_55oz" and evidence_type == "direct":
        return "sku_level_confirmed"

    if is_direct_supplier_relationship_source(blob):
        return "company_level_confirmed"

    if packet in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"] and category in ["ingredient", "packaging"]:
        if evidence_type == "benchmark_proxy":
            return "benchmark_only"
        return "unknown"

    if evidence_type == "benchmark_proxy":
        return "benchmark_only"

    if category == "supplier" and is_company_profile_only(blob):
        return "illustrative_only"

    return blob.get("relationship_strength", "unknown")


def corrected_related_company(blob: dict[str, Any]) -> str:
    packet = blob.get("packet", "")
    name = source_name(blob)
    text = lower_blob_text(blob)

    if packet in SUPPLIER_COMPANY_BY_PACKET and is_direct_supplier_relationship_source(blob):
        return SUPPLIER_COMPANY_BY_PACKET[packet]

    if "barry" in name or "barry callebaut" in text:
        return "Barry Callebaut"
    if "land_o_lakes" in name or "land o'lakes" in text or "land o lakes" in text:
        return "Land O'Lakes"
    if "asr" in name or "american sugar refining" in text or "domino" in name:
        return "American Sugar Refining / ASR"
    if "mclane" in name or "mclane" in text:
        return "McLane"
    if "walmart" in name:
        return "Walmart"
    if "target" in name:
        return "Target"
    if "cvs" in name:
        return "CVS"
    if "walgreens" in name:
        return "Walgreens"
    if "hershey" in name or "hershey" in text:
        return "The Hershey Company"
    if "usda" in name or "usda" in text:
        return "USDA"
    if "bls" in name or "ppi" in name:
        return "BLS"
    if "eia" in name:
        return "EIA"
    if "icco" in name:
        return "ICCO"
    if "fda" in name or "fda" in text:
        return "FDA"
    if "efsa" in name or "efsa" in text:
        return "EFSA"
    if "fema" in name or "fema" in text:
        return "FEMA"

    current = blob.get("related_company", "")
    if current in ["Target", "USDA", "USDA ERS"] and packet == "cocoa_chocolate_cocoa_butter":
        return ""

    return current


def corrected_related_ingredient(blob: dict[str, Any]) -> str:
    packet = blob.get("packet", "")
    text = lower_blob_text(blob)

    if "cocoa butter" in text:
        return "Cocoa Butter"
    if packet in INGREDIENT_BY_PACKET:
        return INGREDIENT_BY_PACKET[packet]
    return blob.get("related_ingredient", "")


def claim_scope(relationship_strength: str, evidence_type: str) -> str:
    if relationship_strength == "sku_level_confirmed":
        return "sku_level"
    if relationship_strength == "company_level_confirmed":
        return "company_level"
    if relationship_strength == "benchmark_only":
        return "market_level"
    if evidence_type == "reference_only":
        return "illustrative_only"
    if relationship_strength in ["unknown", "probable"]:
        return "assumption_or_needs_review"
    return "unknown"


def safe_wording(blob: dict[str, Any], rel: str, etype: str, company: str, ingredient: str) -> tuple[str, str]:
    packet = blob.get("packet", "")
    source = blob.get("source_file", "")

    if rel == "sku_level_confirmed" and packet == "retail_price_evidence":
        return (
            f"{company} evidence is retained as a SKU-level retail price source for the HERSHEY'S 1.55 oz bar, pending final visual/price verification.",
            "This retailer price proves Hershey's internal cost, margin, or supplier invoice cost."
        )

    if rel == "sku_level_confirmed" and packet == "product_sku_1_55oz":
        return (
            "This source supports the product/SKU identity for the HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g.",
            "This product image alone proves supplier relationships or cost values."
        )

    if rel == "company_level_confirmed":
        if packet == "sugar":
            return (
                "ASR is supported as a Hershey company-level sugar sourcing partner. Exact 1.55 oz SKU sugar allocation is not publicly confirmed.",
                "ASR supplies the exact sugar in every 1.55 oz Hershey bar."
            )
        if packet == "cocoa_chocolate_cocoa_butter":
            return (
                "Barry Callebaut is supported as a Hershey company-level cocoa/chocolate supply partner. Exact 1.55 oz SKU cocoa or cocoa butter allocation is not publicly confirmed.",
                "Barry Callebaut supplies the exact cocoa or cocoa butter in every 1.55 oz Hershey bar."
            )
        if packet == "dairy_milk_skim_milk_milk_fat":
            return (
                "Land O'Lakes is supported as a Hershey company-level dairy partner/supplier. Exact 1.55 oz SKU dairy allocation is not publicly confirmed.",
                "Land O'Lakes supplies the exact milk, skim milk, or milk fat in every 1.55 oz Hershey bar."
            )
        if packet == "logistics_distribution":
            return (
                "McLane or Hershey distribution evidence supports company-level downstream/distribution context. Exact route for this 1.55 oz bar is not publicly confirmed.",
                "McLane distributes every 1.55 oz Hershey bar to every retailer."
            )

    if rel == "benchmark_only":
        return (
            f"{source} can support benchmark or market context for {ingredient or packet}. It does not represent Hershey's exact SKU-level invoice cost.",
            "This benchmark equals Hershey's actual per-bar cost or supplier invoice."
        )

    if etype == "reference_only":
        return (
            "This file may be used as a visual/reference asset only. It does not support supplier, route, or cost claims.",
            "This visual/reference file proves a supplier, route, or cost."
        )

    if packet in ["soy_lecithin", "pgpr", "natural_flavor"]:
        return (
            f"{ingredient} is retained as an ingredient/function input, but the supplier is not publicly confirmed for the 1.55 oz bar.",
            f"A specific company supplies {ingredient} for this exact bar without direct evidence."
        )

    if packet == "packaging_wrapper":
        return (
            "Packaging/wrapper materials are retained as a modeled input stream. Exact wrapper supplier for the 1.55 oz bar is not publicly confirmed unless direct evidence proves it.",
            "A specific packaging company supplies the exact wrapper for every 1.55 oz Hershey bar."
        )

    return (
        clean(blob.get("safe_website_wording", "")) or clean(blob.get("claim", "")),
        clean(blob.get("unsafe_wording_to_avoid", "")) or "Do not expand this claim beyond the evidence."
    )


def audit_decision(blob: dict[str, Any], etype: str, rel: str) -> tuple[str, str]:
    packet = blob.get("packet", "")
    category = blob.get("category", "")

    if is_generic_or_bad_cost_blob(blob):
        return "rejected", "Rejected because the cost/market signal is generic, too short, or not useful for the cost model."

    if etype == "reference_only":
        return "approved", "Approved only as reference/visual context, not as factual evidence."

    if is_weak_summary_blob(blob):
        if is_direct_supplier_relationship_source(blob) or is_retail_price_candidate(blob) or is_product_sku_visual_or_label(blob):
            return "needs_review", "Candidate is relevant but depends on weak extracted text or visual/page review before public display."
        return "needs_review", "Weak summary-level extraction; keep for manual/AI review but do not display yet."

    if is_company_profile_only(blob) and category == "supplier":
        return "needs_review", "Company profile supports entity context but does not prove Hershey relationship by itself."

    if rel in ["sku_level_confirmed", "company_level_confirmed"]:
        return "approved", "Approved with scoped wording and no SKU-level supplier overclaim."

    if rel == "benchmark_only":
        return "approved", "Approved as benchmark/market/process context only."

    if packet in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"]:
        return "approved", "Approved as ingredient/function/input context with supplier unknown."

    return "needs_review", "Evidence remains uncertain and should not be displayed until reviewed."


def support_flags(blob: dict[str, Any], status: str, rel: str, etype: str) -> dict[str, bool]:
    category = blob.get("category", "")
    packet = blob.get("packet", "")

    if status == "rejected":
        return {
            "supports_node": False,
            "supports_edge": False,
            "supports_cost_bucket": False,
            "supports_supplier_packet": False,
            "supports_ingredient_packet": False,
            "supports_display_blob": False,
        }

    return {
        "supports_node": category in ["product_sku", "ingredient", "packaging", "logistics", "retail", "supplier", "visual_asset"],
        "supports_edge": rel in ["sku_level_confirmed", "company_level_confirmed"] and category in ["supplier", "logistics", "retail"],
        "supports_cost_bucket": category == "cost" and rel == "benchmark_only",
        "supports_supplier_packet": rel == "company_level_confirmed" and packet in SUPPLIER_COMPANY_BY_PACKET,
        "supports_ingredient_packet": packet in INGREDIENT_BY_PACKET,
        "supports_display_blob": status == "approved" and etype != "reference_only",
    }


def display_allowed(status: str, rel: str, etype: str, blob: dict[str, Any]) -> bool:
    if status != "approved":
        return False

    if etype == "reference_only":
        return False

    if rel in ["sku_level_confirmed", "company_level_confirmed", "benchmark_only"]:
        # Keep visual-priority retail/product candidates for later manual/vision confirmation.
        if blob.get("requires_human_review") and blob.get("packet") in ["retail_price_evidence", "product_sku_1_55oz"]:
            return False
        return True

    if blob.get("packet") in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"]:
        return True

    return False


def display_priority(blob: dict[str, Any], rel: str, status: str) -> int:
    if status != "approved":
        return 0

    packet = blob.get("packet", "")
    category = blob.get("category", "")

    score = 10

    if rel == "sku_level_confirmed":
        score += 40
    if rel == "company_level_confirmed":
        score += 35
    if rel == "benchmark_only":
        score += 20
    if category == "cost":
        score += 10
    if packet in ["sugar", "cocoa_chocolate_cocoa_butter", "dairy_milk_skim_milk_milk_fat"]:
        score += 10
    if packet == "product_sku_1_55oz":
        score += 15
    if packet == "retail_price_evidence":
        score += 15

    if blob.get("requires_human_review"):
        score -= 15

    return max(0, score)


def audit_blob(blob: dict[str, Any]) -> dict[str, Any]:
    etype = corrected_evidence_type(blob)
    company = corrected_related_company(blob)
    ingredient = corrected_related_ingredient(blob)

    temp_blob = dict(blob)
    temp_blob["related_company"] = company
    temp_blob["related_ingredient"] = ingredient

    rel = corrected_relationship_strength(temp_blob, etype)
    status, reason = audit_decision(temp_blob, etype, rel)
    safe, unsafe = safe_wording(temp_blob, rel, etype, company, ingredient)
    scope = claim_scope(rel, etype)
    flags = support_flags(temp_blob, status, rel, etype)

    allowed = display_allowed(status, rel, etype, temp_blob)
    priority = display_priority(temp_blob, rel, status)

    audited = dict(blob)
    audited.update({
        "audit_status": status,
        "audit_reason": reason,
        "corrected_evidence_type": etype,
        "corrected_relationship_strength": rel,
        "corrected_related_company": company,
        "corrected_related_ingredient": ingredient,
        "claim_scope": scope,
        "display_allowed": allowed,
        "reason_display_allowed": (
            "Approved by Level 2 local audit with scoped wording."
            if allowed else
            "Not display-ready without later AI/manual review or because it is reference-only/rejected."
        ),
        "safe_website_wording": safe,
        "unsafe_wording_to_avoid": unsafe,
        "display_priority": priority,
        "human_review_required": (
            blob.get("requires_human_review", False)
            or status == "needs_review"
            or (blob.get("packet") in ["retail_price_evidence", "product_sku_1_55oz"] and blob.get("requires_human_review"))
        ),
        **flags,
        "level2_audit_meta": {
            "auditor": "step10_level2_local_evidence_audit",
            "audited_at": datetime.now().isoformat(timespec="seconds"),
            "audit_type": "deterministic_local_safety_filter"
        }
    })

    return audited


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    input_path = root / "artifacts" / "03_evidence_blobs" / "evidence_blobs.json"
    out_dir = root / "artifacts" / "04_level2_audited_blobs"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Missing evidence blobs: {input_path}")

    evidence_blobs = read_json(input_path)
    audited_blobs = [audit_blob(blob) for blob in evidence_blobs]

    approved = [b for b in audited_blobs if b["audit_status"] == "approved"]
    needs_review = [b for b in audited_blobs if b["audit_status"] == "needs_review"]
    rejected = [b for b in audited_blobs if b["audit_status"] == "rejected"]
    display_candidates = [b for b in audited_blobs if b["display_allowed"]]

    audited_path = out_dir / "audited_evidence_blobs.json"
    approved_path = out_dir / "approved_evidence_blobs.json"
    needs_review_path = out_dir / "needs_review_evidence_blobs.json"
    rejected_path = out_dir / "rejected_evidence_blobs.json"
    display_path = out_dir / "approved_display_candidates.json"

    write_json(audited_path, audited_blobs)
    write_json(approved_path, approved)
    write_json(needs_review_path, needs_review)
    write_json(rejected_path, rejected)
    write_json(display_path, display_candidates)

    summary_csv = out_dir / "audited_evidence_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "evidence_id",
            "doc_id",
            "source_file",
            "packet",
            "category",
            "audit_status",
            "audit_reason",
            "corrected_evidence_type",
            "corrected_relationship_strength",
            "claim_scope",
            "corrected_related_company",
            "corrected_related_ingredient",
            "related_cost_bucket",
            "display_allowed",
            "display_priority",
            "human_review_required",
            "supports_node",
            "supports_edge",
            "supports_cost_bucket",
            "supports_supplier_packet",
            "supports_ingredient_packet",
            "claim",
            "safe_website_wording",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for b in audited_blobs:
            writer.writerow({
                "evidence_id": b.get("evidence_id"),
                "doc_id": b.get("doc_id"),
                "source_file": b.get("source_file"),
                "packet": b.get("packet"),
                "category": b.get("category"),
                "audit_status": b.get("audit_status"),
                "audit_reason": b.get("audit_reason"),
                "corrected_evidence_type": b.get("corrected_evidence_type"),
                "corrected_relationship_strength": b.get("corrected_relationship_strength"),
                "claim_scope": b.get("claim_scope"),
                "corrected_related_company": b.get("corrected_related_company"),
                "corrected_related_ingredient": b.get("corrected_related_ingredient"),
                "related_cost_bucket": b.get("related_cost_bucket"),
                "display_allowed": b.get("display_allowed"),
                "display_priority": b.get("display_priority"),
                "human_review_required": b.get("human_review_required"),
                "supports_node": b.get("supports_node"),
                "supports_edge": b.get("supports_edge"),
                "supports_cost_bucket": b.get("supports_cost_bucket"),
                "supports_supplier_packet": b.get("supports_supplier_packet"),
                "supports_ingredient_packet": b.get("supports_ingredient_packet"),
                "claim": b.get("claim"),
                "safe_website_wording": b.get("safe_website_wording"),
            })

    audit_status_counts: dict[str, int] = {}
    relationship_counts: dict[str, int] = {}
    evidence_type_counts: dict[str, int] = {}
    packet_counts: dict[str, int] = {}

    for b in audited_blobs:
        audit_status_counts[b["audit_status"]] = audit_status_counts.get(b["audit_status"], 0) + 1
        relationship_counts[b["corrected_relationship_strength"]] = relationship_counts.get(b["corrected_relationship_strength"], 0) + 1
        evidence_type_counts[b["corrected_evidence_type"]] = evidence_type_counts.get(b["corrected_evidence_type"], 0) + 1
        packet_counts[b["packet"]] = packet_counts.get(b["packet"], 0) + 1

    report = {
        "run_name": "step10_level2_evidence_audit",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "evidence_blobs_seen": len(evidence_blobs),
        "approved_count": len(approved),
        "needs_review_count": len(needs_review),
        "rejected_count": len(rejected),
        "display_allowed_count": len(display_candidates),
        "audit_status_counts": audit_status_counts,
        "corrected_evidence_type_counts": evidence_type_counts,
        "corrected_relationship_strength_counts": relationship_counts,
        "packet_counts": packet_counts,
        "audited_evidence_blobs_json": str(audited_path).replace("\\", "/"),
        "approved_evidence_blobs_json": str(approved_path).replace("\\", "/"),
        "needs_review_evidence_blobs_json": str(needs_review_path).replace("\\", "/"),
        "rejected_evidence_blobs_json": str(rejected_path).replace("\\", "/"),
        "approved_display_candidates_json": str(display_path).replace("\\", "/"),
        "audited_summary_csv": str(summary_csv).replace("\\", "/"),
        "next_step": "Step 11: build supplier and ingredient packets from audited evidence."
    }

    report_path = report_dir / "step10_level2_evidence_audit_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 10 LEVEL 2 EVIDENCE AUDIT COMPLETE")
    print("---------------------------------------")
    print(f"Evidence blobs seen: {len(evidence_blobs)}")
    print(f"Approved: {len(approved)}")
    print(f"Needs review: {len(needs_review)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Display allowed: {len(display_candidates)}")
    print("")
    print(f"Audited JSON: {audited_path}")
    print(f"Summary CSV:  {summary_csv}")
    print(f"Report JSON:  {report_path}")
    print("")


if __name__ == "__main__":
    main()