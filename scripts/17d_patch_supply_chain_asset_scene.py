from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
page = root / "src" / "app" / "supply-chain" / "page.tsx"

text = page.read_text(encoding="utf-8")

import_line = 'import CinematicAssetScene from "@/components/hershey/CinematicAssetScene";\n'

if "CinematicAssetScene" not in text:
    # Add after storyboard/connected map imports if present, otherwise after enrichedArtifacts import area.
    marker = 'import CinematicConnectedMap from "@/components/hershey/CinematicConnectedMap";\n'
    if marker in text:
        text = text.replace(marker, marker + import_line)
    else:
        text = import_line + text

component_block = """\n      <CinematicAssetScene
        ingredients={data.ingredients}
        suppliers={data.suppliers}
        costBreakdown={data.costBreakdown}
      />\n"""

if "<CinematicAssetScene" not in text:
    marker = """      <CinematicConnectedMap
        ingredients={data.ingredients}
        suppliers={data.suppliers}
        graph={data.graph}
        costBreakdown={data.costBreakdown}
      />
"""
    if marker in text:
        text = text.replace(marker, component_block + "\n" + marker)
    else:
        fallback_marker = '<section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-3">'
        text = text.replace(fallback_marker, component_block + "\n      " + fallback_marker, 1)

page.write_text(text, encoding="utf-8")

print("PATCH COMPLETE")
print(f"Updated: {page}")
print("CinematicAssetScene import:", "CinematicAssetScene" in text)
print("CinematicAssetScene component:", "<CinematicAssetScene" in text)