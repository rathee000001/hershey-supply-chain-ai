from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

required_files = [
    "src/app/supply-chain/page.tsx",
    "src/components/archive/hershey_legacy_17d",
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/hershey3d/HersheySceneCanvas.tsx",
    "src/components/hershey3d/HersheySupplyChainScene.tsx",
    "src/components/hershey/evidence/EvidenceDrawer.tsx",
    "src/components/hershey/cost/CostPulsePanel.tsx",
    "src/components/hershey/fallback/SupplyChainFallbackMap.tsx",
    "src/lib/hershey/visualAssets.ts",
    "src/lib/hershey/sceneNodes.ts",
    "src/lib/hershey/evidenceMapping.ts",
    "src/store/hersheyCinematicStore.ts",
    "docs/roadmap/17E_cinematic_engine_foundation.md",
    "docs/roadmap/17M_final_qa_deployment.md",
]

page = root / "src" / "app" / "supply-chain" / "page.tsx"
page_text = page.read_text(encoding="utf-8") if page.exists() else ""

forbidden_imports = [
    "ChocolateDripOverlay",
    "HersheyCinematicHero",
    "CinematicAssetScene",
    "CinematicConnectedMap",
    "CinematicSupplyChainStoryboard",
]

required_page_terms = [
    "Step 17E",
    "Advanced cinematic engine foundation",
    "Three.js supply-chain scene",
    "Evidence-aware nodes",
    "Cinematic process animation",
]

missing_paths = [
    item for item in required_files
    if not (root / item).exists()
]

forbidden_found = [
    item for item in forbidden_imports
    if item in page_text
]

missing_page_terms = [
    item for item in required_page_terms
    if item not in page_text
]

validation_status = "pass"
if missing_paths or forbidden_found or missing_page_terms:
    validation_status = "fail"

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e0_validate_cleanup_scaffold",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "missing_paths": missing_paths,
    "forbidden_legacy_imports_found_in_supply_chain_page": forbidden_found,
    "missing_page_terms": missing_page_terms,
    "next_step": (
        "Step 17E: install advanced cinematic dependencies and begin engine foundation."
        if validation_status == "pass"
        else "Fix cleanup/scaffold before Step 17E."
    )
}

report_path = report_dir / "step17e0_cleanup_scaffold_validation_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-0 CLEANUP + SCAFFOLD VALIDATION COMPLETE")
print("-------------------------------------------------")
print(f"Validation status: {validation_status}")
print(f"Missing paths:     {len(missing_paths)}")
print(f"Legacy imports:    {len(forbidden_found)}")
print(f"Missing terms:     {len(missing_page_terms)}")
print(f"Report JSON:       {report_path}")
print("")