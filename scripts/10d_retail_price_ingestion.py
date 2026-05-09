from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any


PRODUCT_NAME = "HERSHEY'S Milk Chocolate Candy Bar"
EXPECTED_SIZE_OZ = 1.55
EXPECTED_SIZE_G = 43.0
EXPECTED_PACK_SIZE = 1


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: Any) -> float | None:
    text = str(value or "").strip().replace("$", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def as_int(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def round4(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)


def validate_retail_row(row: dict[str, str]) -> tuple[bool, list[str]]:
    warnings: list[str] = []

    retailer = str(row.get("retailer", "")).strip().lower()
    price = as_float(row.get("verified_price_usd"))
    size_oz = as_float(row.get("verified_size_oz"))
    size_g = as_float(row.get("verified_size_g"))
    pack_size = as_int(row.get("verified_pack_size"))
    status = str(row.get("verification_status", "")).strip().lower()

    if not retailer:
        warnings.append("Missing retailer.")
    if status != "verified":
        warnings.append("Verification status is not verified.")
    if price is None:
        warnings.append("Missing or invalid verified_price_usd.")
    elif not (0.25 <= price <= 10.00):
        warnings.append("Price outside expected single-bar range.")
    if size_oz is None or abs(size_oz - EXPECTED_SIZE_OZ) > 0.02:
        warnings.append("Size oz does not match expected 1.55 oz.")
    if size_g is None or abs(size_g - EXPECTED_SIZE_G) > 1.0:
        warnings.append("Size g does not match expected 43 g.")
    if pack_size != EXPECTED_PACK_SIZE:
        warnings.append("Pack size is not 1; possible multipack risk.")

    return len(warnings) == 0, warnings


def build_verified_retail_prices(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    verified: list[dict[str, Any]] = []
    rejected_or_warning: list[dict[str, Any]] = []

    for row in rows:
        valid, warnings = validate_retail_row(row)

        retailer = str(row.get("retailer", "")).strip().lower()
        price_usd = as_float(row.get("verified_price_usd"))

        item = {
            "retailer": retailer,
            "review_id": row.get("review_id", ""),
            "file_name": row.get("file_name", ""),
            "contact_sheet_path": row.get("contact_sheet_path", ""),
            "verified_product_name": row.get("verified_product_name", ""),
            "verified_size_oz": as_float(row.get("verified_size_oz")),
            "verified_size_g": as_float(row.get("verified_size_g")),
            "verified_pack_size": as_int(row.get("verified_pack_size")),
            "verified_price_usd": price_usd,
            "verified_price_cents": round4(price_usd * 100.0) if price_usd is not None else None,
            "verified_price_type": row.get("verified_price_type", ""),
            "verified_date_visible": row.get("verified_date_visible", ""),
            "verified_store_or_zip_visible": row.get("verified_store_or_zip_visible", ""),
            "verification_status": row.get("verification_status", ""),
            "manual_notes": row.get("manual_notes", ""),
            "validation_passed": valid,
            "validation_warnings": warnings,
        }

        if valid:
            verified.append(item)
        else:
            rejected_or_warning.append(item)

    return verified, rejected_or_warning


def summarize_retail_prices(verified: list[dict[str, Any]]) -> dict[str, Any]:
    cents = [float(item["verified_price_cents"]) for item in verified if item.get("verified_price_cents") is not None]

    if not cents:
        return {
            "retail_price_status": "not_verified",
            "retailers_verified": 0,
            "low_retail_price_cents": None,
            "base_retail_price_cents": None,
            "high_retail_price_cents": None,
            "average_retail_price_cents": None,
            "median_retail_price_cents": None,
            "low_retail_price_usd": None,
            "base_retail_price_usd": None,
            "high_retail_price_usd": None,
        }

    low = min(cents)
    high = max(cents)
    avg = sum(cents) / len(cents)
    median = statistics.median(cents)

    # Base uses average because this is a cross-retailer observed price range.
    base = avg

    return {
        "retail_price_status": "verified",
        "retailers_verified": len(cents),
        "low_retail_price_cents": round4(low),
        "base_retail_price_cents": round4(base),
        "high_retail_price_cents": round4(high),
        "average_retail_price_cents": round4(avg),
        "median_retail_price_cents": round4(median),
        "low_retail_price_usd": round4(low / 100.0),
        "base_retail_price_usd": round4(base / 100.0),
        "high_retail_price_usd": round4(high / 100.0),
    }


def build_residual_pool(cost_stack: dict[str, Any], retail_summary: dict[str, Any]) -> dict[str, Any]:
    physical = cost_stack["totals"]

    physical_low = float(physical["low_cents_per_bar"])
    physical_base = float(physical["base_cents_per_bar"])
    physical_high = float(physical["high_cents_per_bar"])

    retail_low = retail_summary["low_retail_price_cents"]
    retail_base = retail_summary["base_retail_price_cents"]
    retail_high = retail_summary["high_retail_price_cents"]

    if retail_low is None or retail_base is None or retail_high is None:
        return {
            "residual_status": "not_calculated",
            "reason": "Retail prices are not fully verified.",
        }

    retail_low = float(retail_low)
    retail_base = float(retail_base)
    retail_high = float(retail_high)

    residual_low = retail_low - physical_high
    residual_base = retail_base - physical_base
    residual_high = retail_high - physical_low

    return {
        "residual_status": "calculated",
        "definition": (
            "Residual channel/commercial pool = observed retail shelf price minus estimated physical supply-chain cost. "
            "It is not profit. It can include retailer margin, distributor margin, trade promotions, taxes/fees where applicable, "
            "corporate SG&A allocation, brand economics, and estimation error."
        ),
        "low_cents_per_bar": round4(residual_low),
        "base_cents_per_bar": round4(residual_base),
        "high_cents_per_bar": round4(residual_high),
        "physical_cost_low_cents": round4(physical_low),
        "physical_cost_base_cents": round4(physical_base),
        "physical_cost_high_cents": round4(physical_high),
        "retail_price_low_cents": round4(retail_low),
        "retail_price_base_cents": round4(retail_base),
        "retail_price_high_cents": round4(retail_high),
        "physical_cost_share_of_retail_low_case": round4((physical_low / retail_high) * 100.0),
        "physical_cost_share_of_retail_base_case": round4((physical_base / retail_base) * 100.0),
        "physical_cost_share_of_retail_high_case": round4((physical_high / retail_low) * 100.0),
        "safe_display_wording": (
            "The residual is the gap between observed shelf price and estimated physical cost. "
            "It should not be interpreted as Hershey profit or retailer profit."
        ),
    }


def build_retail_cost_record(retail_summary: dict[str, Any], verified: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cost_bucket_id": "COST_RETAIL_PRICE_VERIFIED",
        "cost_bucket": "Observed Retail Shelf Price",
        "cost_type": "retail_price",
        "cost_logic": (
            "Retail price is calculated from manually verified retailer pages for the exact HERSHEY'S 1.55 oz / 43 g single bar."
        ),
        "evidence_type": "direct_visual_verified",
        "source_evidence_ids": [],
        "low_cents_per_bar": retail_summary["low_retail_price_cents"],
        "base_cents_per_bar": retail_summary["base_retail_price_cents"],
        "high_cents_per_bar": retail_summary["high_retail_price_cents"],
        "confidence_level": "medium",
        "notes": "Retail prices are visually verified from collected retailer evidence. Prices may vary by store, date, and promotion.",
        "retailer_observations": verified,
    }


def build_residual_cost_record(residual: dict[str, Any]) -> dict[str, Any]:
    return {
        "cost_bucket_id": "COST_RESIDUAL_CHANNEL_COMMERCIAL_POOL",
        "cost_bucket": "Residual Channel / Commercial Pool",
        "cost_type": "residual_channel_pool",
        "cost_logic": residual.get("definition", ""),
        "evidence_type": "calculated_from_verified_retail_and_benchmark_cost",
        "source_evidence_ids": [],
        "low_cents_per_bar": residual.get("low_cents_per_bar"),
        "base_cents_per_bar": residual.get("base_cents_per_bar"),
        "high_cents_per_bar": residual.get("high_cents_per_bar"),
        "confidence_level": "low",
        "notes": residual.get("safe_display_wording", ""),
        "calculation_inputs": residual,
    }


def remove_old_placeholder_retail_record(cost_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in cost_records
        if row.get("cost_bucket_id") != "COST_RETAIL_PRICE_VISUAL_VERIFICATION_PENDING"
    ]


def write_retail_summary_csv(path: Path, verified: list[dict[str, Any]]) -> None:
    fieldnames = [
        "retailer",
        "verified_price_usd",
        "verified_price_cents",
        "verified_product_name",
        "verified_size_oz",
        "verified_size_g",
        "verified_pack_size",
        "verified_price_type",
        "verified_store_or_zip_visible",
        "verification_status",
        "manual_notes",
    ]

    write_csv(path, verified, fieldnames)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    retail_csv = root / "artifacts" / "08_visual_verification" / "retail_price_manual_entry_template.csv"
    cost_stack_path = root / "artifacts" / "07_cost_model_blobs" / "cost_stack_summary.json"
    cost_records_path = root / "artifacts" / "07_cost_model_blobs" / "cost_model_records.json"

    out_dir = root / "artifacts" / "07_cost_model_blobs"
    report_dir = root / "artifacts" / "10_run_reports"

    report_dir.mkdir(parents=True, exist_ok=True)

    if not retail_csv.exists():
        raise FileNotFoundError(f"Missing retail verification CSV: {retail_csv}")
    if not cost_stack_path.exists():
        raise FileNotFoundError(f"Missing cost stack summary: {cost_stack_path}")
    if not cost_records_path.exists():
        raise FileNotFoundError(f"Missing cost model records: {cost_records_path}")

    retail_rows = read_csv(retail_csv)
    cost_stack = read_json(cost_stack_path)
    cost_records = read_json(cost_records_path)

    verified, warnings = build_verified_retail_prices(retail_rows)
    retail_summary = summarize_retail_prices(verified)
    residual = build_residual_pool(cost_stack, retail_summary)

    retail_record = build_retail_cost_record(retail_summary, verified)
    residual_record = build_residual_cost_record(residual)

    cost_records_without_placeholder = remove_old_placeholder_retail_record(cost_records)
    cost_records_with_retail = cost_records_without_placeholder + [retail_record, residual_record]

    cost_stack_with_retail = dict(cost_stack)
    cost_stack_with_retail["retail_price_status"] = retail_summary["retail_price_status"]
    cost_stack_with_retail["retail_residual_status"] = residual["residual_status"]
    cost_stack_with_retail["retail_price_summary"] = retail_summary
    cost_stack_with_retail["residual_channel_commercial_pool"] = residual
    cost_stack_with_retail["safe_retail_display_wording"] = (
        "Retail price is visually verified from collected retailer pages. "
        "Residual pool is a modeled gap, not profit."
    )
    cost_stack_with_retail["updated_at"] = datetime.now().isoformat(timespec="seconds")

    retail_verified_path = out_dir / "retail_price_verified.json"
    retail_summary_csv = out_dir / "retail_price_summary.csv"
    residual_path = out_dir / "retail_residual_channel_pool.json"
    cost_records_with_retail_path = out_dir / "cost_model_records_with_retail.json"
    cost_stack_with_retail_path = out_dir / "cost_stack_with_retail_summary.json"

    write_json(retail_verified_path, {
        "product": PRODUCT_NAME,
        "expected_size_oz": EXPECTED_SIZE_OZ,
        "expected_size_g": EXPECTED_SIZE_G,
        "expected_pack_size": EXPECTED_PACK_SIZE,
        "verified_retail_prices": verified,
        "warning_or_rejected_rows": warnings,
        "retail_price_summary": retail_summary,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })

    write_retail_summary_csv(retail_summary_csv, verified)
    write_json(residual_path, residual)
    write_json(cost_records_with_retail_path, cost_records_with_retail)
    write_json(cost_stack_with_retail_path, cost_stack_with_retail)

    report = {
        "run_name": "step13b_retail_price_ingestion",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "retail_rows_seen": len(retail_rows),
        "verified_retail_rows": len(verified),
        "warning_or_rejected_rows": len(warnings),
        "retail_price_summary": retail_summary,
        "residual_status": residual.get("residual_status"),
        "residual_base_cents_per_bar": residual.get("base_cents_per_bar"),
        "physical_cost_base_cents_per_bar": cost_stack["totals"]["base_cents_per_bar"],
        "retail_base_cents_per_bar": retail_summary.get("base_retail_price_cents"),
        "retail_price_verified_json": str(retail_verified_path).replace("\\", "/"),
        "retail_price_summary_csv": str(retail_summary_csv).replace("\\", "/"),
        "retail_residual_channel_pool_json": str(residual_path).replace("\\", "/"),
        "cost_model_records_with_retail_json": str(cost_records_with_retail_path).replace("\\", "/"),
        "cost_stack_with_retail_summary_json": str(cost_stack_with_retail_path).replace("\\", "/"),
        "next_step": "Step 14: build node/edge architecture for interactive supply chain."
    }

    report_path = report_dir / "step13b_retail_price_ingestion_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 13B RETAIL PRICE INGESTION COMPLETE")
    print("----------------------------------------")
    print(f"Retail rows seen: {len(retail_rows)}")
    print(f"Verified retail rows: {len(verified)}")
    print(f"Warning/rejected rows: {len(warnings)}")
    print(f"Retail low cents:  {retail_summary.get('low_retail_price_cents')}")
    print(f"Retail base cents: {retail_summary.get('base_retail_price_cents')}")
    print(f"Retail high cents: {retail_summary.get('high_retail_price_cents')}")
    print(f"Residual base cents: {residual.get('base_cents_per_bar')}")
    print("")
    print(f"Cost stack with retail: {cost_stack_with_retail_path}")
    print(f"Report JSON:            {report_path}")
    print("")


if __name__ == "__main__":
    main()
