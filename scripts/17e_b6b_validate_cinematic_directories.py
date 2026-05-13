import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
REPORT_PATH = ROOT / "artifacts" / "10_run_reports" / "step17e_b6b_directory_scaffold_report.json"

REQUIRED_DIRS = [
    "src/components/cinematic",
    "src/components/home",
    "src/components/evidence",
    "src/components/cost",
    "src/components/sources",
    "src/components/methodology",

    "src/components/hershey3d/home",
    "src/components/hershey3d/supply-chain",
    "src/components/hershey3d/factory",
    "src/components/hershey3d/distribution",
    "src/components/hershey3d/evidence",
    "src/components/hershey3d/cost",
    "src/components/hershey3d/sources",
    "src/components/hershey3d/methodology",

    "src/lib/hershey",
    "scripts",
    "artifacts/10_run_reports",
]

CORE_FILES = [
    "package.json",
    "tsconfig.json",
    "src/app/layout.tsx",
    "src/app/page.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
    "src/lib/hershey/enrichedArtifacts.ts",
]

CURRENT_CINEMATIC_FILES = [
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/ChocolateAtmosphere.tsx",
    "src/components/cinematic/ProductIdentityBadge.tsx",
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/components/cinematic/PremiumLoadingScene.tsx",
]

CURRENT_HERO_FILES = [
    "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
]

PRODUCT_ASSETS = [
    "public/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
    "public/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
    "public/data/hershey/visual_assets/source_assets/hershey_unwrapped_bar.png",
]

PUBLIC_ARTIFACTS = [
    "public/data/hershey/enriched_display/enriched_frontend_manifest_v2.json",
    "public/data/hershey/enriched_display/enriched_evidence_panel_lookup_v2.json",
    "public/data/hershey/enriched_display/enriched_packet_summary_v2.json",
    "public/data/hershey/enriched_display/enriched_supplier_cards_v2.json",
    "public/data/hershey/enriched_display/enriched_ingredient_cards_v2.json",
    "public/data/hershey/enriched_display/enriched_cost_breakdown_display_v2.json",
    "public/data/hershey/enriched_display/enriched_interactive_graph_payload_v2.json",
    "public/data/hershey/enriched_display/enriched_home_summary_cards_v2.json",
]

def exists_report(paths):
    return [
        {
            "path": path,
            "exists": (ROOT / path).exists(),
        }
        for path in paths
    ]

def list_tsx_files(relative_dir):
    base = ROOT / relative_dir
    if not base.exists():
        return []
    return sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in base.rglob("*")
        if path.suffix.lower() in [".ts", ".tsx"]
    )

def read_tsconfig_summary():
    path = ROOT / "tsconfig.json"
    if not path.exists():
        return {"exists": False}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "exists": True,
            "json_parse_ok": False,
            "error": str(exc),
        }

    compiler_options = data.get("compilerOptions", {})
    return {
        "exists": True,
        "json_parse_ok": True,
        "baseUrl": compiler_options.get("baseUrl"),
        "paths": compiler_options.get("paths"),
        "exclude": data.get("exclude"),
    }

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    directory_status = exists_report(REQUIRED_DIRS)
    core_status = exists_report(CORE_FILES)
    cinematic_status = exists_report(CURRENT_CINEMATIC_FILES)
    hero_status = exists_report(CURRENT_HERO_FILES)
    asset_status = exists_report(PRODUCT_ASSETS)
    artifact_status = exists_report(PUBLIC_ARTIFACTS)

    missing_required_dirs = [item["path"] for item in directory_status if not item["exists"]]
    missing_core_files = [item["path"] for item in core_status if not item["exists"]]
    missing_product_assets = [item["path"] for item in asset_status if not item["exists"]]
    missing_public_artifacts = [item["path"] for item in artifact_status if not item["exists"]]

    component_inventory = {
        "src/components/cinematic": list_tsx_files("src/components/cinematic"),
        "src/components/hershey3d": list_tsx_files("src/components/hershey3d"),
        "src/components/hershey": list_tsx_files("src/components/hershey"),
        "src/components/archive": list_tsx_files("src/components/archive"),
    }

    # These are only candidates for later inspection. This script does not move or delete anything.
    legacy_inspection_candidates = []
    for folder, files in component_inventory.items():
        if folder in ["src/components/hershey", "src/components/hershey3d"]:
            for file in files:
                if "/archive/" not in file and not file.endswith(".d.ts"):
                    legacy_inspection_candidates.append(file)

    status = "PASS"
    warnings = []

    if missing_required_dirs:
        status = "FAIL"
        warnings.append("One or more required clean directories are missing.")

    if missing_core_files:
        status = "REVIEW"
        warnings.append("One or more expected active app/core files are missing.")

    if missing_product_assets:
        warnings.append("One or more product visual assets are missing. This may block the product-first hero later.")

    if missing_public_artifacts:
        warnings.append("One or more enriched public JSON artifacts are missing. Claims must not be hardcoded to compensate.")

    report = {
        "step": "17E-B6B-1",
        "name": "Create clean cinematic directory structure and validation report",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "status": status,
        "warnings": warnings,
        "directory_status": directory_status,
        "core_file_status": core_status,
        "current_cinematic_file_status": cinematic_status,
        "current_home_hero_file_status": hero_status,
        "product_asset_status": asset_status,
        "public_artifact_status": artifact_status,
        "tsconfig_summary": read_tsconfig_summary(),
        "component_inventory": component_inventory,
        "legacy_inspection_candidates_only_not_moved": legacy_inspection_candidates,
        "rules_confirmed": {
            "no_files_deleted": True,
            "no_files_moved": True,
            "claims_must_come_from_json": True,
            "decorative_visuals_do_not_create_evidence_claims": True,
            "next_step_requires_user_report_review": True,
        },
        "next_recommended_step": "Step 17E-B6B-2 — inspect legacy/duplicate components before archiving anything",
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": status,
        "report_path": str(REPORT_PATH),
        "missing_required_dirs": missing_required_dirs,
        "missing_core_files": missing_core_files,
        "missing_product_assets": missing_product_assets,
        "missing_public_artifacts": missing_public_artifacts,
        "legacy_candidate_count": len(legacy_inspection_candidates),
    }, indent=2))

    if status == "FAIL":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
