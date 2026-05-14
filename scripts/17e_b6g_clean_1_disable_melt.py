from pathlib import Path
import json
from datetime import datetime

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
report = ROOT / "artifacts/10_run_reports/step17e_b6g_clean_1_disable_melt_report.json"

overlay.write_text(r'''"use client";

/*
  Step 17E-B6G-CLEAN-1

  Chocolate melt is intentionally disabled.

  Purpose:
  - remove all portal layers
  - remove video/shader/canvas side effects
  - remove z-index interference with navbar
  - keep imports/usages elsewhere safe
  - create a clean restart point for the next melt system

  Do not add animation back into this file until the next approved step.
*/

export default function HeroChocolateMeltOverlay() {
  return null;
}
''', encoding="utf-8")

report.parent.mkdir(parents=True, exist_ok=True)
report.write_text(json.dumps({
    "step": "17E-B6G-CLEAN-1",
    "name": "Disable chocolate melt overlay and create clean restart point",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "status": "PASS",
    "file": "src/components/cinematic/HeroChocolateMeltOverlay.tsx",
    "result": "HeroChocolateMeltOverlay now returns null. No portal, video, shader, canvas, or z-index layer remains.",
    "rollback_command": "powershell -ExecutionPolicy Bypass -File .\\scripts\\rollback_last_step.ps1"
}, indent=2), encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g_clean_1_disable_melt")
print("ROLLBACK: powershell -ExecutionPolicy Bypass -File .\\scripts\\rollback_last_step.ps1")
