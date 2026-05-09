from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageOps
from tqdm import tqdm


OCR_ENGINE_NAME = "tesseract_local"
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def normalize_ocr_text(text: str) -> str:
    text = clean_text(text)
    fixes = {
        "HERSHEY S": "HERSHEY'S",
        "HERSHEY’S": "HERSHEY'S",
        "Land O Lakes": "Land O'Lakes",
        "Land O’Lakes": "Land O'Lakes",
        "Barry Callebaut": "Barry Callebaut",
        "ASR Group": "ASR Group",
    }

    for old, new in fixes.items():
        text = text.replace(old, new)

    return text


def find_tesseract_cmd() -> str:
    candidates = [
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)

    return ""


def check_tesseract_available() -> tuple[bool, str]:
    cmd = find_tesseract_cmd()
    if not cmd:
        return False, ""

    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, cmd
    except Exception:
        pass

    return False, ""


def configure_pytesseract(tesseract_cmd: str) -> None:
    import pytesseract

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def preprocess_image_for_ocr(image_path: Path, max_width: int = 2400) -> Image.Image:
    img = Image.open(image_path).convert("RGB")

    # Upscale smaller images but avoid giant memory load.
    width, height = img.size
    if width < 1600:
        scale = min(max_width / max(width, 1), 2.5)
        new_size = (int(width * scale), int(height * scale))
        img = img.resize(new_size)

    # Improve contrast for webpage screenshots.
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(1.45)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    return img


def run_ocr(image_path: Path, tesseract_cmd: str) -> dict[str, Any]:
    import pytesseract

    configure_pytesseract(tesseract_cmd)

    try:
        img = preprocess_image_for_ocr(image_path)

        config = "--oem 3 --psm 6"
        text = pytesseract.image_to_string(img, lang="eng", config=config)
        text = normalize_ocr_text(text)

        data = pytesseract.image_to_data(
            img,
            lang="eng",
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        confidences = []
        words = []

        for word, conf in zip(data.get("text", []), data.get("conf", [])):
            word = str(word or "").strip()
            if not word:
                continue

            try:
                conf_value = float(conf)
            except Exception:
                conf_value = -1.0

            if conf_value >= 0:
                confidences.append(conf_value)
            words.append(word)

        avg_conf = sum(confidences) / len(confidences) if confidences else None

        return {
            "ocr_status": "success",
            "ocr_text": text,
            "ocr_text_length": len(text),
            "word_count": len(words),
            "avg_confidence": round(avg_conf, 2) if avg_conf is not None else None,
            "error": "",
        }

    except Exception as exc:
        return {
            "ocr_status": "error",
            "ocr_text": "",
            "ocr_text_length": 0,
            "word_count": 0,
            "avg_confidence": None,
            "error": str(exc),
        }


def get_stage05_artifacts(root: Path) -> list[Path]:
    folder = root / "artifacts" / "02_document_artifacts"
    if not folder.exists():
        return []
    return sorted(folder.glob("DOC_*.stage05_extraction.json"))


def resolve_path(root: Path, path_text: str) -> Path | None:
    if not path_text:
        return None

    raw = path_text.replace("\\", "/").strip()
    p = Path(raw)

    candidates = []
    if p.is_absolute():
        candidates.append(p)

    candidates.extend(
        [
            root / raw,
            root / "artifacts" / raw,
            root / "public" / raw.lstrip("/"),
        ]
    )

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def collect_images_for_doc(root: Path, stage05: dict[str, Any]) -> list[dict[str, Any]]:
    images = []
    extraction = stage05.get("extraction", {})
    pdf = extraction.get("pdf", {})
    image_block = extraction.get("image", {})

    for idx, path_text in enumerate(pdf.get("rendered_page_images", []) or [], start=1):
        p = resolve_path(root, str(path_text))
        if p and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            images.append(
                {
                    "image_role": "rendered_pdf_page",
                    "page_number": idx,
                    "source_path": str(p).replace("\\", "/"),
                    "original_path_text": str(path_text),
                }
            )

    copied_asset = image_block.get("copied_asset_path")
    if copied_asset:
        p = resolve_path(root, str(copied_asset))
        if p and p.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            images.append(
                {
                    "image_role": "image_or_logo_asset",
                    "page_number": None,
                    "source_path": str(p).replace("\\", "/"),
                    "original_path_text": str(copied_asset),
                }
            )

    return images


def should_ocr_doc(stage05: dict[str, Any], images: list[dict[str, Any]], force_all: bool) -> bool:
    if force_all:
        return bool(images)

    extraction = stage05.get("extraction", {})
    pdf = extraction.get("pdf", {})
    image_block = extraction.get("image", {})
    stage_status = stage05.get("stage05_status", "")

    text_len = int(pdf.get("total_text_length") or image_block.get("text_length") or 0)
    needs_visual = bool(pdf.get("needs_visual_review") or image_block.get("needs_visual_review"))

    if stage_status == "error":
        return bool(images)

    if needs_visual:
        return bool(images)

    if text_len < 500 and images:
        return True

    return False


def detect_visual_entities(text: str) -> dict[str, list[str]]:
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
            "mclane",
            "walmart",
            "target",
            "cvs",
            "walgreens",
            "usda",
            "fda",
            "efsa",
            "icco",
            "bls",
            "eia",
        ],
        "ingredients": [
            "sugar",
            "cocoa",
            "chocolate",
            "cocoa butter",
            "milk",
            "skim milk",
            "milk fat",
            "soy lecithin",
            "lecithin",
            "pgpr",
            "natural flavor",
            "packaging",
            "wrapper",
        ],
        "supply_chain_terms": [
            "supplier",
            "sourcing",
            "sourced",
            "sustainability",
            "sustainable",
            "ingredient",
            "products",
            "refinery",
            "distribution",
            "warehouse",
            "retail",
            "price",
            "cost",
            "market",
            "farm",
            "farmers",
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
        ],
    }

    hits: dict[str, list[str]] = {}

    for group, terms in groups.items():
        group_hits = []
        for term in terms:
            if term.lower() in lower:
                group_hits.append(term)
        hits[group] = group_hits

    return hits


def chunk_visual_text(doc_id: str, text: str, max_chars: int = 2200, overlap: int = 300) -> list[dict[str, Any]]:
    text = clean_text(text)
    chunks = []

    if not text:
        return chunks

    start = 0
    idx = 1

    while start < len(text):
        end = min(start + max_chars, len(text))

        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary > start + int(max_chars * 0.5):
                end = boundary

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                {
                    "chunk_id": f"{doc_id}_VISUAL_CHUNK_{idx:04d}",
                    "doc_id": doc_id,
                    "chunk_number": idx,
                    "chunk_source": "visual_ocr",
                    "start_char": start,
                    "end_char": end,
                    "text": chunk_text,
                    "signals": detect_visual_entities(chunk_text),
                }
            )
            idx += 1

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks


def process_document(
    root: Path,
    stage05_path: Path,
    out_doc_dir: Path,
    tesseract_cmd: str,
    force_all: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    stage05 = read_json(stage05_path)
    doc_id = stage05.get("doc_id", stage05_path.stem.split(".")[0])
    file_name = stage05.get("file_name", "")
    packet = stage05.get("packet", "")
    document_type = stage05.get("document_type", "")

    images = collect_images_for_doc(root, stage05)
    ocr_needed = should_ocr_doc(stage05, images, force_all)

    page_results = []
    combined_parts = []

    if ocr_needed:
        for image in images:
            image_path = Path(image["source_path"])
            ocr_result = run_ocr(image_path, tesseract_cmd)

            page_record = {
                **image,
                "sha256": sha256_file(image_path),
                "ocr_engine": OCR_ENGINE_NAME,
                **ocr_result,
            }

            page_results.append(page_record)

            if ocr_result["ocr_text"]:
                page_label = image.get("page_number")
                label = f"PAGE {page_label}" if page_label else image.get("image_role", "IMAGE")
                combined_parts.append(
                    f"\n--- VISUAL OCR {label}: {image_path.name} ---\n{ocr_result['ocr_text']}"
                )

    combined_text = clean_text("\n".join(combined_parts))
    chunks = chunk_visual_text(doc_id, combined_text)

    doc_record = {
        "doc_id": doc_id,
        "file_name": file_name,
        "packet": packet,
        "document_type": document_type,
        "stage05_artifact": str(stage05_path).replace("\\", "/"),
        "ocr_needed": ocr_needed,
        "image_count": len(images),
        "pages_ocr_attempted": len(page_results),
        "pages_ocr_success": sum(1 for p in page_results if p.get("ocr_status") == "success"),
        "total_visual_ocr_text_length": len(combined_text),
        "total_visual_ocr_chunks": len(chunks),
        "visual_signal_hits": detect_visual_entities(combined_text),
        "page_results": page_results,
        "combined_visual_ocr_text_path": str((out_doc_dir / f"{doc_id}.visual_ocr.txt")).replace("\\", "/"),
        "visual_ocr_json_path": str((out_doc_dir / f"{doc_id}.visual_ocr.json")).replace("\\", "/"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    out_doc_dir.mkdir(parents=True, exist_ok=True)
    (out_doc_dir / f"{doc_id}.visual_ocr.txt").write_text(combined_text, encoding="utf-8")
    write_json(out_doc_dir / f"{doc_id}.visual_ocr.json", doc_record)

    for chunk in chunks:
        chunk.update(
            {
                "file_name": file_name,
                "packet": packet,
                "document_type": document_type,
                "visual_ocr_text_path": doc_record["combined_visual_ocr_text_path"],
            }
        )

    return doc_record, chunks


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "doc_id",
        "file_name",
        "packet",
        "document_type",
        "ocr_needed",
        "image_count",
        "pages_ocr_attempted",
        "pages_ocr_success",
        "total_visual_ocr_text_length",
        "total_visual_ocr_chunks",
        "visual_ocr_json_path",
        "combined_visual_ocr_text_path",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    parser.add_argument("--force-all", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    available, tesseract_cmd = check_tesseract_available()
    if not available:
        raise RuntimeError(
            "Tesseract OCR is not available. Install it with: "
            "winget install --id UB-Mannheim.TesseractOCR -e"
        )

    out_dir = root / "artifacts" / "02_visual_text"
    out_doc_dir = out_dir / "per_document"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    stage05_paths = get_stage05_artifacts(root)

    doc_records = []
    all_chunks = []

    for stage05_path in tqdm(stage05_paths, desc="Visual OCR documents"):
        doc_record, chunks = process_document(
            root=root,
            stage05_path=stage05_path,
            out_doc_dir=out_doc_dir,
            tesseract_cmd=tesseract_cmd,
            force_all=args.force_all,
        )
        doc_records.append(doc_record)
        all_chunks.extend(chunks)

    docs_json_path = out_dir / "visual_ocr_documents.json"
    chunks_jsonl_path = out_dir / "visual_ocr_chunks.jsonl"
    summary_csv_path = out_dir / "visual_ocr_summary.csv"

    write_json(docs_json_path, doc_records)

    with chunks_jsonl_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    write_summary_csv(summary_csv_path, doc_records)

    report = {
        "run_name": "step16c_visual_ocr_parser",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "ocr_engine": OCR_ENGINE_NAME,
        "tesseract_cmd": tesseract_cmd,
        "stage05_documents_seen": len(stage05_paths),
        "documents_with_visual_ocr_attempted": sum(1 for d in doc_records if d["ocr_needed"]),
        "documents_with_visual_text": sum(1 for d in doc_records if d["total_visual_ocr_text_length"] > 0),
        "total_pages_or_images_ocr_attempted": sum(d["pages_ocr_attempted"] for d in doc_records),
        "total_pages_or_images_ocr_success": sum(d["pages_ocr_success"] for d in doc_records),
        "total_visual_ocr_chunks": len(all_chunks),
        "visual_ocr_documents_json": str(docs_json_path).replace("\\", "/"),
        "visual_ocr_chunks_jsonl": str(chunks_jsonl_path).replace("\\", "/"),
        "visual_ocr_summary_csv": str(summary_csv_path).replace("\\", "/"),
        "next_step": "Step 16D: merge visual OCR chunks with existing text chunks into unified parser memory.",
    }

    report_path = report_dir / "step16c_visual_ocr_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16C VISUAL OCR PARSER COMPLETE")
    print("-----------------------------------")
    print(f"Stage05 docs seen: {len(stage05_paths)}")
    print(f"Docs OCR attempted: {report['documents_with_visual_ocr_attempted']}")
    print(f"Docs with visual text: {report['documents_with_visual_text']}")
    print(f"Pages/images OCR attempted: {report['total_pages_or_images_ocr_attempted']}")
    print(f"Pages/images OCR success: {report['total_pages_or_images_ocr_success']}")
    print(f"Visual OCR chunks: {len(all_chunks)}")
    print("")
    print(f"Visual OCR docs:   {docs_json_path}")
    print(f"Visual OCR chunks: {chunks_jsonl_path}")
    print(f"Summary CSV:       {summary_csv_path}")
    print(f"Report JSON:       {report_path}")
    print("")


if __name__ == "__main__":
    main()