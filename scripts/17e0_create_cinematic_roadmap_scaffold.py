from pathlib import Path
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

folders = [
    "src/components/cinematic",
    "src/components/hershey3d",
    "src/components/hershey/evidence",
    "src/components/hershey/cost",
    "src/components/hershey/fallback",
    "src/lib/hershey",
    "src/store",
    "src/app/evidence-brain",
    "src/app/cost-model",
    "src/app/sources",
    "src/app/methodology",
    "docs/roadmap",
    "artifacts/20_frontend_cinematic_engine",
]

empty_files = [
    # Cinematic global system
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/cinematic/ChocolateAtmosphere.tsx",
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/components/cinematic/PremiumLoadingScene.tsx",
    "src/components/cinematic/SectionReveal.tsx",
    "src/components/cinematic/GlassMetricCard.tsx",
    "src/components/cinematic/ChocolateDivider.tsx",

    # Hershey 3D engine
    "src/components/hershey3d/HersheySceneCanvas.tsx",
    "src/components/hershey3d/HersheySupplyChainScene.tsx",
    "src/components/hershey3d/SceneCameraRig.tsx",
    "src/components/hershey3d/ChocolateMeltSystem.tsx",
    "src/components/hershey3d/IngredientStream3D.tsx",
    "src/components/hershey3d/SupplierNode3D.tsx",
    "src/components/hershey3d/HersheyFactory3D.tsx",
    "src/components/hershey3d/ConveyorBelt3D.tsx",
    "src/components/hershey3d/WrapperMachine3D.tsx",
    "src/components/hershey3d/TruckRoute3D.tsx",
    "src/components/hershey3d/RetailShelf3D.tsx",
    "src/components/hershey3d/EvidenceHotspot3D.tsx",

    # Evidence / cost / fallback
    "src/components/hershey/evidence/EvidenceDrawer.tsx",
    "src/components/hershey/evidence/EvidenceMiniTooltip.tsx",
    "src/components/hershey/cost/CostPulsePanel.tsx",
    "src/components/hershey/cost/CostWaterfall.tsx",
    "src/components/hershey/fallback/SupplyChainFallbackMap.tsx",

    # Libraries
    "src/lib/hershey/visualAssets.ts",
    "src/lib/hershey/sceneNodes.ts",
    "src/lib/hershey/evidenceMapping.ts",
    "src/lib/hershey/cinematicTypes.ts",

    # State
    "src/store/hersheyCinematicStore.ts",

    # Future pages
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",

    # Docs / artifacts
    "docs/roadmap/17E_cinematic_engine_foundation.md",
    "docs/roadmap/17F_3d_hero_scene.md",
    "docs/roadmap/17G_upstream_ingredient_streams.md",
    "docs/roadmap/17H_hershey_factory_process.md",
    "docs/roadmap/17I_distribution_retail_consumer.md",
    "docs/roadmap/17J_evidence_interaction_layer.md",
    "docs/roadmap/17K_cost_pulse_layer.md",
    "docs/roadmap/17L_whole_site_design_system.md",
    "docs/roadmap/17M_final_qa_deployment.md",
    "artifacts/20_frontend_cinematic_engine/.gitkeep",
]

created_folders = []
created_files = []
existing_files = []

for folder in folders:
    folder_path = root / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    created_folders.append(str(folder_path).replace("\\", "/"))

for file in empty_files:
    file_path = root / file
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        existing_files.append(str(file_path).replace("\\", "/"))
    else:
        file_path.write_text("", encoding="utf-8")
        created_files.append(str(file_path).replace("\\", "/"))

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e0_create_cinematic_roadmap_scaffold",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "folders_requested": len(folders),
    "files_requested": len(empty_files),
    "folders_ready": created_folders,
    "files_created": created_files,
    "files_already_existing": existing_files,
    "next_step": "Run scaffold validation, then install cinematic dependencies in Step 17E."
}

report_path = report_dir / "step17e0_cinematic_roadmap_scaffold_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-0 CINEMATIC ROADMAP SCAFFOLD COMPLETE")
print("----------------------------------------------")
print(f"Folders ready:          {len(created_folders)}")
print(f"Files created:          {len(created_files)}")
print(f"Files already existing: {len(existing_files)}")
print(f"Report JSON:            {report_path}")
print("")