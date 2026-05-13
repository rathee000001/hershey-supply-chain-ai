from pathlib import Path
import re

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"

text = overlay.read_text(encoding="utf-8-sig")

# 1) Make sure the portal host is really the final top layer.
if "node.style.zIndex" in text:
    text = re.sub(
        r'node\.style\.zIndex\s*=\s*"[^"]+";',
        'node.style.zIndex = "2147483647";',
        text,
    )

if "node.style.mixBlendMode" not in text and "node.style.zIndex = \"2147483647\";" in text:
    text = text.replace(
        'node.style.zIndex = "2147483647";',
        'node.style.zIndex = "2147483647";\n    node.style.mixBlendMode = "normal";\n    node.style.transform = "translateZ(0)";',
    )

# 2) Add an explicit liquid layer that sits above the nav pills.
if "function ChocolateNavSpillLayer" not in text:
    insert_after = re.search(r"function ChocolatePortalLayer\(", text)
    if not insert_after:
        raise SystemExit("Could not find ChocolatePortalLayer. Open HeroChocolateMeltOverlay.tsx.")

    nav_layer = r'''
function ChocolateNavSpillLayer({
  scrollY,
  visible,
}: {
  scrollY: number;
  visible: boolean;
}) {
  /*
    This is not the main video. It is the top-compositor spill layer.
    Purpose: make chocolate visibly pass over the transparent navbar pills,
    because the green-screen video has transparent/cutout regions around that area.
  */
  return (
    <div
      className="pointer-events-none absolute left-0 top-0 w-screen"
      style={{
        height: 132,
        opacity: visible ? 1 : 0,
        transform: `translate3d(0, ${-scrollY}px, 0)`,
        zIndex: 3,
        contain: "layout paint style",
      }}
      data-hero-chocolate-nav-spill="above-navbar-pills"
      aria-hidden="true"
    >
      <motion.div
        className="absolute right-3 top-3 hidden h-[64px] rounded-full xl:block"
        style={{
          width: "min(720px, calc(100vw - 620px))",
          background:
            "linear-gradient(180deg, rgba(48,10,4,0.44), rgba(81,22,9,0.28) 42%, rgba(34,7,3,0.18) 100%)",
          boxShadow:
            "inset 0 2px 9px rgba(255,230,174,0.32), inset 0 -10px 22px rgba(32,5,2,0.34), 0 14px 38px rgba(62,18,8,0.12)",
          border: "1px solid rgba(94,30,13,0.18)",
          backdropFilter: "blur(2px) saturate(1.08)",
          WebkitBackdropFilter: "blur(2px) saturate(1.08)",
          mixBlendMode: "multiply",
        }}
        initial={{ opacity: 0, scaleX: 0.86, y: -5 }}
        animate={{ opacity: 1, scaleX: 1, y: 0 }}
        transition={{ duration: 1.25, ease: [0.18, 0.86, 0.26, 1] }}
      />

      <motion.div
        className="absolute right-[214px] top-[28px] hidden h-[56px] w-[26px] rounded-b-full rounded-t-[999px] xl:block"
        style={{
          background:
            "radial-gradient(circle at 45% 12%, rgba(255,221,150,0.38), transparent 16%), linear-gradient(180deg, rgba(59,13,5,0.7), rgba(96,27,10,0.42) 55%, rgba(39,8,3,0.16))",
          filter: "drop-shadow(0 12px 9px rgba(42,9,4,0.14))",
          mixBlendMode: "multiply",
        }}
        animate={{
          height: [42, 62, 50],
          y: [0, 4, 1],
          borderBottomLeftRadius: ["999px", "20px", "999px"],
          borderBottomRightRadius: ["999px", "20px", "999px"],
        }}
        transition={{
          duration: 5.8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute right-[42px] top-[18px] hidden h-[80px] w-[32px] rounded-b-full rounded-t-[999px] xl:block"
        style={{
          background:
            "radial-gradient(circle at 52% 10%, rgba(255,224,158,0.34), transparent 15%), linear-gradient(180deg, rgba(48,10,4,0.74), rgba(97,27,10,0.46) 50%, rgba(39,8,3,0.14))",
          filter: "drop-shadow(0 16px 12px rgba(42,9,4,0.16))",
          mixBlendMode: "multiply",
        }}
        animate={{
          height: [64, 92, 72],
          y: [0, 8, 2],
          opacity: [0.82, 1, 0.88],
        }}
        transition={{
          duration: 7.2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      <motion.div
        className="absolute right-8 top-4 hidden h-[60px] rounded-full xl:block"
        style={{
          width: "min(694px, calc(100vw - 646px))",
          background:
            "linear-gradient(100deg, transparent 0%, rgba(255,232,174,0.12) 20%, rgba(255,232,174,0.22) 38%, transparent 62%)",
          mixBlendMode: "screen",
          filter: "blur(1px)",
        }}
        animate={{ x: [-80, 120, -80], opacity: [0.18, 0.5, 0.18] }}
        transition={{ duration: 6.4, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

'''
    text = text[:insert_after.start()] + nav_layer + text[insert_after.start():]

# 3) Make the video layer itself lower than the nav-spill layer.
text = text.replace('data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"', 'data-hero-chocolate-melt-overlay="top-layer-video-plus-nav-spill-melt"')
text = text.replace('data-hero-chocolate-melt-overlay="top-layer-host-scrollaway-video-melt"', 'data-hero-chocolate-melt-overlay="top-layer-video-plus-nav-spill-melt"')

# 4) Insert ChocolateNavSpillLayer inside the portal returned markup.
if "<ChocolateNavSpillLayer" not in text:
    target = r'''      <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#170302]/10 via-transparent to-transparent" />'''
    if target not in text:
        raise SystemExit("Could not find portal overlay gradient insertion point.")

    text = text.replace(
        target,
        '''      <ChocolateNavSpillLayer scrollY={scrollY} visible={visible} />
''' + target,
        1,
    )

# 5) Ensure ChocolatePortalLayer receives scrollY + visible in scope; if already there this is no-op.
# 6) Reduce video opacity a little so the dedicated nav-spill does the navbar work.
text = re.sub(
    r'uOpacity:\s*\{\s*value:\s*reducedMotion\s*\?\s*0\.\d+\s*:\s*0\.\d+\s*\}',
    'uOpacity: { value: reducedMotion ? 0.72 : 0.88 }',
    text,
)

overlay.write_text(text, encoding="utf-8")
print("PATCH_APPLIED: step17e_b6g2a_r4_fix8_nav_spill_above_navbar")
