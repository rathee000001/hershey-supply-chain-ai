from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""

def exists(rel):
    return (root / rel).exists()

def nonempty(rel):
    path = root / rel
    return path.exists() and len(path.read_text(encoding="utf-8", errors="ignore").strip()) > 0

def json_load(rel):
    path = root / rel
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

required_active_files = [
    "src/app/page.tsx",
    "src/app/layout.tsx",
    "src/app/supply-chain/page.tsx",
    "src/app/evidence-brain/page.tsx",
    "src/app/cost-model/page.tsx",
    "src/app/sources/page.tsx",
    "src/app/methodology/page.tsx",
    "src/components/cinematic/CinematicNavbar.tsx",
    "src/components/cinematic/CinematicPageShell.tsx",
    "src/components/cinematic/ChocolateAtmosphere.tsx",
    "src/components/cinematic/ProductIdentityBadge.tsx",
    "src/components/cinematic/MotionSafeWrapper.tsx",
    "src/components/cinematic/PremiumLoadingScene.tsx",
    "src/components/hershey3d/HomeChocolateBarHero.tsx",
    "src/components/hershey3d/HomeChocolateBarHeroSlot.tsx",
    "src/lib/hershey/enrichedArtifacts.ts",
    "public/data/hershey/enriched_display/enriched_frontend_manifest_v2.json",
    "public/data/hershey/visual_assets/hershey_visual_assets_manifest.json",
]

required_terms = {
    "src/app/page.tsx": [
        "CinematicPageShell",
        "ProductIdentityBadge",
        "HomeChocolateBarHeroSlot",
        "Praveen Rathee",
        "Dr. Rajendra Tibrewala",
        "MGMT 780",
        "Supply Chain Management",
    ],
    "src/components/cinematic/CinematicPageShell.tsx": [
        "ChocolateAtmosphere",
        "CinematicNavbar",
        "showFloatingProductBadge",
        "Not affiliated with",
    ],
    "src/components/cinematic/ProductIdentityBadge.tsx": [
        "hershey_wrapper_front",
        "Hershey 1.55 oz Milk Chocolate",
        "variant",
    ],
    "src/components/hershey3d/HomeChocolateBarHero.tsx": [
        "Canvas",
        "ChocolateBlockGrid",
        "hershey_unwrapped_bar",
        "hershey_wrapper_front",
        "Unwrapped bar as the cinematic product anchor",
    ],
    "src/lib/hershey/enrichedArtifacts.ts": [
        "ENRICHED_FRONTEND_MANIFEST_URL",
        "loadEnrichedArtifacts",
        "EnrichedArtifacts",
        "GraphPayload",
        "CostBreakdown",
    ],
}

missing_files = [rel for rel in required_active_files if not exists(rel)]
empty_files = [rel for rel in required_active_files if exists(rel) and not nonempty(rel)]

missing_terms = {}
for rel, terms in required_terms.items():
    text = read_text(root / rel)
    missing = [term for term in terms if term not in text]
    if missing:
        missing_terms[rel] = missing

# Dangerous compiled legacy files
dangerous_hershey_root_ts = []
hershey_root = root / "src" / "components" / "hershey"
if hershey_root.exists():
    for path in list(hershey_root.glob("*.tsx")) + list(hershey_root.glob("*.ts")):
        if not path.name.endswith(".d.ts"):
            dangerous_hershey_root_ts.append(str(path).replace("\\", "/"))

archive_ts_files = []
archive_roots = [
    root / "project_archive",
    root / "src" / "components" / "archive",
]
for archive_root in archive_roots:
    if archive_root.exists():
        for path in list(archive_root.rglob("*.tsx")) + list(archive_root.rglob("*.ts")):
            if not path.name.endswith(".d.ts"):
                archive_ts_files.append(str(path).replace("\\", "/"))

# Package dependency check
package = json_load("package.json") or {}
deps = package.get("dependencies", {})
dev_deps = package.get("devDependencies", {})

required_deps = [
    "three",
    "@react-three/fiber",
    "@react-three/drei",
    "framer-motion",
    "gsap",
    "zustand",
]

missing_deps = [dep for dep in required_deps if dep not in deps]
missing_dev_deps = ["@types/three"] if "@types/three" not in dev_deps else []

# TS config check
tsconfig = json_load("tsconfig.json") or {}
compiler_options = tsconfig.get("compilerOptions", {})
paths = compiler_options.get("paths", {})
exclude = tsconfig.get("exclude", [])

tsconfig_issues = []
if paths.get("@/*") != ["./src/*"]:
    tsconfig_issues.append("paths alias @/* is not ./src/*")
if "baseUrl" in compiler_options:
    tsconfig_issues.append("baseUrl still exists; it was expected to be removed")
for item in ["project_archive", "project_archive/**/*", "src/components/archive", "src/components/archive/**/*", ".next"]:
    if item not in exclude:
        tsconfig_issues.append(f"missing exclude: {item}")

# Manifest / public artifact check
frontend_manifest = json_load("public/data/hershey/enriched_display/enriched_frontend_manifest_v2.json")
visual_manifest = json_load("public/data/hershey/visual_assets/hershey_visual_assets_manifest.json")

manifest_issues = []
primary_paths_checked = []

if not frontend_manifest:
    manifest_issues.append("Missing or invalid enriched frontend manifest")
else:
    primary = frontend_manifest.get("primary_artifacts", {})
    for key, url in primary.items():
        if isinstance(url, str) and url.startswith("/"):
            rel = "public" + url
            primary_paths_checked.append({"key": key, "url": url, "exists": exists(rel)})
            if not exists(rel):
                manifest_issues.append(f"Manifest artifact missing: {key} -> {url}")

visual_asset_status = {}
if not visual_manifest:
    manifest_issues.append("Missing or invalid visual asset manifest")
else:
    assets = visual_manifest.get("assets", {})
    for key in ["hershey_wrapper_front", "hershey_wrapper_back", "hershey_unwrapped_bar"]:
        asset = assets.get(key)
        url = asset.get("url") if isinstance(asset, dict) else None
        asset_exists = False
        if isinstance(url, str) and url.startswith("/"):
            asset_exists = exists("public" + url)
        visual_asset_status[key] = {"url": url, "exists": asset_exists}
        if not asset_exists:
            manifest_issues.append(f"Visual asset missing or unresolved: {key}")

# Route readiness check
routes = {
    "/": "src/app/page.tsx",
    "/supply-chain": "src/app/supply-chain/page.tsx",
    "/evidence-brain": "src/app/evidence-brain/page.tsx",
    "/cost-model": "src/app/cost-model/page.tsx",
    "/sources": "src/app/sources/page.tsx",
    "/methodology": "src/app/methodology/page.tsx",
}
route_status = {route: {"file": rel, "exists": exists(rel), "nonempty": nonempty(rel)} for route, rel in routes.items()}

# Optional build run
run_build = "--run-build" in sys.argv
build_result = None
build_log_path = root / "artifacts" / "10_run_reports" / "step17e6h_npm_build_log.txt"

if run_build:
    completed = subprocess.run(
        ["cmd", "/c", "npm run build"],
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
    )
    build_log = (completed.stdout or "") + "\n\nSTDERR:\n" + (completed.stderr or "")
    build_log_path.parent.mkdir(parents=True, exist_ok=True)
    build_log_path.write_text(build_log, encoding="utf-8", errors="ignore")
    build_result = {
        "return_code": completed.returncode,
        "passed": completed.returncode == 0,
        "build_log_path": str(build_log_path).replace("\\", "/"),
    }

# Final status
blocking_issues = []
blocking_issues.extend([f"missing file: {x}" for x in missing_files])
blocking_issues.extend([f"empty file: {x}" for x in empty_files])
blocking_issues.extend([f"dangerous root Hershey TS file still active: {x}" for x in dangerous_hershey_root_ts])
blocking_issues.extend([f"archive TS/TSX still active: {x}" for x in archive_ts_files])
blocking_issues.extend([f"missing dependency: {x}" for x in missing_deps])
blocking_issues.extend([f"missing dev dependency: {x}" for x in missing_dev_deps])
blocking_issues.extend([f"tsconfig issue: {x}" for x in tsconfig_issues])
blocking_issues.extend([f"manifest issue: {x}" for x in manifest_issues])
for rel, terms in missing_terms.items():
    blocking_issues.append(f"missing terms in {rel}: {terms}")

if build_result and not build_result["passed"]:
    blocking_issues.append("npm run build failed")

status = "pass" if not blocking_issues else "fail"

finished_steps = [
    "Step 00-16K: artifact brain / parser / OCR / RAG / evidence / enriched public JSON pipeline",
    "Step 17E-0: frontend cleanup and cinematic scaffold",
    "Step 17E-A: cinematic dependencies installed",
    "Step 17E-B1: motion safety and premium loading foundation",
    "Step 17E-B2: homepage rebuild and route stabilization",
    "Step 17E-B3: shared CinematicNavbar and CinematicPageShell",
    "Step 17E-B4: global ChocolateAtmosphere and product identity shell",
    "Step 17E-B5: home product identity + Three.js unwrapped bar hero",
    "Step 17E-B5G: hard legacy cleanup and enrichedArtifacts remake",
]

unfinished_steps = [
    "Step 17F: supply-chain Three.js scene foundation",
    "Step 17G: upstream ingredient streams",
    "Step 17H: Hershey factory process animation",
    "Step 17I: distribution, retail shelf, and consumer purchase animation",
    "Step 17J: evidence drawer and node interaction layer",
    "Step 17K: cost pulse and business intelligence overlay",
    "Step 17L: whole-site cinematic page rebuilds",
    "Step 17M: final QA, deployment, performance, and Hershey-ready polish",
    "Step 17N: optional portfolio case-study page / submission package",
]

report = {
    "run_name": "step17e6h_project_state_snapshot",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "blocking_issues": blocking_issues,
    "build_result": build_result,
    "project_root": str(root).replace("\\", "/"),
    "required_active_files_missing": missing_files,
    "required_active_files_empty": empty_files,
    "missing_terms": missing_terms,
    "dangerous_hershey_root_ts_files": dangerous_hershey_root_ts,
    "archive_ts_files_still_active": archive_ts_files,
    "dependencies_missing": missing_deps,
    "dev_dependencies_missing": missing_dev_deps,
    "tsconfig_paths": paths,
    "tsconfig_exclude": exclude,
    "tsconfig_issues": tsconfig_issues,
    "route_status": route_status,
    "primary_artifact_paths_checked": primary_paths_checked,
    "visual_asset_status": visual_asset_status,
    "finished_steps": finished_steps,
    "unfinished_steps": unfinished_steps,
    "next_step": "Step 17F: supply-chain Three.js scene foundation" if status == "pass" else "Fix blocking issues before Step 17F",
}

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)
report_path = report_dir / "step17e6h_project_state_snapshot_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

handoff_path = root / "docs" / "roadmap" / "17E_to_17F_project_state_handoff.md"
handoff_path.parent.mkdir(parents=True, exist_ok=True)

handoff = f"""# Hershey Supply Chain AI — Step 17E to 17F Handoff

Generated: {report["run_time"]}

## Current status

Status: {status}

## Finished

""" + "\n".join([f"- {item}" for item in finished_steps]) + """

## Unfinished

""" + "\n".join([f"- {item}" for item in unfinished_steps]) + f"""

## Blocking issues

{json.dumps(blocking_issues, indent=2)}

## Next step

{"Step 17F — supply-chain Three.js scene foundation." if status == "pass" else "Fix blocking issues before Step 17F."}

## Design rules

- JSON-first claims only.
- Animation can hardcode layout and motion, but evidence, costs, supplier claims, counts, and safe wording come from artifacts.
- Global chocolate atmosphere remains shared through CinematicPageShell.
- Home page has product-first Three.js hero.
- Supply-chain page is next and will become the main full 3D journey.
- Academic framing stays visible: Praveen Rathee, MGMT 780, Supply Chain Management, Professor Dr. Rajendra Tibrewala.
- Disclaimer remains: not affiliated with, endorsed by, or sponsored by The Hershey Company.
"""
handoff_path.write_text(handoff, encoding="utf-8")

print("")
print("STEP 17E-B5H PROJECT STATE SNAPSHOT COMPLETE")
print("--------------------------------------------")
print(f"Status:                 {status}")
print(f"Blocking issues:        {len(blocking_issues)}")
print(f"Missing active files:   {len(missing_files)}")
print(f"Empty active files:     {len(empty_files)}")
print(f"Dangerous Hershey TS:   {len(dangerous_hershey_root_ts)}")
print(f"Archive TS active:      {len(archive_ts_files)}")
print(f"Missing deps:           {len(missing_deps)}")
print(f"Manifest issues:        {len(manifest_issues)}")
if build_result:
    print(f"npm build passed:       {build_result['passed']}")
    print(f"Build log:              {build_result['build_log_path']}")
print(f"Report JSON:            {report_path}")
print(f"Handoff MD:             {handoff_path}")
print("")
