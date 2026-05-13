from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"
showcase = ROOT / "src/components/home/HomeProductShowcase.tsx"
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

page_text = page.read_text(encoding="utf-8")
showcase_text = showcase.read_text(encoding="utf-8")
field_text = field.read_text(encoding="utf-8")

# Ensure import exists.
if 'HomeIntelligencePipelineMap' not in page_text:
    page_text = page_text.replace(
        'import HomeProductShowcase from "@/components/home/HomeProductShowcase";',
        'import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";\nimport HomeProductShowcase from "@/components/home/HomeProductShowcase";',
    )

# Remove old pipelineItems const block if present.
page_text = re.sub(
    r'\nconst pipelineItems = \[[\s\S]*?\];\n',
    '\n',
    page_text,
)

# Replace old static Intelligence Pipeline section with the component.
page_text = re.sub(
    r'\n\s*<section className="px-6 pb-20">\s*<MotionSafeWrapper>\s*<div className="mx-auto max-w-7xl[\s\S]*?<\/MotionSafeWrapper>\s*<\/section>',
    '\n\n        <HomeIntelligencePipelineMap />',
    page_text,
    count=1,
)

# If old static section is still present because the exact wrapper differed, replace by marker span.
if "pipelineItems.map" in page_text:
    start = page_text.find('<section className="px-6 pb-20">', page_text.find("Intelligence Pipeline") - 1200)
    end = page_text.find("</section>", page_text.find("Intelligence Pipeline"))
    if start != -1 and end != -1:
        page_text = page_text[:start] + '<HomeIntelligencePipelineMap />' + page_text[end + len("</section>"):]

# Force exact course language in hero and academic section.
page_text = page_text.replace("MGMT 780 — Supply Chain Management", "Spring 2026 - M01")
page_text = page_text.replace("Course: MGMT 780", "Spring 2026 - M01")
page_text = page_text.replace("Subject: Supply Chain Management", "Operations Management Applications")
page_text = page_text.replace("Operations Management Applications · Professor: Dr. Rajendra Tibrewala", "Operations Management Applications · QANT_760-M01-2026SP-S")
page_text = page_text.replace("Spring 2026 - M01 - Course: Operations Management Applications", "Spring 2026 - M01 - Operations Management Applications")

# Fix the visible academic framing line from the screenshot.
page_text = re.sub(
    r'Spring 2026\s*-\s*M01\s*[·\-]\s*Operations Management Applications\s*[·\-]\s*QANT_760-M01-2026SP-S\s*[·\-]\s*Professor: Dr\. Rajendra Tibrewala',
    'Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S',
    page_text,
)

page_text = re.sub(
    r'Course:\s*MGMT 780\s*·\s*Course:\s*Operations Management Applications\s*·\s*Professor:\s*Dr\. Rajendra Tibrewala',
    'Spring 2026 - M01 - Operations Management Applications · QANT_760-M01-2026SP-S',
    page_text,
)

# Product display: make wrapper large without relying on image inset.
showcase_text = re.sub(
    r'className="relative mx-auto min-h-\[[^\]]+\] w-full max-w-\[[^\]]+\]"',
    'className="relative mx-auto min-h-[430px] w-full max-w-[860px]"',
    showcase_text,
)

showcase_text = re.sub(
    r'className="relative h-\[[^\]]+\] overflow-[^"]+ rounded-\[1\.8rem\] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-\[#3a160d\]/14 backdrop-blur-md sm:h-\[[^\]]+\]"',
    'className="relative h-[260px] overflow-hidden rounded-[1.8rem] border border-white/70 bg-white/42 p-3 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md sm:h-[300px]"',
    showcase_text,
)

showcase_text = re.sub(
    r'className="absolute [^"]*object-contain drop-shadow-2xl"',
    'className="absolute left-1/2 top-1/2 h-auto w-[170%] max-w-none -translate-x-1/2 -translate-y-1/2 object-contain drop-shadow-2xl"',
    showcase_text,
)

showcase_text = showcase_text.replace("Product Visual Anchor", "Product Study Anchor")

# Shift 3D funnel more left.
field_text = re.sub(
    r'position={\[[\-0-9.]+, 0\.08, 0\]}',
    'position={[-0.85, 0.08, 0]}',
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
    'absolute inset-y-0 right-[14vw] w-[54vw] min-w-[700px]',
    field_text,
)

page.write_text(page_text, encoding="utf-8")
showcase.write_text(showcase_text, encoding="utf-8")
field.write_text(field_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_force_pipeline_course_product_funnel_fix")
