from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path("D:/HersheySupplyChainAI")

REQUIRED_DIRS = [
    "data/raw_sources",
    "data/raw_sources/00_hershey_company",
    "data/raw_sources/01_product_sku_1_55oz",
    "data/raw_sources/02_supplier_packets",
    "data/raw_sources/03_ingredient_research",
    "data/raw_sources/03_ingredient_research/sugar",
    "data/raw_sources/03_ingredient_research/cocoa_chocolate_cocoa_butter",
    "data/raw_sources/03_ingredient_research/dairy_milk_skim_milk_milk_fat",
    "data/raw_sources/03_ingredient_research/soy_lecithin",
    "data/raw_sources/03_ingredient_research/pgpr",
    "data/raw_sources/03_ingredient_research/natural_flavor",
    "data/raw_sources/03_ingredient_research/packaging_wrapper",
    "data/raw_sources/04_logistics_distribution",
    "data/raw_sources/05_retail_price_evidence",
    "data/raw_sources/06_brand_logo_assets",
    "data/raw_sources/07_reference_only",
    "schemas",
    "prompts",
    "scripts",
]

REQUIRED_SCHEMAS = [
    "source_inventory.schema.json",
    "parsed_document.schema.json",
    "evidence_blob.schema.json",
    "supplier_packet.schema.json",
    "ingredient_packet.schema.json",
    "cost_model.schema.json",
    "node.schema.json",
    "edge.schema.json",
    "display_blob.schema.json",
    "quality_control.schema.json",
]

REQUIRED_PROMPTS = [
    "level1_document_parser.md",
    "level1_evidence_extractor.md",
    "level2_evidence_auditor.md",
    "level2_supplier_classifier.md",
    "level2_cost_model_builder.md",
    "level2_node_edge_builder.md",
    "final_display_blob_builder.md",
]

ARTIFACT_DIRS_TO_CREATE = [
    "artifacts/00_source_inventory",
    "artifacts/01_extracted_text",
    "artifacts/01_extracted_tables",
    "artifacts/01_page_images",
    "artifacts/02_document_artifacts",
    "artifacts/02_text_chunks",
    "artifacts/03_evidence_blobs",
    "artifacts/04_level2_audited_blobs",
    "artifacts/05_supplier_blobs",
    "artifacts/06_ingredient_blobs",
    "artifacts/07_cost_model_blobs",
    "artifacts/08_node_edge_architecture",
    "artifacts/09_display_ready",
    "artifacts/10_run_reports",
]

PACKET_DIRS = {
    "hershey_company": "data/raw_sources/00_hershey_company",
    "product_sku_1_55oz": "data/raw_sources/01_product_sku_1_55oz",
    "supplier_packets": "data/raw_sources/02_supplier_packets",
    "sugar": "data/raw_sources/03_ingredient_research/sugar",
    "cocoa_chocolate_cocoa_butter": "data/raw_sources/03_ingredient_research/cocoa_chocolate_cocoa_butter",
    "dairy_milk_skim_milk_milk_fat": "data/raw_sources/03_ingredient_research/dairy_milk_skim_milk_milk_fat",
    "soy_lecithin": "data/raw_sources/03_ingredient_research/soy_lecithin",
    "pgpr": "data/raw_sources/03_ingredient_research/pgpr",
    "natural_flavor": "data/raw_sources/03_ingredient_research/natural_flavor",
    "packaging_wrapper": "data/raw_sources/03_ingredient_research/packaging_wrapper",
    "logistics_distribution": "data/raw_sources/04_logistics_distribution",
    "retail_price_evidence": "data/raw_sources/05_retail_price_evidence",
    "brand_logo_assets": "data/raw_sources/06_brand_logo_assets",
    "reference_only": "data/raw_sources/07_reference_only",
}


SUPPORTED_RAW_EXTENSIONS = {
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


def count_files(folder: Path) -> dict:
    files = [p for p in folder.rglob("*") if p.is_file()]
    supported = [p for p in files if p.suffix.lower() in SUPPORTED_RAW_EXTENSIONS]
    by_extension = {}

    for file in files:
        ext = file.suffix.lower() or "[no_extension]"
        by_extension[ext] = by_extension.get(ext, 0) + 1

    return {
        "total_files": len(files),
        "supported_files": len(supported),
        "unsupported_files": len(files) - len(supported),
        "by_extension": by_extension,
    }


def main() -> None:
    run_time = datetime.now().isoformat(timespec="seconds")

    for artifact_dir in ARTIFACT_DIRS_TO_CREATE:
        (ROOT / artifact_dir).mkdir(parents=True, exist_ok=True)

    missing_dirs = []
    existing_dirs = []

    for rel_dir in REQUIRED_DIRS:
        path = ROOT / rel_dir
        if path.exists() and path.is_dir():
            existing_dirs.append(rel_dir)
        else:
            missing_dirs.append(rel_dir)

    missing_schemas = []
    existing_schemas = []

    for schema in REQUIRED_SCHEMAS:
        path = ROOT / "schemas" / schema
        if path.exists() and path.is_file():
            existing_schemas.append(schema)
        else:
            missing_schemas.append(schema)

    missing_prompts = []
    existing_prompts = []

    for prompt in REQUIRED_PROMPTS:
        path = ROOT / "prompts" / prompt
        if path.exists() and path.is_file():
            existing_prompts.append(prompt)
        else:
            missing_prompts.append(prompt)

    packet_summary = []
    empty_packet_dirs = []

    for packet_name, rel_dir in PACKET_DIRS.items():
        folder = ROOT / rel_dir
        if folder.exists():
            stats = count_files(folder)
            row = {
                "packet": packet_name,
                "relative_path": rel_dir,
                "exists": True,
                **stats,
            }
            if stats["total_files"] == 0:
                empty_packet_dirs.append(rel_dir)
        else:
            row = {
                "packet": packet_name,
                "relative_path": rel_dir,
                "exists": False,
                "total_files": 0,
                "supported_files": 0,
                "unsupported_files": 0,
                "by_extension": {},
            }
            empty_packet_dirs.append(rel_dir)

        packet_summary.append(row)

    raw_root = ROOT / "data" / "raw_sources"
    all_raw_files = [p for p in raw_root.rglob("*") if p.is_file()] if raw_root.exists() else []
    unsupported_files = [
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in all_raw_files
        if p.suffix.lower() not in SUPPORTED_RAW_EXTENSIONS
    ]

    total_supported_files = sum(1 for p in all_raw_files if p.suffix.lower() in SUPPORTED_RAW_EXTENSIONS)

    if missing_dirs or missing_schemas or missing_prompts:
        validation_status = "fail"
    elif total_supported_files == 0:
        validation_status = "fail"
    elif empty_packet_dirs:
        validation_status = "pass_with_warnings"
    else:
        validation_status = "pass"

    warnings = []
    if empty_packet_dirs:
        warnings.append("Some packet folders are empty. This may be okay if those folders are optional or future-use.")
    if unsupported_files:
        warnings.append("Some files have unsupported extensions and may not be parsed by the first parser.")
    if total_supported_files < 20:
        warnings.append("Raw source file count seems low for this project. Confirm data collection is complete.")

    report = {
        "run_name": "step03_project_structure_validation",
        "run_time": run_time,
        "root": str(ROOT).replace("\\", "/"),
        "validation_status": validation_status,
        "required_dirs_existing_count": len(existing_dirs),
        "required_dirs_missing_count": len(missing_dirs),
        "missing_dirs": missing_dirs,
        "schemas_existing_count": len(existing_schemas),
        "schemas_missing_count": len(missing_schemas),
        "missing_schemas": missing_schemas,
        "prompts_existing_count": len(existing_prompts),
        "prompts_missing_count": len(missing_prompts),
        "missing_prompts": missing_prompts,
        "total_raw_files": len(all_raw_files),
        "total_supported_raw_files": total_supported_files,
        "unsupported_files": unsupported_files,
        "empty_packet_dirs": empty_packet_dirs,
        "packet_summary": packet_summary,
        "warnings": warnings,
        "next_step": "If validation passes or only has acceptable warnings, create Step 04 source inventory parser.",
    }

    report_dir = ROOT / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "step03_project_structure_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    packet_csv_path = report_dir / "step03_packet_file_counts.csv"
    with packet_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "packet",
                "relative_path",
                "exists",
                "total_files",
                "supported_files",
                "unsupported_files",
                "by_extension",
            ],
        )
        writer.writeheader()
        for row in packet_summary:
            row_copy = dict(row)
            row_copy["by_extension"] = json.dumps(row_copy["by_extension"])
            writer.writerow(row_copy)

    print("")
    print("STEP 03 STRUCTURE VALIDATION COMPLETE")
    print("------------------------------------")
    print(f"Validation status: {validation_status}")
    print(f"Total raw files: {len(all_raw_files)}")
    print(f"Supported raw files: {total_supported_files}")
    print(f"Missing dirs: {len(missing_dirs)}")
    print(f"Missing schemas: {len(missing_schemas)}")
    print(f"Missing prompts: {len(missing_prompts)}")
    print(f"Empty packet dirs: {len(empty_packet_dirs)}")
    print("")
    print(f"Report JSON: {report_path}")
    print(f"Packet CSV:  {packet_csv_path}")
    print("")


if __name__ == "__main__":
    main()