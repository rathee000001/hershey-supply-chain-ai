from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


KNOWN_COMPANIES = [
    "Hershey",
    "The Hershey Company",
    "Barry Callebaut",
    "ASR",
    "American Sugar Refining",
    "Domino",
    "Land O'Lakes",
    "McLane",
    "Walmart",
    "Target",
    "CVS",
    "Walgreens",
    "USDA",
    "USDA ERS",
    "USDA AMS",
    "FDA",
    "EFSA",
    "ICCO",
    "EPA",
    "BLS",
    "EIA",
    "FEMA",
    "Alliance for the Chesapeake Bay",
]

KEYWORD_GROUPS = {
    "product_sku": [
        "1.55 oz",
        "43 g",
        "milk chocolate",
        "nutrition facts",
        "ingredients",
        "barcode",
        "upc",
        "calories",
        "serving",
    ],
    "ingredient": [
        "sugar",
        "chocolate",
        "cocoa",
        "cocoa butter",
        "milk",
        "skim milk",
        "milk fat",
        "lecithin",
        "soy",
        "pgpr",
        "natural flavor",
    ],
    "supplier": [
        "supplier",
        "suppliers",
        "sourcing",
        "sourced",
        "partner",
        "partnership",
        "supply agreement",
        "strategic agreement",
        "member-owner",
        "cooperative",
    ],
    "cost_price": [
        "cost",
        "price",
        "prices",
        "pricing",
        "benchmark",
        "market",
        "futures",
        "ppi",
        "index",
        "per lb",
        "per pound",
        "cents",
        "$",
    ],
    "manufacturing": [
        "manufacturing",
        "production",
        "plant",
        "factory",
        "processing",
        "molding",
        "wrapping",
        "packaging",
        "tempering",
        "conching",
        "refining",
    ],
    "logistics": [
        "distribution",
        "warehouse",
        "warehousing",
        "freight",
        "truck",
        "trucking",
        "diesel",
        "common carrier",
        "transport",
    ],
    "retail": [
        "retail",
        "retailer",
        "store",
        "pickup",
        "delivery",
        "walmart",
        "target",
        "cvs",
        "walgreens",
    ],
    "regulatory": [
        "fda",
        "gras",
        "efsa",
        "cfr",
        "food additive",
        "natural flavor",
        "lecithin",
        "emulsifier",
    ],
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def find_page_marker_near(text: str, start: int) -> str:
    before = text[:start]
    matches = list(re.finditer(r"--- PAGE\s+(\d+)\s+---", before, flags=re.IGNORECASE))
    if matches:
        return f"page_{matches[-1].group(1)}"
    return ""


def detect_keyword_hits(text: str) -> dict[str, list[str]]:
    lower = text.lower()
    hits: dict[str, list[str]] = {}

    for group, keywords in KEYWORD_GROUPS.items():
        group_hits = []
        for keyword in keywords:
            if keyword.lower() in lower:
                group_hits.append(keyword)
        hits[group] = group_hits

    return hits


def detect_companies(text: str) -> list[str]:
    lower = text.lower()
    companies = []

    for company in KNOWN_COMPANIES:
        if company.lower() in lower:
            companies.append(company)

    return list(dict.fromkeys(companies))


def detect_price_mentions(text: str) -> list[str]:
    patterns = [
        r"\$[\d,]+(?:\.\d+)?",
        r"\b\d+(?:\.\d+)?\s?¢",
        r"\b\d+(?:\.\d+)?\s?cents\b",
        r"\b\d+(?:\.\d+)?\s?(?:per lb|/lb|per pound)\b",
        r"\b\d+(?:\.\d+)?\s?(?:dollars per pound|cents per pound)\b",
    ]

    mentions = []
    for pattern in patterns:
        mentions.extend(re.findall(pattern, text, flags=re.IGNORECASE))

    return list(dict.fromkeys([str(x) for x in mentions]))[:50]


def detect_percentages(text: str) -> list[str]:
    matches = re.findall(r"\b\d+(?:\.\d+)?\s?%", text)
    return list(dict.fromkeys(matches))[:50]


def detect_years(text: str) -> list[str]:
    matches = re.findall(r"\b(?:19|20)\d{2}\b", text)
    return list(dict.fromkeys(matches))[:50]


def detect_units(text: str) -> list[str]:
    patterns = [
        r"\b\d+(?:\.\d+)?\s?(?:g|gram|grams)\b",
        r"\b\d+(?:\.\d+)?\s?(?:oz|ounce|ounces)\b",
        r"\b\d+(?:\.\d+)?\s?(?:lb|lbs|pound|pounds)\b",
        r"\b\d+(?:\.\d+)?\s?(?:kg|kilogram|kilograms)\b",
    ]

    units = []
    for pattern in patterns:
        units.extend(re.findall(pattern, text, flags=re.IGNORECASE))

    return list(dict.fromkeys([str(x) for x in units]))[:50]


def chunk_text(
    text: str,
    doc_id: str,
    max_chars: int = 2200,
    overlap: int = 300,
) -> list[dict[str, Any]]:
    text = normalize_text(text)
    chunks = []

    if not text:
        return chunks

    start = 0
    chunk_number = 1

    while start < len(text):
        end = min(start + max_chars, len(text))

        # Try to end chunks near paragraph boundary.
        if end < len(text):
            paragraph_break = text.rfind("\n\n", start, end)
            if paragraph_break > start + int(max_chars * 0.55):
                end = paragraph_break

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(
                {
                    "chunk_id": f"{doc_id}_CHUNK_{chunk_number:04d}",
                    "doc_id": doc_id,
                    "chunk_number": chunk_number,
                    "start_char": start,
                    "end_char": end,
                    "page_or_section_hint": find_page_marker_near(text, start),
                    "text": chunk,
                }
            )
            chunk_number += 1

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks


def load_extracted_text_for_record(root: Path, record: dict[str, Any]) -> str:
    doc_id = record["doc_id"]
    text_path = root / "artifacts" / "01_extracted_text" / f"{doc_id}.txt"

    if text_path.exists():
        return text_path.read_text(encoding="utf-8", errors="ignore")

    return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    parser.add_argument("--max-chars", type=int, default=2200)
    parser.add_argument("--overlap", type=int, default=300)
    args = parser.parse_args()

    root = Path(args.root).resolve()

    inventory_path = (
        root
        / "artifacts"
        / "00_source_inventory"
        / "source_inventory_stage05_enriched.json"
    )

    if not inventory_path.exists():
        raise FileNotFoundError(
            f"Missing enriched inventory from Step 05: {inventory_path}"
        )

    inventory = read_json(inventory_path)

    chunks_dir = root / "artifacts" / "02_text_chunks"
    report_dir = root / "artifacts" / "10_run_reports"

    chunks_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    all_chunks: list[dict[str, Any]] = []
    doc_chunk_summary: list[dict[str, Any]] = []

    files_with_text = 0
    files_without_text = 0

    for record in inventory:
        doc_id = record["doc_id"]
        text = load_extracted_text_for_record(root, record)

        if text.strip():
            files_with_text += 1
        else:
            files_without_text += 1

        chunks = chunk_text(
            text=text,
            doc_id=doc_id,
            max_chars=args.max_chars,
            overlap=args.overlap,
        )

        for chunk in chunks:
            signals = {
                "keyword_hits": detect_keyword_hits(chunk["text"]),
                "candidate_companies": detect_companies(chunk["text"]),
                "candidate_price_mentions": detect_price_mentions(chunk["text"]),
                "candidate_percentages": detect_percentages(chunk["text"]),
                "candidate_years": detect_years(chunk["text"]),
                "candidate_units": detect_units(chunk["text"]),
            }

            chunk.update(
                {
                    "file_name": record["file_name"],
                    "relative_path": record["relative_path"],
                    "packet": record["packet"],
                    "source_category": record.get("source_category", ""),
                    "document_type": record["document_type"],
                    "evidence_role": record["evidence_role"],
                    "signals": signals,
                }
            )

        all_chunks.extend(chunks)

        doc_chunk_summary.append(
            {
                "doc_id": doc_id,
                "file_name": record["file_name"],
                "packet": record["packet"],
                "document_type": record["document_type"],
                "evidence_role": record["evidence_role"],
                "text_length": len(text),
                "chunk_count": len(chunks),
                "has_text": bool(text.strip()),
            }
        )

    chunks_jsonl_path = chunks_dir / "text_chunks.jsonl"
    with chunks_jsonl_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    chunks_json_path = chunks_dir / "text_chunks_preview.json"
    write_json(chunks_json_path, all_chunks[:100])

    doc_summary_json = chunks_dir / "document_chunk_summary.json"
    write_json(doc_summary_json, doc_chunk_summary)

    doc_summary_csv = chunks_dir / "document_chunk_summary.csv"
    with doc_summary_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "doc_id",
            "file_name",
            "packet",
            "document_type",
            "evidence_role",
            "text_length",
            "chunk_count",
            "has_text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(doc_chunk_summary)

    packet_summary: dict[str, dict[str, Any]] = {}
    for row in doc_chunk_summary:
        packet = row["packet"]
        if packet not in packet_summary:
            packet_summary[packet] = {
                "packet": packet,
                "documents": 0,
                "documents_with_text": 0,
                "total_chunks": 0,
                "total_text_length": 0,
            }

        packet_summary[packet]["documents"] += 1
        packet_summary[packet]["total_chunks"] += row["chunk_count"]
        packet_summary[packet]["total_text_length"] += row["text_length"]

        if row["has_text"]:
            packet_summary[packet]["documents_with_text"] += 1

    packet_summary_list = list(packet_summary.values())
    write_json(chunks_dir / "packet_chunk_summary.json", packet_summary_list)

    report = {
        "run_name": "step06_build_text_chunks",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "source_inventory_input": str(inventory_path).replace("\\", "/"),
        "documents_seen": len(inventory),
        "files_with_text": files_with_text,
        "files_without_text": files_without_text,
        "total_chunks": len(all_chunks),
        "max_chars": args.max_chars,
        "overlap": args.overlap,
        "text_chunks_jsonl": str(chunks_jsonl_path).replace("\\", "/"),
        "text_chunks_preview_json": str(chunks_json_path).replace("\\", "/"),
        "document_chunk_summary_json": str(doc_summary_json).replace("\\", "/"),
        "document_chunk_summary_csv": str(doc_summary_csv).replace("\\", "/"),
        "packet_chunk_summary_json": str(chunks_dir / "packet_chunk_summary.json").replace("\\", "/"),
        "next_step": "Step 07: create Level 1 AI document parser inputs from chunks and extraction artifacts.",
    }

    report_path = report_dir / "step06_text_chunk_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 06 TEXT CHUNK BUILDER COMPLETE")
    print("-----------------------------------")
    print(f"Documents seen: {len(inventory)}")
    print(f"Files with text: {files_with_text}")
    print(f"Files without text: {files_without_text}")
    print(f"Total chunks: {len(all_chunks)}")
    print("")
    print(f"Chunks JSONL: {chunks_jsonl_path}")
    print(f"Doc summary:  {doc_summary_csv}")
    print(f"Report JSON:  {report_path}")
    print("")


if __name__ == "__main__":
    main()