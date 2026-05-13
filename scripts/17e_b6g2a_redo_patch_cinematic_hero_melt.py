from pathlib import Path
import re

ROOT = Path.cwd()
page = ROOT / "src/app/page.tsx"

text = page.read_text(encoding="utf-8-sig")

# Remove old chocolate info/flat drip imports if they exist.
text = re.sub(
    r'import \{ ChocolateDripRibbon, ChocolateFlowDivider \} from "@/components/cinematic/ChocolateDripRibbon";\n?',
    "",
    text,
)

# Ensure pure hero overlay import exists.
import_line = 'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";'
if import_line not in text:
    target = 'import CinematicPageShell from "@/components/cinematic/CinematicPageShell";'
    if target in text:
        text = text.replace(target, target + "\n" + import_line, 1)
    else:
        imports = list(re.finditer(r'^import .+;$', text, flags=re.MULTILINE))
        if not imports:
            raise SystemExit("ERROR: Could not find import block.")
        last_import = imports[-1]
        text = text[:last_import.end()] + "\n" + import_line + text[last_import.end():]

# Remove wrong old components if present.
text = text.replace('      <ChocolateDripRibbon variant="heroTop" />\n', "")
text = text.replace('        <ChocolateFlowDivider />\n\n', "")
text = text.replace('      <ChocolateFlowDivider />\n\n', "")
text = text.replace('<ChocolateFlowDivider />\n\n', "")

# Ensure overlay is inside shell once.
if "<HeroChocolateMeltOverlay />" not in text:
    text = text.replace(
        "<CinematicPageShell>",
        "<CinematicPageShell>\n      <HeroChocolateMeltOverlay />",
        1,
    )

page.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_redo_cinematic_hero_melt")
