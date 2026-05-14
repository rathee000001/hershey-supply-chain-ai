import json
from pathlib import Path

overlay = Path("src/components/cinematic/HeroChocolateMeltOverlay.tsx")
text = overlay.read_text(encoding="utf-8")

required = [
    'export default function HeroChocolateMeltOverlay()',
    'return null;',
    'Chocolate melt is intentionally disabled',
]

forbidden = [
    'createPortal',
    'Canvas',
    'VideoTexture',
    'document.body',
    'zIndex',
    'CHOCOLATE_VIDEO_SRC',
    'shaderMaterial',
    'useFrame',
    'ChocolateNavSpillLayer',
]

missing = [x for x in required if x not in text]
found_forbidden = [x for x in forbidden if x in text]

status = "PASS" if not missing and not found_forbidden else "FAIL"

print(json.dumps({
    "status": status,
    "missing_required": missing,
    "forbidden_found": found_forbidden,
    "rollback_command": "powershell -ExecutionPolicy Bypass -File .\\scripts\\rollback_last_step.ps1"
}, indent=2))

if status != "PASS":
    raise SystemExit(1)
