from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

text = page.read_text(encoding="utf-8")

import_line = 'import { ChocolateDripRibbon, ChocolateFlowDivider } from "@/components/cinematic/ChocolateDripRibbon";'

if import_line not in text:
    imports = list(re.finditer(r'^import .+;$', text, flags=re.MULTILINE))
    if imports:
        last = imports[-1]
        text = text[:last.end()] + "\n" + import_line + text[last.end():]
    else:
        text = import_line + "\n" + text

if '<ChocolateDripRibbon variant="heroTop" />' not in text:
    main_match = re.search(r'(<main\b[^>]*>)', text)
    if main_match:
        text = text[:main_match.end()] + '\n        <ChocolateDripRibbon variant="heroTop" />' + text[main_match.end():]
    else:
        raise SystemExit("Could not find <main> tag in src/app/page.tsx")

if '<ChocolateFlowDivider />' not in text:
    if '<HomeProjectOverviewSection />' in text:
        text = text.replace(
            '<HomeProjectOverviewSection />',
            '<ChocolateFlowDivider />\n\n        <HomeProjectOverviewSection />',
            1,
        )
    elif '<HomeIntelligencePipelineMap />' in text:
        text = text.replace(
            '<HomeIntelligencePipelineMap />',
            '<ChocolateFlowDivider />\n\n        <HomeIntelligencePipelineMap />',
            1,
        )
    else:
        raise SystemExit("Could not find a safe insertion point for ChocolateFlowDivider")

page.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_home_chocolate_drip_integration")
