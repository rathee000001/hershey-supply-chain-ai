from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
page = root / "src" / "app" / "page.tsx"

text = page.read_text(encoding="utf-8")

old = '{title}</h2>'
new = '{String(title)}</h2>'

if old not in text:
    print("Could not find exact {title}</h2> pattern.")
    print("Open src/app/page.tsx and replace {title} inside the h2 with {String(title)} manually.")
else:
    text = text.replace(old, new)
    page.write_text(text, encoding="utf-8")
    print("PATCH COMPLETE")
    print("Updated src/app/page.tsx: {title} -> {String(title)} inside h2.")