from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def chunk_signal_score(chunk: dict[str, Any]) -> int:
    signals = chunk.get("signals", {})
    score = 0

    keyword_hits = signals.get("keyword_hits", {})
    for _, hits in keyword_hits.items():
        score += len(hits) * 3

    score += len(signals.get("candidate_companies", [])) * 4
    score += len(signals.get("candidate_price_mentions", [])) * 5
    score += len(signals.get("candidate_percentages", [])) * 2
    score += len(signals.get("candidate_units", [])) * 2
    score += len(signals.get("candidate_years", []))

    return score


def load_stage05_artifact(root: Path, doc_id: str) -> dict[str, Any] | None:
    path = root / "artifacts" / "02_document_artifacts" / f"{doc_id}.stage05_extraction.json"
    if not path.exists():
        return None
    return read_json(path)


def get_extraction_summary(stage05: dict[str, Any] | None) -> dict[str, Any]:
    if not stage05:
        return {
            "has_stage05_artifact": False,
            "text_path": None,
            "page_count": None,
            "total_text_length": 0,
            "rendered_page_images": [],
            "tables": [],
            "copied_image_asset": None,
            "needs_visual_review": False,
            "errors": [],
        }

    extraction = stage05.get("extraction", {})
    pdf = extraction.get("pdf", {})
    tables = extraction.get("tables", {})
    image = extraction.get("image", {})
    text = extraction.get("text", {})

    errors = []
    for block in [pdf, tables, image, text]:
        if isinstance(block, dict):
            errors.extend(block.get("errors", []) or [])

    table_list = []
    for table in tables.get("tables", []) or []:
        table_list.append(
            {
                "sheet_or_table_name": table.get("sheet_or_table_name"),
                "rows": table.get("rows"),
                "columns": table.get("columns"),
                "headers": table.get("headers", []),
                "csv_path": table.get("csv_path"),
                "preview_rows": table.get("preview_rows", [])[:3],
            }
        )

    return {
        "has_stage05_artifact": True,
        "text_path": pdf.get("text_path") or tables.get("combined_text_path") or text.get("text_path"),
        "page_count": pdf.get("page_count"),
        "total_text_length": pdf.get("total_text_length") or text.get("text_length") or 0,
        "rendered_page_images": pdf.get("rendered_page_images", [])[:8],
        "tables": table_list,
        "copied_image_asset": image.get("copied_asset_path"),
        "image_width": image.get("width"),
        "image_height": image.get("height"),
        "needs_visual_review": bool(
            pdf.get("needs_visual_review")
            or image.get("needs_visual_review")
            or stage05.get("stage05_status") == "error"
        ),
        "errors": errors,
    }


def select_chunks_for_doc(
    chunks: list[dict[str, Any]],
    max_chunks: int,
    max_total_chars: int,
) -> list[dict[str, Any]]:
    if not chunks:
        return []

    # Always keep first chunk because it usually includes title/header/context.
    selected_by_id = {}

    for chunk in chunks[:2]:
        selected_by_id[chunk["chunk_id"]] = chunk

    scored = sorted(
        chunks,
        key=lambda c: chunk_signal_score(c),
        reverse=True,
    )

    for chunk in scored:
        selected_by_id[chunk["chunk_id"]] = chunk
        if len(selected_by_id) >= max_chunks:
            break

    selected = sorted(
        selected_by_id.values(),
        key=lambda c: c.get("chunk_number", 0),
    )

    final = []
    total_chars = 0

    for chunk in selected:
        text = chunk.get("text", "")
        if total_chars + len(text) > max_total_chars and final:
            continue

        final.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "chunk_number": chunk.get("chunk_number"),
                "page_or_section_hint": chunk.get("page_or_section_hint", ""),
                "signal_score": chunk_signal_score(chunk),
                "signals": chunk.get("signals", {}),
                "text": text,
            }
        )
        total_chars += len(text)

    return final


def choose_ai_input_mode(
    record: dict[str, Any],
    doc_chunks: list[dict[str, Any]],
    extraction_summary: dict[str, Any],
) -> str:
    document_type = record.get("document_type")
    text_len = sum(len(c.get("text", "")) for c in doc_chunks)

    if document_type == "image_or_logo":
        return "visual_asset_only"

    if document_type in ["excel_workbook", "csv_table"]:
        return "table_summary_plus_text"

    if extraction_summary.get("needs_visual_review") and text_len < 500:
        return "visual_priority"

    if extraction_summary.get("needs_visual_review") and extraction_summary.get("rendered_page_images"):
        return "text_plus_page_images"

    if text_len > 0:
        return "text_only"

    return "needs_manual_review"


def priority_score_for_doc(
    record: dict[str, Any],
    chunks: list[dict[str, Any]],
    extraction_summary: dict[str, Any],
) -> int:
    score = 0

    packet = record.get("packet")
    role = record.get("evidence_role")
    doc_type = record.get("document_type")
    name = record.get("file_name", "").lower()

    if role == "direct_company_evidence":
        score += 40
    if role == "supplier_relationship_context":
        score += 35
    if role == "retail_price_evidence":
        score += 35
    if role == "benchmark_proxy":
        score += 25
    if role == "process_or_function_context":
        score += 20
    if role == "regulatory_definition":
        score += 20
    if role == "visual_asset":
        score += 5
    if role == "reference_only":
        score -= 50

    if packet == "product_sku_1_55oz":
        score += 50
    if packet in ["sugar", "cocoa_chocolate_cocoa_butter", "dairy_milk_skim_milk_milk_fat"]:
        score += 25
    if packet in ["soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"]:
        score += 15
    if packet == "retail_price_evidence":
        score += 30
    if packet == "logistics_distribution":
        score += 20

    if "hershey" in name:
        score += 15
    if any(x in name for x in ["asr", "barry", "land_o_lakes", "mclane"]):
        score += 15
    if any(x in name for x in ["price", "benchmark", "ppi", "usda", "icco", "bls", "eia"]):
        score += 10

    score += min(len(chunks), 10)

    if extraction_summary.get("needs_visual_review"):
        score += 5

    if doc_type == "image_or_logo":
        score -= 20

    return score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    parser.add_argument("--max-chunks-per-doc", type=int, default=8)
    parser.add_argument("--max-total-chars-per-doc", type=int, default=14000)
    args = parser.parse_args()

    root = Path(args.root).resolve()

    inventory_path = root / "artifacts" / "00_source_inventory" / "source_inventory_stage05_enriched.json"
    chunks_path = root / "artifacts" / "02_text_chunks" / "text_chunks.jsonl"

    if not inventory_path.exists():
        raise FileNotFoundError(f"Missing inventory: {inventory_path}")

    if not chunks_path.exists():
        raise FileNotFoundError(f"Missing chunks: {chunks_path}")

    inventory = read_json(inventory_path)
    all_chunks = read_jsonl(chunks_path)

    chunks_by_doc: dict[str, list[dict[str, Any]]] = {}
    for chunk in all_chunks:
        chunks_by_doc.setdefault(chunk["doc_id"], []).append(chunk)

    output_dir = root / "artifacts" / "02_document_artifacts" / "level1_inputs"
    report_dir = root / "artifacts" / "10_run_reports"

    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = root / "prompts" / "level1_document_parser.md"

    manifest = []
    priority_rows = []

    for record in inventory:
        doc_id = record["doc_id"]
        doc_chunks = chunks_by_doc.get(doc_id, [])
        stage05 = load_stage05_artifact(root, doc_id)
        extraction_summary = get_extraction_summary(stage05)

        selected_chunks = select_chunks_for_doc(
            chunks=doc_chunks,
            max_chunks=args.max_chunks_per_doc,
            max_total_chars=args.max_total_chars_per_doc,
        )

        ai_input_mode = choose_ai_input_mode(record, selected_chunks, extraction_summary)
        priority_score = priority_score_for_doc(record, selected_chunks, extraction_summary)

        level1_input = {
            "level1_input_version": "v1",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "project_scope": {
                "project": "Hershey Supply Chain AI",
                "product": "HERSHEY'S Milk Chocolate Candy Bar",
                "sku_size": "1.55 oz / 43 g",
                "market": "United States",
                "rule": "Extract facts only. Do not create final supplier or cost conclusions at Level 1."
            },
            "prompt_file": str(prompt_path).replace("\\", "/"),
            "doc_metadata": {
                "doc_id": doc_id,
                "file_name": record.get("file_name"),
                "relative_path": record.get("relative_path"),
                "absolute_path": record.get("absolute_path"),
                "packet": record.get("packet"),
                "source_category": record.get("source_category"),
                "document_type": record.get("document_type"),
                "evidence_role": record.get("evidence_role"),
                "file_extension": record.get("file_extension"),
                "file_size_bytes": record.get("file_size_bytes"),
                "sha256": record.get("sha256"),
            },
            "ai_input_mode": ai_input_mode,
            "priority_score": priority_score,
            "extraction_summary": extraction_summary,
            "selected_chunks": selected_chunks,
            "level1_expected_output": "parsed_document_artifact_json",
            "level1_warnings": [],
        }

        if ai_input_mode in ["visual_priority", "visual_asset_only"]:
            level1_input["level1_warnings"].append(
                "This source needs visual/manual/vision review because text extraction is weak or the file is image-based."
            )

        if record.get("evidence_role") == "reference_only":
            level1_input["level1_warnings"].append(
                "Reference-only file. Do not use as factual evidence for final claims."
            )

        if record.get("evidence_role") == "visual_asset":
            level1_input["level1_warnings"].append(
                "Visual asset only. Logo/image does not prove supplier relationship."
            )

        out_path = output_dir / f"{doc_id}.level1_input.json"
        write_json(out_path, level1_input)

        manifest_row = {
            "doc_id": doc_id,
            "file_name": record.get("file_name"),
            "packet": record.get("packet"),
            "document_type": record.get("document_type"),
            "evidence_role": record.get("evidence_role"),
            "ai_input_mode": ai_input_mode,
            "priority_score": priority_score,
            "selected_chunk_count": len(selected_chunks),
            "has_page_images": bool(extraction_summary.get("rendered_page_images")),
            "has_tables": bool(extraction_summary.get("tables")),
            "needs_visual_review": extraction_summary.get("needs_visual_review"),
            "level1_input_path": str(out_path).replace("\\", "/"),
        }

        manifest.append(manifest_row)
        priority_rows.append(manifest_row)

    priority_rows = sorted(priority_rows, key=lambda x: x["priority_score"], reverse=True)

    manifest_path = output_dir / "_all_level1_inputs_manifest.json"
    priority_csv_path = output_dir / "_level1_priority_queue.csv"
    priority_json_path = output_dir / "_level1_priority_queue.json"

    write_json(manifest_path, manifest)
    write_json(priority_json_path, priority_rows)

    with priority_csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "doc_id",
            "file_name",
            "packet",
            "document_type",
            "evidence_role",
            "ai_input_mode",
            "priority_score",
            "selected_chunk_count",
            "has_page_images",
            "has_tables",
            "needs_visual_review",
            "level1_input_path",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(priority_rows)

    mode_counts: dict[str, int] = {}
    packet_counts: dict[str, int] = {}

    for row in manifest:
        mode_counts[row["ai_input_mode"]] = mode_counts.get(row["ai_input_mode"], 0) + 1
        packet_counts[row["packet"]] = packet_counts.get(row["packet"], 0) + 1

    report = {
        "run_name": "step07_build_level1_ai_inputs",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "documents_packaged": len(manifest),
        "total_chunks_available": len(all_chunks),
        "max_chunks_per_doc": args.max_chunks_per_doc,
        "max_total_chars_per_doc": args.max_total_chars_per_doc,
        "ai_input_mode_counts": mode_counts,
        "packet_counts": packet_counts,
        "level1_inputs_folder": str(output_dir).replace("\\", "/"),
        "manifest_json": str(manifest_path).replace("\\", "/"),
        "priority_queue_csv": str(priority_csv_path).replace("\\", "/"),
        "priority_queue_json": str(priority_json_path).replace("\\", "/"),
        "next_step": "Step 08: run Level 1 parser on selected high-priority document input packets."
    }

    report_path = report_dir / "step07_level1_input_builder_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 07 LEVEL 1 AI INPUT BUILDER COMPLETE")
    print("-----------------------------------------")
    print(f"Documents packaged: {len(manifest)}")
    print(f"Total chunks available: {len(all_chunks)}")
    print(f"Input modes: {mode_counts}")
    print("")
    print(f"Priority queue CSV: {priority_csv_path}")
    print(f"Report JSON:        {report_path}")
    print("")


if __name__ == "__main__":
    main()