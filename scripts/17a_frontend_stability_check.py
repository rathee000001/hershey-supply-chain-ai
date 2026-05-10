from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_FRONTEND_FILES = [
    "src/lib/hershey/enrichedArtifacts.ts",
    "src/app/supply-chain/page.tsx",
    "public/data/hershey/enriched_display/enriched_frontend_manifest_v2.json",
    "public/data/hershey/enriched_display/enriched_home_summary_cards_v2.json",
    "public/data/hershey/enriched_display/enriched_interactive_graph_payload_v2.json",
    "public/data/hershey/enriched_display/enriched_supplier_cards_v2.json",
    "public/data/hershey/enriched_display/enriched_ingredient_cards_v2.json",
    "public/data/hershey/enriched_display/enriched_cost_breakdown_display_v2.json",
    "public/data/hershey/enriched_display/enriched_packet_summary_v2.json",
    "public/data/hershey/enriched_display/enriched_evidence_panel_lookup_v2.json",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_dir = root / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    missing_files = []
    present_files = []

    for rel_path in REQUIRED_FRONTEND_FILES:
        path = root / rel_path
        if path.exists():
            present_files.append(rel_path)
        else:
            missing_files.append(rel_path)

    manifest_path = root / "public" / "data" / "hershey" / "enriched_display" / "enriched_frontend_manifest_v2.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}

    primary = manifest.get("primary_artifacts", {})
    unresolved_manifest_urls = []

    for key, url in primary.items():
        local_path = root / "public" / str(url).lstrip("/")
        if not local_path.exists():
            unresolved_manifest_urls.append({"key": key, "url": url})

    graph_path = root / "public" / "data" / "hershey" / "enriched_display" / "enriched_interactive_graph_payload_v2.json"
    ingredients_path = root / "public" / "data" / "hershey" / "enriched_display" / "enriched_ingredient_cards_v2.json"
    suppliers_path = root / "public" / "data" / "hershey" / "enriched_display" / "enriched_supplier_cards_v2.json"
    evidence_path = root / "public" / "data" / "hershey" / "enriched_display" / "enriched_evidence_panel_lookup_v2.json"

    graph = read_json(graph_path) if graph_path.exists() else {"nodes": [], "edges": []}
    ingredients = read_json(ingredients_path) if ingredients_path.exists() else []
    suppliers = read_json(suppliers_path) if suppliers_path.exists() else []
    evidence = read_json(evidence_path) if evidence_path.exists() else {}

    validation_status = "pass"
    if missing_files or unresolved_manifest_urls:
        validation_status = "fail"

    report = {
        "run_name": "step17a_frontend_stability_check",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "validation_status": validation_status,
        "present_files": present_files,
        "missing_files": missing_files,
        "unresolved_manifest_urls": unresolved_manifest_urls,
        "frontend_manifest_url": "/data/hershey/enriched_display/enriched_frontend_manifest_v2.json",
        "supply_chain_route": "/supply-chain",
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_edges": len(graph.get("edges", [])),
        "ingredient_cards": len(ingredients),
        "supplier_cards": len(suppliers),
        "evidence_items": len(evidence),
        "next_step": (
            "Run npm run dev and npm run build. If both pass, Step 17B can begin cinematic supply-chain layout."
            if validation_status == "pass"
            else "Fix missing frontend files or unresolved manifest URLs before frontend build."
        ),
    }

    report_path = report_dir / "step17a_frontend_stability_check_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 17A FRONTEND STABILITY CHECK COMPLETE")
    print("------------------------------------------")
    print(f"Validation status: {validation_status}")
    print(f"Missing files:     {len(missing_files)}")
    print(f"Unresolved URLs:   {len(unresolved_manifest_urls)}")
    print(f"Graph nodes:       {report['graph_nodes']}")
    print(f"Graph edges:       {report['graph_edges']}")
    print(f"Ingredient cards:  {report['ingredient_cards']}")
    print(f"Supplier cards:    {report['supplier_cards']}")
    print(f"Evidence items:    {report['evidence_items']}")
    print("")
    print(f"Report JSON:       {report_path}")
    print("")


if __name__ == "__main__":
    main()