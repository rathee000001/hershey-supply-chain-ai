from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps


REVIEW_PACKETS = {
    "product_sku_1_55oz",
    "retail_price_evidence",
}

RETAILERS = ["walmart", "target", "cvs", "walgreens", "amazon", "instacart"]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: Any) -> str:
    return str(value or "").strip()


def safe_name(value: str) -> str:
    allowed = []
    for ch in value:
        if ch.isalnum() or ch in ["_", "-", "."]:
            allowed.append(ch)
        else:
            allowed.append("_")
    out = "".join(allowed)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_").lower() or "untitled"


def load_stage05_artifact(root: Path, doc_id: str) -> dict[str, Any] | None:
    path = root / "artifacts" / "02_document_artifacts" / f"{doc_id}.stage05_extraction.json"
    if not path.exists():
        return None
    return read_json(path)


def get_page_images_from_stage05(stage05: dict[str, Any] | None) -> list[str]:
    if not stage05:
        return []

    extraction = stage05.get("extraction", {})
    pdf = extraction.get("pdf", {})
    images = pdf.get("rendered_page_images", []) or []

    return [str(x) for x in images if x]


def get_image_asset_from_stage05(stage05: dict[str, Any] | None) -> str:
    if not stage05:
        return ""

    extraction = stage05.get("extraction", {})
    image = extraction.get("image", {})
    return clean(image.get("copied_asset_path"))


def infer_retailer(record: dict[str, Any]) -> str:
    text = f"{record.get('file_name', '')} {record.get('relative_path', '')}".lower()

    for retailer in RETAILERS:
        if retailer in text:
            return retailer

    return ""


def infer_review_type(record: dict[str, Any]) -> str:
    packet = record.get("packet", "")
    if packet == "product_sku_1_55oz":
        return "product_sku_visual_check"
    if packet == "retail_price_evidence":
        return "retail_price_visual_check"
    return "general_visual_check"


def draw_text_block(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, max_width_chars: int = 120) -> int:
    x, y = xy
    words = text.split()
    lines = []
    current = ""

    for word in words:
        if len(current) + len(word) + 1 <= max_width_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    for line in lines[:5]:
        draw.text((x, y), line, fill=(0, 0, 0))
        y += 18

    return y


def create_contact_sheet(
    root: Path,
    review_id: str,
    title: str,
    image_paths: list[str],
    out_dir: Path,
) -> str:
    existing_images = []

    for path_text in image_paths:
        img_path = Path(path_text)
        if not img_path.is_absolute():
            img_path = root / path_text

        if img_path.exists() and img_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            existing_images.append(img_path)

    if not existing_images:
        return ""

    max_images = min(len(existing_images), 8)
    thumb_w = 900
    thumb_h = 700
    pad = 30
    header_h = 130
    caption_h = 70

    sheet_w = thumb_w + pad * 2
    sheet_h = header_h + max_images * (thumb_h + caption_h + pad) + pad

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    y = pad
    y = draw_text_block(draw, (pad, y), title, max_width_chars=105)
    y += 20

    for idx, img_path in enumerate(existing_images[:max_images], start=1):
        draw.text((pad, y), f"Image {idx}: {img_path.name}", fill=(0, 0, 0))
        y += caption_h

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img = ImageOps.contain(img, (thumb_w, thumb_h))
                x = pad + (thumb_w - img.width) // 2
                sheet.paste(img, (x, y))
        except Exception as exc:
            draw.text((pad, y), f"Could not open image: {exc}", fill=(0, 0, 0))

        y += thumb_h + pad

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe_name(review_id)}_contact_sheet.png"
    sheet.save(out_path)

    return str(out_path).replace("\\", "/")


def copy_source_or_asset(
    root: Path,
    record: dict[str, Any],
    asset_path_text: str,
    out_dir: Path,
) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)

    source_candidates = []

    if asset_path_text:
        source_candidates.append(Path(asset_path_text))

    absolute_path = clean(record.get("absolute_path"))
    if absolute_path:
        source_candidates.append(Path(absolute_path))

    for src in source_candidates:
        if not src.is_absolute():
            src = root / src

        if src.exists() and src.is_file():
            dest = out_dir / src.name
            try:
                shutil.copy2(src, dest)
                return str(dest).replace("\\", "/")
            except Exception:
                pass

    return ""


def build_review_rows(root: Path, inventory: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    rows = []
    contact_sheet_dir = out_dir / "contact_sheets"
    copied_assets_dir = out_dir / "copied_review_assets"

    for record in inventory:
        packet = record.get("packet", "")

        if packet not in REVIEW_PACKETS:
            continue

        doc_id = record["doc_id"]
        stage05 = load_stage05_artifact(root, doc_id)
        page_images = get_page_images_from_stage05(stage05)
        image_asset = get_image_asset_from_stage05(stage05)

        image_paths = list(page_images)
        if image_asset:
            image_paths.append(image_asset)

        review_type = infer_review_type(record)
        retailer = infer_retailer(record)

        review_id = f"REV_{doc_id}"

        title = (
            f"{review_id} | {review_type} | {record.get('file_name')} | "
            f"Packet: {packet} | Retailer: {retailer or 'not_applicable'}"
        )

        contact_sheet = create_contact_sheet(
            root=root,
            review_id=review_id,
            title=title,
            image_paths=image_paths,
            out_dir=contact_sheet_dir,
        )

        copied_asset = copy_source_or_asset(
            root=root,
            record=record,
            asset_path_text=image_asset,
            out_dir=copied_assets_dir,
        )

        rows.append(
            {
                "review_id": review_id,
                "doc_id": doc_id,
                "file_name": record.get("file_name"),
                "relative_path": record.get("relative_path"),
                "absolute_path": record.get("absolute_path"),
                "packet": packet,
                "review_type": review_type,
                "retailer": retailer,
                "document_type": record.get("document_type"),
                "evidence_role": record.get("evidence_role"),
                "page_image_count": len(page_images),
                "page_images": image_paths,
                "contact_sheet_path": contact_sheet,
                "copied_review_asset_path": copied_asset,
                "verification_status": "pending_manual_review",
                "review_notes": "",
            }
        )

    return rows


def write_queue_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "review_id",
        "doc_id",
        "file_name",
        "packet",
        "review_type",
        "retailer",
        "document_type",
        "evidence_role",
        "page_image_count",
        "contact_sheet_path",
        "copied_review_asset_path",
        "verification_status",
        "review_notes",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_retail_template(path: Path, rows: list[dict[str, Any]]) -> None:
    retail_rows = [row for row in rows if row["review_type"] == "retail_price_visual_check"]

    fieldnames = [
        "review_id",
        "retailer",
        "file_name",
        "contact_sheet_path",
        "verified_product_name",
        "verified_size_oz",
        "verified_size_g",
        "verified_pack_size",
        "verified_price_usd",
        "verified_price_type",
        "verified_date_visible",
        "verified_store_or_zip_visible",
        "verification_status",
        "manual_notes",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in retail_rows:
            writer.writerow(
                {
                    "review_id": row["review_id"],
                    "retailer": row["retailer"],
                    "file_name": row["file_name"],
                    "contact_sheet_path": row["contact_sheet_path"],
                    "verified_product_name": "",
                    "verified_size_oz": "",
                    "verified_size_g": "",
                    "verified_pack_size": "",
                    "verified_price_usd": "",
                    "verified_price_type": "",
                    "verified_date_visible": "",
                    "verified_store_or_zip_visible": "",
                    "verification_status": "pending_manual_entry",
                    "manual_notes": "",
                }
            )


def write_product_template(path: Path, rows: list[dict[str, Any]]) -> None:
    product_rows = [row for row in rows if row["review_type"] == "product_sku_visual_check"]

    fieldnames = [
        "review_id",
        "file_name",
        "contact_sheet_path",
        "verified_product_name",
        "verified_size_oz",
        "verified_size_g",
        "verified_upc",
        "verified_ingredients",
        "verified_contains_sugar",
        "verified_contains_cocoa_or_chocolate",
        "verified_contains_milk",
        "verified_contains_skim_milk",
        "verified_contains_milk_fat",
        "verified_contains_soy_lecithin",
        "verified_contains_pgpr",
        "verified_contains_natural_flavor",
        "verification_status",
        "manual_notes",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in product_rows:
            writer.writerow(
                {
                    "review_id": row["review_id"],
                    "file_name": row["file_name"],
                    "contact_sheet_path": row["contact_sheet_path"],
                    "verified_product_name": "",
                    "verified_size_oz": "",
                    "verified_size_g": "",
                    "verified_upc": "",
                    "verified_ingredients": "",
                    "verified_contains_sugar": "",
                    "verified_contains_cocoa_or_chocolate": "",
                    "verified_contains_milk": "",
                    "verified_contains_skim_milk": "",
                    "verified_contains_milk_fat": "",
                    "verified_contains_soy_lecithin": "",
                    "verified_contains_pgpr": "",
                    "verified_contains_natural_flavor": "",
                    "verification_status": "pending_manual_entry",
                    "manual_notes": "",
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    inventory_path = root / "artifacts" / "00_source_inventory" / "source_inventory_stage05_enriched.json"

    out_dir = root / "artifacts" / "08_visual_verification"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not inventory_path.exists():
        raise FileNotFoundError(f"Missing source inventory: {inventory_path}")

    inventory = read_json(inventory_path)

    rows = build_review_rows(root, inventory, out_dir)

    queue_json_path = out_dir / "visual_verification_queue.json"
    queue_csv_path = out_dir / "visual_verification_queue.csv"
    retail_template_path = out_dir / "retail_price_manual_entry_template.csv"
    product_template_path = out_dir / "product_sku_manual_check_template.csv"

    write_json(queue_json_path, rows)
    write_queue_csv(queue_csv_path, rows)
    write_retail_template(retail_template_path, rows)
    write_product_template(product_template_path, rows)

    product_count = sum(1 for row in rows if row["review_type"] == "product_sku_visual_check")
    retail_count = sum(1 for row in rows if row["review_type"] == "retail_price_visual_check")
    contact_sheet_count = sum(1 for row in rows if row["contact_sheet_path"])

    report = {
        "run_name": "step13_visual_verification_packet",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "review_items_created": len(rows),
        "product_sku_review_items": product_count,
        "retail_price_review_items": retail_count,
        "contact_sheets_created": contact_sheet_count,
        "visual_verification_queue_json": str(queue_json_path).replace("\\", "/"),
        "visual_verification_queue_csv": str(queue_csv_path).replace("\\", "/"),
        "retail_price_manual_entry_template_csv": str(retail_template_path).replace("\\", "/"),
        "product_sku_manual_check_template_csv": str(product_template_path).replace("\\", "/"),
        "contact_sheets_folder": str(out_dir / "contact_sheets").replace("\\", "/"),
        "next_step": "Step 13B: manually fill product and retail verification CSVs, then ingest verified retail prices into the cost model.",
    }

    report_path = report_dir / "step13_visual_verification_packet_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 13 VISUAL VERIFICATION PACKET COMPLETE")
    print("-------------------------------------------")
    print(f"Review items created: {len(rows)}")
    print(f"Product SKU review items: {product_count}")
    print(f"Retail price review items: {retail_count}")
    print(f"Contact sheets created: {contact_sheet_count}")
    print("")
    print(f"Queue CSV:        {queue_csv_path}")
    print(f"Retail template:  {retail_template_path}")
    print(f"Product template: {product_template_path}")
    print(f"Report JSON:      {report_path}")
    print("")


if __name__ == "__main__":
    main()