from __future__ import annotations

import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path


PRODUCT_NAME = "HERSHEY'S Milk Chocolate Candy Bar"
SIZE_OZ = "1.55"
SIZE_G = "43"
PACK_SIZE = "1"

# Enter retail prices here ONLY after reading the contact sheets.
# Leave blank if not clearly visible.
RETAIL_PRICE_PATCH = {
    "walmart": {
        "verified_price_usd": "",
        "verified_price_type": "single_bar_price",
        "verified_store_or_zip_visible": "",
        "manual_notes": "Price left blank until contact sheet is visually verified."
    },
    "target": {
        "verified_price_usd": "",
        "verified_price_type": "single_bar_price",
        "verified_store_or_zip_visible": "",
        "manual_notes": "Price left blank until contact sheet is visually verified."
    },
    "cvs": {
        "verified_price_usd": "",
        "verified_price_type": "single_bar_price",
        "verified_store_or_zip_visible": "",
        "manual_notes": "Price left blank until contact sheet is visually verified."
    },
    "walgreens": {
        "verified_price_usd": "",
        "verified_price_type": "single_bar_price",
        "verified_store_or_zip_visible": "",
        "manual_notes": "Price left blank until contact sheet is visually verified."
    },
}


def backup_file(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(path.suffix + f".pre_patch_{timestamp}.bak")
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


def patch_product_sku(path: Path) -> dict:
    rows = read_csv(path)
    backup = backup_file(path)

    for row in rows:
        row["verified_product_name"] = PRODUCT_NAME
        row["verified_size_oz"] = SIZE_OZ
        row["verified_size_g"] = SIZE_G

        # These are ingredient presence fields prepared from the known SKU packet,
        # but exact ingredient text still needs visual/manual confirmation.
        row["verified_contains_sugar"] = "yes"
        row["verified_contains_cocoa_or_chocolate"] = "yes"
        row["verified_contains_milk"] = "yes"
        row["verified_contains_skim_milk"] = "not_visible"
        row["verified_contains_milk_fat"] = "not_visible"
        row["verified_contains_soy_lecithin"] = "yes"
        row["verified_contains_pgpr"] = "yes"
        row["verified_contains_natural_flavor"] = "yes"

        # Keep exact UPC and exact ingredient list blank unless read from contact sheet.
        if not row.get("verified_upc"):
            row["verified_upc"] = ""
        if not row.get("verified_ingredients"):
            row["verified_ingredients"] = ""

        row["verification_status"] = "partial"
        row["manual_notes"] = (
            "Patched with SKU identity fields. Exact UPC, exact ingredient text, "
            "skim milk, and milk fat should be visually verified from contact sheet before final display."
        )

    write_csv(path, rows, list(rows[0].keys()) if rows else [])

    return {
        "file": str(path),
        "backup": str(backup),
        "rows_patched": len(rows),
    }


def patch_retail_prices(path: Path) -> dict:
    rows = read_csv(path)
    backup = backup_file(path)

    for row in rows:
        retailer = (row.get("retailer") or "").strip().lower()
        patch = RETAIL_PRICE_PATCH.get(retailer, {})

        row["verified_product_name"] = PRODUCT_NAME
        row["verified_size_oz"] = SIZE_OZ
        row["verified_size_g"] = SIZE_G
        row["verified_pack_size"] = PACK_SIZE

        price = patch.get("verified_price_usd", "")

        row["verified_price_usd"] = price
        row["verified_price_type"] = patch.get("verified_price_type", "single_bar_price")
        row["verified_store_or_zip_visible"] = patch.get("verified_store_or_zip_visible", "")

        if price:
            row["verification_status"] = "verified"
            row["manual_notes"] = patch.get("manual_notes", "Price manually entered after contact sheet verification.")
        else:
            row["verification_status"] = "partial"
            row["manual_notes"] = patch.get(
                "manual_notes",
                "Retailer/product fields patched. Price left blank until visually verified."
            )

    write_csv(path, rows, list(rows[0].keys()) if rows else [])

    return {
        "file": str(path),
        "backup": str(backup),
        "rows_patched": len(rows),
        "prices_entered": sum(1 for r in rows if r.get("verified_price_usd")),
        "prices_pending": sum(1 for r in rows if not r.get("verified_price_usd")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    visual_dir = root / "artifacts" / "08_visual_verification"

    product_csv = visual_dir / "product_sku_manual_check_template.csv"
    retail_csv = visual_dir / "retail_price_manual_entry_template.csv"

    if not product_csv.exists():
        raise FileNotFoundError(f"Missing product template: {product_csv}")

    if not retail_csv.exists():
        raise FileNotFoundError(f"Missing retail template: {retail_csv}")

    product_result = patch_product_sku(product_csv)
    retail_result = patch_retail_prices(retail_csv)

    print("")
    print("STEP 13A PATCH COMPLETE")
    print("-----------------------")
    print(f"Product rows patched: {product_result['rows_patched']}")
    print(f"Retail rows patched: {retail_result['rows_patched']}")
    print(f"Retail prices entered: {retail_result['prices_entered']}")
    print(f"Retail prices pending: {retail_result['prices_pending']}")
    print("")
    print(f"Product CSV: {product_csv}")
    print(f"Retail CSV:  {retail_csv}")
    print("")


if __name__ == "__main__":
    main()