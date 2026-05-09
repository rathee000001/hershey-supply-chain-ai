from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


PATCH_TARGETS = {
    "SUP_LAND_O_LAKES_DAIRY": {
        "company_name": "Land O'Lakes",
        "packet": "dairy_milk_skim_milk_milk_fat",
        "relationship_level": "company_level_confirmed",
        "confidence_level": "medium",
        "review_note": (
            "Promoted after reviewed relationship pass. Evidence remains company-level dairy context only; "
            "exact 1.55 oz SKU dairy allocation is not publicly confirmed."
        ),
    },
    "SUP_MCLANE_DISTRIBUTION": {
        "company_name": "McLane",
        "packet": "logistics_distribution",
        "relationship_level": "company_level_confirmed",
        "confidence_level": "medium",
        "review_note": (
            "Promoted after reviewed relationship pass. Evidence remains company-level downstream/distribution context only; "
            "exact route for the 1.55 oz SKU is not publicly confirmed."
        ),
    },
}


DAIRY_INGREDIENT_IDS = {
    "ING_MILK",
    "ING_SKIM_MILK",
    "ING_MILK_FAT",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean(value: Any) -> str:
    return str(value or "").strip()


def collect_review_candidate_evidence(
    audited_rows: list[dict[str, Any]],
    packet: str,
    company_name: str,
) -> list[str]:
    ids: list[str] = []

    company_key = company_name.lower().replace("'", "")
    packet_key = packet.lower()

    for row in audited_rows:
        if clean(row.get("packet")).lower() != packet_key:
            continue

        if clean(row.get("audit_status")) == "rejected":
            continue

        text = " ".join(
            [
                clean(row.get("source_file")),
                clean(row.get("claim")),
                clean(row.get("evidence_text")),
                clean(row.get("safe_website_wording")),
                clean(row.get("corrected_related_company")),
            ]
        ).lower().replace("'", "")

        has_company = company_key in text
        has_company_level = clean(row.get("corrected_relationship_strength")) == "company_level_confirmed"

        if has_company and has_company_level:
            ids.append(clean(row.get("evidence_id")))

    return sorted(set([x for x in ids if x]))


def backup_file(path: Path) -> Path | None:
    if not path.exists():
        return None

    backup_path = path.with_suffix(path.suffix + ".pre_step11b_backup")
    shutil.copy2(path, backup_path)
    return backup_path


def patch_supplier_packets(
    supplier_packets: list[dict[str, Any]],
    audited_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    patched = []
    changes = []

    for packet in supplier_packets:
        packet_id = packet.get("supplier_packet_id")

        if packet_id in PATCH_TARGETS:
            config = PATCH_TARGETS[packet_id]
            evidence_ids = collect_review_candidate_evidence(
                audited_rows=audited_rows,
                packet=config["packet"],
                company_name=config["company_name"],
            )

            old_level = packet.get("relationship_level")

            packet["relationship_level"] = config["relationship_level"]
            packet["sku_level_confirmed"] = False
            packet["confidence_level"] = config["confidence_level"]
            packet["evidence_ids"] = evidence_ids
            packet["reviewed_relationship_patch"] = {
                "patched_at": datetime.now().isoformat(timespec="seconds"),
                "patch_script": "08b_reviewed_relationship_patch.py",
                "old_relationship_level": old_level,
                "new_relationship_level": config["relationship_level"],
                "review_note": config["review_note"],
                "evidence_count_after_patch": len(evidence_ids),
                "safe_rule": "Company-level only. No SKU-level supplier claim."
            }

            changes.append(
                {
                    "target": packet_id,
                    "type": "supplier_packet",
                    "old_relationship_level": old_level,
                    "new_relationship_level": config["relationship_level"],
                    "evidence_count": len(evidence_ids),
                }
            )

        patched.append(packet)

    return patched, changes


def patch_ingredient_packets(
    ingredient_packets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    patched = []
    changes = []

    for packet in ingredient_packets:
        ingredient_id = packet.get("ingredient_id")

        if ingredient_id in DAIRY_INGREDIENT_IDS:
            old_status = packet.get("supplier_status")

            packet["supplier_status"] = "company_level_confirmed"
            packet["confirmed_supplier_names"] = ["Land O'Lakes"]
            packet["confidence_level"] = "medium"
            packet["supplier_limitations"] = [
                "Supplier relationship is company-level only.",
                "Exact 1.55 oz SKU-level dairy allocation is not publicly confirmed.",
                "Use safe wording only; do not claim exact supplier-to-bar allocation."
            ]
            packet["reviewed_relationship_patch"] = {
                "patched_at": datetime.now().isoformat(timespec="seconds"),
                "patch_script": "08b_reviewed_relationship_patch.py",
                "old_supplier_status": old_status,
                "new_supplier_status": "company_level_confirmed",
                "review_note": (
                    "Dairy ingredient supplier status aligned to reviewed Land O'Lakes company-level supplier packet. "
                    "This is not SKU-level confirmation."
                ),
            }

            changes.append(
                {
                    "target": ingredient_id,
                    "type": "ingredient_packet",
                    "old_supplier_status": old_status,
                    "new_supplier_status": "company_level_confirmed",
                }
            )

        patched.append(packet)

    return patched, changes


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

    audited_path = root / "artifacts" / "04_level2_audited_blobs_strict" / "audited_evidence_blobs_strict.json"
    supplier_path = root / "artifacts" / "05_supplier_blobs" / "supplier_packets.json"
    ingredient_path = root / "artifacts" / "06_ingredient_blobs" / "ingredient_packets.json"
    report_dir = root / "artifacts" / "10_run_reports"

    report_dir.mkdir(parents=True, exist_ok=True)

    audited_rows = read_json(audited_path)
    supplier_packets = read_json(supplier_path)
    ingredient_packets = read_json(ingredient_path)

    backup_supplier = backup_file(supplier_path)
    backup_ingredient = backup_file(ingredient_path)

    patched_suppliers, supplier_changes = patch_supplier_packets(supplier_packets, audited_rows)
    patched_ingredients, ingredient_changes = patch_ingredient_packets(ingredient_packets)

    write_json(supplier_path, patched_suppliers)
    write_json(ingredient_path, patched_ingredients)

    reviewed_supplier_path = root / "artifacts" / "05_supplier_blobs" / "supplier_packets_reviewed.json"
    reviewed_ingredient_path = root / "artifacts" / "06_ingredient_blobs" / "ingredient_packets_reviewed.json"

    write_json(reviewed_supplier_path, patched_suppliers)
    write_json(reviewed_ingredient_path, patched_ingredients)

    report = {
        "run_name": "step11b_reviewed_relationship_patch",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(root).replace("\\", "/"),
        "backup_supplier_file": str(backup_supplier).replace("\\", "/") if backup_supplier else "",
        "backup_ingredient_file": str(backup_ingredient).replace("\\", "/") if backup_ingredient else "",
        "supplier_changes": supplier_changes,
        "ingredient_changes": ingredient_changes,
        "supplier_relationship_level_counts_after_patch": count_by(patched_suppliers, "relationship_level"),
        "ingredient_supplier_status_counts_after_patch": count_by(patched_ingredients, "supplier_status"),
        "supplier_packets_json": str(supplier_path).replace("\\", "/"),
        "ingredient_packets_json": str(ingredient_path).replace("\\", "/"),
        "reviewed_supplier_packets_json": str(reviewed_supplier_path).replace("\\", "/"),
        "reviewed_ingredient_packets_json": str(reviewed_ingredient_path).replace("\\", "/"),
        "next_step": "Step 12: build benchmark-backed cost model inputs and low/base/high cost stack."
    }

    report_path = report_dir / "step11b_reviewed_relationship_patch_report.json"
    write_json(report_path, report)

    print("")
    print("STEP 11B REVIEWED RELATIONSHIP PATCH COMPLETE")
    print("---------------------------------------------")
    print(f"Supplier changes: {len(supplier_changes)}")
    print(f"Ingredient changes: {len(ingredient_changes)}")
    print(f"Supplier levels after patch: {report['supplier_relationship_level_counts_after_patch']}")
    print(f"Ingredient supplier statuses after patch: {report['ingredient_supplier_status_counts_after_patch']}")
    print("")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()