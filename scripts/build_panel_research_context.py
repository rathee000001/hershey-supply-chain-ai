"""Build attributed panel context using the existing local RAG, not a new model.

Raw retrieved text never enters the public export. Retrieval is a discovery aid;
graph assignments, packet membership and document-level matches remain distinct.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("existing_rag", ROOT / "scripts/16f_rag_retrieval_tester.py")
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)

paths = {
    "index": "artifacts/12_vector_rag_index/inverted_index.json",
    "chunks": "artifacts/12_vector_rag_index/vector_chunks.jsonl",
    "graph": "public/data/hershey/enriched_display/enriched_interactive_graph_payload_v2.json",
    "evidence": "public/data/hershey/enriched_display/enriched_evidence_panel_lookup_v2.json",
}
graph = rag.read_json(ROOT / paths["graph"])
evidence = rag.read_json(ROOT / paths["evidence"])
approved = {key: value for key, value in evidence.items() if value.get("public_display_allowed") is True}
index = rag.read_json(ROOT / paths["index"])
chunks = rag.load_vector_chunks(ROOT / paths["chunks"])
nodes = {node["id"]: node for node in graph["nodes"]}
contexts = {}
for node_id, node in nodes.items():
    incoming = [edge for edge in graph["edges"] if edge["target"] == node_id]
    outgoing = [edge for edge in graph["edges"] if edge["source"] == node_id]
    query = " ".join(filter(None, [node.get("label"), node.get("material"), node.get("companyName"), node.get("description")]))
    matches = rag.score_query(query, index, chunks, top_k=20)
    packets = set(node.get("enrichedEvidencePackets", []))
    assigned = [entry["evidence_id"] for entry in node.get("enrichedEvidencePreview", []) if entry.get("evidence_id") in approved]
    packet_ids = [key for key, value in approved.items() if value.get("packet") in packets]
    ranked_files = list(dict.fromkeys(match["file_name"] for match in matches))
    discovered = [key for name in ranked_files for key, value in approved.items() if value.get("file_name") == name and (not packets or value.get("packet") in packets)]
    # This ordering does not claim that every retrieved document proves the node.
    ordered = list(dict.fromkeys(assigned + [key for key in discovered if key in packet_ids] + packet_ids))
    contexts[node_id] = {
        "query": query,
        "incoming_edge_ids": [edge["id"] for edge in incoming],
        "outgoing_edge_ids": [edge["id"] for edge in outgoing],
        "graph_assigned_evidence_ids": list(dict.fromkeys(assigned)),
        "packet_evidence_ids": packet_ids,
        "ordered_evidence_ids": ordered,
        "retrieved_document_context_ids": list(dict.fromkeys(discovered)),
        "retrieved_public_documents": [name for name in ranked_files if any(value.get("file_name") == name for value in approved.values())],
        "retrieved_chunk_count": len(matches),
        "scope": "Graph-assigned and same-packet evidence are distinguished from additional retrieved document context. Retrieval is not proof of supplier allocation, exact routes or internal cost.",
    }

output = {
    "version": "panel_research_context_v1",
    "retrieval_engine": "existing_16f_sparse_tfidf_score_query",
    "source_sha256": {key: hashlib.sha256((ROOT / value).read_bytes()).hexdigest() for key, value in paths.items()},
    "node_contexts": contexts,
    "coverage": {
        "graph_nodes": len(nodes), "graph_edges": len(graph["edges"]),
        "nodes_with_graph_assigned_evidence": sum(bool(value["graph_assigned_evidence_ids"]) for value in contexts.values()),
        "nodes_with_packet_evidence": sum(bool(value["packet_evidence_ids"]) for value in contexts.values()),
        "nodes_with_retrieved_approved_document_context": sum(bool(value["retrieved_document_context_ids"]) for value in contexts.values()),
        "nodes_without_direct_evidence": [key for key, value in contexts.items() if not value["graph_assigned_evidence_ids"]],
        "boundary": "This measures context mapping only, not rendered panel completeness or factual verification of the physical supply chain.",
    },
}
for value in contexts.values():
    for field in ["graph_assigned_evidence_ids", "packet_evidence_ids", "ordered_evidence_ids", "retrieved_document_context_ids"]:
        assert all(key in approved for key in value[field])
destination = ROOT / "public/data/hershey/enriched_display/panel_research_context_v1.json"
destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(output["coverage"], indent=2))
