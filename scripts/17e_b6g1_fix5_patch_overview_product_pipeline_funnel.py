from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"
field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"

page_text = page.read_text(encoding="utf-8")
field_text = field.read_text(encoding="utf-8")

if 'HomeProjectOverviewSection' not in page_text:
    page_text = page_text.replace(
        'import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";',
        'import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";\nimport HomeProjectOverviewSection from "@/components/home/HomeProjectOverviewSection";',
    )

# Replace the old project overview section immediately before the pipeline map.
page_text = re.sub(
    r'\n\s*<section className="px-6 pb-12">[\s\S]*?<\/section>\s*\n\s*<HomeIntelligencePipelineMap />',
    '\n\n        <HomeProjectOverviewSection />\n\n        <HomeIntelligencePipelineMap />',
    page_text,
    count=1,
)

# If old overview still exists from a different formatting, inject the component before pipeline and leave no duplicate static overview marker.
if "<HomeProjectOverviewSection />" not in page_text:
    page_text = page_text.replace("<HomeIntelligencePipelineMap />", "<HomeProjectOverviewSection />\n\n        <HomeIntelligencePipelineMap />", 1)

# Shift 3D funnel so it begins after the product showcase edge.
field_text = re.sub(
    r'position={\[[\-0-9.]+, 0\.08, 0\]}',
    'position={[0.42, 0.08, 0]}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'scale={0\.[0-9]+}',
    'scale={0.78}',
    field_text,
    count=1,
)

field_text = re.sub(
    r'absolute inset-y-0 right-\[[^\]]+\] w-\[[^\]]+\] min-w-\[[^\]]+\]',
    'absolute inset-y-0 right-[-6vw] w-[42vw] min-w-[520px]',
    field_text,
)

page.write_text(page_text, encoding="utf-8")
field.write_text(field_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix5_overview_funnel_page_integration")
