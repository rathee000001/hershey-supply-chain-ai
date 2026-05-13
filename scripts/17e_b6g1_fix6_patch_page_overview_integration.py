from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

page_text = page.read_text(encoding="utf-8")

if 'HomeProjectOverviewSection' not in page_text:
    page_text = page_text.replace(
        'import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";',
        'import HomeIntelligencePipelineMap from "@/components/home/HomeIntelligencePipelineMap";\nimport HomeProjectOverviewSection from "@/components/home/HomeProjectOverviewSection";',
    )

if "<HomeProjectOverviewSection />" not in page_text:
    page_text = page_text.replace(
        "<HomeIntelligencePipelineMap />",
        "<HomeProjectOverviewSection />\n\n        <HomeIntelligencePipelineMap />",
        1,
    )

# Remove old inline project overview section if it still exists before the pipeline.
page_text = re.sub(
    r'\n\s*<section className="px-6 pb-12">[\s\S]*?<\/section>\s*\n\s*<HomeProjectOverviewSection />',
    '\n\n        <HomeProjectOverviewSection />',
    page_text,
    count=1,
)

page.write_text(page_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix6_page_overview_integration")
