from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".xlsx",
    ".xls",
    ".csv",
    ".docx",
    ".txt",
    ".md",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_doc_id(path: Path, raw_root: Path) -> str:
    rel = str(path.relative_to(raw_root)).replace("\\", "/").lower()
    return "DOC_" + hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12].upper()


def classify_document_type(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return "pdf_document"
    if ext in [".xlsx", ".xls"]:
        return "excel_workbook"
    if ext == ".csv":
        return "csv_table"
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
        return "image_or_logo"
    if ext == ".docx":
        return "word_document"
    if ext in [".txt", ".md"]:
        return "text_document"

    return "unknown"


def classify_packet(path: Path, raw_root: Path) -> str:
    rel = str(path.relative_to(raw_root)).replace("\\", "/").lower()
    parts = rel.split("/")

    if "00_hershey_company" in parts:
        return "hershey_company"
    if "01_product_sku_1_55oz" in parts:
        return "product_sku_1_55oz"
    if "02_supplier_packets" in parts:
        return "supplier_packet"

    if "sugar" in parts:
        return "sugar"
    if "cocoa_chocolate_cocoa_butter" in parts:
        return "cocoa_chocolate_cocoa_butter"
    if "dairy_milk_skim_milk_milk_fat" in parts:
        return "dairy_milk_skim_milk_milk_fat"
    if "soy_lecithin" in parts:
        return "soy_lecithin"
    if "pgpr" in parts:
        return "pgpr"
    if "natural_flavor" in parts:
        return "natural_flavor"
    if "packaging_wrapper" in parts:
        return "packaging_wrapper"

    if "04_logistics_distribution" in parts:
        return "logistics_distribution"
    if "05_retail_price_evidence" in parts:
        return "retail_price_evidence"
    if "06_brand_logo_assets" in parts:
        return "brand_logo_assets"
    if "07_reference_only" in parts:
        return "reference_only"

    return "unknown"


def classify_evidence_role(path: Path, raw_root: Path) -> str:
    rel = str(path.relative_to(raw_root)).replace("\\", "/").lower()
    name = path.name.lower()

    if "reference_only" in rel or "old_generated_visuals" in rel:
        return "reference_only"

    if "logo" in rel or "brand_logo_assets" in rel:
        return "visual_asset"

    if "retail_price" in rel or "walmart" in rel or "target" in rel or "cvs" in rel or "walgreens" in rel:
        return "retail_price_evidence"

    if "regulatory" in rel or "fda" in name or "efsa" in name or "gras" in name or "definition" in name:
        return "regulatory_definition"

    if (
        "price_benchmarks" in rel
        or "cost_benchmarks" in rel
        or "benchmark" in name
        or "market" in name
        or "ppi" in name
        or "eia" in name
        or "usda" in name
        or "icco" in name
        or "bls" in name
    ):
        return "benchmark_proxy"

    if (
        "supplier" in rel
        or "asr" in name
        or "barry" in name
        or "land_o_lakes" in name
        or "mclane" in name
    ):
        return "supplier_relationship_context"

    if (
        "processing" in rel
        or "process" in name
        or "function" in rel
        or "explanation" in name
        or "common_carrier" in name
    ):
        return "process_or_function_context"

    if (
        "hershey" in rel
        or "annual_reports" in rel
        or "sustainability" in rel
        or "responsible_sourcing" in rel
        or "company" in rel
    ):
        return "direct_company_evidence"

    return "unknown"


def infer_source_category(packet: str, evidence_role: str) -> str:
    if packet == "reference_only" or evidence_role == "reference_only":
        return "reference_only"
    if packet == "product_sku_1_55oz":
        return "product_sku"
    if packet == "hershey_company":
        return "hershey_company"
    if packet in {
        "sugar",
        "cocoa_chocolate_cocoa_butter",
        "dairy_milk_skim_milk_milk_fat",
        "soy_lecithin",
        "pgpr",
        "natural_flavor",
        "packaging_wrapper",
    }:
        return "ingredient_or_packaging_research"
    if packet == "logistics_distribution":
        return "logistics_distribution"
    if packet == "retail_price_evidence":
        return "retail_price"
    if packet == "brand_logo_assets":
        return "brand_asset"
    if packet == "supplier_packet":
        return "supplier_packet"
    return "unknown"


def build_packet_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}

    for record in records:
        packet = record["packet"]

        if packet not in summary:
            summary[packet] = {
                "packet": packet,
                "file_count": 0,
                "supported_file_count": 0,
                "document_type_counts": {},
                "evidence_role_counts": {},
                "extension_counts": {},
            }

        row = summary[packet]
        row["file_count"] += 1

        if record["file_extension"] in SUPPORTED_EXTENSIONS:
            row["supported_file_count"] += 1

        doc_type = record["document_type"]
        role = record["evidence_role"]
        ext = record["file_extension"] or "[no_extension]"

        row["document_type_counts"][doc_type] = row["document_type_counts"].get(doc_type, 0) + 1
        row["evidence_role_counts"][role] = row["evidence_role_counts"].get(role, 0) + 1
        row["extension_counts"][ext] = row["extension_counts"].get(ext, 0) + 1

    return list(summary.values())


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            clean_row = {}
            for field in fieldnames:
                value = row.get(field, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                clean_row[field] = value
            writer.writerow(clean_row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    raw_root = root / "data" / "raw_sources"

    out_dir = root / "artifacts" / "00_source_inventory"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not raw_root.exists():
        raise FileNotFoundError(f"Raw source folder not found: {raw_root}")

    files = sorted([p for p in raw_root.rglob("*") if p.is_file()])

    records: list[dict[str, Any]] = []

    for file_path in files:
        ext = file_path.suffix.lower()
        supported = ext in SUPPORTED_EXTENSIONS

        packet = classify_packet(file_path, raw_root)
        document_type = classify_document_type(file_path)
        evidence_role = classify_evidence_role(file_path, raw_root)
        source_category = infer_source_category(packet, evidence_role)

        record = {
            "doc_id": stable_doc_id(file_path, raw_root),
            "file_name": file_path.name,
            "relative_path": str(file_path.relative_to(raw_root)).replace("\\", "/"),
            "absolute_path": str(file_path).replace("\\", "/"),
            "packet": packet,
            "source_category": source_category,
            "document_type": document_type,
            "evidence_role": evidence_role,
            "file_extension": ext,
            "file_size_bytes": file_path.stat().st_size,
            "sha256": sha256_file(file_path),
            "supported_by_parser": supported,
            "parser_status": "pending",
            "notes": "",
        }

        if not supported:
            record["notes"] = "Unsupported file extension for first parser."

        records.append(record)

    packet_summary = build_packet_summary(records)

    source_json = out_dir / "source_inventory.json"
    source_csv = out_dir / "source_inventory.csv"
    packet_json = out_dir / "packet_summary.json"
    packet_csv = out_dir / "packet_summary.csv"

    write_json(source_json, records)
    write_json(packet_json, packet_summary)

    write_csv(
        source_csv,
        records,
        [
            "doc_id",
            "file_name",
            "relative_path",
            "absolute_path",
            "packet",
            "source_category",
            "document_type",
            "evidence_role",
            "file_extension",
            "file_size_bytes",
            "sha256",
            "supported_by_parser",
            "parser_status",
            "notes",
        ],
    )

    write_csv(
        packet_csv,
        packet_summary,
        [
            "packet",
            "file_count",
            "supported_file_count",
            "document_type_counts",
            "evidence_role_counts",
            "extension_counts",
        ],
    )

    report = {
        "run_name": "step04_source_inventory_parser",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "raw_root": str(raw_root).replace("\\", "/"),
        "total_files_indexed": len(records),
        "supported_files": sum(1 for r in records if r["supported_by_parser"]),
        "unsupported_files": sum(1 for r in records if not r["supported_by_parser"]),
        "packets_seen": sorted({r["packet"] for r in records}),
        "source_inventory_json": str(source_json).replace("\\", "/"),
        "source_inventory_csv": str(source_csv).replace("\\", "/"),
        "packet_summary_json": str(packet_json).replace("\\", "/"),
        "packet_summary_csv": str(packet_csv).replace("\\", "/"),
        "next_step": "Step 05: extract text, tables, and page images from indexed raw sources.",
    }

    report_path = report_dir / "step04_source_inventory_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 04 SOURCE INVENTORY COMPLETE")
    print("--------------------------------")
    print(f"Total files indexed: {report['total_files_indexed']}")
    print(f"Supported files: {report['supported_files']}")
    print(f"Unsupported files: {report['unsupported_files']}")
    print(f"Packets seen: {len(report['packets_seen'])}")
    print("")
    print(f"Inventory JSON: {source_json}")
    print(f"Inventory CSV:  {source_csv}")
    print(f"Packet summary: {packet_csv}")
    print(f"Report JSON:    {report_path}")
    print("")


if __name__ == "__main__":
    main()