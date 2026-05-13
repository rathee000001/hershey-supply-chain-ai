from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
path = root / "scripts" / "17d2_cleanup_validation.py"

text = path.read_text(encoding="utf-8")

old = '''    required_drip_terms = [
        "chocolateSlide",
        "chocolateDrop",
        "chocolateLiquid",
    ]'''

new = '''    required_drip_terms = [
        "chocolateMeltSway",
        "chocolateDropStretch",
        "meltBase",
        "premium-chocolate-layer",
        "premium-drip",
    ]'''

if old not in text:
    raise SystemExit("Could not find old required_drip_terms block. Open the file and check manually.")

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")

print("PATCH COMPLETE")
print(f"Updated: {path}")
print("Validator now matches the premium chocolate melt overlay.")