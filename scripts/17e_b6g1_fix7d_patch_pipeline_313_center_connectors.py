from pathlib import Path
import re

ROOT = Path.cwd()
pipeline = ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx"

text = pipeline.read_text(encoding="utf-8")

# 3 / 1 / 3 layout, pulled inward so no card leaves the panel.
# Card width is patched to 188px, so center points are:
# top:    (124,106) -> (360,106) -> (596,106)
# middle:                         (360,314)
# bottom: (124,522) -> (360,522) -> (596,522)
text = re.sub(
    r'const nodePositions = \[[\s\S]*?\];',
'''const nodePositions = [
  { left: 30, top: 42 },
  { left: 266, top: 42 },
  { left: 502, top: 42 },
  { left: 266, top: 250 },
  { left: 30, top: 458 },
  { left: 266, top: 458 },
  { left: 502, top: 458 },
];''',
    text,
    count=1,
)

# Direct center-to-center connector paths.
text = re.sub(
    r'const routePaths: RoutePath\[\] = \[[\s\S]*?\];',
'''const routePaths: RoutePath[] = [
  { id: "sources-parser", d: "M 124 106 C 218 106, 266 106, 360 106", accent: "#1f62ff", soft: "rgba(31,98,255,0.50)" },
  { id: "parser-rag", d: "M 360 106 C 454 106, 502 106, 596 106", accent: "#d6a526", soft: "rgba(216,165,38,0.54)" },
  { id: "rag-audit", d: "M 596 106 C 596 210, 470 248, 360 314", accent: "#9b5cf6", soft: "rgba(155,92,246,0.50)" },
  { id: "audit-packets", d: "M 360 314 C 248 382, 124 424, 124 522", accent: "#0f9f6e", soft: "rgba(15,159,110,0.50)" },
  { id: "packets-cost", d: "M 124 522 C 218 522, 266 522, 360 522", accent: "#7b2a15", soft: "rgba(123,42,21,0.48)" },
  { id: "cost-frontend", d: "M 360 522 C 454 522, 502 522, 596 522", accent: "#38bdf8", soft: "rgba(56,189,248,0.54)" },
];''',
    text,
    count=1,
)

text = text.replace(
    'data-home-intelligence-pipeline="three-one-three-direct-pulsing-connectors"',
    'data-home-intelligence-pipeline="contained-three-one-three-center-pulsing-connectors"',
)

text = text.replace(
    'data-home-intelligence-pipeline="absolute-card-map-direct-pulsing-connectors"',
    'data-home-intelligence-pipeline="contained-three-one-three-center-pulsing-connectors"',
)

# Give enough vertical room, keep the right map clean.
text = text.replace(
    'className="relative min-h-[680px] rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/88 p-5 shadow-inner shadow-slate-200/60"',
    'className="relative min-h-[710px] overflow-hidden rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/88 p-5 shadow-inner shadow-slate-200/60"',
)

text = text.replace(
    'className="relative min-h-[650px] rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/84 p-5 shadow-inner shadow-slate-200/60"',
    'className="relative min-h-[710px] overflow-hidden rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/88 p-5 shadow-inner shadow-slate-200/60"',
)

text = text.replace(
    'className="relative z-10 hidden h-[590px] w-full sm:block"',
    'className="relative z-10 mx-auto hidden h-[610px] w-full max-w-[720px] sm:block"',
)

text = text.replace(
    'className="relative z-10 hidden h-[560px] w-full sm:block"',
    'className="relative z-10 mx-auto hidden h-[610px] w-full max-w-[720px] sm:block"',
)

text = text.replace(
    'viewBox="0 0 760 560"',
    'viewBox="0 0 720 610"',
)

text = text.replace(
    'viewBox="0 0 760 430"',
    'viewBox="0 0 720 610"',
)

# Make connectors clearer but not huge blobs.
text = text.replace(
    'strokeWidth="8"',
    'strokeWidth="6"',
)

text = text.replace(
    'strokeWidth="7"',
    'strokeWidth="6"',
)

text = text.replace(
    'opacity="0.92"',
    'opacity="0.82"',
)

text = text.replace(
    'opacity="0.78"',
    'opacity="0.82"',
)

text = text.replace(
    'strokeWidth={routeIsActive ? "8" : "6"}',
    'strokeWidth={routeIsActive ? "6.5" : "5"}',
)

text = text.replace(
    'strokeWidth={routeIsActive ? "7" : "5.5"}',
    'strokeWidth={routeIsActive ? "6.5" : "5"}',
)

text = text.replace(
    'strokeDasharray="72 340"',
    'strokeDasharray="64 300"',
)

text = text.replace(
    'strokeDasharray="58 380"',
    'strokeDasharray="64 300"',
)

text = text.replace(
    'strokeDashoffset: 340',
    'strokeDashoffset: 300',
)

text = text.replace(
    'strokeDashoffset: 380',
    'strokeDashoffset: 300',
)

text = text.replace(
    'strokeDashoffset: [340, 0]',
    'strokeDashoffset: [300, 0]',
)

text = text.replace(
    'strokeDashoffset: [380, 0]',
    'strokeDashoffset: [300, 0]',
)

text = text.replace(
    'duration: 2.7 + index * 0.14',
    'duration: 2.55 + index * 0.12',
)

text = text.replace(
    'duration: 3.2 + index * 0.16',
    'duration: 2.55 + index * 0.12',
)

# Shrink card width slightly so right-side cards stay inside the panel.
text = text.replace(
    'absolute w-[205px]',
    'absolute w-[188px]',
)

# Make every card stable/visible. No fading card nodes.
text = text.replace(
    'initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}',
    'initial={false}',
)

text = text.replace(
    'whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}',
    '',
)

text = text.replace(
    'viewport={{ once: true, margin: "-70px" }}',
    '',
)

text = text.replace(
    '"group min-h-[128px] rounded-[1.6rem] border p-4 text-left shadow-lg shadow-slate-200/50 ring-1 ring-transparent transition duration-300 hover:ring-[#d6a526]/25",',
    '"group min-h-[128px] rounded-[1.6rem] border p-4 text-left opacity-100 shadow-lg shadow-slate-200/50 ring-1 ring-transparent transition duration-300 hover:ring-[#d6a526]/25",',
)

# If opacity was not already forced in inline style, add it.
if "opacity: 1," not in text:
    text = text.replace(
        'boxShadow: active ? `0 22px 48px ${step.soft}` : undefined,',
        'boxShadow: active ? `0 22px 48px ${step.soft}` : undefined,\n        opacity: 1,',
    )

pipeline.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix7d_pipeline_313_center_connectors")
