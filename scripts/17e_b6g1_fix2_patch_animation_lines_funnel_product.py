from pathlib import Path
import re

ROOT = Path.cwd()
showcase = ROOT / "src/components/home/HomeProductShowcase.tsx"
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

showcase_text = showcase.read_text(encoding="utf-8")
field_text = field.read_text(encoding="utf-8")

# Product was too huge after prior patch. Restore a premium contained scale.
showcase_text = re.sub(
    r'w-\[[0-9]+%\] max-w-none',
    'w-[118%] max-w-none',
    showcase_text,
)

showcase_text = showcase_text.replace(
    "scale: 2.08",
    "scale: 1.18",
)

showcase_text = showcase_text.replace(
    "scale: 1.92",
    "scale: 1.1",
)

showcase_text = re.sub(
    r'h-\[[0-9]+px\] overflow-hidden rounded-\[1\.8rem\].*?sm:h-\[[0-9]+px\]',
    'h-[260px] overflow-hidden rounded-[1.8rem] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md sm:h-[300px]',
    showcase_text,
)

# 3D funnel was too far left. Move it to a balanced right-background position.
field_text = re.sub(
    r'position={\[[\-0-9.]+, 0\.08, 0\]}',
    'position={[-0.42, 0.08, 0]}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'scale={0\.[0-9]+}',
    'scale={0.84}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'absolute inset-y-0 right-\[[^\]]+\] w-\[[^\]]+\] min-w-\[[^\]]+\]',
    'absolute inset-y-0 right-[7vw] w-[50vw] min-w-[660px]',
    field_text,
)

showcase.write_text(showcase_text, encoding="utf-8")
field.write_text(field_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix2_animation_lines_funnel_product_balance")
