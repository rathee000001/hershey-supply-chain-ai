from pathlib import Path

ROOT = Path.cwd()

page = ROOT / "src/app/page.tsx"
showcase = ROOT / "src/components/home/HomeProductShowcase.tsx"
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

def replace_required(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Missing expected text in {path}: {old}")
    path.write_text(text.replace(old, new), encoding="utf-8")

# 1) Course correction on homepage.
replace_required(
    page,
    "MGMT 780 — Supply Chain Management",
    "QANT_760-M01-2026SP-S",
)

replace_required(
    page,
    "Subject",
    "Course",
)

replace_required(
    page,
    "Supply Chain Management",
    "Operations Management Applications",
)

replace_required(
    page,
    "Course: MGMT 780 · Subject: Supply Chain Management · Professor: Dr. Rajendra Tibrewala",
    "Spring 2026 - M01 · Operations Management Applications · QANT_760-M01-2026SP-S",
)

# 2) Shift vertical 3D funnel left and give it more canvas room.
replace_required(
    field,
    "position={[1.52, 0.08, 0]}",
    "position={[0.62, 0.08, 0]}",
)

replace_required(
    field,
    "scale={0.92}",
    "scale={0.9}",
)

replace_required(
    field,
    'className="absolute inset-y-0 right-0 w-[42vw] min-w-[560px]"',
    'className="absolute inset-y-0 right-[2vw] w-[48vw] min-w-[620px]"',
)

replace_required(
    field,
    'className="absolute inset-y-0 right-0 w-[42vw] min-w-[560px] bg-[radial-gradient(circle_at_58%_34%,rgba(111,29,18,0.07),transparent_29%),radial-gradient(circle_at_56%_52%,rgba(244,199,93,0.08),transparent_34%),radial-gradient(circle_at_78%_70%,rgba(255,241,208,0.12),transparent_28%)]"',
    'className="absolute inset-y-0 right-[2vw] w-[48vw] min-w-[620px] bg-[radial-gradient(circle_at_58%_34%,rgba(111,29,18,0.06),transparent_29%),radial-gradient(circle_at_56%_52%,rgba(244,199,93,0.07),transparent_34%),radial-gradient(circle_at_78%_70%,rgba(255,241,208,0.10),transparent_28%)]"',
)

# 3) Product showcase scale/layout patch.
replace_required(
    showcase,
    'className="relative mx-auto min-h-[460px] w-full max-w-[760px]"',
    'className="relative mx-auto min-h-[430px] w-full max-w-[820px]"',
)

replace_required(
    showcase,
    "min-h-[460px] flex-col",
    "min-h-[430px] flex-col",
)

replace_required(
    showcase,
    'className="relative w-full max-w-[640px]"',
    'className="relative w-full max-w-[760px]"',
)

replace_required(
    showcase,
    'className="relative aspect-[5.8/2] rounded-[1.8rem] border border-white/70 bg-white/42 p-4 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md"',
    'className="relative h-[250px] overflow-visible rounded-[1.8rem] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md sm:h-[285px]"',
)

replace_required(
    showcase,
    'className="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain drop-shadow-2xl"',
    'className="absolute inset-[-18%] h-[136%] w-[136%] object-contain drop-shadow-2xl"',
)

replace_required(
    showcase,
    "Product Visual Anchor",
    "Product Study Anchor",
)

print("PATCH_APPLIED: step17e_b6f_r4c3_course_product_funnel_patch")
