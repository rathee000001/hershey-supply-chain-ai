from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


SUPPLIER_TARGETS = {
    "sugar": {
        "supplier_packet_id": "SUP_ASR_SUGAR",
        "company_name": "American Sugar Refining / ASR",
        "related_ingredient_or_stage": "Sugar",
        "safe_display_name": "ASR / American Sugar Refining",
        "logo_keywords": ["asr", "ASR_Group_logo"],
        "safe_website_wording": (
            "ASR is supported as a Hershey company-level sugar sourcing partner. "
            "Exact 1.55 oz SKU sugar allocation is not publicly confirmed."
        ),
        "limits": [
            "Company-level relationship only.",
            "Exact supplier allocation for the HERSHEY'S 1.55 oz bar is not publicly confirmed.",
            "Do not state that ASR supplies the exact sugar in every bar."
        ],
    },
    "cocoa_chocolate_cocoa_butter": {
        "supplier_packet_id": "SUP_BARRY_CALLEBAUT_COCOA_CHOCOLATE",
        "company_name": "Barry Callebaut",
        "related_ingredient_or_stage": "Cocoa / Chocolate / Cocoa Butter",
        "safe_display_name": "Barry Callebaut",
        "logo_keywords": ["barry", "callebaut"],
        "safe_website_wording": (
            "Barry Callebaut is supported as a Hershey company-level cocoa/chocolate supply partner. "
            "Exact 1.55 oz SKU cocoa or cocoa butter allocation is not publicly confirmed."
        ),
        "limits": [
            "Company-level relationship only.",
            "Exact cocoa, chocolate, or cocoa butter allocation for the 1.55 oz SKU is not publicly confirmed.",
            "Do not state that Barry Callebaut supplies the exact cocoa or cocoa butter in every bar."
        ],
    },
    "dairy_milk_skim_milk_milk_fat": {
        "supplier_packet_id": "SUP_LAND_O_LAKES_DAIRY",
        "company_name": "Land O'Lakes",
        "related_ingredient_or_stage": "Milk / Skim Milk / Milk Fat",
        "safe_display_name": "Land O'Lakes",
        "logo_keywords": ["land_o_lakes", "land"],
        "safe_website_wording": (
            "Land O'Lakes is supported as a Hershey company-level dairy partner/supplier. "
            "Exact 1.55 oz SKU dairy allocation is not publicly confirmed."
        ),
        "limits": [
            "Company-level relationship only.",
            "Exact milk, skim milk, or milk fat allocation for the 1.55 oz SKU is not publicly confirmed.",
            "Do not state that Land O'Lakes supplies the exact dairy ingredients in every bar."
        ],
    },
    "logistics_distribution": {
        "supplier_packet_id": "SUP_MCLANE_DISTRIBUTION",
        "company_name": "McLane",
        "related_ingredient_or_stage": "Distribution / Downstream Channel",
        "safe_display_name": "McLane",
        "logo_keywords": ["mclane"],
        "safe_website_wording": (
            "McLane/Hershey evidence supports company-level downstream or distribution context. "
            "Exact route for the 1.55 oz bar is not publicly confirmed."
        ),
        "limits": [
            "Company-level downstream/distribution context only.",
            "Exact route for this 1.55 oz SKU is not publicly confirmed.",
            "Do not state that McLane distributes every 1.55 oz Hershey bar to every retailer."
        ],
    },
}


INGREDIENT_TARGETS = [
    {
        "ingredient_id": "ING_SUGAR",
        "ingredient_name": "Sugar",
        "packet": "sugar",
        "label_order_position": 1,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["American Sugar Refining / ASR"],
        "origin_logic": (
            "Sugar is modeled as an upstream sweetener input. Hershey sugar sourcing evidence and ASR evidence "
            "support company-level sugar sourcing context, while exact SKU-level allocation remains unconfirmed."
        ),
        "processing_logic": "Farm cane/beet sugar stream → milling/refining → refined sugar input → Hershey manufacturing.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_COCOA_CHOCOLATE",
        "ingredient_name": "Chocolate / Cocoa",
        "packet": "cocoa_chocolate_cocoa_butter",
        "label_order_position": 2,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["Barry Callebaut"],
        "origin_logic": (
            "Cocoa/chocolate is modeled as a major upstream cocoa stream. Barry Callebaut evidence supports "
            "company-level cocoa/chocolate relationship context, while exact SKU-level allocation remains unconfirmed."
        ),
        "processing_logic": "Cocoa origin/processing → cocoa liquor/chocolate inputs → Hershey manufacturing.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_COCOA_BUTTER",
        "ingredient_name": "Cocoa Butter",
        "packet": "cocoa_chocolate_cocoa_butter",
        "label_order_position": 3,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["Barry Callebaut"],
        "origin_logic": (
            "Cocoa butter is modeled as part of the cocoa ingredient stream. Public evidence supports company-level "
            "cocoa/chocolate context, not exact SKU-level cocoa butter supplier allocation."
        ),
        "processing_logic": "Cocoa bean processing → cocoa liquor pressing/separation → cocoa butter input → chocolate manufacturing.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_MILK",
        "ingredient_name": "Milk",
        "packet": "dairy_milk_skim_milk_milk_fat",
        "label_order_position": 4,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["Land O'Lakes"],
        "origin_logic": (
            "Milk is modeled as a dairy input. Hershey/Land O'Lakes evidence supports company-level dairy relationship "
            "context, while exact SKU-level dairy allocation remains unconfirmed."
        ),
        "processing_logic": "Dairy farms → cooperative/processor → milk stream → Hershey manufacturing.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_SKIM_MILK",
        "ingredient_name": "Skim Milk",
        "packet": "dairy_milk_skim_milk_milk_fat",
        "label_order_position": 5,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["Land O'Lakes"],
        "origin_logic": (
            "Skim milk is modeled as part of the dairy solids stream. Supplier is treated as company-level dairy context, "
            "not SKU-level confirmation."
        ),
        "processing_logic": "Milk separation → skim/nonfat solids stream → chocolate ingredient input.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_MILK_FAT",
        "ingredient_name": "Milk Fat",
        "packet": "dairy_milk_skim_milk_milk_fat",
        "label_order_position": 6,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "company_level_confirmed",
        "confirmed_supplier_names": ["Land O'Lakes"],
        "origin_logic": (
            "Milk fat is modeled as part of the dairy fat stream. Supplier evidence supports company-level dairy context, "
            "not exact SKU-level allocation."
        ),
        "processing_logic": "Milk separation → cream/butterfat stream → milk fat input → chocolate manufacturing.",
        "confidence_level": "medium",
    },
    {
        "ingredient_id": "ING_SOY_LECITHIN",
        "ingredient_name": "Soy Lecithin",
        "packet": "soy_lecithin",
        "label_order_position": 7,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "unknown",
        "confirmed_supplier_names": [],
        "origin_logic": "Soy lecithin is modeled as an emulsifier input. Supplier is not publicly confirmed for the 1.55 oz bar.",
        "processing_logic": "Soybean oil processing byproduct/refining → lecithin emulsifier input.",
        "confidence_level": "low",
    },
    {
        "ingredient_id": "ING_PGPR",
        "ingredient_name": "PGPR",
        "packet": "pgpr",
        "label_order_position": 8,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "unknown",
        "confirmed_supplier_names": [],
        "origin_logic": "PGPR is modeled as an emulsifier/flow-modifier input. Supplier is not publicly confirmed for the 1.55 oz bar.",
        "processing_logic": "Castor oil / ricinoleic acid related stream → PGPR specialty ingredient → chocolate processing aid.",
        "confidence_level": "low",
    },
    {
        "ingredient_id": "ING_NATURAL_FLAVOR",
        "ingredient_name": "Natural Flavor",
        "packet": "natural_flavor",
        "label_order_position": 9,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "unknown",
        "confirmed_supplier_names": [],
        "origin_logic": "Natural flavor is modeled as a flavor input. Exact composition and supplier are not publicly confirmed.",
        "processing_logic": "Flavor source/extraction/fermentation/distillation context → natural flavor input.",
        "confidence_level": "low",
    },
    {
        "ingredient_id": "ING_PACKAGING_WRAPPER",
        "ingredient_name": "Packaging / Wrapper",
        "packet": "packaging_wrapper",
        "label_order_position": 10,
        "label_status": "confirmed_by_label",
        "supplier_status_default": "unknown",
        "confirmed_supplier_names": [],
        "origin_logic": (
            "Packaging is modeled as a material input stream. Hershey packaging/pulp-paper evidence supports sourcing policy "
            "context, but exact wrapper supplier for the 1.55 oz bar is not publicly confirmed."
        ),
        "processing_logic": "Pulp/paper/flexible packaging stream → wrapper/carton/case packaging → Hershey wrapping/distribution.",
        "confidence_level": "medium",
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: Any) -> str:
    return str(value or "").strip()


def evidence_ids_for_supplier(rows: list[dict[str, Any]], packet: str, company_name: str) -> list[str]:
    ids = []

    for row in rows:
        if row.get("packet") != packet:
            continue

        if not row.get("supports_supplier_packet"):
            continue

        company = clean(row.get("corrected_related_company"))
        if company.lower() != company_name.lower():
            continue

        ids.append(row["evidence_id"])

    return sorted(set(ids))


def evidence_ids_for_ingredient(rows: list[dict[str, Any]], packet: str, ingredient_name: str) -> list[str]:
    ids = []

    for row in rows:
        if row.get("packet") != packet:
            continue

        if row.get("audit_status") == "rejected":
            continue

        if not row.get("supports_ingredient_packet"):
            continue

        related = clean(row.get("corrected_related_ingredient"))
        if ingredient_name.lower() in related.lower() or related.lower() in ingredient_name.lower():
            ids.append(row["evidence_id"])
        elif packet in ["sugar", "soy_lecithin", "pgpr", "natural_flavor", "packaging_wrapper"]:
            ids.append(row["evidence_id"])
        elif packet == "cocoa_chocolate_cocoa_butter" and ingredient_name.lower() in [
            "chocolate / cocoa",
            "cocoa butter",
        ]:
            ids.append(row["evidence_id"])
        elif packet == "dairy_milk_skim_milk_milk_fat" and ingredient_name.lower() in [
            "milk",
            "skim milk",
            "milk fat",
        ]:
            ids.append(row["evidence_id"])

    return sorted(set(ids))


def find_logo_path(source_inventory: list[dict[str, Any]], keywords: list[str]) -> str:
    for row in source_inventory:
        path_text = f"{row.get('file_name', '')} {row.get('relative_path', '')}".lower()
        if row.get("document_type") != "image_or_logo":
            continue
        if any(keyword.lower() in path_text for keyword in keywords):
            return row.get("relative_path", "")

    return ""


def build_supplier_packets(
    audited_rows: list[dict[str, Any]],
    source_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packets = []

    for packet_name, config in SUPPLIER_TARGETS.items():
        evidence_ids = evidence_ids_for_supplier(
            audited_rows,
            packet_name,
            config["company_name"],
        )

        if evidence_ids:
            relationship_level = "company_level_confirmed"
            sku_level_confirmed = False
            confidence_level = "high" if len(evidence_ids) >= 2 else "medium"
        else:
            relationship_level = "unknown"
            sku_level_confirmed = False
            confidence_level = "low"

        packets.append(
            {
                "supplier_packet_id": config["supplier_packet_id"],
                "company_name": config["company_name"],
                "related_ingredient_or_stage": config["related_ingredient_or_stage"],
                "relationship_level": relationship_level,
                "sku_level_confirmed": sku_level_confirmed,
                "evidence_ids": evidence_ids,
                "safe_display_name": config["safe_display_name"],
                "safe_website_wording": config["safe_website_wording"],
                "logo_allowed": bool(find_logo_path(source_inventory, config["logo_keywords"])),
                "logo_path": find_logo_path(source_inventory, config["logo_keywords"]),
                "confidence_level": confidence_level,
                "limits": config["limits"],
                "packet_builder_meta": {
                    "created_by": "step11_supplier_ingredient_packet_builder",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "source": "strict audited evidence only",
                },
            }
        )

    return packets


def supplier_status_for_ingredient(
    target: dict[str, Any],
    supplier_packets: list[dict[str, Any]],
) -> str:
    if not target["confirmed_supplier_names"]:
        return "unknown"

    for supplier in supplier_packets:
        if supplier["company_name"] in target["confirmed_supplier_names"]:
            if supplier["relationship_level"] == "company_level_confirmed":
                return "company_level_confirmed"

    return "unknown"


def supplier_limitations_for_ingredient(target: dict[str, Any]) -> list[str]:
    if target["confirmed_supplier_names"]:
        return [
            "Supplier relationship is company-level only unless stated otherwise.",
            "Exact 1.55 oz SKU-level allocation is not publicly confirmed.",
            "Use safe wording only; do not claim exact supplier-to-bar allocation."
        ]

    return [
        "Supplier is not publicly confirmed for the 1.55 oz bar.",
        "Use as ingredient/function/process input only.",
        "Do not attach a specific supplier unless later direct evidence supports it."
    ]


def build_ingredient_packets(
    audited_rows: list[dict[str, Any]],
    supplier_packets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    packets = []

    for target in INGREDIENT_TARGETS:
        evidence_ids = evidence_ids_for_ingredient(
            audited_rows,
            target["packet"],
            target["ingredient_name"],
        )

        supplier_status = supplier_status_for_ingredient(target, supplier_packets)

        packets.append(
            {
                "ingredient_id": target["ingredient_id"],
                "ingredient_name": target["ingredient_name"],
                "label_order_position": target["label_order_position"],
                "label_status": target["label_status"],
                "source_evidence_ids": evidence_ids,
                "origin_logic": target["origin_logic"],
                "processing_logic": target["processing_logic"],
                "supplier_status": supplier_status,
                "confirmed_supplier_names": target["confirmed_supplier_names"] if supplier_status == "company_level_confirmed" else [],
                "supplier_limitations": supplier_limitations_for_ingredient(target),
                "estimated_grams_low": None,
                "estimated_grams_base": None,
                "estimated_grams_high": None,
                "price_proxy_low_per_lb": None,
                "price_proxy_base_per_lb": None,
                "price_proxy_high_per_lb": None,
                "estimated_cost_low_cents": None,
                "estimated_cost_base_cents": None,
                "estimated_cost_high_cents": None,
                "estimated_cost_status": "not_started",
                "confidence_level": target["confidence_level"] if evidence_ids else "low",
                "notes": (
                    "Cost estimates are intentionally not calculated in Step 11. "
                    "They will be added in Step 12 cost model builder using benchmark evidence and assumptions."
                ),
                "packet_builder_meta": {
                    "created_by": "step11_supplier_ingredient_packet_builder",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "source": "strict audited evidence only",
                    "packet": target["packet"],
                },
            }
        )

    return packets


def write_supplier_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "supplier_packet_id",
        "company_name",
        "related_ingredient_or_stage",
        "relationship_level",
        "sku_level_confirmed",
        "confidence_level",
        "evidence_count",
        "logo_allowed",
        "logo_path",
        "safe_website_wording",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "supplier_packet_id": row["supplier_packet_id"],
                    "company_name": row["company_name"],
                    "related_ingredient_or_stage": row["related_ingredient_or_stage"],
                    "relationship_level": row["relationship_level"],
                    "sku_level_confirmed": row["sku_level_confirmed"],
                    "confidence_level": row["confidence_level"],
                    "evidence_count": len(row["evidence_ids"]),
                    "logo_allowed": row["logo_allowed"],
                    "logo_path": row["logo_path"],
                    "safe_website_wording": row["safe_website_wording"],
                }
            )


def write_ingredient_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "ingredient_id",
        "ingredient_name",
        "label_order_position",
        "label_status",
        "supplier_status",
        "confirmed_supplier_names",
        "confidence_level",
        "evidence_count",
        "estimated_cost_status",
        "origin_logic",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    "ingredient_id": row["ingredient_id"],
                    "ingredient_name": row["ingredient_name"],
                    "label_order_position": row["label_order_position"],
                    "label_status": row["label_status"],
                    "supplier_status": row["supplier_status"],
                    "confirmed_supplier_names": "; ".join(row["confirmed_supplier_names"]),
                    "confidence_level": row["confidence_level"],
                    "evidence_count": len(row["source_evidence_ids"]),
                    "estimated_cost_status": row["estimated_cost_status"],
                    "origin_logic": row["origin_logic"],
                }
            )


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda item: item[0]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="D:/HersheySupplyChainAI")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    strict_evidence_path = (
        root
        / "artifacts"
        / "04_level2_audited_blobs_strict"
        / "audited_evidence_blobs_strict.json"
    )

    source_inventory_path = (
        root
        / "artifacts"
        / "00_source_inventory"
        / "source_inventory_stage05_enriched.json"
    )

    supplier_dir = root / "artifacts" / "05_supplier_blobs"
    ingredient_dir = root / "artifacts" / "06_ingredient_blobs"
    report_dir = root / "artifacts" / "10_run_reports"

    supplier_dir.mkdir(parents=True, exist_ok=True)
    ingredient_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not strict_evidence_path.exists():
        raise FileNotFoundError(
            f"Missing strict audited evidence file: {strict_evidence_path}. Run Step 10B first."
        )

    if not source_inventory_path.exists():
        raise FileNotFoundError(
            f"Missing source inventory file: {source_inventory_path}."
        )

    audited_rows = read_json(strict_evidence_path)
    source_inventory = read_json(source_inventory_path)

    supplier_packets = build_supplier_packets(audited_rows, source_inventory)
    ingredient_packets = build_ingredient_packets(audited_rows, supplier_packets)

    supplier_json_path = supplier_dir / "supplier_packets.json"
    supplier_csv_path = supplier_dir / "supplier_packets_summary.csv"
    ingredient_json_path = ingredient_dir / "ingredient_packets.json"
    ingredient_csv_path = ingredient_dir / "ingredient_packets_summary.csv"

    write_json(supplier_json_path, supplier_packets)
    write_json(ingredient_json_path, ingredient_packets)

    write_supplier_csv(supplier_csv_path, supplier_packets)
    write_ingredient_csv(ingredient_csv_path, ingredient_packets)

    report = {
        "run_name": "step11_supplier_ingredient_packet_builder",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "strict_evidence_input": str(strict_evidence_path).replace("\\", "/"),
        "supplier_packets_created": len(supplier_packets),
        "ingredient_packets_created": len(ingredient_packets),
        "supplier_relationship_level_counts": count_by(supplier_packets, "relationship_level"),
        "ingredient_supplier_status_counts": count_by(ingredient_packets, "supplier_status"),
        "ingredient_cost_status_counts": count_by(ingredient_packets, "estimated_cost_status"),
        "supplier_packets_json": str(supplier_json_path).replace("\\", "/"),
        "supplier_packets_summary_csv": str(supplier_csv_path).replace("\\", "/"),
        "ingredient_packets_json": str(ingredient_json_path).replace("\\", "/"),
        "ingredient_packets_summary_csv": str(ingredient_csv_path).replace("\\", "/"),
        "next_step": "Step 12: build cost model inputs and benchmark-backed low/base/high cost stack.",
    }

    report_path = report_dir / "step11_supplier_ingredient_packet_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 11 SUPPLIER + INGREDIENT PACKET BUILDER COMPLETE")
    print("----------------------------------------------------")
    print(f"Supplier packets created: {len(supplier_packets)}")
    print(f"Ingredient packets created: {len(ingredient_packets)}")
    print(f"Supplier levels: {report['supplier_relationship_level_counts']}")
    print(f"Ingredient supplier statuses: {report['ingredient_supplier_status_counts']}")
    print("")
    print(f"Supplier JSON:   {supplier_json_path}")
    print(f"Ingredient JSON: {ingredient_json_path}")
    print(f"Report JSON:     {report_path}")
    print("")


if __name__ == "__main__":
    main()