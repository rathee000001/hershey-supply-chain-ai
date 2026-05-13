from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

text = page.read_text(encoding="utf-8-sig")

text = re.sub(
    r'import \{ ChocolateDripRibbon, ChocolateFlowDivider \} from "@/components/cinematic/ChocolateDripRibbon";\n?',
    "",
    text,
)

import_line = 'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";'

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

text = text.replace('      <ChocolateDripRibbon variant="heroTop" />\n', "")
text = text.replace('        <ChocolateFlowDivider />\n\n', "")
text = text.replace('      <ChocolateFlowDivider />\n\n', "")
text = text.replace('<ChocolateFlowDivider />\n\n', "")

if "<HeroChocolateMeltOverlay />" not in text:
    if "<CinematicPageShell>" in text:
        text = text.replace(
            "<CinematicPageShell>",
            "<CinematicPageShell>\n      <HeroChocolateMeltOverlay />",
            1,
        )
    else:
        raise SystemExit("ERROR: Could not find <CinematicPageShell> in src/app/page.tsx")

page.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_r4_video_based_melt_overlay_homepage_safe")
