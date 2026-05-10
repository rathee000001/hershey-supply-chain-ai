from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


root = Path("D:/HersheySupplyChainAI")

package_path = root / "package.json"
package = json.loads(package_path.read_text(encoding="utf-8"))

dependencies = package.get("dependencies", {})
dev_dependencies = package.get("devDependencies", {})

required_dependencies = [
    "three",
    "@react-three/fiber",
    "@react-three/drei",
    "framer-motion",
    "gsap",
    "zustand",
]

required_dev_dependencies = [
    "@types/three",
]

missing_dependencies = [
    name for name in required_dependencies if name not in dependencies
]

missing_dev_dependencies = [
    name for name in required_dev_dependencies if name not in dev_dependencies
]

scaffold_files = [
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/cinematic/ChocolateAtmosphere.tsx",
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/components/cinematic/PremiumLoadingScene.tsx",
    "src/components/hershey3d/HersheySceneCanvas.tsx",
    "src/components/hershey3d/HersheySupplyChainScene.tsx",
    "src/components/hershey3d/SceneCameraRig.tsx",
    "src/components/hershey3d/ChocolateMeltSystem.tsx",
    "src/components/hershey3d/IngredientStream3D.tsx",
    "src/components/hershey/evidence/EvidenceDrawer.tsx",
    "src/components/hershey/cost/CostPulsePanel.tsx",
    "src/components/hershey/fallback/SupplyChainFallbackMap.tsx",
    "src/store/hersheyCinematicStore.ts",
]

missing_scaffold_files = [
    path for path in scaffold_files if not (root / path).exists()
]

validation_status = "pass"
if missing_dependencies or missing_dev_dependencies or missing_scaffold_files:
    validation_status = "fail"

report = {
    "run_name": "step17e1_validate_cinematic_dependencies",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "validation_status": validation_status,
    "required_dependencies": required_dependencies,
    "required_dev_dependencies": required_dev_dependencies,
    "missing_dependencies": missing_dependencies,
    "missing_dev_dependencies": missing_dev_dependencies,
    "missing_scaffold_files": missing_scaffold_files,
    "installed_dependency_versions": {
        name: dependencies.get(name) for name in required_dependencies if name in dependencies
    },
    "installed_dev_dependency_versions": {
        name: dev_dependencies.get(name) for name in required_dev_dependencies if name in dev_dependencies
    },
    "next_step": (
        "Step 17E-B: build MotionSafeWrapper, PremiumLoadingScene, and CinematicPageShell."
        if validation_status == "pass"
        else "Install missing dependencies or restore missing scaffold files before Step 17E-B."
    ),
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report_path = report_dir / "step17e1_cinematic_dependencies_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-A CINEMATIC DEPENDENCY VALIDATION COMPLETE")
print("---------------------------------------------------")
print(f"Validation status:       {validation_status}")
print(f"Missing dependencies:    {len(missing_dependencies)}")
print(f"Missing dev dependencies:{len(missing_dev_dependencies)}")
print(f"Missing scaffold files:  {len(missing_scaffold_files)}")
print(f"Report JSON:             {report_path}")
print("")