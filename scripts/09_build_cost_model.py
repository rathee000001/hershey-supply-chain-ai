from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


GRAMS_PER_BAR = 43.0
GRAMS_PER_LB = 453.59237


INGREDIENT_COST_ASSUMPTIONS = {
    "ING_SUGAR": {
        "cost_bucket_id": "COST_ING_SUGAR",
        "cost_bucket": "Sugar",
        "cost_type": "ingredient",
        "grams_low": 21.0,
        "grams_base": 24.0,
        "grams_high": 26.0,
        "price_low_per_lb": 0.35,
        "price_base_per_lb": 0.55,
        "price_high_per_lb": 0.80,
        "evidence_packet": "sugar",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "medium",
        "cost_logic": (
            "Estimated sugar grams are anchored to the 43 g bar and expected sugar-heavy chocolate formulation. "
            "Price is a refined-sugar benchmark proxy, not Hershey invoice cost."
        ),
    },
    "ING_COCOA_CHOCOLATE": {
        "cost_bucket_id": "COST_ING_COCOA_CHOCOLATE",
        "cost_bucket": "Chocolate / Cocoa",
        "cost_type": "ingredient",
        "grams_low": 4.0,
        "grams_base": 5.5,
        "grams_high": 7.0,
        "price_low_per_lb": 3.00,
        "price_base_per_lb": 5.00,
        "price_high_per_lb": 8.00,
        "evidence_packet": "cocoa_chocolate_cocoa_butter",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Cocoa/chocolate mass allocation is estimated because Hershey does not disclose the exact bill of materials. "
            "Benchmark price represents cocoa/chocolate ingredient proxy, not actual contract price."
        ),
    },
    "ING_COCOA_BUTTER": {
        "cost_bucket_id": "COST_ING_COCOA_BUTTER",
        "cost_bucket": "Cocoa Butter",
        "cost_type": "ingredient",
        "grams_low": 3.0,
        "grams_base": 4.5,
        "grams_high": 6.0,
        "price_low_per_lb": 5.50,
        "price_base_per_lb": 8.50,
        "price_high_per_lb": 12.50,
        "evidence_packet": "cocoa_chocolate_cocoa_butter",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Cocoa butter is modeled separately from cocoa/chocolate because it is a distinct ingredient stream. "
            "Weight and price are benchmark assumptions."
        ),
    },
    "ING_MILK": {
        "cost_bucket_id": "COST_ING_MILK",
        "cost_bucket": "Milk / Dairy Solids",
        "cost_type": "ingredient",
        "grams_low": 2.0,
        "grams_base": 3.0,
        "grams_high": 4.0,
        "price_low_per_lb": 1.10,
        "price_base_per_lb": 1.60,
        "price_high_per_lb": 2.20,
        "evidence_packet": "dairy_milk_skim_milk_milk_fat",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Milk is modeled as a dairy solids input rather than liquid milk weight. "
            "Price is a dairy product benchmark proxy."
        ),
    },
    "ING_SKIM_MILK": {
        "cost_bucket_id": "COST_ING_SKIM_MILK",
        "cost_bucket": "Skim Milk / Nonfat Solids",
        "cost_type": "ingredient",
        "grams_low": 1.0,
        "grams_base": 2.0,
        "grams_high": 3.0,
        "price_low_per_lb": 1.00,
        "price_base_per_lb": 1.35,
        "price_high_per_lb": 1.80,
        "evidence_packet": "dairy_milk_skim_milk_milk_fat",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Skim milk is proxied with nonfat dry milk / dairy solids pricing. "
            "Exact ingredient form and quantity are not publicly disclosed."
        ),
    },
    "ING_MILK_FAT": {
        "cost_bucket_id": "COST_ING_MILK_FAT",
        "cost_bucket": "Milk Fat / Butterfat",
        "cost_type": "ingredient",
        "grams_low": 1.5,
        "grams_base": 2.5,
        "grams_high": 3.5,
        "price_low_per_lb": 2.20,
        "price_base_per_lb": 3.00,
        "price_high_per_lb": 4.20,
        "evidence_packet": "dairy_milk_skim_milk_milk_fat",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Milk fat is proxied using butterfat/butter-related dairy benchmarks. "
            "Exact milk fat quantity is modeled, not disclosed."
        ),
    },
    "ING_SOY_LECITHIN": {
        "cost_bucket_id": "COST_ING_SOY_LECITHIN",
        "cost_bucket": "Soy Lecithin",
        "cost_type": "ingredient",
        "grams_low": 0.08,
        "grams_base": 0.15,
        "grams_high": 0.30,
        "price_low_per_lb": 1.50,
        "price_base_per_lb": 2.50,
        "price_high_per_lb": 4.00,
        "evidence_packet": "soy_lecithin",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Soy lecithin is used at very small emulsifier rates. "
            "Supplier is unknown and price is a specialty ingredient proxy."
        ),
    },
    "ING_PGPR": {
        "cost_bucket_id": "COST_ING_PGPR",
        "cost_bucket": "PGPR",
        "cost_type": "ingredient",
        "grams_low": 0.03,
        "grams_base": 0.06,
        "grams_high": 0.12,
        "price_low_per_lb": 4.00,
        "price_base_per_lb": 7.00,
        "price_high_per_lb": 12.00,
        "evidence_packet": "pgpr",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "PGPR is modeled as a tiny specialty emulsifier/flow-modifier input. "
            "Supplier is unknown and price is a specialty ingredient proxy."
        ),
    },
    "ING_NATURAL_FLAVOR": {
        "cost_bucket_id": "COST_ING_NATURAL_FLAVOR",
        "cost_bucket": "Natural Flavor",
        "cost_type": "ingredient",
        "grams_low": 0.01,
        "grams_base": 0.03,
        "grams_high": 0.08,
        "price_low_per_lb": 8.00,
        "price_base_per_lb": 18.00,
        "price_high_per_lb": 35.00,
        "evidence_packet": "natural_flavor",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Natural flavor is modeled as a very small flavor input. "
            "Exact composition and supplier are unknown."
        ),
    },
}


NON_INGREDIENT_COST_ASSUMPTIONS = [
    {
        "cost_bucket_id": "COST_PACKAGING_PRIMARY_SECONDARY",
        "cost_bucket": "Packaging / Wrapper / Secondary Packaging",
        "cost_type": "packaging",
        "low_cents_per_bar": 1.5,
        "base_cents_per_bar": 2.8,
        "high_cents_per_bar": 5.0,
        "evidence_packet": "packaging_wrapper",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Packaging includes primary wrapper plus allocated paperboard/case packaging. "
            "Exact wrapper supplier and exact SKU packaging cost are not public."
        ),
    },
    {
        "cost_bucket_id": "COST_MANUFACTURING_CONVERSION",
        "cost_bucket": "Manufacturing Conversion",
        "cost_type": "manufacturing_conversion",
        "low_cents_per_bar": 3.0,
        "base_cents_per_bar": 6.0,
        "high_cents_per_bar": 10.0,
        "evidence_packet": "hershey_company",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Manufacturing conversion includes labor, utilities, overhead, maintenance, depreciation, and plant operations allocation. "
            "This is a modeled public-information allocation, not Hershey internal SKU accounting."
        ),
    },
    {
        "cost_bucket_id": "COST_STORAGE_WAREHOUSING",
        "cost_bucket": "Storage / Warehousing",
        "cost_type": "storage",
        "low_cents_per_bar": 0.3,
        "base_cents_per_bar": 0.8,
        "high_cents_per_bar": 1.5,
        "evidence_packet": "logistics_distribution",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Storage and warehousing are allocated using public logistics/warehousing benchmark context. "
            "Exact SKU storage cost is not public."
        ),
    },
    {
        "cost_bucket_id": "COST_OUTBOUND_FREIGHT",
        "cost_bucket": "Outbound Freight / Trucking",
        "cost_type": "freight",
        "low_cents_per_bar": 0.5,
        "base_cents_per_bar": 1.2,
        "high_cents_per_bar": 2.5,
        "evidence_packet": "logistics_distribution",
        "evidence_type": "assumption_supported_by_evidence",
        "confidence_level": "low",
        "cost_logic": (
            "Freight is allocated using trucking/diesel/logistics benchmark context. "
            "Exact route cost for the 1.55 oz SKU is not public."
        ),
    },
]


RETAIL_PRICE_PLACEHOLDER = {
    "cost_bucket_id": "COST_RETAIL_PRICE_VISUAL_VERIFICATION_PENDING",
    "cost_bucket": "Observed Retail Shelf Price",
    "cost_type": "retail_price",
    "low_cents_per_bar": None,
    "base_cents_per_bar": None,
    "high_cents_per_bar": None,
    "evidence_packet": "retail_price_evidence",
    "evidence_type": "direct_but_visual_verification_pending",
    "confidence_level": "unknown",
    "cost_logic": (
        "Retail price pages were collected, but exact shelf prices are not entered into the cost model until final visual verification. "
        "This prevents using screenshot/PDF prices incorrectly."
    ),
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def dollars_per_lb_to_cents_per_gram(price_per_lb: float) -> float:
    return (price_per_lb / GRAMS_PER_LB) * 100.0


def ingredient_cost_cents(grams: float, price_per_lb: float) -> float:
    return grams * dollars_per_lb_to_cents_per_gram(price_per_lb)


def round4(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)


def evidence_ids_for_packet(
    audited_rows: list[dict[str, Any]],
    packet: str,
    limit: int = 20,
) -> list[str]:
    ids = []

    for row in audited_rows:
        if row.get("packet") != packet:
            continue

        if row.get("audit_status") == "rejected":
            continue

        if row.get("supports_cost_bucket") or row.get("display_allowed") or row.get("supports_ingredient_packet"):
            ids.append(row.get("evidence_id"))

    return sorted(set([x for x in ids if x]))[:limit]


def build_assumptions_register() -> list[dict[str, Any]]:
    rows = []

    for ingredient_id, item in INGREDIENT_COST_ASSUMPTIONS.items():
        rows.append(
            {
                "assumption_id": f"ASM_{ingredient_id}",
                "assumption_type": "ingredient_quantity_and_price_proxy",
                "related_id": ingredient_id,
                "description": item["cost_logic"],
                "low_value": {
                    "grams": item["grams_low"],
                    "price_per_lb": item["price_low_per_lb"],
                },
                "base_value": {
                    "grams": item["grams_base"],
                    "price_per_lb": item["price_base_per_lb"],
                },
                "high_value": {
                    "grams": item["grams_high"],
                    "price_per_lb": item["price_high_per_lb"],
                },
                "confidence_level": item["confidence_level"],
                "display_note": "Modeled estimate; not Hershey proprietary SKU-level cost accounting.",
            }
        )

    for item in NON_INGREDIENT_COST_ASSUMPTIONS:
        rows.append(
            {
                "assumption_id": f"ASM_{item['cost_bucket_id']}",
                "assumption_type": "non_ingredient_cost_allocation",
                "related_id": item["cost_bucket_id"],
                "description": item["cost_logic"],
                "low_value": {"cents_per_bar": item["low_cents_per_bar"]},
                "base_value": {"cents_per_bar": item["base_cents_per_bar"]},
                "high_value": {"cents_per_bar": item["high_cents_per_bar"]},
                "confidence_level": item["confidence_level"],
                "display_note": "Allocation estimate; not Hershey proprietary SKU-level cost accounting.",
            }
        )

    rows.append(
        {
            "assumption_id": "ASM_RETAIL_PRICE_PENDING",
            "assumption_type": "retail_price_visual_verification",
            "related_id": RETAIL_PRICE_PLACEHOLDER["cost_bucket_id"],
            "description": RETAIL_PRICE_PLACEHOLDER["cost_logic"],
            "low_value": None,
            "base_value": None,
            "high_value": None,
            "confidence_level": "unknown",
            "display_note": "Retail price evidence is collected but not numerically used until visual verification.",
        }
    )

    return rows


def build_ingredient_cost_records(
    ingredient_packets: list[dict[str, Any]],
    audited_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cost_records = []
    costed_ingredients = []

    by_id = {item["ingredient_id"]: item for item in ingredient_packets}

    for ingredient_id, assumption in INGREDIENT_COST_ASSUMPTIONS.items():
        ingredient = dict(by_id.get(ingredient_id, {}))

        low = ingredient_cost_cents(assumption["grams_low"], assumption["price_low_per_lb"])
        base = ingredient_cost_cents(assumption["grams_base"], assumption["price_base_per_lb"])
        high = ingredient_cost_cents(assumption["grams_high"], assumption["price_high_per_lb"])

        source_ids = sorted(
            set(
                list(ingredient.get("source_evidence_ids", []))[:12]
                + evidence_ids_for_packet(audited_rows, assumption["evidence_packet"], limit=12)
            )
        )

        record = {
            "cost_bucket_id": assumption["cost_bucket_id"],
            "cost_bucket": assumption["cost_bucket"],
            "cost_type": assumption["cost_type"],
            "cost_logic": assumption["cost_logic"],
            "evidence_type": assumption["evidence_type"],
            "source_evidence_ids": source_ids,
            "low_cents_per_bar": round4(low),
            "base_cents_per_bar": round4(base),
            "high_cents_per_bar": round4(high),
            "confidence_level": assumption["confidence_level"],
            "notes": "Calculated from modeled grams per 43 g bar and benchmark price per lb. Not Hershey actual cost.",
            "calculation_inputs": {
                "grams_low": assumption["grams_low"],
                "grams_base": assumption["grams_base"],
                "grams_high": assumption["grams_high"],
                "price_low_per_lb": assumption["price_low_per_lb"],
                "price_base_per_lb": assumption["price_base_per_lb"],
                "price_high_per_lb": assumption["price_high_per_lb"],
                "formula": "grams_per_bar * (price_per_lb / 453.59237) * 100 = cents_per_bar",
            },
        }

        cost_records.append(record)

        if ingredient:
            ingredient["estimated_grams_low"] = assumption["grams_low"]
            ingredient["estimated_grams_base"] = assumption["grams_base"]
            ingredient["estimated_grams_high"] = assumption["grams_high"]
            ingredient["price_proxy_low_per_lb"] = assumption["price_low_per_lb"]
            ingredient["price_proxy_base_per_lb"] = assumption["price_base_per_lb"]
            ingredient["price_proxy_high_per_lb"] = assumption["price_high_per_lb"]
            ingredient["estimated_cost_low_cents"] = round4(low)
            ingredient["estimated_cost_base_cents"] = round4(base)
            ingredient["estimated_cost_high_cents"] = round4(high)
            ingredient["estimated_cost_status"] = "calculated"
            ingredient["cost_model_notes"] = record["notes"]
            costed_ingredients.append(ingredient)

    # Keep packaging ingredient packet in costed set if it exists, but its cost is non-ingredient bucket.
    for ingredient in ingredient_packets:
        if ingredient["ingredient_id"] not in INGREDIENT_COST_ASSUMPTIONS:
            costed_ingredients.append(ingredient)

    return cost_records, costed_ingredients


def build_non_ingredient_cost_records(audited_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []

    for item in NON_INGREDIENT_COST_ASSUMPTIONS:
        source_ids = evidence_ids_for_packet(audited_rows, item["evidence_packet"], limit=15)

        rows.append(
            {
                "cost_bucket_id": item["cost_bucket_id"],
                "cost_bucket": item["cost_bucket"],
                "cost_type": item["cost_type"],
                "cost_logic": item["cost_logic"],
                "evidence_type": item["evidence_type"],
                "source_evidence_ids": source_ids,
                "low_cents_per_bar": round4(item["low_cents_per_bar"]),
                "base_cents_per_bar": round4(item["base_cents_per_bar"]),
                "high_cents_per_bar": round4(item["high_cents_per_bar"]),
                "confidence_level": item["confidence_level"],
                "notes": "Allocation estimate. Not Hershey actual SKU-level cost.",
                "calculation_inputs": {
                    "allocation_low_cents": item["low_cents_per_bar"],
                    "allocation_base_cents": item["base_cents_per_bar"],
                    "allocation_high_cents": item["high_cents_per_bar"],
                },
            }
        )

    retail_source_ids = evidence_ids_for_packet(audited_rows, RETAIL_PRICE_PLACEHOLDER["evidence_packet"], limit=10)
    rows.append(
        {
            "cost_bucket_id": RETAIL_PRICE_PLACEHOLDER["cost_bucket_id"],
            "cost_bucket": RETAIL_PRICE_PLACEHOLDER["cost_bucket"],
            "cost_type": RETAIL_PRICE_PLACEHOLDER["cost_type"],
            "cost_logic": RETAIL_PRICE_PLACEHOLDER["cost_logic"],
            "evidence_type": RETAIL_PRICE_PLACEHOLDER["evidence_type"],
            "source_evidence_ids": retail_source_ids,
            "low_cents_per_bar": None,
            "base_cents_per_bar": None,
            "high_cents_per_bar": None,
            "confidence_level": RETAIL_PRICE_PLACEHOLDER["confidence_level"],
            "notes": "Pending visual verification of retailer price pages.",
            "calculation_inputs": {},
        }
    )

    return rows


def summarize_cost_stack(cost_records: list[dict[str, Any]]) -> dict[str, Any]:
    included = [
        row for row in cost_records
        if row["cost_type"] not in ["retail_price", "residual_channel_pool"]
        and row["low_cents_per_bar"] is not None
    ]

    by_type: dict[str, dict[str, float]] = {}

    for row in included:
        cost_type = row["cost_type"]
        if cost_type not in by_type:
            by_type[cost_type] = {
                "low_cents_per_bar": 0.0,
                "base_cents_per_bar": 0.0,
                "high_cents_per_bar": 0.0,
            }

        by_type[cost_type]["low_cents_per_bar"] += float(row["low_cents_per_bar"])
        by_type[cost_type]["base_cents_per_bar"] += float(row["base_cents_per_bar"])
        by_type[cost_type]["high_cents_per_bar"] += float(row["high_cents_per_bar"])

    for item in by_type.values():
        item["low_cents_per_bar"] = round4(item["low_cents_per_bar"])
        item["base_cents_per_bar"] = round4(item["base_cents_per_bar"])
        item["high_cents_per_bar"] = round4(item["high_cents_per_bar"])

    total_low = sum(float(row["low_cents_per_bar"]) for row in included)
    total_base = sum(float(row["base_cents_per_bar"]) for row in included)
    total_high = sum(float(row["high_cents_per_bar"]) for row in included)

    return {
        "cost_stack_version": "v1_public_benchmark_assumption_model",
        "unit": "one HERSHEY'S Milk Chocolate Candy Bar, 1.55 oz / 43 g",
        "grams_per_bar": GRAMS_PER_BAR,
        "model_scope": "physical ingredient + packaging + conversion + logistics allocation estimate",
        "not_in_scope": [
            "Hershey proprietary SKU-level bill of materials",
            "actual supplier invoice prices",
            "actual plant route costs",
            "actual retailer margin",
            "actual Hershey gross margin"
        ],
        "totals": {
            "low_cents_per_bar": round4(total_low),
            "base_cents_per_bar": round4(total_base),
            "high_cents_per_bar": round4(total_high),
        },
        "totals_by_type": by_type,
        "retail_price_status": "pending_visual_verification",
        "retail_residual_status": "not_calculated_until_retail_price_is_verified",
        "safe_display_wording": (
            "This is a public-evidence benchmark cost model. It estimates physical supply-chain cost ranges per 1.55 oz bar "
            "and should not be read as Hershey's actual internal SKU cost."
        ),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def write_cost_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "cost_bucket_id",
        "cost_bucket",
        "cost_type",
        "evidence_type",
        "low_cents_per_bar",
        "base_cents_per_bar",
        "high_cents_per_bar",
        "confidence_level",
        "source_evidence_count",
        "notes",
        "cost_logic",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "cost_bucket_id": row["cost_bucket_id"],
                    "cost_bucket": row["cost_bucket"],
                    "cost_type": row["cost_type"],
                    "evidence_type": row["evidence_type"],
                    "low_cents_per_bar": row["low_cents_per_bar"],
                    "base_cents_per_bar": row["base_cents_per_bar"],
                    "high_cents_per_bar": row["high_cents_per_bar"],
                    "confidence_level": row["confidence_level"],
                    "source_evidence_count": len(row.get("source_evidence_ids", [])),
                    "notes": row["notes"],
                    "cost_logic": row["cost_logic"],
                }
            )


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

    ingredient_path = root / "artifacts" / "06_ingredient_blobs" / "ingredient_packets.json"
    strict_evidence_path = root / "artifacts" / "04_level2_audited_blobs_strict" / "audited_evidence_blobs_strict.json"

    out_dir = root / "artifacts" / "07_cost_model_blobs"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not ingredient_path.exists():
        raise FileNotFoundError(f"Missing ingredient packets: {ingredient_path}")

    if not strict_evidence_path.exists():
        raise FileNotFoundError(f"Missing strict evidence: {strict_evidence_path}")

    ingredient_packets = read_json(ingredient_path)
    audited_rows = read_json(strict_evidence_path)

    assumptions_register = build_assumptions_register()
    ingredient_cost_records, costed_ingredient_packets = build_ingredient_cost_records(
        ingredient_packets=ingredient_packets,
        audited_rows=audited_rows,
    )
    non_ingredient_records = build_non_ingredient_cost_records(audited_rows)

    cost_records = ingredient_cost_records + non_ingredient_records
    cost_stack_summary = summarize_cost_stack(cost_records)

    assumptions_path = out_dir / "assumptions_register.json"
    cost_assumptions_path = out_dir / "cost_assumptions_v1.json"
    cost_records_path = out_dir / "cost_model_records.json"
    cost_stack_path = out_dir / "cost_stack_summary.json"
    cost_csv_path = out_dir / "cost_model_summary.csv"
    costed_ingredients_path = out_dir / "ingredient_packets_costed.json"

    write_json(assumptions_path, assumptions_register)
    write_json(cost_assumptions_path, {
        "unit": "one 1.55 oz / 43 g bar",
        "grams_per_bar": GRAMS_PER_BAR,
        "ingredient_cost_assumptions": INGREDIENT_COST_ASSUMPTIONS,
        "non_ingredient_cost_assumptions": NON_INGREDIENT_COST_ASSUMPTIONS,
        "retail_price_placeholder": RETAIL_PRICE_PLACEHOLDER,
    })
    write_json(cost_records_path, cost_records)
    write_json(cost_stack_path, cost_stack_summary)
    write_json(costed_ingredients_path, costed_ingredient_packets)
    write_cost_csv(cost_csv_path, cost_records)

    report = {
        "run_name": "step12_cost_model_builder",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "ingredient_packets_seen": len(ingredient_packets),
        "ingredient_cost_records_created": len(ingredient_cost_records),
        "non_ingredient_cost_records_created": len(non_ingredient_records),
        "total_cost_records_created": len(cost_records),
        "cost_type_counts": count_by(cost_records, "cost_type"),
        "cost_stack_totals": cost_stack_summary["totals"],
        "retail_price_status": cost_stack_summary["retail_price_status"],
        "cost_records_json": str(cost_records_path).replace("\\", "/"),
        "cost_stack_summary_json": str(cost_stack_path).replace("\\", "/"),
        "cost_model_summary_csv": str(cost_csv_path).replace("\\", "/"),
        "ingredient_packets_costed_json": str(costed_ingredients_path).replace("\\", "/"),
        "assumptions_register_json": str(assumptions_path).replace("\\", "/"),
        "next_step": "Step 13: visual verification packet for product SKU and retail price pages, then retail residual calculation."
    }

    report_path = report_dir / "step12_cost_model_builder_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 12 COST MODEL BUILDER COMPLETE")
    print("-----------------------------------")
    print(f"Ingredient cost records: {len(ingredient_cost_records)}")
    print(f"Non-ingredient cost records: {len(non_ingredient_records)}")
    print(f"Total cost records: {len(cost_records)}")
    print(f"Low total cents/bar:  {cost_stack_summary['totals']['low_cents_per_bar']}")
    print(f"Base total cents/bar: {cost_stack_summary['totals']['base_cents_per_bar']}")
    print(f"High total cents/bar: {cost_stack_summary['totals']['high_cents_per_bar']}")
    print("")
    print(f"Cost stack JSON: {cost_stack_path}")
    print(f"Summary CSV:     {cost_csv_path}")
    print(f"Report JSON:     {report_path}")
    print("")


if __name__ == "__main__":
    main()