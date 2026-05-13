from pathlib import Path
import re

ROOT = Path.cwd()
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

field_text = field.read_text(encoding="utf-8")

field_text = re.sub(
    r'position={\[[\-0-9.]+, 0\.08, 0\]}',
    'position={[0.06, 0.08, 0]}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'scale={0\.[0-9]+}',
    'scale={0.82}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'absolute inset-y-0 right-\[[^\]]+\] w-\[[^\]]+\] min-w-\[[^\]]+\]',
    'absolute inset-y-0 right-[2vw] w-[44vw] min-w-[560px]',
    field_text,
)

field.write_text(field_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix3_rebalance_funnel_right")
