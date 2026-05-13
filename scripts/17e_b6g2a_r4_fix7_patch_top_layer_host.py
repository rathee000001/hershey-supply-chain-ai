from pathlib import Path
import re

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"

text = overlay.read_text(encoding="utf-8-sig")

if "useChocolateTopLayerHost" not in text:
    marker = "const FINAL_IDLE_LOOP_SECONDS = 1.35;"
    if marker not in text:
        raise SystemExit("Could not find FIX6 marker. Stop and open HeroChocolateMeltOverlay.tsx.")

    insert = r'''
function useChocolateTopLayerHost() {
  const [host, setHost] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const hostId = "hero-chocolate-melt-top-layer-host";
    let node = document.getElementById(hostId) as HTMLElement | null;
    let created = false;

    if (!node) {
      node = document.createElement("div");
      node.id = hostId;
      node.setAttribute("data-hero-chocolate-top-layer-host", "true");
      document.body.appendChild(node);
      created = true;
    }

    /*
      Critical stacking fix:
      The old portal rendered into body, but could still sit below app/nav stacking
      contexts. This host is a dedicated final body child with maximum z-index.
    */
    node.style.position = "fixed";
    node.style.inset = "0";
    node.style.width = "100vw";
    node.style.height = "100vh";
    node.style.pointerEvents = "none";
    node.style.zIndex = "2147483647";
    node.style.isolation = "isolate";
    node.style.contain = "layout paint style";
    node.style.overflow = "visible";

    setHost(node);

    return () => {
      if (created && node && node.parentNode) {
        node.parentNode.removeChild(node);
      }
    };
  }, []);

  return host;
}
'''
    text = text.replace(marker, marker + "\n" + insert)

# Portal child should be absolute inside the max-z fixed host.
text = text.replace('position: "fixed",', 'position: "absolute",')
text = text.replace('zIndex: 2147483000,', 'zIndex: 1,')
text = text.replace('zIndex: 2147483647,', 'zIndex: 1,')

# Add top-layer marker to existing overlay data attribute.
text = text.replace(
    'data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"',
    'data-hero-chocolate-melt-overlay="top-layer-host-scrollaway-video-melt"'
)

# Replace default export portal target.
pattern = re.compile(
    r'''export default function HeroChocolateMeltOverlay\(\) \{\s*
  const prefersReducedMotion = useReducedMotion\(\);\s*
  const \{ mounted, height, scrollY, visible \} = useHeroTopScrollAwayBox\(\);\s*

  if \(!mounted\) return null;\s*

  return createPortal\(\s*
    <ChocolatePortalLayer\s*
      height=\{height\}\s*
      scrollY=\{scrollY\}\s*
      visible=\{visible\}\s*
      reducedMotion=\{prefersReducedMotion\}\s*
    />,\s*
    document\.body,\s*
  \);\s*
\}''',
    re.DOTALL
)

replacement = r'''export default function HeroChocolateMeltOverlay() {
  const prefersReducedMotion = useReducedMotion();
  const { mounted, height, scrollY, visible } = useHeroTopScrollAwayBox();
  const host = useChocolateTopLayerHost();

  if (!mounted || !host) return null;

  return createPortal(
    <ChocolatePortalLayer
      height={height}
      scrollY={scrollY}
      visible={visible}
      reducedMotion={prefersReducedMotion}
    />,
    host,
  );
}'''

if not pattern.search(text):
    raise SystemExit("Could not replace default export safely. Open HeroChocolateMeltOverlay.tsx and inspect.")

text = pattern.sub(replacement, text)

overlay.write_text(text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_r4_fix7_top_layer_host")
