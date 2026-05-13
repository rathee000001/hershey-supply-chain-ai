from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

text = page.read_text(encoding="utf-8-sig")

import_line = 'import { ChocolateDripRibbon, ChocolateFlowDivider } from "@/components/cinematic/ChocolateDripRibbon";'

if import_line not in text:
    target = 'import CinematicPageShell from "@/components/cinematic/CinematicPageShell";'
    if target in text:
        text = text.replace(target, target + "\n" + import_line, 1)
    else:
        imports = list(re.finditer(r'^import .+;$', text, flags=re.MULTILINE))
        if not imports:
            raise SystemExit("ERROR: Could not find import block in src/app/page.tsx")
        last_import = imports[-1]
        text = text[:last_import.end()] + "\n" + import_line + text[last_import.end():]

if '<ChocolateDripRibbon variant="heroTop" />' not in text:
    if "<CinematicPageShell>" in text:
        text = text.replace(
            "<CinematicPageShell>",
            "<CinematicPageShell>\n      <ChocolateDripRibbon variant=\"heroTop\" />",
            1,
        )
    else:
        raise SystemExit("ERROR: Could not find <CinematicPageShell> in src/app/page.tsx")

if "<ChocolateFlowDivider />" not in text:
    if "<HomeProjectOverviewSection />" in text:
        text = text.replace(
            "<HomeProjectOverviewSection />",
            "<ChocolateFlowDivider />\n\n        <HomeProjectOverviewSection />",
            1,
        )
    else:
        raise SystemExit("ERROR: Could not find <HomeProjectOverviewSection /> in src/app/page.tsx")

page.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix1_integrated_chocolate_drip_into_page")
