from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
from tqdm import tqdm


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_sheet_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ["_", "-"] else "_" for ch in name.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_").lower() or "sheet"


def extract_pdf_text_and_images(
    record: dict[str, Any],
    text_dir: Path,
    page_image_dir: Path,
) -> dict[str, Any]:
    doc_id = record["doc_id"]
    source_path = Path(record["absolute_path"])

    result = {
        "extractor": "pymupdf",
        "text_path": None,
        "page_count": 0,
        "total_text_length": 0,
        "page_text_stats": [],
        "rendered_page_images": [],
        "needs_visual_review": False,
        "errors": [],
    }

    try:
        pdf = fitz.open(source_path)
        result["page_count"] = len(pdf)

        all_text = []
        doc_image_dir = page_image_dir / doc_id
        doc_image_dir.mkdir(parents=True, exist_ok=True)

        for page_index in range(len(pdf)):
            page_num = page_index + 1
            page = pdf[page_index]

            text = page.get_text("text") or ""
            text = text.replace("\x00", " ").strip()

            all_text.append(f"\n\n--- PAGE {page_num} ---\n{text}")

            page_text_len = len(text)
            result["page_text_stats"].append(
                {
                    "page": page_num,
                    "text_length": page_text_len,
                }
            )

            should_render_page = False

            # Render all pages for very small PDFs and product/retail evidence.
            if result["page_count"] <= 4:
                should_render_page = True

            # Render weak-text pages for later manual/vision review.
            if page_text_len < 100:
                should_render_page = True

            # Do not render hundreds of pages from large reports.
            if page_index >= 30 and result["page_count"] > 30:
                should_render_page = False

            if should_render_page:
                try:
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                    image_path = doc_image_dir / f"page_{page_num:03d}.png"
                    pix.save(str(image_path))
                    result["rendered_page_images"].append(str(image_path).replace("\\", "/"))
                except Exception as image_error:
                    result["errors"].append(f"page_image_error_page_{page_num}: {image_error}")

        full_text = "\n".join(all_text).strip()
        result["total_text_length"] = len(full_text)

        out_text_path = text_dir / f"{doc_id}.txt"
        out_text_path.write_text(full_text, encoding="utf-8", errors="ignore")
        result["text_path"] = str(out_text_path).replace("\\", "/")

        weak_pages = [p for p in result["page_text_stats"] if p["text_length"] < 100]
        if weak_pages or result["total_text_length"] < 250:
            result["needs_visual_review"] = True

        pdf.close()

    except Exception as exc:
        result["errors"].append(str(exc))
        result["needs_visual_review"] = True

    return result


def extract_spreadsheet_or_csv(
    record: dict[str, Any],
    table_dir: Path,
    text_dir: Path,
) -> dict[str, Any]:
    doc_id = record["doc_id"]
    source_path = Path(record["absolute_path"])
    ext = source_path.suffix.lower()

    result = {
        "extractor": "pandas",
        "tables": [],
        "combined_text_path": None,
        "errors": [],
    }

    doc_table_dir = table_dir / doc_id
    doc_table_dir.mkdir(parents=True, exist_ok=True)

    combined_text_parts = []

    try:
        if ext == ".csv":
            df = pd.read_csv(source_path)
            out_csv = doc_table_dir / f"{safe_sheet_name(source_path.stem)}.csv"
            df.to_csv(out_csv, index=False)

            table_record = {
                "sheet_or_table_name": source_path.stem,
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "headers": [str(c) for c in df.columns],
                "csv_path": str(out_csv).replace("\\", "/"),
                "preview_rows": df.head(10).fillna("").astype(str).to_dict(orient="records"),
            }
            result["tables"].append(table_record)

            combined_text_parts.append(
                f"TABLE: {source_path.stem}\n"
                f"ROWS: {df.shape[0]}\n"
                f"COLUMNS: {df.shape[1]}\n"
                f"HEADERS: {', '.join([str(c) for c in df.columns])}\n"
                f"PREVIEW:\n{df.head(20).to_string(index=False)}"
            )

        else:
            excel = pd.ExcelFile(source_path)
            for sheet_name in excel.sheet_names:
                df = pd.read_excel(source_path, sheet_name=sheet_name)
                out_csv = doc_table_dir / f"{safe_sheet_name(sheet_name)}.csv"
                df.to_csv(out_csv, index=False)

                table_record = {
                    "sheet_or_table_name": sheet_name,
                    "rows": int(df.shape[0]),
                    "columns": int(df.shape[1]),
                    "headers": [str(c) for c in df.columns],
                    "csv_path": str(out_csv).replace("\\", "/"),
                    "preview_rows": df.head(10).fillna("").astype(str).to_dict(orient="records"),
                }
                result["tables"].append(table_record)

                combined_text_parts.append(
                    f"TABLE/SHEET: {sheet_name}\n"
                    f"ROWS: {df.shape[0]}\n"
                    f"COLUMNS: {df.shape[1]}\n"
                    f"HEADERS: {', '.join([str(c) for c in df.columns])}\n"
                    f"PREVIEW:\n{df.head(20).to_string(index=False)}"
                )

        combined_text = "\n\n---\n\n".join(combined_text_parts)
        text_path = text_dir / f"{doc_id}.txt"
        text_path.write_text(combined_text, encoding="utf-8", errors="ignore")
        result["combined_text_path"] = str(text_path).replace("\\", "/")

    except Exception as exc:
        result["errors"].append(str(exc))

    return result


def extract_image_or_logo(
    record: dict[str, Any],
    image_asset_dir: Path,
) -> dict[str, Any]:
    doc_id = record["doc_id"]
    source_path = Path(record["absolute_path"])

    result = {
        "extractor": "pillow_metadata_or_file_copy",
        "copied_asset_path": None,
        "width": None,
        "height": None,
        "format": source_path.suffix.lower().replace(".", ""),
        "needs_visual_review": True,
        "errors": [],
    }

    doc_asset_dir = image_asset_dir / doc_id
    doc_asset_dir.mkdir(parents=True, exist_ok=True)

    dest_path = doc_asset_dir / source_path.name

    try:
        shutil.copy2(source_path, dest_path)
        result["copied_asset_path"] = str(dest_path).replace("\\", "/")
    except Exception as exc:
        result["errors"].append(f"copy_error: {exc}")

    if source_path.suffix.lower() == ".svg":
        return result

    try:
        with Image.open(source_path) as img:
            result["width"] = img.width
            result["height"] = img.height
            result["format"] = img.format
    except Exception as exc:
        result["errors"].append(f"image_metadata_error: {exc}")

    return result


def extract_docx_or_text(
    record: dict[str, Any],
    text_dir: Path,
) -> dict[str, Any]:
    doc_id = record["doc_id"]
    source_path = Path(record["absolute_path"])
    ext = source_path.suffix.lower()

    result = {
        "extractor": "docx_or_plain_text",
        "text_path": None,
        "text_length": 0,
        "errors": [],
    }

    try:
        if ext == ".docx":
            from docx import Document

            document = Document(source_path)
            text = "\n".join([p.text for p in document.paragraphs if p.text.strip()])
        else:
            text = source_path.read_text(encoding="utf-8", errors="ignore")

        out_text_path = text_dir / f"{doc_id}.txt"
        out_text_path.write_text(text, encoding="utf-8", errors="ignore")

        result["text_path"] = str(out_text_path).replace("\\", "/")
        result["text_length"] = len(text)

    except Exception as exc:
        result["errors"].append(str(exc))

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    inventory_path = root / "artifacts" / "00_source_inventory" / "source_inventory.json"

    text_dir = root / "artifacts" / "01_extracted_text"
    table_dir = root / "artifacts" / "01_extracted_tables"
    page_image_dir = root / "artifacts" / "01_page_images"
    image_asset_dir = root / "artifacts" / "01_image_assets"
    document_artifact_dir = root / "artifacts" / "02_document_artifacts"
    report_dir = root / "artifacts" / "10_run_reports"

    for folder in [
        text_dir,
        table_dir,
        page_image_dir,
        image_asset_dir,
        document_artifact_dir,
        report_dir,
    ]:
        folder.mkdir(parents=True, exist_ok=True)

    if not inventory_path.exists():
        raise FileNotFoundError(
            f"Missing source inventory: {inventory_path}. Run Step 04 first."
        )

    source_inventory = read_json(inventory_path)

    extraction_artifacts = []
    updated_inventory = []

    totals = {
        "files_processed": 0,
        "pdf_files": 0,
        "spreadsheet_or_csv_files": 0,
        "image_or_logo_files": 0,
        "docx_or_text_files": 0,
        "errors": 0,
        "visual_review_files": 0,
        "tables_extracted": 0,
        "page_images_rendered": 0,
    }

    for record in tqdm(source_inventory, desc="Step 05 extracting local research memory"):
        updated_record = dict(record)
        doc_id = record["doc_id"]
        document_type = record["document_type"]

        extraction_result: dict[str, Any] = {
            "doc_id": doc_id,
            "file_name": record["file_name"],
            "relative_path": record["relative_path"],
            "packet": record["packet"],
            "document_type": document_type,
            "evidence_role": record["evidence_role"],
            "extracted_at": datetime.now().isoformat(timespec="seconds"),
            "extraction": {},
            "stage05_status": "pending",
            "stage05_notes": [],
        }

        try:
            if document_type == "pdf_document":
                totals["pdf_files"] += 1
                pdf_result = extract_pdf_text_and_images(record, text_dir, page_image_dir)
                extraction_result["extraction"]["pdf"] = pdf_result

                if pdf_result.get("needs_visual_review"):
                    extraction_result["stage05_notes"].append(
                        "PDF has weak/extracted text on some pages or needs visual review."
                    )
                    totals["visual_review_files"] += 1

                totals["page_images_rendered"] += len(pdf_result.get("rendered_page_images", []))
                if pdf_result.get("errors"):
                    totals["errors"] += len(pdf_result["errors"])

            elif document_type in ["excel_workbook", "csv_table"]:
                totals["spreadsheet_or_csv_files"] += 1
                table_result = extract_spreadsheet_or_csv(record, table_dir, text_dir)
                extraction_result["extraction"]["tables"] = table_result
                totals["tables_extracted"] += len(table_result.get("tables", []))

                if table_result.get("errors"):
                    totals["errors"] += len(table_result["errors"])

            elif document_type == "image_or_logo":
                totals["image_or_logo_files"] += 1
                image_result = extract_image_or_logo(record, image_asset_dir)
                extraction_result["extraction"]["image"] = image_result
                extraction_result["stage05_notes"].append(
                    "Image/logo copied and metadata captured. Use later vision/manual review for factual extraction."
                )
                totals["visual_review_files"] += 1

                if image_result.get("errors"):
                    totals["errors"] += len(image_result["errors"])

            elif document_type in ["word_document", "text_document"]:
                totals["docx_or_text_files"] += 1
                text_result = extract_docx_or_text(record, text_dir)
                extraction_result["extraction"]["text"] = text_result

                if text_result.get("errors"):
                    totals["errors"] += len(text_result["errors"])

            else:
                extraction_result["stage05_notes"].append("Unsupported or unknown document type.")

            extraction_result["stage05_status"] = "extracted"
            updated_record["parser_status"] = "extracted"

        except Exception as exc:
            extraction_result["stage05_status"] = "error"
            extraction_result["stage05_notes"].append(str(exc))
            updated_record["parser_status"] = "needs_review"
            totals["errors"] += 1

        artifact_path = document_artifact_dir / f"{doc_id}.stage05_extraction.json"
        write_json(artifact_path, extraction_result)

        updated_record["stage05_extraction_artifact_path"] = str(artifact_path).replace("\\", "/")

        extraction_artifacts.append(extraction_result)
        updated_inventory.append(updated_record)
        totals["files_processed"] += 1

    write_json(
        root / "artifacts" / "00_source_inventory" / "source_inventory_stage05_enriched.json",
        updated_inventory,
    )

    write_json(
        document_artifact_dir / "all_stage05_extraction_artifacts.json",
        extraction_artifacts,
    )

    report = {
        "run_name": "step05_extract_text_tables_images",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        **totals,
        "source_inventory_input": str(inventory_path).replace("\\", "/"),
        "source_inventory_stage05_enriched": str(
            root / "artifacts" / "00_source_inventory" / "source_inventory_stage05_enriched.json"
        ).replace("\\", "/"),
        "extracted_text_folder": str(text_dir).replace("\\", "/"),
        "extracted_tables_folder": str(table_dir).replace("\\", "/"),
        "page_images_folder": str(page_image_dir).replace("\\", "/"),
        "image_assets_folder": str(image_asset_dir).replace("\\", "/"),
        "document_artifacts_folder": str(document_artifact_dir).replace("\\", "/"),
        "next_step": "Step 06: build text chunks from extracted text and table previews.",
    }

    report_path = report_dir / "step05_extraction_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 05 EXTRACTION COMPLETE")
    print("---------------------------")
    print(f"Files processed: {totals['files_processed']}")
    print(f"PDF files: {totals['pdf_files']}")
    print(f"Spreadsheet/CSV files: {totals['spreadsheet_or_csv_files']}")
    print(f"Image/logo files: {totals['image_or_logo_files']}")
    print(f"Tables extracted: {totals['tables_extracted']}")
    print(f"Page images rendered: {totals['page_images_rendered']}")
    print(f"Files needing visual review: {totals['visual_review_files']}")
    print(f"Errors: {totals['errors']}")
    print("")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()