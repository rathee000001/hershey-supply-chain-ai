from pathlib import Path

path = Path("src/components/cinematic/CinematicNavbar.tsx")
text = path.read_text(encoding="utf-8")

replacements = {
    'text-[#ffe878]': 'text-[#fff1a8]',
    'text-[#ffe676]': 'text-[#fff1a8]',
    'text-slate-400': 'text-[#9a6a28]',
    'text-slate-950': 'text-[#2d0d06]',
    'bg-[#181a20]/94': 'bg-[#151820]/98',
    'bg-[#181a20]/96': 'bg-[#151820]/98',
}

for old, new in replacements.items():
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("Patched navbar pill text contrast and opacity.")
