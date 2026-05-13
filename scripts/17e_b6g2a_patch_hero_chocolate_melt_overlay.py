from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

text = page.read_text(encoding="utf-8-sig")

# Remove old chocolate drip import if present.
text = re.sub(
    r'import \{ ChocolateDripRibbon, ChocolateFlowDivider \} from "@/components/cinematic/ChocolateDripRibbon";\n?',
    "",
    text,
)

# Add new pure visual overlay import.
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

# Remove old visual/info components from homepage.
text = text.replace('      <ChocolateDripRibbon variant="heroTop" />\n', "")
text = text.replace('        <ChocolateFlowDivider />\n\n', "")
text = text.replace('      <ChocolateFlowDivider />\n\n', "")
text = text.replace('<ChocolateFlowDivider />\n\n', "")

# Add pure overlay inside CinematicPageShell.
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

print("PATCH_APPLIED: step17e_b6g2a_remove_info_section_add_pure_melt_overlay")
