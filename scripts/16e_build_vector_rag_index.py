from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "are", "was", "were", "have", "has",
    "had", "not", "but", "you", "your", "our", "their", "they", "them", "its", "into", "will",
    "can", "may", "more", "than", "about", "also", "all", "any", "each", "other", "such",
    "use", "used", "using", "www", "com", "pdf", "page", "home", "contact", "privacy",
    "policy", "copyright", "reserved", "rights", "terms", "conditions", "report", "section",
    "source", "sources", "information", "data", "table", "figure", "image", "download",
}


IMPORTANT_TERMS = {
    "hershey", "asr", "sugar", "cocoa", "chocolate", "barry", "callebaut", "milk",
    "land", "lakes", "mclane", "walmart", "target", "cvs", "walgreens", "lecithin",
    "pgpr", "flavor", "packaging", "wrapper", "supplier", "sourcing", "cost", "price",
    "retail", "distribution", "warehouse", "ingredient", "ingredients", "1.55", "43g",
    "nutrition", "upc",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        raise FileNotFoundError(f"Missing input JSONL: {path}")

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row["_source_line"] = line_no
            rows.append(row)
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


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


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = text.replace("o'lakes", "olakes")
    text = text.replace("o’lakes", "olakes")
    text = text.replace("1.55-ounce", "1.55 oz")
    text = text.replace("1.55-ounce", "1.55oz")
    text = text.replace("43 g", "43g")

    raw_tokens = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text)

    tokens = []
    for tok in raw_tokens:
        if len(tok) < 3 and tok not in {"oz"}:
            continue
        if tok in STOPWORDS:
            continue
        tokens.append(tok)

    # Add important phrase tokens for better retrieval.
    phrase_map = {
        "barry callebaut": "barry_callebaut",
        "land o'lakes": "land_olakes",
        "land o’lakes": "land_olakes",
        "asr group": "asr_group",
        "american sugar refining": "american_sugar_refining",
        "soy lecithin": "soy_lecithin",
        "cocoa butter": "cocoa_butter",
        "skim milk": "skim_milk",
        "milk fat": "milk_fat",
        "natural flavor": "natural_flavor",
        "milk chocolate": "milk_chocolate",
        "nutrition facts": "nutrition_facts",
        "retail price": "retail_price",
        "distribution center": "distribution_center",
        "supply chain": "supply_chain",
        "responsible sourcing": "responsible_sourcing",
        "1.55 oz": "1_55_oz",
    }

    lower = text.lower()
    for phrase, token in phrase_map.items():
        if phrase in lower:
            tokens.append(token)

    return tokens


def usefulness_weight(usefulness_class: str) -> float:
    weights = {
        "high_sku_evidence": 1.45,
        "high_supplier_or_ingredient_evidence": 1.35,
        "high_cost_or_price_evidence": 1.35,
        "medium_context_evidence": 1.15,
        "low_background": 0.85,
        "low_short_text": 0.70,
    }
    return weights.get(usefulness_class, 1.0)


def source_weight(source_type: str) -> float:
    if source_type == "visual_ocr":
        return 1.08
    return 1.0


def build_vectors(chunks: list[dict[str, Any]], max_terms_per_chunk: int = 350) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, list[dict[str, Any]]]]:
    tokenized_rows = []
    document_frequency = Counter()

    for chunk in chunks:
        text = clean_text(chunk.get("text", ""))
        tokens = tokenize(text)
        tf = Counter(tokens)

        for term in tf.keys():
            document_frequency[term] += 1

        tokenized_rows.append((chunk, tf))

    n_docs = len(tokenized_rows)
    idf = {
        term: math.log((1 + n_docs) / (1 + df)) + 1.0
        for term, df in document_frequency.items()
    }

    vector_rows = []
    inverted_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    global_term_weight = Counter()

    for chunk, tf in tokenized_rows:
        text = clean_text(chunk.get("text", ""))
        if not text:
            continue

        base_weight = usefulness_weight(str(chunk.get("usefulness_class", ""))) * source_weight(str(chunk.get("source_type", "")))

        raw_vector = {}
        for term, count in tf.items():
            tf_weight = 1.0 + math.log(count)
            boost = 1.25 if term in IMPORTANT_TERMS else 1.0
            weight = tf_weight * idf.get(term, 1.0) * boost * base_weight
            raw_vector[term] = weight

        norm = math.sqrt(sum(v * v for v in raw_vector.values())) or 1.0

        normalized_terms = {
            term: round(weight / norm, 8)
            for term, weight in raw_vector.items()
        }

        # Store top weighted terms to keep Git artifact compact.
        top_terms = sorted(normalized_terms.items(), key=lambda x: x[1], reverse=True)[:max_terms_per_chunk]
        vector_terms = dict(top_terms)

        chunk_id = chunk.get("unified_chunk_id", "")
        vector_row = {
            "vector_chunk_id": chunk_id,
            "doc_id": chunk.get("doc_id", ""),
            "file_name": chunk.get("file_name", ""),
            "packet": chunk.get("packet", ""),
            "source_type": chunk.get("source_type", ""),
            "document_type": chunk.get("document_type", ""),
            "usefulness_class": chunk.get("usefulness_class", ""),
            "text_length": chunk.get("text_length", len(text)),
            "word_count": chunk.get("word_count", len(text.split())),
            "signals": chunk.get("signals", {}),
            "top_terms": vector_terms,
            "text_preview": text[:900],
            "text": text,
        }

        vector_rows.append(vector_row)

        for term, weight in vector_terms.items():
            inverted_index[term].append(
                {
                    "vector_chunk_id": chunk_id,
                    "doc_id": chunk.get("doc_id", ""),
                    "file_name": chunk.get("file_name", ""),
                    "packet": chunk.get("packet", ""),
                    "weight": weight,
                }
            )
            global_term_weight[term] += weight

    # Keep top postings per term.
    compact_inverted = {}
    for term, postings in inverted_index.items():
        compact_inverted[term] = sorted(postings, key=lambda x: x["weight"], reverse=True)[:80]

    term_stats = {
        "document_count": n_docs,
        "unique_terms": len(document_frequency),
        "top_terms_by_document_frequency": document_frequency.most_common(200),
        "top_terms_by_vector_weight": global_term_weight.most_common(200),
    }

    return vector_rows, term_stats, compact_inverted


def write_terms_summary(path: Path, term_stats: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    df_terms = dict(term_stats.get("top_terms_by_document_frequency", []))
    weight_terms = dict(term_stats.get("top_terms_by_vector_weight", []))
    all_terms = sorted(set(df_terms.keys()) | set(weight_terms.keys()))

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["term", "document_frequency_ranked_count", "global_vector_weight"],
            lineterminator="\n",
        )
        writer.writeheader()

        for term in all_terms:
            writer.writerow(
                {
                    "term": term,
                    "document_frequency_ranked_count": df_terms.get(term, ""),
                    "global_vector_weight": round(float(weight_terms.get(term, 0)), 6),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    input_path = root / "artifacts" / "11_unified_memory" / "unified_chunks.jsonl"
    out_dir = root / "artifacts" / "12_vector_rag_index"
    report_dir = root / "artifacts" / "10_run_reports"

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    chunks = read_jsonl(input_path)

    vector_rows, term_stats, inverted_index = build_vectors(chunks)

    vector_chunks_path = out_dir / "vector_chunks.jsonl"
    inverted_index_path = out_dir / "inverted_index.json"
    manifest_path = out_dir / "vector_index_manifest.json"
    terms_csv_path = out_dir / "vector_terms_summary.csv"
    retrieval_config_path = out_dir / "retrieval_config.json"

    write_jsonl(vector_chunks_path, vector_rows)
    write_json(inverted_index_path, inverted_index)
    write_terms_summary(terms_csv_path, term_stats)

    source_counts = Counter(row.get("source_type", "unknown") for row in vector_rows)
    packet_counts = Counter(row.get("packet", "unknown") for row in vector_rows)
    usefulness_counts = Counter(row.get("usefulness_class", "unknown") for row in vector_rows)

    retrieval_config = {
        "index_type": "local_sparse_tfidf_rag_v1",
        "query_mode": "tokenized_sparse_cosine",
        "top_k_default": 8,
        "top_k_max": 20,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "rule": "Use retrieved chunks for research and artifact building. Frontend must display only audited public JSON.",
    }

    write_json(retrieval_config_path, retrieval_config)

    manifest = {
        "index_name": "hershey_supply_chain_local_rag_index",
        "index_type": "local_sparse_tfidf_rag_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "input_unified_chunks": str(input_path).replace("\\", "/"),
        "outputs": {
            "vector_chunks_jsonl": str(vector_chunks_path).replace("\\", "/"),
            "inverted_index_json": str(inverted_index_path).replace("\\", "/"),
            "vector_terms_summary_csv": str(terms_csv_path).replace("\\", "/"),
            "retrieval_config_json": str(retrieval_config_path).replace("\\", "/"),
        },
        "chunk_count": len(vector_rows),
        "document_count": len(set(row.get("doc_id", "") for row in vector_rows)),
        "unique_terms": term_stats["unique_terms"],
        "source_type_counts": dict(sorted(source_counts.items())),
        "packet_counts": dict(sorted(packet_counts.items())),
        "usefulness_counts": dict(sorted(usefulness_counts.items())),
        "next_step": "Step 16F: build retrieval tester to query this local RAG index.",
    }

    write_json(manifest_path, manifest)

    report = {
        "run_name": "step16e_vector_rag_index",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "index_type": "local_sparse_tfidf_rag_v1",
        "input_chunks_seen": len(chunks),
        "vector_chunks_created": len(vector_rows),
        "documents_indexed": manifest["document_count"],
        "unique_terms": term_stats["unique_terms"],
        "source_type_counts": dict(sorted(source_counts.items())),
        "packet_counts": dict(sorted(packet_counts.items())),
        "usefulness_counts": dict(sorted(usefulness_counts.items())),
        "vector_chunks_jsonl": str(vector_chunks_path).replace("\\", "/"),
        "inverted_index_json": str(inverted_index_path).replace("\\", "/"),
        "vector_terms_summary_csv": str(terms_csv_path).replace("\\", "/"),
        "manifest_json": str(manifest_path).replace("\\", "/"),
        "retrieval_config_json": str(retrieval_config_path).replace("\\", "/"),
        "next_step": "Step 16F: run RAG retrieval tests for supplier, ingredient, SKU, price, and cost evidence questions.",
    }

    report_path = report_dir / "step16e_vector_rag_index_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16E VECTOR / RAG INDEX COMPLETE")
    print("------------------------------------")
    print(f"Input chunks seen:      {len(chunks)}")
    print(f"Vector chunks created:  {len(vector_rows)}")
    print(f"Documents indexed:      {manifest['document_count']}")
    print(f"Unique terms:           {term_stats['unique_terms']}")
    print("")
    print(f"Vector chunks: {vector_chunks_path}")
    print(f"Inverted index:{inverted_index_path}")
    print(f"Manifest:      {manifest_path}")
    print(f"Report JSON:   {report_path}")
    print("")


if __name__ == "__main__":
    main()