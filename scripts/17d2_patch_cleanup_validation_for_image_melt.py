from pathlib import Path

root = Path("D:/HersheySupplyChainAI")
path = root / "scripts" / "17d2_cleanup_validation.py"

text = path.read_text(encoding="utf-8")

start = text.find("    required_drip_terms = [")
if start == -1:
    raise SystemExit("Could not find required_drip_terms block.")

end = text.find("    ]", start)
if end == -1:
    raise SystemExit("Could not find end of required_drip_terms block.")

end = end + len("    ]")

new_block = '''    required_drip_terms = [
        "CHOCOLATE_MELT_URL",
        "real-chocolate-melt",
        "chocolateImageFloat",
        "chocolateGlossSweep",
        "chocolate_melt_drip.webp",
    ]'''

text = text[:start] + new_block + text[end:]

path.write_text(text, encoding="utf-8")

print("PATCH COMPLETE")
print("Validator now checks for real image-based chocolate melt overlay.")