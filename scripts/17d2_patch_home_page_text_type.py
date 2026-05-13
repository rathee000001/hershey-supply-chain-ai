from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
page = root / "src" / "app" / "page.tsx"

text = page.read_text(encoding="utf-8")

replacements = {
    "{text}</p>": "{String(text)}</p>",
    "{subtitle}</p>": "{String(subtitle)}</p>",
    "{description}</p>": "{String(description)}</p>",
}

changed = False

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed = True
        print(f"Patched: {old} -> {new}")

if not changed:
    print("No exact text/subtitle/description paragraph patterns found.")
    print("Open src/app/page.tsx and manually wrap the red variable with String(...).")

page.write_text(text, encoding="utf-8")

print("PATCH COMPLETE")
print(f"Updated: {page}")