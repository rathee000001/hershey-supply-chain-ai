from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
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
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if isinstance(row, dict):
                    row["_jsonl_source_path"] = str(path).replace("\\", "/")
                    row["_jsonl_line_number"] = line_number
                    rows.append(row)
            except Exception as exc:
                rows.append(
                    {
                        "_jsonl_source_path": str(path).replace("\\", "/"),
                        "_jsonl_line_number": line_number,
                        "_parse_error": str(exc),
                        "text": "",
                    }
                )
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def clean_text(text: Any) -> str:
    text = str(text or "")
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]


def detect_signals(text: str) -> dict[str, list[str]]:
    lower = text.lower()

    groups = {
        "companies": [
            "hershey",
            "asr",
            "asr group",
            "american sugar refining",
            "domino",
            "barry callebaut",
            "land o'lakes",
            "land o’lakes",
            "mclane",
            "walmart",
            "target",
            "cvs",
            "walgreens",
            "usda",
            "fda",
            "epa",
            "icco",
            "bls",
            "eia",
            "fred",
            "ice",
        ],
        "ingredients": [
            "sugar",
            "cocoa",
            "cocoa mass",
            "chocolate",
            "cocoa butter",
            "milk",
            "skim milk",
            "milk fat",
            "soy lecithin",
            "lecithin",
            "pgpr",
            "polyglycerol polyricinoleate",
            "natural flavor",
            "packaging",
            "wrapper",
            "pulp",
            "paper",
        ],
        "claim_terms": [
            "supplier",
            "sourcing",
            "sourced",
            "partner",
            "agreement",
            "sustainability",
            "sustainable",
            "responsible sourcing",
            "ingredients",
            "manufacturing",
            "distribution",
            "warehouse",
            "retail",
            "price",
            "cost",
            "market",
            "farm",
            "farmers",
            "cooperative",
        ],
        "sku_terms": [
            "1.55 oz",
            "43 g",
            "milk chocolate",
            "nutrition facts",
            "calories",
            "upc",
            "barcode",
            "ingredients",
            "serving size",
        ],
        "cost_terms": [
            "price",
            "cost",
            "market",
            "index",
            "ppi",
            "cents",
            "dollars",
            "$",
            "per kg",
            "per pound",
            "per metric ton",
            "retail",
        ],
    }

    out: dict[str, list[str]] = {}

    for group, terms in groups.items():
        hits = []
        for term in terms:
            if term.lower() in lower:
                hits.append(term)
        out[group] = sorted(set(hits))

    return out


def classify_chunk_usefulness(text: str, signals: dict[str, list[str]]) -> str:
    length = len(text)

    if length < 80:
        return "low_short_text"

    has_company = bool(signals.get("companies"))
    has_ingredient = bool(signals.get("ingredients"))
    has_claim = bool(signals.get("claim_terms"))
    has_sku = bool(signals.get("sku_terms"))
    has_cost = bool(signals.get("cost_terms"))

    if has_sku and (has_company or has_ingredient):
        return "high_sku_evidence"
    if has_company and has_ingredient and has_claim:
        return "high_supplier_or_ingredient_evidence"
    if has_cost and (has_ingredient or has_company):
        return "high_cost_or_price_evidence"
    if has_company or has_ingredient or has_claim:
        return "medium_context_evidence"

    return "low_background"


def get_text_from_row(row: dict[str, Any]) -> str:
    for key in ["text", "chunk_text", "content", "ocr_text", "page_text", "body"]:
        if row.get(key):
            return clean_text(row.get(key))
    return ""


def normalize_source_type(row: dict[str, Any], fallback: str) -> str:
    chunk_source = str(row.get("chunk_source") or row.get("source_type") or "").strip().lower()

    if "visual" in chunk_source or "ocr" in chunk_source:
        return "visual_ocr"

    if fallback:
        return fallback

    return "text_or_table"


def normalize_doc_id(row: dict[str, Any]) -> str:
    for key in ["doc_id", "document_id", "source_doc_id"]:
        if row.get(key):
            return str(row.get(key))
    source = str(row.get("source_file") or row.get("file_name") or row.get("_jsonl_source_path") or "unknown")
    return "DOC_UNKNOWN_" + stable_hash(source)


def normalize_file_name(row: dict[str, Any]) -> str:
    for key in ["file_name", "source_file", "document_name", "raw_file_name"]:
        if row.get(key):
            return str(row.get(key))
    return ""


def normalize_packet(row: dict[str, Any]) -> str:
    for key in ["packet", "packet_name", "source_packet", "category"]:
        if row.get(key):
            return str(row.get(key))
    return "unknown"


def load_original_text_chunks(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    chunk_dir = root / "artifacts" / "02_text_chunks"
    rows: list[dict[str, Any]] = []
    files_used: list[str] = []

    if not chunk_dir.exists():
        return rows, files_used

    candidates = sorted(chunk_dir.glob("*.jsonl"))

    for path in candidates:
        if "unified" in path.name.lower():
            continue
        if "visual" in path.name.lower():
            continue

        file_rows = read_jsonl(path)
        if file_rows:
            files_used.append(str(path).replace("\\", "/"))
            rows.extend(file_rows)

    return rows, files_used


def load_visual_ocr_chunks(root: Path) -> tuple[list[dict[str, Any]], str]:
    path = root / "artifacts" / "02_visual_text" / "visual_ocr_chunks.jsonl"
    rows = read_jsonl(path)
    return rows, str(path).replace("\\", "/")


def build_unified_chunks(
    original_rows: list[dict[str, Any]],
    visual_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    unified = []
    duplicate_hashes = set()
    duplicate_count = 0

    combined_sources = [
        ("text_or_table", original_rows),
        ("visual_ocr", visual_rows),
    ]

    counter = 1

    for fallback_source_type, rows in combined_sources:
        for row in rows:
            text = get_text_from_row(row)
            if not text:
                continue

            doc_id = normalize_doc_id(row)
            file_name = normalize_file_name(row)
            packet = normalize_packet(row)
            source_type = normalize_source_type(row, fallback_source_type)

            dedupe_key = stable_hash(f"{doc_id}|{source_type}|{text[:1200]}")
            if dedupe_key in duplicate_hashes:
                duplicate_count += 1
                continue
            duplicate_hashes.add(dedupe_key)

            signals = row.get("signals") if isinstance(row.get("signals"), dict) else detect_signals(text)
            usefulness = classify_chunk_usefulness(text, signals)

            original_chunk_id = (
                row.get("chunk_id")
                or row.get("id")
                or row.get("chunk_number")
                or f"ROW_{counter:06d}"
            )

            unified_chunk = {
                "unified_chunk_id": f"UCHUNK_{counter:06d}",
                "original_chunk_id": str(original_chunk_id),
                "doc_id": doc_id,
                "file_name": file_name,
                "packet": packet,
                "document_type": row.get("document_type", ""),
                "source_type": source_type,
                "chunk_source_path": row.get("_jsonl_source_path", ""),
                "chunk_source_line": row.get("_jsonl_line_number", ""),
                "page_number": row.get("page_number", row.get("page", "")),
                "chunk_number": row.get("chunk_number", ""),
                "start_char": row.get("start_char", ""),
                "end_char": row.get("end_char", ""),
                "text_length": len(text),
                "word_count": len(text.split()),
                "usefulness_class": usefulness,
                "signals": signals,
                "text": text,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }

            unified.append(unified_chunk)
            counter += 1

    stats = {
        "duplicates_removed": duplicate_count,
        "unified_chunks_created": len(unified),
    }

    return unified, stats


def build_document_memory(unified_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for chunk in unified_chunks:
        grouped[chunk["doc_id"]].append(chunk)

    docs = []

    for doc_id, chunks in sorted(grouped.items()):
        packets = sorted(set(str(c.get("packet", "")) for c in chunks if c.get("packet")))
        file_names = sorted(set(str(c.get("file_name", "")) for c in chunks if c.get("file_name")))
        source_types = sorted(set(str(c.get("source_type", "")) for c in chunks if c.get("source_type")))
        usefulness_counts = defaultdict(int)

        merged_signals = {
            "companies": set(),
            "ingredients": set(),
            "claim_terms": set(),
            "sku_terms": set(),
            "cost_terms": set(),
        }

        for chunk in chunks:
            usefulness_counts[chunk.get("usefulness_class", "unknown")] += 1
            signals = chunk.get("signals", {})
            if isinstance(signals, dict):
                for key in merged_signals:
                    for value in signals.get(key, []) or []:
                        merged_signals[key].add(value)

        docs.append(
            {
                "doc_id": doc_id,
                "file_names": file_names,
                "primary_file_name": file_names[0] if file_names else "",
                "packets": packets,
                "source_types": source_types,
                "chunk_count": len(chunks),
                "total_text_length": sum(int(c.get("text_length", 0)) for c in chunks),
                "usefulness_counts": dict(sorted(usefulness_counts.items())),
                "signals": {k: sorted(v) for k, v in merged_signals.items()},
                "has_visual_ocr": "visual_ocr" in source_types,
                "has_text_or_table": "text_or_table" in source_types,
            }
        )

    return docs


def write_summary_csv(path: Path, unified_chunks: list[dict[str, Any]]) -> None:
    fieldnames = [
        "unified_chunk_id",
        "doc_id",
        "file_name",
        "packet",
        "source_type",
        "document_type",
        "text_length",
        "word_count",
        "usefulness_class",
        "companies",
        "ingredients",
        "claim_terms",
        "sku_terms",
        "cost_terms",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for chunk in unified_chunks:
            signals = chunk.get("signals", {})
            writer.writerow(
                {
                    "unified_chunk_id": chunk.get("unified_chunk_id", ""),
                    "doc_id": chunk.get("doc_id", ""),
                    "file_name": chunk.get("file_name", ""),
                    "packet": chunk.get("packet", ""),
                    "source_type": chunk.get("source_type", ""),
                    "document_type": chunk.get("document_type", ""),
                    "text_length": chunk.get("text_length", ""),
                    "word_count": chunk.get("word_count", ""),
                    "usefulness_class": chunk.get("usefulness_class", ""),
                    "companies": "; ".join(signals.get("companies", []) if isinstance(signals, dict) else []),
                    "ingredients": "; ".join(signals.get("ingredients", []) if isinstance(signals, dict) else []),
                    "claim_terms": "; ".join(signals.get("claim_terms", []) if isinstance(signals, dict) else []),
                    "sku_terms": "; ".join(signals.get("sku_terms", []) if isinstance(signals, dict) else []),
                    "cost_terms": "; ".join(signals.get("cost_terms", []) if isinstance(signals, dict) else []),
                }
            )


def write_document_summary_csv(path: Path, docs: list[dict[str, Any]]) -> None:
    fieldnames = [
        "doc_id",
        "primary_file_name",
        "packets",
        "source_types",
        "chunk_count",
        "total_text_length",
        "has_visual_ocr",
        "has_text_or_table",
        "companies",
        "ingredients",
        "claim_terms",
        "sku_terms",
        "cost_terms",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for doc in docs:
            signals = doc.get("signals", {})
            writer.writerow(
                {
                    "doc_id": doc.get("doc_id", ""),
                    "primary_file_name": doc.get("primary_file_name", ""),
                    "packets": "; ".join(doc.get("packets", [])),
                    "source_types": "; ".join(doc.get("source_types", [])),
                    "chunk_count": doc.get("chunk_count", ""),
                    "total_text_length": doc.get("total_text_length", ""),
                    "has_visual_ocr": doc.get("has_visual_ocr", False),
                    "has_text_or_table": doc.get("has_text_or_table", False),
                    "companies": "; ".join(signals.get("companies", [])),
                    "ingredients": "; ".join(signals.get("ingredients", [])),
                    "claim_terms": "; ".join(signals.get("claim_terms", [])),
                    "sku_terms": "; ".join(signals.get("sku_terms", [])),
                    "cost_terms": "; ".join(signals.get("cost_terms", [])),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    out_dir = root / "artifacts" / "11_unified_memory"
    report_dir = root / "artifacts" / "10_run_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    original_rows, original_files_used = load_original_text_chunks(root)
    visual_rows, visual_file_used = load_visual_ocr_chunks(root)

    unified_chunks, stats = build_unified_chunks(original_rows, visual_rows)
    document_memory = build_document_memory(unified_chunks)

    unified_jsonl = out_dir / "unified_chunks.jsonl"
    unified_summary_csv = out_dir / "unified_chunks_summary.csv"
    document_memory_json = out_dir / "unified_document_memory.json"
    document_memory_csv = out_dir / "unified_document_memory_summary.csv"
    manifest_json = out_dir / "unified_memory_manifest.json"

    write_jsonl(unified_jsonl, unified_chunks)
    write_summary_csv(unified_summary_csv, unified_chunks)
    write_json(document_memory_json, document_memory)
    write_document_summary_csv(document_memory_csv, document_memory)

    source_type_counts = defaultdict(int)
    usefulness_counts = defaultdict(int)
    packet_counts = defaultdict(int)

    for chunk in unified_chunks:
        source_type_counts[chunk.get("source_type", "unknown")] += 1
        usefulness_counts[chunk.get("usefulness_class", "unknown")] += 1
        packet_counts[chunk.get("packet", "unknown")] += 1

    manifest = {
        "unified_memory_version": "v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "purpose": "Merged parser memory from original extracted text/table chunks plus visual OCR screenshot/image chunks.",
        "input_sources": {
            "original_text_chunk_files": original_files_used,
            "visual_ocr_chunk_file": visual_file_used,
        },
        "outputs": {
            "unified_chunks_jsonl": str(unified_jsonl).replace("\\", "/"),
            "unified_chunks_summary_csv": str(unified_summary_csv).replace("\\", "/"),
            "unified_document_memory_json": str(document_memory_json).replace("\\", "/"),
            "unified_document_memory_summary_csv": str(document_memory_csv).replace("\\", "/"),
        },
        "frontend_rule": "This is a research brain artifact. Frontend should not display raw unified memory directly; frontend displays approved audited JSON only.",
        "rag_rule": "Vector/RAG index should be built from unified_chunks.jsonl with metadata preserved.",
    }

    write_json(manifest_json, manifest)

    report = {
        "run_name": "step16d_unified_memory_merge",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "original_text_rows_seen": len(original_rows),
        "visual_ocr_rows_seen": len(visual_rows),
        "unified_chunks_created": len(unified_chunks),
        "documents_in_unified_memory": len(document_memory),
        "duplicates_removed": stats["duplicates_removed"],
        "source_type_counts": dict(sorted(source_type_counts.items())),
        "usefulness_counts": dict(sorted(usefulness_counts.items())),
        "packet_counts": dict(sorted(packet_counts.items())),
        "unified_chunks_jsonl": str(unified_jsonl).replace("\\", "/"),
        "unified_chunks_summary_csv": str(unified_summary_csv).replace("\\", "/"),
        "unified_document_memory_json": str(document_memory_json).replace("\\", "/"),
        "unified_document_memory_summary_csv": str(document_memory_csv).replace("\\", "/"),
        "manifest_json": str(manifest_json).replace("\\", "/"),
        "next_step": "Step 16E: build local vector/RAG index from unified_chunks.jsonl.",
    }

    report_path = report_dir / "step16d_unified_memory_merge_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16D UNIFIED MEMORY MERGE COMPLETE")
    print("--------------------------------------")
    print(f"Original text rows seen: {len(original_rows)}")
    print(f"Visual OCR rows seen: {len(visual_rows)}")
    print(f"Unified chunks created: {len(unified_chunks)}")
    print(f"Documents in memory: {len(document_memory)}")
    print(f"Duplicates removed: {stats['duplicates_removed']}")
    print("")
    print(f"Unified chunks: {unified_jsonl}")
    print(f"Summary CSV:    {unified_summary_csv}")
    print(f"Document memory:{document_memory_json}")
    print(f"Report JSON:    {report_path}")
    print("")


if __name__ == "__main__":
    main()