from pathlib import Path
import re

ROOT = Path.cwd()

field = ROOT / "src/components/hershey3d/home/HersheySupplyChainFieldScene.tsx"
pipeline = ROOT / "src/components/home/HomeIntelligencePipelineMap.tsx"

field_text = field.read_text(encoding="utf-8")
pipeline_text = pipeline.read_text(encoding="utf-8")

# -----------------------------
# 1) 3D field: bigger, still right-side background only
# -----------------------------
field_text = field_text.replace(
    'pointer-events-none fixed inset-y-0 right-0 z-0 hidden w-[32vw] min-w-[390px] overflow-visible lg:block',
    'pointer-events-none fixed inset-y-0 right-[-2vw] z-0 hidden w-[36vw] min-w-[460px] overflow-visible lg:block',
)

field_text = field_text.replace(
    'camera={{ position: [0, 0, 6.4], fov: 34 }}',
    'camera={{ position: [0, 0, 6.15], fov: 35 }}',
)

field_text = field_text.replace(
    'position={[0.42, 0.08, 0]}',
    'position={[0.3, 0.08, 0]}',
)

field_text = field_text.replace(
    'scale={0.78}',
    'scale={0.9}',
)

field_text = field_text.replace(
    'data-hershey-home-background="portfolio-right-background-funnel"',
    'data-hershey-home-background="portfolio-right-background-funnel-bigger-solid-core"',
)

field_text = field_text.replace(
    'data-hershey-scene-world="portfolio-right-background-funnel"',
    'data-hershey-scene-world="portfolio-right-background-funnel-bigger-solid-core"',
)

# Make center sphere solid and larger.
field_text = field_text.replace(
    '<sphereGeometry args={[0.24, 56, 56]} />',
    '<sphereGeometry args={[0.31, 64, 64]} />',
)

field_text = field_text.replace(
'''<meshStandardMaterial
              color="#d8a533"
              emissive="#d8a533"
              emissiveIntensity={0.38}
              metalness={0.66}
              roughness={0.18}
              transparent
              opacity={0.78}
            />''',
'''<meshStandardMaterial
              color="#d8a533"
              emissive="#a66f10"
              emissiveIntensity={0.18}
              metalness={0.58}
              roughness={0.2}
            />''',
)

# Add small surface color-variance points that revolve with the solid core group.
if 'data-solid-core-color-variance="true"' not in field_text:
    field_text = field_text.replace(
'''          <mesh rotation={[Math.PI / 2.35, 0, 0]}>
            <torusGeometry args={[0.56, 0.006, 18, 150]} />''',
'''          <group data-solid-core-color-variance="true">
            <mesh position={[0.09, 0.13, 0.27]}>
              <sphereGeometry args={[0.038, 18, 18]} />
              <meshStandardMaterial color="#fff1d0" emissive="#fff1d0" emissiveIntensity={0.22} roughness={0.18} metalness={0.35} />
            </mesh>

            <mesh position={[-0.18, -0.07, 0.23]}>
              <sphereGeometry args={[0.032, 18, 18]} />
              <meshStandardMaterial color="#7b2a15" emissive="#7b2a15" emissiveIntensity={0.12} roughness={0.22} metalness={0.28} />
            </mesh>

            <mesh position={[0.19, -0.16, -0.19]}>
              <sphereGeometry args={[0.03, 18, 18]} />
              <meshStandardMaterial color="#f4c75d" emissive="#f4c75d" emissiveIntensity={0.18} roughness={0.2} metalness={0.3} />
            </mesh>
          </group>

          <mesh rotation={[Math.PI / 2.35, 0, 0]}>
            <torusGeometry args={[0.66, 0.006, 18, 150]} />''',
    )

# Slightly enlarge orbit rings after sphere grows.
field_text = field_text.replace(
    '<torusGeometry args={[0.82, 0.0045, 18, 160]} />',
    '<torusGeometry args={[0.94, 0.0045, 18, 160]} />',
)

# -----------------------------
# 2) Pipeline: 3 / 1 / 3 layout with direct pulsing lines
# -----------------------------
pipeline_text = re.sub(
    r'const nodePositions = \[[\s\S]*?\];',
'''const nodePositions = [
  { left: 42, top: 42 },
  { left: 278, top: 42 },
  { left: 514, top: 42 },
  { left: 278, top: 246 },
  { left: 42, top: 448 },
  { left: 278, top: 448 },
  { left: 514, top: 448 },
];''',
    pipeline_text,
    count=1,
)

pipeline_text = re.sub(
    r'const routePaths: RoutePath\[\] = \[[\s\S]*?\];',
'''const routePaths: RoutePath[] = [
  { id: "sources-parser", d: "M 247 108 C 258 108, 267 108, 278 108", accent: "#1f62ff", soft: "rgba(31,98,255,0.48)" },
  { id: "parser-rag", d: "M 483 108 C 494 108, 503 108, 514 108", accent: "#d6a526", soft: "rgba(216,165,38,0.52)" },
  { id: "rag-audit", d: "M 616 172 C 616 226, 456 214, 380 246", accent: "#9b5cf6", soft: "rgba(155,92,246,0.46)" },
  { id: "audit-packets", d: "M 336 374 C 278 410, 204 430, 144 448", accent: "#0f9f6e", soft: "rgba(15,159,110,0.46)" },
  { id: "packets-cost", d: "M 247 514 C 258 514, 267 514, 278 514", accent: "#7b2a15", soft: "rgba(123,42,21,0.44)" },
  { id: "cost-frontend", d: "M 483 514 C 494 514, 503 514, 514 514", accent: "#38bdf8", soft: "rgba(56,189,248,0.52)" },
];''',
    pipeline_text,
    count=1,
)

pipeline_text = pipeline_text.replace(
    'data-home-intelligence-pipeline="absolute-card-map-direct-pulsing-connectors"',
    'data-home-intelligence-pipeline="three-one-three-direct-pulsing-connectors"',
)

pipeline_text = pipeline_text.replace(
    'className="relative min-h-[650px] rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/84 p-5 shadow-inner shadow-slate-200/60"',
    'className="relative min-h-[680px] rounded-[2.25rem] border border-[#2a0805]/10 bg-[#f9fbff]/88 p-5 shadow-inner shadow-slate-200/60"',
)

pipeline_text = pipeline_text.replace(
    'className="relative z-10 hidden h-[560px] w-full sm:block"',
    'className="relative z-10 hidden h-[590px] w-full sm:block"',
)

# Stronger base and pulse lines.
pipeline_text = pipeline_text.replace(
    'strokeWidth="7"',
    'strokeWidth="8"',
)

pipeline_text = pipeline_text.replace(
    'opacity="0.78"',
    'opacity="0.92"',
)

pipeline_text = pipeline_text.replace(
    'strokeWidth={routeIsActive ? "7" : "5.5"}',
    'strokeWidth={routeIsActive ? "8" : "6"}',
)

pipeline_text = pipeline_text.replace(
    'strokeDasharray="58 380"',
    'strokeDasharray="72 340"',
)

pipeline_text = pipeline_text.replace(
    'strokeDashoffset: 380',
    'strokeDashoffset: 340',
)

pipeline_text = pipeline_text.replace(
    'strokeDashoffset: [380, 0]',
    'strokeDashoffset: [340, 0]',
)

pipeline_text = pipeline_text.replace(
    'duration: 3.2 + index * 0.16',
    'duration: 2.7 + index * 0.14',
)

# Prevent Sources/Public Evidence card disappearance: no whileInView opacity hiding on map nodes.
pipeline_text = pipeline_text.replace(
'''      initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
      whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
      animate=''', 
'''      initial={false}
      animate=''',
)

pipeline_text = pipeline_text.replace(
    'viewport={{ once: true, margin: "-70px" }}\n',
    '',
)

pipeline_text = pipeline_text.replace(
    '"group min-h-[128px] rounded-[1.6rem] border p-4 text-left shadow-lg shadow-slate-200/50 ring-1 ring-transparent transition duration-300 hover:ring-[#d6a526]/25",',
    '"group min-h-[128px] rounded-[1.6rem] border p-4 text-left opacity-100 shadow-lg shadow-slate-200/50 ring-1 ring-transparent transition duration-300 hover:ring-[#d6a526]/25",',
)

pipeline_text = pipeline_text.replace(
    'boxShadow: active ? `0 22px 48px ${step.soft}` : undefined,',
    'boxShadow: active ? `0 22px 48px ${step.soft}` : undefined,\n        opacity: 1,',
)

field.write_text(field_text, encoding="utf-8")
pipeline.write_text(pipeline_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g1_fix7c_bigger_3d_stable_313_pipeline")
