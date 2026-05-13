from pathlib import Path
import re

ROOT = Path.cwd()

page = ROOT / "src/app/page.tsx"
showcase = ROOT / "src/components/home/HomeProductShowcase.tsx"
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

def write(path: Path, text: str):
    path.write_text(text, encoding="utf-8")

page_text = page.read_text(encoding="utf-8")
showcase_text = showcase.read_text(encoding="utf-8")
field_text = field.read_text(encoding="utf-8")

# -----------------------------
# 1) Course text cleanup
# -----------------------------

# Replace obvious old/partial course strings.
course_replacements = {
    "MGMT 780 — Supply Chain Management": "Spring 2026 - M01 - Operations Management Applications",
    "Course: MGMT 780 · Course: Operations Management Applications · Professor: Dr. Rajendra Tibrewala": "Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala",
    "Course: MGMT 780 · Subject: Operations Management Applications · Professor: Dr. Rajendra Tibrewala": "Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala",
    "Course: MGMT 780 · Subject: Supply Chain Management · Professor: Dr. Rajendra Tibrewala": "Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala",
    "QANT_760-M01-2026SP-S": "Spring 2026 - M01 - Operations Management Applications",
}

for old, new in course_replacements.items():
    page_text = page_text.replace(old, new)

# Normalize the hero course badge: label + course + code.
page_text = re.sub(
    r'(<p className="text-\[10px\] font-black uppercase tracking-\[0\.25em\] text-\[#9c6a27\]">\s*)Course Project(\s*</p>\s*<p className="text-sm font-black text-\[#2a0805\]">\s*)[^<]+(\s*</p>)',
    r'\1Course Project\2Spring 2026 - M01\3\n                    <p className="mt-1 text-xs font-black text-[#2a0805]/72">Operations Management Applications · QANT_760-M01-2026SP-S</p>',
    page_text,
    count=1,
    flags=re.DOTALL,
)

# Normalize the academic framing line wherever it appears.
page_text = re.sub(
    r'Course:\s*MGMT 780\s*·\s*(Subject|Course):\s*Operations Management Applications\s*·\s*Professor:\s*Dr\. Rajendra Tibrewala',
    'Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala',
    page_text,
)

page_text = re.sub(
    r'Spring 2026 - M01 - Operations Management Applications\s*·\s*Spring 2026 - M01 - Operations Management Applications\s*·\s*Professor:\s*Dr\. Rajendra Tibrewala',
    'Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S · Professor: Dr. Rajendra Tibrewala',
    page_text,
)

# Fix the small summary card label if the previous patch changed Subject incorrectly.
page_text = page_text.replace(
    '<p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">\n                      Course\n                    </p>\n                    <p className="mt-2 text-lg font-black text-[#2a0805]">\n                      Operations Management Applications\n                    </p>',
    '<p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9c6a27]">\n                      Course\n                    </p>\n                    <p className="mt-2 text-lg font-black text-[#2a0805]">\n                      QANT 760\n                    </p>',
)

# -----------------------------
# 2) Product showcase scale correction
# -----------------------------

showcase_text = showcase_text.replace(
    'className="relative mx-auto min-h-[430px] w-full max-w-[820px]"',
    'className="relative mx-auto min-h-[420px] w-full max-w-[860px]"',
)

showcase_text = showcase_text.replace(
    'className="relative h-[250px] overflow-visible rounded-[1.8rem] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md sm:h-[285px]"',
    'className="relative h-[245px] overflow-hidden rounded-[1.8rem] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md sm:h-[280px]"',
)

showcase_text = showcase_text.replace(
    'className="absolute inset-[-18%] h-[136%] w-[136%] object-contain drop-shadow-2xl"',
    'className="absolute inset-0 h-full w-full object-contain drop-shadow-2xl"',
)

# Framer Motion scale was overriding CSS scale. Make the product visually large again.
showcase_text = showcase_text.replace(
    'initial={prefersReducedMotion ? false : { opacity: 0, rotateY: showBack ? -12 : 12, scale: 0.985 }}',
    'initial={prefersReducedMotion ? false : { opacity: 0, rotateY: showBack ? -12 : 12, scale: 1.92 }}',
)

showcase_text = showcase_text.replace(
    'animate={prefersReducedMotion ? undefined : { opacity: 1, rotateY: 0, scale: 1 }}',
    'animate={prefersReducedMotion ? undefined : { opacity: 1, rotateY: 0, scale: 2.08 }}',
)

showcase_text = showcase_text.replace(
    'exit={prefersReducedMotion ? undefined : { opacity: 0, rotateY: showBack ? 12 : -12, scale: 0.985 }}',
    'exit={prefersReducedMotion ? undefined : { opacity: 0, rotateY: showBack ? 12 : -12, scale: 1.92 }}',
)

# Make the showcase less tall and less empty.
showcase_text = showcase_text.replace(
    'className="relative flex flex-1 items-center justify-center py-5"',
    'className="relative flex flex-1 items-center justify-center py-2"',
)

showcase_text = showcase_text.replace(
    'className="relative w-full max-w-[760px]"',
    'className="relative w-full max-w-[820px]"',
)

# -----------------------------
# 3) Shift vertical 3D funnel left
# -----------------------------

field_text = field_text.replace(
    'position={[0.62, 0.08, 0]}',
    'position={[-0.18, 0.08, 0]}',
)

field_text = field_text.replace(
    'scale={0.9}',
    'scale={0.86}',
)

field_text = field_text.replace(
    'className="absolute inset-y-0 right-[2vw] w-[48vw] min-w-[620px]"',
    'className="absolute inset-y-0 right-[9vw] w-[50vw] min-w-[640px]"',
)

field_text = field_text.replace(
    'className="absolute inset-y-0 right-[2vw] w-[48vw] min-w-[620px] bg-[radial-gradient(circle_at_58%_34%,rgba(111,29,18,0.06),transparent_29%),radial-gradient(circle_at_56%_52%,rgba(244,199,93,0.07),transparent_34%),radial-gradient(circle_at_78%_70%,rgba(255,241,208,0.10),transparent_28%)]"',
    'className="absolute inset-y-0 right-[9vw] w-[50vw] min-w-[640px] bg-[radial-gradient(circle_at_58%_34%,rgba(111,29,18,0.055),transparent_29%),radial-gradient(circle_at_56%_52%,rgba(244,199,93,0.065),transparent_34%),radial-gradient(circle_at_78%_70%,rgba(255,241,208,0.09),transparent_28%)]"',
)

write(page, page_text)
write(showcase, showcase_text)
write(field, field_text)

print("PATCH_APPLIED: step17e_b6f_r4c4_course_product_funnel_correction")
