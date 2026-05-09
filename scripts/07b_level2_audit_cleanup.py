from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


KNOWN_INGREDIENT_BY_PACKET = {
    "sugar": "Sugar",
    "cocoa_chocolate_cocoa_butter": "Cocoa / Chocolate / Cocoa Butter",
    "dairy_milk_skim_milk_milk_fat": "Milk / Skim Milk / Milk Fat",
    "soy_lecithin": "Soy Lecithin",
    "pgpr": "PGPR",
    "natural_flavor": "Natural Flavor",
    "packaging_wrapper": "Packaging / Wrapper",
    "product_sku_1_55oz": "HERSHEY'S Milk Chocolate Candy Bar 1.55 oz / 43 g",
    "retail_price_evidence": "Retail Price Evidence",
}

TRUSTED_SUPPLIER_FILES = {
    "sugar": [
        "hershey_sugar_sourcing_page",
        "asr_hershey_learn_to_grow_belize",
        "hershey_sustainable_sugar_sourcing_policy",
    ],
    "cocoa_chocolate_cocoa_butter": [
        "barry_callebaut_hershey_supply_agreement_news_release",
    ],
    "dairy_milk_skim_milk_milk_fat": [
        "hershey_dairy_sourcing_page",
        "hershey_sustainable_dairy_pa_2021_press_release",
        "epa_hershey_land_o_lakes_pa_dairy_farms_2m_commitment",
        "land_o_lakes_hershey_chesapeake_bay_page",
        "alliance_sustainable_dairy_pa_page",
    ],
    "logistics_distribution": [
        "hershey_10k_mclane_customer_section",
        "hershey_10k_distribution_common_carriers_section",
        "hershey_distribution_center_logistics_reference",
    ],
}

SUPPLIER_BY_PACKET = {
    "sugar": "American Sugar Refining / ASR",
    "cocoa_chocolate_cocoa_butter": "Barry Callebaut",
    "dairy_milk_skim_milk_milk_fat": "Land O'Lakes",
    "logistics_distribution": "McLane",
}

WEAK_TEXT_PHRASES = [
    "local level 1 parse",
    "source document available for packet",
    "detected entities/stages include: none detected",
    "no extracted text available",
    "likely image/logo",
]

GENERIC_BAD_COST_PHRASES = [
    "share price",
    "market capitalization",
    "price-earnings",
    "gdp",
    "marketing opportunities",
    "marketing for our beloved brands",
    "efficient and cost-effective manner",
    "export markets include",
    "source contains cost, price, market, benchmark, or index language",
]

BENCHMARK_HINTS = [
    "usda",
    "ers",
    "ams",
    "bls",
    "ppi",
    "fred",
    "eia",
    "icco",
    "ice",
    "futures",
    "market",
    "price",
    "prices",
    "monthly",
    "weekly",
    "index",
    "benchmark",
    "dairy market news",
    "national dairy products",
    "sugar and sweeteners",
    "producer price index",
]

RELATIONSHIP_WORDS = [
    "agreement",
    "long-term",
    "partnership",
    "partner",
    "supplier",
    "supplies",
    "sourcing",
    "sourced",
    "customer",
    "provides",
    "distribution",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def lower_all(blob: dict[str, Any]) -> str:
    return " ".join(
        [
            clean(blob.get("source_file")),
            clean(blob.get("claim")),
            clean(blob.get("evidence_text")),
            clean(blob.get("safe_website_wording")),
            clean(blob.get("corrected_related_company")),
            clean(blob.get("corrected_related_ingredient")),
            clean(blob.get("related_cost_bucket")),
        ]
    ).lower()


def source_stem(blob: dict[str, Any]) -> str:
    return Path(clean(blob.get("source_file"))).stem.lower()


def has_any(text: str, terms: list[str]) -> bool:
    return any(term.lower() in text for term in terms)


def has_number(text: str) -> bool:
    return bool(re.search(r"\d", text or ""))


def is_weak(blob: dict[str, Any]) -> bool:
    text = lower_all(blob)
    evidence = clean(blob.get("evidence_text")).lower()
    return has_any(text, WEAK_TEXT_PHRASES) or has_any(evidence, WEAK_TEXT_PHRASES)


def is_trusted_supplier_source(blob: dict[str, Any]) -> bool:
    packet = clean(blob.get("packet"))
    name = source_stem(blob)
    text = lower_all(blob)

    trusted_names = TRUSTED_SUPPLIER_FILES.get(packet, [])
    if any(item in name for item in trusted_names):
        return True

    supplier = SUPPLIER_BY_PACKET.get(packet, "")
    if supplier:
        supplier_key = supplier.lower().split("/")[0].strip()
        if supplier_key in text and "hershey" in text and has_any(text, RELATIONSHIP_WORDS):
            return True

    return False


def is_good_cost_context(blob: dict[str, Any]) -> bool:
    text = lower_all(blob)
    evidence = clean(blob.get("evidence_text")).lower()

    if clean(blob.get("category")) != "cost":
        return False

    if len(evidence) < 45:
        return False

    if has_any(evidence, GENERIC_BAD_COST_PHRASES):
        return False

    if not has_number(evidence) and not has_any(text, BENCHMARK_HINTS):
        return False

    return True


def infer_company(blob: dict[str, Any]) -> str:
    packet = clean(blob.get("packet"))
    name = source_stem(blob)
    text = lower_all(blob)

    if packet in SUPPLIER_BY_PACKET and is_trusted_supplier_source(blob):
        return SUPPLIER_BY_PACKET[packet]

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

    return clean(blob.get("corrected_related_company"))


def infer_ingredient(blob: dict[str, Any]) -> str:
    packet = clean(blob.get("packet"))
    text = lower_all(blob)

    if packet in KNOWN_INGREDIENT_BY_PACKET:
        return KNOWN_INGREDIENT_BY_PACKET[packet]

    if "cocoa butter" in text:
        return "Cocoa Butter"
    if "cocoa" in text or "chocolate" in text:
        return "Cocoa / Chocolate"
    if "milk" in text or "dairy" in text:
        return "Milk / Dairy"
    if "sugar" in text:
        return "Sugar"
    if "pgpr" in text:
        return "PGPR"
    if "lecithin" in text:
        return "Soy Lecithin"
    if "natural flavor" in text:
        return "Natural Flavor"

    return clean(blob.get("corrected_related_ingredient"))


def safe_wording(blob: dict[str, Any], status: str, rel: str, company: str, ingredient: str) -> tuple[str, str]:
    packet = clean(blob.get("packet"))
    source = clean(blob.get("source_file"))

    if status == "rejected":
        return (
            "Rejected from display because this evidence is too generic, weak, or not useful for the current supply-chain model.",
            "Do not use rejected evidence for website claims."
        )

    if clean(blob.get("corrected_evidence_type")) == "reference_only":
        return (
            "This file can be used only as a visual/reference asset. It does not support supplier, route, or cost claims.",
            "This visual/reference file proves supplier, route, or cost evidence."
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
                "McLane/Hershey evidence supports company-level downstream or distribution context. Exact route for the 1.55 oz bar is not publicly confirmed.",
                "McLane distributes every 1.55 oz Hershey bar to every retailer."
            )

    if rel == "sku_level_confirmed" and packet == "retail_price_evidence":
        return (
            f"{company} is retained as SKU-level retail price evidence for the HERSHEY'S 1.55 oz bar, pending final visual price verification.",
            "This retailer price proves Hershey's internal cost, margin, or supplier invoice cost."
        )

    if rel == "sku_level_confirmed" and packet == "product_sku_1_55oz":
        return (
            "This source supports the product/SKU identity for the HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g.",
            "This product image alone proves supplier relationships or cost values."
        )

    if rel == "benchmark_only":
        return (
            f"{source} can support benchmark, process, regulatory, or market context for {ingredient or packet}. It does not represent Hershey's exact SKU-level invoice cost.",
            "This benchmark equals Hershey's actual per-bar cost or supplier invoice."
        )

    return (
        f"{ingredient or packet} is retained as a modeled input, but supplier and SKU-level allocation remain unconfirmed unless direct evidence supports them.",
        "Do not imply exact supplier, route, or cost without direct evidence."
    )


def strict_audit(blob: dict[str, Any]) -> dict[str, Any]:
    b = dict(blob)

    packet = clean(b.get("packet"))
    category = clean(b.get("category"))
    evidence_type = clean(b.get("corrected_evidence_type") or b.get("evidence_type"))
    company = infer_company(b)
    ingredient = infer_ingredient(b)

    status = clean(b.get("audit_status"))
    reason = clean(b.get("audit_reason"))
    rel = clean(b.get("corrected_relationship_strength") or b.get("relationship_strength"))

    weak = is_weak(b)
    trusted_supplier = is_trusted_supplier_source(b)
    good_cost = is_good_cost_context(b)

    # Hard resets for categories.
    if evidence_type == "reference_only" or category == "visual_asset" or packet in ["brand_logo_assets", "reference_only"]:
        status = "approved"
        reason = "Approved only as reference/visual context."
        evidence_type = "reference_only"
        rel = "illustrative_only"

    elif category == "cost":
        if good_cost:
            status = "approved"
            reason = "Approved strictly as benchmark/cost context only."
            evidence_type = "benchmark_proxy"
            rel = "benchmark_only"
        else:
            status = "rejected"
            reason = "Rejected because the cost signal is generic, weak, too short, or not useful for cost modeling."
            evidence_type = "benchmark_proxy"
            rel = "benchmark_only"

    elif packet == "retail_price_evidence":
        status = "needs_review"
        reason = "Retail price source requires final visual verification before display."
        evidence_type = "direct"
        rel = "sku_level_confirmed"

    elif packet == "product_sku_1_55oz":
        status = "needs_review" if weak else "approved"
        reason = "Product/SKU evidence requires visual verification before final display." if weak else "Approved as product/SKU identity context."
        evidence_type = "direct"
        rel = "sku_level_confirmed"

    elif category == "supplier":
        if trusted_supplier and not weak:
            status = "approved"
            reason = "Approved as company-level supplier relationship evidence with scoped wording."
            evidence_type = "direct"
            rel = "company_level_confirmed"
        elif trusted_supplier:
            status = "needs_review"
            reason = "Trusted supplier source, but extracted evidence is weak and needs manual/AI review."
            evidence_type = "direct"
            rel = "company_level_confirmed"
        else:
            status = "needs_review"
            reason = "Supplier-like evidence is not strong enough for display without review."
            rel = "unknown" if rel not in ["benchmark_only"] else rel

    elif packet in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"]:
        if weak:
            status = "needs_review"
            reason = "Ingredient/function source has weak extraction and needs review."
            rel = "unknown"
        else:
            status = "approved"
            reason = "Approved as ingredient/function/process context with supplier unknown."
            rel = "unknown" if packet in ["soy_lecithin", "pgpr", "natural_flavor"] else "benchmark_only"

    elif weak:
        status = "needs_review"
        reason = "Weak extraction; retained for review but not display."

    # Supplier packet support must be very strict.
    supports_supplier_packet = (
        status == "approved"
        and category == "supplier"
        and rel == "company_level_confirmed"
        and trusted_supplier
    )

    supports_edge = (
        status == "approved"
        and rel in ["company_level_confirmed", "sku_level_confirmed"]
        and category in ["supplier", "retail"]
    )

    supports_cost_bucket = (
        status == "approved"
        and category == "cost"
        and rel == "benchmark_only"
        and good_cost
    )

    supports_ingredient_packet = (
        status != "rejected"
        and packet in KNOWN_INGREDIENT_BY_PACKET
    )

    supports_node = (
        status != "rejected"
        and category in ["ingredient", "packaging", "logistics", "retail", "supplier", "product_sku", "visual_asset"]
    )

    # Display is now stricter.
    display_allowed = False
    if status == "approved" and evidence_type != "reference_only":
        if supports_supplier_packet or supports_cost_bucket:
            display_allowed = True
        elif packet in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"] and not weak:
            display_allowed = True

    safe, unsafe = safe_wording(b, status, rel, company, ingredient)

    if rel == "company_level_confirmed":
        claim_scope = "company_level"
    elif rel == "sku_level_confirmed":
        claim_scope = "sku_level"
    elif rel == "benchmark_only":
        claim_scope = "market_level"
    elif rel == "illustrative_only":
        claim_scope = "illustrative_only"
    else:
        claim_scope = "assumption_or_needs_review"

    display_priority = 0
    if display_allowed:
        display_priority = 50
        if supports_supplier_packet:
            display_priority += 20
        if supports_cost_bucket:
            display_priority += 10
        if packet in ["sugar", "cocoa_chocolate_cocoa_butter", "dairy_milk_skim_milk_milk_fat"]:
            display_priority += 10

    b.update(
        {
            "audit_status": status,
            "audit_reason": reason,
            "corrected_evidence_type": evidence_type,
            "corrected_relationship_strength": rel,
            "corrected_related_company": company,
            "corrected_related_ingredient": ingredient,
            "claim_scope": claim_scope,
            "display_allowed": display_allowed,
            "reason_display_allowed": (
                "Approved by strict Step 10B cleanup."
                if display_allowed
                else "Not display-ready under strict Step 10B cleanup."
            ),
            "safe_website_wording": safe,
            "unsafe_wording_to_avoid": unsafe,
            "display_priority": display_priority,
            "human_review_required": status == "needs_review" or bool(b.get("requires_human_review")),
            "supports_node": supports_node,
            "supports_edge": supports_edge,
            "supports_cost_bucket": supports_cost_bucket,
            "supports_supplier_packet": supports_supplier_packet,
            "supports_ingredient_packet": supports_ingredient_packet,
            "supports_display_blob": display_allowed,
            "step10b_cleanup_meta": {
                "cleanup_script": "07b_level2_audit_cleanup.py",
                "cleaned_at": datetime.now().isoformat(timespec="seconds"),
                "strict_rules": True,
            },
        }
    )

    return b


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda item: item[0]))


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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
        "supports_display_blob",
        "claim",
        "safe_website_wording",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    input_path = root / "artifacts" / "04_level2_audited_blobs" / "audited_evidence_blobs.json"
    out_dir = root / "artifacts" / "04_level2_audited_blobs_strict"
    report_dir = root / "artifacts" / "10_run_reports"

    if not input_path.exists():
        raise FileNotFoundError(f"Missing Step 10 audited evidence file: {input_path}")

    original = read_json(input_path)
    cleaned = [strict_audit(blob) for blob in original]

    approved = [b for b in cleaned if b["audit_status"] == "approved"]
    needs_review = [b for b in cleaned if b["audit_status"] == "needs_review"]
    rejected = [b for b in cleaned if b["audit_status"] == "rejected"]
    display = [b for b in cleaned if b["display_allowed"]]

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    write_json(out_dir / "audited_evidence_blobs_strict.json", cleaned)
    write_json(out_dir / "approved_evidence_blobs_strict.json", approved)
    write_json(out_dir / "needs_review_evidence_blobs_strict.json", needs_review)
    write_json(out_dir / "rejected_evidence_blobs_strict.json", rejected)
    write_json(out_dir / "approved_display_candidates_strict.json", display)

    write_summary_csv(out_dir / "audited_evidence_summary_strict.csv", cleaned)

    report = {
        "run_name": "step10b_level2_strict_evidence_cleanup",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "input_evidence_rows": len(original),
        "cleaned_evidence_rows": len(cleaned),
        "approved_count": len(approved),
        "needs_review_count": len(needs_review),
        "rejected_count": len(rejected),
        "display_allowed_count": len(display),
        "audit_status_counts": count_by(cleaned, "audit_status"),
        "corrected_evidence_type_counts": count_by(cleaned, "corrected_evidence_type"),
        "corrected_relationship_strength_counts": count_by(cleaned, "corrected_relationship_strength"),
        "display_allowed_by_packet": count_by(display, "packet"),
        "supports_supplier_packet_count": sum(1 for b in cleaned if b.get("supports_supplier_packet")),
        "supports_edge_count": sum(1 for b in cleaned if b.get("supports_edge")),
        "supports_cost_bucket_count": sum(1 for b in cleaned if b.get("supports_cost_bucket")),
        "strict_output_folder": str(out_dir).replace("\\", "/"),
        "strict_audited_json": str(out_dir / "audited_evidence_blobs_strict.json").replace("\\", "/"),
        "strict_summary_csv": str(out_dir / "audited_evidence_summary_strict.csv").replace("\\", "/"),
        "strict_display_candidates_json": str(out_dir / "approved_display_candidates_strict.json").replace("\\", "/"),
        "next_step": "Step 11 should use the strict audited evidence folder, not the loose Step 10 folder.",
    }

    report_path = report_dir / "step10b_level2_strict_evidence_cleanup_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 10B STRICT EVIDENCE CLEANUP COMPLETE")
    print("----------------------------------------")
    print(f"Input evidence rows: {len(original)}")
    print(f"Approved: {len(approved)}")
    print(f"Needs review: {len(needs_review)}")
    print(f"Rejected: {len(rejected)}")
    print(f"Display allowed strict: {len(display)}")
    print(f"Supplier packet support: {report['supports_supplier_packet_count']}")
    print(f"Edge support: {report['supports_edge_count']}")
    print(f"Cost bucket support: {report['supports_cost_bucket_count']}")
    print("")
    print(f"Report JSON: {report_path}")
    print(f"Strict CSV:  {out_dir / 'audited_evidence_summary_strict.csv'}")
    print("")


if __name__ == "__main__":
    main()