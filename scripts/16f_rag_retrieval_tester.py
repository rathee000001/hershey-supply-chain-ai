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
    "what", "which", "where", "does", "show", "find", "evidence", "support", "supports",
}


TEST_QUESTIONS = [
    {
        "test_id": "RAG_ASR_SUGAR",
        "question": "What evidence supports ASR or American Sugar Refining as Hershey sugar supplier or sugar sourcing partner?",
        "expected_packets": ["sugar", "hershey_company"],
        "expected_terms": ["asr", "american_sugar_refining", "hershey", "sugar", "sourcing"],
        "purpose": "Validate sugar supplier retrieval."
    },
    {
        "test_id": "RAG_BARRY_COCOA",
        "question": "What evidence supports Barry Callebaut and Hershey chocolate or cocoa supply relationship?",
        "expected_packets": ["cocoa_chocolate_cocoa_butter"],
        "expected_terms": ["barry_callebaut", "hershey", "chocolate", "cocoa"],
        "purpose": "Validate cocoa/chocolate supplier retrieval."
    },
    {
        "test_id": "RAG_LAND_O_LAKES_DAIRY",
        "question": "What evidence supports Land O'Lakes as Hershey dairy supplier or strategic dairy partner?",
        "expected_packets": ["dairy_milk_skim_milk_milk_fat", "hershey_company"],
        "expected_terms": ["land_olakes", "hershey", "milk", "dairy"],
        "purpose": "Validate dairy supplier retrieval."
    },
    {
        "test_id": "RAG_WRAPPER_INGREDIENTS",
        "question": "What does the Hershey 1.55 oz wrapper or product page say about ingredients and nutrition?",
        "expected_packets": ["product_sku_1_55oz", "retail_price_evidence"],
        "expected_terms": ["hershey", "1_55_oz", "ingredients", "nutrition_facts", "milk_chocolate"],
        "purpose": "Validate SKU wrapper/product evidence retrieval."
    },
    {
        "test_id": "RAG_RETAIL_PRICE",
        "question": "Which retailer evidence supports verified price for the Hershey 1.55 oz milk chocolate bar?",
        "expected_packets": ["retail_price_evidence"],
        "expected_terms": ["walmart", "target", "cvs", "walgreens", "retail_price", "1_55_oz"],
        "purpose": "Validate retail price evidence retrieval."
    },
    {
        "test_id": "RAG_PGPR",
        "question": "What evidence explains PGPR function and use in chocolate?",
        "expected_packets": ["pgpr"],
        "expected_terms": ["pgpr", "chocolate", "ingredients"],
        "purpose": "Validate PGPR ingredient retrieval."
    },
    {
        "test_id": "RAG_SOY_LECITHIN",
        "question": "What evidence explains soy lecithin function and use in chocolate?",
        "expected_packets": ["soy_lecithin"],
        "expected_terms": ["soy_lecithin", "lecithin", "chocolate", "ingredients"],
        "purpose": "Validate soy lecithin retrieval."
    },
    {
        "test_id": "RAG_NATURAL_FLAVOR",
        "question": "What evidence explains natural flavor definition and use in food or chocolate?",
        "expected_packets": ["natural_flavor"],
        "expected_terms": ["natural_flavor", "fda", "ingredients"],
        "purpose": "Validate natural flavor retrieval."
    },
    {
        "test_id": "RAG_PACKAGING",
        "question": "What evidence supports Hershey packaging, wrapper, pulp, paper, or packaging cost benchmark?",
        "expected_packets": ["packaging_wrapper", "hershey_company"],
        "expected_terms": ["hershey", "packaging", "wrapper", "pulp", "paper"],
        "purpose": "Validate packaging evidence retrieval."
    },
    {
        "test_id": "RAG_MCLANE_LOGISTICS",
        "question": "What evidence supports McLane, distribution, warehouse, or downstream logistics for the Hershey supply chain model?",
        "expected_packets": ["logistics_distribution", "hershey_company"],
        "expected_terms": ["mclane", "distribution", "warehouse", "logistics"],
        "purpose": "Validate logistics/distribution retrieval."
    },
    {
        "test_id": "RAG_HERSHEY_10K_RAW_MATERIALS",
        "question": "What Hershey 10-K evidence mentions raw materials, cocoa, sugar, dairy, packaging, or distribution risk?",
        "expected_packets": ["hershey_company"],
        "expected_terms": ["hershey", "cocoa", "sugar", "milk", "packaging", "distribution"],
        "purpose": "Validate Hershey company filing retrieval."
    },
    {
        "test_id": "RAG_COST_BENCHMARKS",
        "question": "Which sources support benchmark cost logic for sugar, cocoa, dairy, packaging, diesel, trucking, warehousing, or retail?",
        "expected_packets": [
            "sugar",
            "cocoa_chocolate_cocoa_butter",
            "dairy_milk_skim_milk_milk_fat",
            "packaging_wrapper",
            "logistics_distribution",
            "retail_price_evidence"
        ],
        "expected_terms": ["cost", "price", "market", "sugar", "cocoa", "milk", "packaging", "diesel", "retail"],
        "purpose": "Validate cost benchmark retrieval."
    }
]


PHRASE_MAP = {
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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def tokenize(text: str) -> list[str]:
    text = str(text or "").lower()
    text = text.replace("o'lakes", "olakes")
    text = text.replace("o’lakes", "olakes")
    text = text.replace("1.55-ounce", "1.55 oz")
    text = text.replace("43 g", "43g")

    tokens = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text)

    cleaned = []
    for token in tokens:
        if len(token) < 3 and token not in {"oz"}:
            continue
        if token in STOPWORDS:
            continue
        cleaned.append(token)

    for phrase, phrase_token in PHRASE_MAP.items():
        if phrase in text:
            cleaned.append(phrase_token)

    return cleaned


def query_vector(query: str) -> dict[str, float]:
    tokens = tokenize(query)
    counts = Counter(tokens)
    if not counts:
        return {}

    raw = {}
    for term, count in counts.items():
        raw[term] = 1.0 + math.log(count)

    norm = math.sqrt(sum(v * v for v in raw.values())) or 1.0
    return {term: weight / norm for term, weight in raw.items()}


def load_vector_chunks(path: Path) -> dict[str, dict[str, Any]]:
    rows = read_jsonl(path)
    return {row["vector_chunk_id"]: row for row in rows if row.get("vector_chunk_id")}


def score_query(
    question: str,
    inverted_index: dict[str, list[dict[str, Any]]],
    vector_chunks: dict[str, dict[str, Any]],
    top_k: int = 10,
) -> list[dict[str, Any]]:
    qv = query_vector(question)
    scores = defaultdict(float)
    matched_terms = defaultdict(list)

    for term, q_weight in qv.items():
        postings = inverted_index.get(term, [])
        for posting in postings:
            chunk_id = posting.get("vector_chunk_id")
            if not chunk_id:
                continue

            scores[chunk_id] += float(posting.get("weight", 0)) * q_weight
            matched_terms[chunk_id].append(term)

    results = []

    for chunk_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]:
        chunk = vector_chunks.get(chunk_id)
        if not chunk:
            continue

        results.append(
            {
                "rank": len(results) + 1,
                "score": round(float(score), 8),
                "matched_terms": sorted(set(matched_terms[chunk_id])),
                "vector_chunk_id": chunk_id,
                "doc_id": chunk.get("doc_id", ""),
                "file_name": chunk.get("file_name", ""),
                "packet": chunk.get("packet", ""),
                "source_type": chunk.get("source_type", ""),
                "usefulness_class": chunk.get("usefulness_class", ""),
                "signals": chunk.get("signals", {}),
                "text_preview": chunk.get("text_preview", ""),
                "text": chunk.get("text", ""),
            }
        )

    return results


def evaluate_test_case(test: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    top_packets = [r.get("packet", "") for r in results[:5]]
    top_files = [r.get("file_name", "") for r in results[:5]]
    top_terms_seen = sorted(set(term for r in results[:5] for term in r.get("matched_terms", [])))

    expected_packets = set(test.get("expected_packets", []))
    expected_terms = set(test.get("expected_terms", []))

    packet_hit_count = sum(1 for packet in top_packets if packet in expected_packets)
    term_hit_count = sum(1 for term in top_terms_seen if term in expected_terms)

    has_any_result = len(results) > 0
    top_score = results[0]["score"] if results else 0

    if not has_any_result:
        status = "fail_no_results"
    elif packet_hit_count >= 1 and term_hit_count >= 1 and top_score > 0:
        status = "pass"
    elif packet_hit_count >= 1:
        status = "pass_packet_only"
    elif term_hit_count >= 2:
        status = "warning_terms_only"
    else:
        status = "fail_weak_retrieval"

    return {
        "test_id": test["test_id"],
        "question": test["question"],
        "status": status,
        "top_score": top_score,
        "packet_hit_count_top5": packet_hit_count,
        "term_hit_count_top5": term_hit_count,
        "top_packets": top_packets,
        "top_files": top_files,
        "top_matched_terms": top_terms_seen,
    }


def compact_result_for_display(result: dict[str, Any]) -> dict[str, Any]:
    text = str(result.get("text", ""))
    return {
        "rank": result.get("rank"),
        "score": result.get("score"),
        "vector_chunk_id": result.get("vector_chunk_id"),
        "doc_id": result.get("doc_id"),
        "file_name": result.get("file_name"),
        "packet": result.get("packet"),
        "source_type": result.get("source_type"),
        "usefulness_class": result.get("usefulness_class"),
        "matched_terms": result.get("matched_terms", []),
        "text_preview": text[:1200],
    }


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "test_id",
        "status",
        "top_score",
        "packet_hit_count_top5",
        "term_hit_count_top5",
        "top_packets",
        "top_files",
        "top_matched_terms",
        "question",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "test_id": row.get("test_id", ""),
                    "status": row.get("status", ""),
                    "top_score": row.get("top_score", ""),
                    "packet_hit_count_top5": row.get("packet_hit_count_top5", ""),
                    "term_hit_count_top5": row.get("term_hit_count_top5", ""),
                    "top_packets": "; ".join(row.get("top_packets", [])),
                    "top_files": "; ".join(row.get("top_files", [])),
                    "top_matched_terms": "; ".join(row.get("top_matched_terms", [])),
                    "question": row.get("question", ""),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    root = Path(args.root).resolve()

    index_dir = root / "artifacts" / "12_vector_rag_index"
    out_dir = root / "artifacts" / "13_rag_tests"
    report_dir = root / "artifacts" / "10_run_reports"

    vector_chunks_path = index_dir / "vector_chunks.jsonl"
    inverted_index_path = index_dir / "inverted_index.json"

    if not vector_chunks_path.exists():
        raise FileNotFoundError(f"Missing vector chunks: {vector_chunks_path}")
    if not inverted_index_path.exists():
        raise FileNotFoundError(f"Missing inverted index: {inverted_index_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    vector_chunks = load_vector_chunks(vector_chunks_path)
    inverted_index = read_json(inverted_index_path)

    test_results = []
    summary_rows = []

    for test in TEST_QUESTIONS:
        retrieved = score_query(
            question=test["question"],
            inverted_index=inverted_index,
            vector_chunks=vector_chunks,
            top_k=args.top_k,
        )

        evaluation = evaluate_test_case(test, retrieved)
        summary_rows.append(evaluation)

        test_results.append(
            {
                **test,
                "evaluation": evaluation,
                "retrieved_chunks": [compact_result_for_display(r) for r in retrieved],
                "safe_usage_rule": (
                    "Retrieved chunks are research support only. Claims must still pass strict audit before frontend display."
                ),
            }
        )

    status_counts = Counter(row["status"] for row in summary_rows)
    passed = sum(count for status, count in status_counts.items() if status.startswith("pass"))
    warnings = sum(count for status, count in status_counts.items() if status.startswith("warning"))
    failures = sum(count for status, count in status_counts.items() if status.startswith("fail"))

    if failures == 0 and warnings == 0:
        overall_status = "pass"
    elif failures == 0:
        overall_status = "pass_with_warnings"
    else:
        overall_status = "needs_tuning"

    questions_path = out_dir / "rag_test_questions.json"
    results_path = out_dir / "rag_test_results.json"
    summary_csv = out_dir / "rag_test_summary.csv"

    write_json(questions_path, TEST_QUESTIONS)
    write_json(results_path, test_results)
    write_summary_csv(summary_csv, summary_rows)

    report = {
        "run_name": "step16f_rag_retrieval_tester",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "index_type": "local_sparse_tfidf_rag_v1",
        "vector_chunks_loaded": len(vector_chunks),
        "inverted_index_terms_loaded": len(inverted_index),
        "tests_run": len(TEST_QUESTIONS),
        "overall_status": overall_status,
        "passed_tests": passed,
        "warning_tests": warnings,
        "failed_tests": failures,
        "status_counts": dict(sorted(status_counts.items())),
        "rag_test_questions_json": str(questions_path).replace("\\", "/"),
        "rag_test_results_json": str(results_path).replace("\\", "/"),
        "rag_test_summary_csv": str(summary_csv).replace("\\", "/"),
        "next_step": (
            "Step 16G: enrich Level 1 parser inputs from RAG retrieval results and unified memory."
            if overall_status in ["pass", "pass_with_warnings"]
            else "Tune vector index/retrieval rules before enriched parsing."
        ),
    }

    report_path = report_dir / "step16f_rag_retrieval_test_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 16F RAG RETRIEVAL TESTER COMPLETE")
    print("--------------------------------------")
    print(f"Vector chunks loaded: {len(vector_chunks)}")
    print(f"Inverted terms loaded: {len(inverted_index)}")
    print(f"Tests run:            {len(TEST_QUESTIONS)}")
    print(f"Overall status:       {overall_status}")
    print(f"Passed tests:         {passed}")
    print(f"Warning tests:        {warnings}")
    print(f"Failed tests:         {failures}")
    print("")
    print(f"Results JSON: {results_path}")
    print(f"Summary CSV:  {summary_csv}")
    print(f"Report JSON:  {report_path}")
    print("")


if __name__ == "__main__":
    main()