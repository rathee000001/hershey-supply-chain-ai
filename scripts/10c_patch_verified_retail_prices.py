from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path


# ============================================================
# ENTER ONLY VISUALLY VERIFIED SINGLE-BAR PRICES HERE
# Must be exact 1.55 oz / 43 g single bar, not multipack.
# Leave blank if not readable.
# ============================================================

VERIFIED_RETAIL_PRICES = {
    "walmart": {
        "price": "1.62",   # example: "1.48"
        "price_type": "single_bar_price",
        "store_or_zip": "",
        "notes": "Manually verified from Walmart contact sheet."
    },
    "target": {
        "price": "1.99",   # example: "1.49"
        "price_type": "single_bar_price",
        "store_or_zip": "",
        "notes": "Manually verified from Target contact sheet."
    },
    "cvs": {
        "price": "2.19",   # example: "2.19"
        "price_type": "single_bar_price",
        "store_or_zip": "",
        "notes": "Manually verified from CVS contact sheet."
    },
    "walgreens": {
        "price": "2.19",   # example: "1.99"
        "price_type": "single_bar_price",
        "store_or_zip": "",
        "notes": "Manually verified from Walgreens contact sheet."
    },
}


PRODUCT_NAME = "HERSHEY'S Milk Chocolate Candy Bar"
SIZE_OZ = "1.55"
SIZE_G = "43"
PACK_SIZE = "1"


def backup_file(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(path.suffix + f".pre_retail_price_patch_{timestamp}.bak")
    shutil.copy2(path, backup)
    return backup


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8", errors="ignore") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_price(value: str) -> str:
    value = str(value or "").strip()
    value = value.replace("$", "").strip()
    return value


def is_valid_price(value: str) -> bool:
    value = clean_price(value)
    if not value:
        return False
    try:
        price = float(value)
    except ValueError:
        return False
    return 0.25 <= price <= 10.00


def patch_retail_csv(retail_csv: Path) -> dict:
    rows = read_csv(retail_csv)
    backup = backup_file(retail_csv)

    patched = 0
    verified = 0
    pending = 0
    invalid = []

    for row in rows:
        retailer = (row.get("retailer") or "").strip().lower()
        patch = VERIFIED_RETAIL_PRICES.get(retailer)

        row["verified_product_name"] = PRODUCT_NAME
        row["verified_size_oz"] = SIZE_OZ
        row["verified_size_g"] = SIZE_G
        row["verified_pack_size"] = PACK_SIZE

        if not patch:
            row["verification_status"] = "pending_manual_entry"
            row["manual_notes"] = "Retailer not found in VERIFIED_RETAIL_PRICES patch dictionary."
            pending += 1
            continue

        price = clean_price(patch.get("price", ""))

        row["verified_price_usd"] = price
        row["verified_price_type"] = patch.get("price_type", "single_bar_price")
        row["verified_store_or_zip_visible"] = patch.get("store_or_zip", "")

        if is_valid_price(price):
            row["verification_status"] = "verified"
            row["manual_notes"] = patch.get("notes", "Price manually verified from contact sheet.")
            verified += 1
        else:
            row["verification_status"] = "partial"
            row["manual_notes"] = (
                "Product/size fields patched, but price is blank or invalid. "
                "Enter only visually verified single-bar price."
            )
            pending += 1
            if price:
                invalid.append({"retailer": retailer, "price": price})

        patched += 1

    write_csv(retail_csv, rows, list(rows[0].keys()) if rows else [])

    return {
        "retail_csv": str(retail_csv),
        "backup_file": str(backup),
        "rows_seen": len(rows),
        "rows_patched": patched,
        "prices_verified": verified,
        "prices_pending": pending,
        "invalid_prices": invalid,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    retail_csv = root / "artifacts" / "08_visual_verification" / "retail_price_manual_entry_template.csv"
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    if not retail_csv.exists():
        raise FileNotFoundError(f"Missing retail CSV: {retail_csv}")

    result = patch_retail_csv(retail_csv)

    report = {
        "run_name": "step13a2_retail_price_patch",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        **result,
        "safe_rule": "Prices are manual visual entries for single 1.55 oz bar only. Do not use multipack prices.",
        "next_step": (
            "If prices_verified is 4 and prices_pending is 0, run Step 13B retail price ingestion."
        ),
    }

    report_path = report_dir / "step13a2_retail_price_patch_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("")
    print("STEP 13A-2 RETAIL PRICE PATCH COMPLETE")
    print("--------------------------------------")
    print(f"Rows patched: {result['rows_patched']}")
    print(f"Prices verified: {result['prices_verified']}")
    print(f"Prices pending: {result['prices_pending']}")
    print(f"Invalid prices: {len(result['invalid_prices'])}")
    print("")
    print(f"Retail CSV:  {retail_csv}")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()