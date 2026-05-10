from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
page = root / "src" / "app" / "page.tsx"

text = page.read_text(encoding="utf-8")

text = text.replace("  Github,\n", "  GitBranch,\n")
text = text.replace("<Github size={15} />", "<GitBranch size={15} />")
text = text.replace("<Github", "<GitBranch")
text = text.replace("</Github>", "</GitBranch>")

page.write_text(text, encoding="utf-8")

print("STEP 17E-B2 ICON FIX COMPLETE")
print("Replaced lucide Github icon with GitBranch.")
print(f"Updated: {page}")