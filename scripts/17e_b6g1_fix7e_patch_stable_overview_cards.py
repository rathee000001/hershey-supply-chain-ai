from pathlib import Path
import re

ROOT = Path.cwd()
overview = ROOT / "src/components/home/HomeProjectOverviewSection.tsx"

text = overview.read_text(encoding="utf-8")

# Mark this stable overview version.
text = text.replace(
    'data-home-project-overview="colorful-interactive-overview"',
    'data-home-project-overview="stable-colorful-interactive-overview-no-fade"',
)

# Force overview card buttons to never fade.
text = text.replace(
    'className="group min-h-[210px] rounded-[2.2rem] border p-6 text-left shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl transition"',
    'className="group min-h-[210px] rounded-[2.2rem] border p-6 text-left opacity-100 shadow-xl shadow-[#3a160d]/5 backdrop-blur-xl transition"',
)

# Force inline opacity to 1 for all overview cards.
text = text.replace(
    'borderColor: active ? card.border : "rgba(42,8,5,0.10)",',
    'borderColor: active ? card.border : "rgba(42,8,5,0.10)",\n                  opacity: 1,',
)

# Remove viewport-based fading from the overview cards only.
text = text.replace(
'''                initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
                whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}''',
'''                initial={false}''',
)

text = text.replace(
'                viewport={{ once: true, margin: "-80px" }}\n',
'',
)

# Ensure active/inactive animation always includes opacity: 1.
text = text.replace(
'''                animate={
                  prefersReducedMotion
                    ? undefined
                    : active
                      ? { y: [0, -5, 0], scale: [1, 1.012, 1] }
                      : undefined
                }''',
'''                animate={
                  prefersReducedMotion
                    ? undefined
                    : active
                      ? { y: [0, -5, 0], scale: [1, 1.012, 1], opacity: 1 }
                      : { y: 0, scale: 1, opacity: 1 }
                }''',
)

# Keep hover visible too.
text = text.replace(
    'whileHover={{ y: -6, scale: 1.012 }}',
    'whileHover={{ y: -6, scale: 1.012, opacity: 1 }}',
)

overview.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix7e_stable_overview_cards_no_fade")
