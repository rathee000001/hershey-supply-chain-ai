from pathlib import Path
import re

ROOT = Path.cwd()

overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
shell = ROOT / "src/components/cinematic/CinematicPageShell.tsx"
home = ROOT / "src/app/page.tsx"

overlay.write_text(r'''"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { motion, useReducedMotion } from "framer-motion";
import {
  type CSSProperties,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import * as THREE from "three";

const CHOCOLATE_VIDEO_SRC =
  "/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4";

const VIDEO_PLAYBACK_RATE = 0.68;
const FINAL_IDLE_LOOP_SECONDS = 1.45;

type PortalBox = {
  top: number;
  height: number;
  visible: boolean;
};

function useHeroAnchoredPortalBox(anchorRef: React.RefObject<HTMLDivElement | null>) {
  const [mounted, setMounted] = useState(false);
  const [box, setBox] = useState<PortalBox>({
    top: -52,
    height: 430,
    visible: false,
  });

  const syncBox = useCallback(() => {
    if (typeof window === "undefined") return;

    const anchor = anchorRef.current;
    if (!anchor) return;

    const rect = anchor.getBoundingClientRect();

    /*
      Portal is rendered into document.body for z-index control,
      but positioned absolute in document coordinates so it scrolls away
      with the first hero/container instead of covering the full site.
    */
    const top = Math.round(window.scrollY + rect.top - 54);

    /*
      Hero-only height. This prevents chocolate from covering overview,
      pipeline, sources, methodology, or later page content.
    */
    const height = Math.round(
      Math.min(460, Math.max(350, window.innerHeight * 0.42)),
    );

    setBox({
      top,
      height,
      visible: true,
    });
  }, [anchorRef]);

  useEffect(() => {
    setMounted(true);

    let frame = window.requestAnimationFrame(syncBox);

    const onResize = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(syncBox);
    };

    window.addEventListener("resize", onResize);
    window.addEventListener("load", onResize);

    /*
      Images/fonts can shift the first container after hydration.
      A short sync window keeps the portal aligned without attaching it
      to scroll position as fixed UI.
    */
    const interval = window.setInterval(syncBox, 500);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("load", onResize);
      window.clearInterval(interval);
    };
  }, [syncBox]);

  return { mounted, box };
}

function ChromaKeyChocolatePlane({
  texture,
  reducedMotion,
  idleMode,
}: {
  texture: THREE.VideoTexture;
  reducedMotion: boolean | null;
  idleMode: boolean;
}) {
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const { viewport, size } = useThree();

  const uniforms = useMemo(
    () => ({
      uTexture: { value: texture },
      uTime: { value: 0 },
      uIdleMode: { value: idleMode ? 1 : 0 },
      uOpacity: { value: reducedMotion ? 0.76 : 0.94 },
      uContainerAspect: { value: size.width / Math.max(size.height, 1) },
      uKeyColor: { value: new THREE.Color("#00ff00") },
      uSimilarity: { value: 0.245 },
      uSmoothness: { value: 0.145 },
      uSpill: { value: 0.94 },
      uContrast: { value: 1.64 },
      uSaturation: { value: 1.5 },
      uBrightness: { value: 0.86 },
      uGlossBoost: { value: 0.78 },
      uWarmth: { value: 0.36 },
      uDepth: { value: 0.26 },
    }),
    [texture, reducedMotion, size.width, size.height, idleMode],
  );

  useFrame(({ clock }) => {
    if (!materialRef.current) return;

    materialRef.current.uniforms.uTime.value = reducedMotion
      ? 1.2
      : clock.elapsedTime * 0.72;

    materialRef.current.uniforms.uContainerAspect.value =
      size.width / Math.max(size.height, 1);

    materialRef.current.uniforms.uIdleMode.value = idleMode ? 1 : 0;
  });

  return (
    <mesh position={[0, 0, 0]}>
      <planeGeometry args={[viewport.width, viewport.height, 1, 1]} />
      <shaderMaterial
        ref={materialRef}
        transparent
        depthWrite={false}
        depthTest={false}
        toneMapped={false}
        blending={THREE.NormalBlending}
        uniforms={uniforms}
        vertexShader={`
          varying vec2 vUv;

          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `}
        fragmentShader={`
          precision highp float;

          uniform sampler2D uTexture;
          uniform float uTime;
          uniform float uIdleMode;
          uniform float uOpacity;
          uniform float uContainerAspect;
          uniform vec3 uKeyColor;
          uniform float uSimilarity;
          uniform float uSmoothness;
          uniform float uSpill;
          uniform float uContrast;
          uniform float uSaturation;
          uniform float uBrightness;
          uniform float uGlossBoost;
          uniform float uWarmth;
          uniform float uDepth;

          varying vec2 vUv;

          vec2 chocolateVideoUv(vec2 uv) {
            /*
              Use the real video shape, but crop vertically so it remains
              a hero melt instead of a full-site curtain.
            */
            vec2 result = uv;
            result.y = mix(0.03, 0.88, uv.y);
            return result;
          }

          vec3 saturateColor(vec3 color, float amount) {
            float luma = dot(color, vec3(0.299, 0.587, 0.114));
            return mix(vec3(luma), color, amount);
          }

          vec3 contrastColor(vec3 color, float amount) {
            return (color - 0.5) * amount + 0.5;
          }

          float heroOnlyMask(vec2 uv) {
            /*
              Preserve top melted sheet + a controlled product-directed corridor.
              Do not allow full-page takeover.
            */
            float topMelt = smoothstep(0.58, 0.86, uv.y);

            float diagonalCenter = 0.78 - (uv.x * 0.28);
            float diagonalFlow = 1.0 - smoothstep(0.16, 0.42, abs(uv.y - diagonalCenter));
            diagonalFlow *= smoothstep(0.22, 0.52, uv.x);
            diagonalFlow *= 1.0 - smoothstep(0.9, 1.0, uv.x);

            float productApproach = 1.0 - smoothstep(0.06, 0.32, uv.y);
            productApproach *= smoothstep(0.46, 0.74, uv.x);
            productApproach *= 1.0 - smoothstep(0.94, 1.0, uv.x);

            return clamp(max(topMelt, max(diagonalFlow * 0.84, productApproach * 0.68)), 0.0, 1.0);
          }

          void main() {
            vec2 uv = chocolateVideoUv(vUv);

            if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
              discard;
            }

            vec4 tex = texture2D(uTexture, uv);
            vec3 rgb = tex.rgb;

            /*
              Runtime green-screen removal.
            */
            float chromaDistance = distance(rgb, uKeyColor);
            float baseAlpha = smoothstep(uSimilarity, uSimilarity + uSmoothness, chromaDistance);

            float greenDominance = max(rgb.g - max(rgb.r, rgb.b), 0.0);
            float greenCut = smoothstep(0.038, 0.3, greenDominance);
            float alpha = baseAlpha * (1.0 - greenCut * 0.975);

            rgb.g = mix(rgb.g, (rgb.r + rgb.b) * 0.38, greenCut * uSpill);

            /*
              Rich chocolate remap.
            */
            vec3 darkChocolate = vec3(0.052, 0.011, 0.006);
            vec3 deepMaroon = vec3(0.18, 0.043, 0.018);
            vec3 warmChocolate = vec3(0.34, 0.086, 0.034);
            vec3 goldenSpecular = vec3(1.0, 0.78, 0.42);

            float luminance = dot(rgb, vec3(0.299, 0.587, 0.114));
            vec3 chocolateRamp = mix(darkChocolate, warmChocolate, smoothstep(0.05, 0.64, luminance));
            chocolateRamp = mix(chocolateRamp, deepMaroon, smoothstep(0.1, 0.38, luminance) * 0.42);

            rgb = mix(rgb, chocolateRamp, uWarmth);
            rgb = contrastColor(rgb, uContrast);
            rgb = saturateColor(rgb, uSaturation);
            rgb *= uBrightness;

            /*
              Moving wet gloss so it feels like liquid, not a flat video layer.
            */
            float glossA = sin((uv.x * 19.0) - (uTime * 1.45)) * 0.5 + 0.5;
            float glossB = sin(((uv.x * 0.8 + uv.y * 1.25) * 29.0) + (uTime * 1.06)) * 0.5 + 0.5;
            float glossC = sin(((uv.x - uv.y) * 17.0) - (uTime * 0.82)) * 0.5 + 0.5;

            float wetGloss =
              pow(glossA, 11.0) * 0.28 +
              pow(glossB, 14.0) * 0.24 +
              pow(glossC, 9.0) * 0.16;

            float navBand = smoothstep(0.72, 0.96, vUv.y);
            float lowerDepth = smoothstep(0.24, 0.8, 1.0 - uv.y);

            rgb = mix(rgb, darkChocolate, uDepth * lowerDepth);
            rgb += goldenSpecular * wetGloss * uGlossBoost * max(navBand * 0.72, heroOnlyMask(vUv));

            /*
              Let chocolate flow visibly over transparent nav pills,
              but soften enough that labels remain readable.
            */
            float navReadability = mix(1.0, 0.72, navBand);

            /*
              The key scope rule: top/hero only.
              This fades out before lower homepage sections.
            */
            float heroBottomFade = 1.0 - smoothstep(0.72, 0.98, vUv.y);
            float topFade = smoothstep(0.0, 0.025, uv.y);
            float pathMask = heroOnlyMask(vUv);

            gl_FragColor = vec4(
              rgb,
              alpha * uOpacity * navReadability * heroBottomFade * topFade * pathMask
            );
          }
        `}
      />
    </mesh>
  );
}

function ChocolateVideoShaderLayer({
  reducedMotion,
}: {
  reducedMotion: boolean | null;
}) {
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const [idleMode, setIdleMode] = useState(false);

  useEffect(() => {
    const video = document.createElement("video");

    video.src = CHOCOLATE_VIDEO_SRC;
    video.muted = true;
    video.loop = false;
    video.playsInline = true;
    video.autoplay = true;
    video.preload = "auto";
    video.crossOrigin = "anonymous";
    video.playbackRate = VIDEO_PLAYBACK_RATE;

    const videoTexture = new THREE.VideoTexture(video);
    videoTexture.colorSpace = THREE.SRGBColorSpace;
    videoTexture.minFilter = THREE.LinearFilter;
    videoTexture.magFilter = THREE.LinearFilter;
    videoTexture.generateMipmaps = false;
    videoTexture.needsUpdate = true;

    setTexture(videoTexture);

    const startPlayback = async () => {
      try {
        video.playbackRate = VIDEO_PLAYBACK_RATE;
        await video.play();
      } catch {
        /*
          Muted + playsInline normally allows autoplay.
          If a browser blocks it, the first user interaction will resume it.
        */
      }
    };

    const onCanPlay = () => {
      void startPlayback();
    };

    const onTimeUpdate = () => {
      if (!Number.isFinite(video.duration)) return;
      if (video.duration <= FINAL_IDLE_LOOP_SECONDS + 0.4) return;

      const idleStart = Math.max(video.duration - FINAL_IDLE_LOOP_SECONDS, 0);

      /*
        Play the entrance once, then loop only the final liquid state.
        This prevents the ugly restart-from-zero behavior.
      */
      if (video.currentTime >= video.duration - 0.08) {
        setIdleMode(true);
        video.currentTime = idleStart;
        void video.play();
      }
    };

    video.addEventListener("canplay", onCanPlay, { once: true });
    video.addEventListener("timeupdate", onTimeUpdate);
    video.load();

    return () => {
      video.pause();
      video.removeEventListener("canplay", onCanPlay);
      video.removeEventListener("timeupdate", onTimeUpdate);
      video.removeAttribute("src");
      video.load();
      videoTexture.dispose();
    };
  }, []);

  if (!texture) return null;

  return (
    <ChromaKeyChocolatePlane
      texture={texture}
      reducedMotion={reducedMotion}
      idleMode={idleMode}
    />
  );
}

function ChocolatePortalLayer({
  box,
  reducedMotion,
}: {
  box: PortalBox;
  reducedMotion: boolean | null;
}) {
  const portalStyle: CSSProperties = {
    position: "absolute",
    left: 0,
    top: `${box.top}px`,
    width: "100vw",
    height: `${box.height}px`,
    zIndex: 2147483000,
    pointerEvents: "none",
    overflow: "hidden",
    opacity: box.visible ? 1 : 0,
    contain: "layout paint style",
  };

  return (
    <div
      style={portalStyle}
      aria-hidden="true"
      data-hero-chocolate-melt-overlay="portal-absolute-hero-scoped-video-melt"
    >
      <motion.div
        className="absolute inset-x-0 top-0 h-full"
        initial={
          reducedMotion
            ? false
            : {
                opacity: 0,
                y: -36,
              }
        }
        animate={
          reducedMotion
            ? undefined
            : {
                opacity: 1,
                y: 0,
              }
        }
        transition={{
          duration: 2.6,
          ease: [0.18, 0.86, 0.26, 1],
        }}
      >
        <Canvas
          className="absolute inset-0 h-full w-full"
          orthographic
          camera={{ position: [0, 0, 5], zoom: 100 }}
          gl={{
            alpha: true,
            antialias: true,
            premultipliedAlpha: false,
            powerPreference: "high-performance",
          }}
        >
          <ChocolateVideoShaderLayer reducedMotion={reducedMotion} />
        </Canvas>
      </motion.div>

      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-[#170302]/16 via-transparent to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent via-[#fff8ee]/18 to-[#fff8ee]/0" />
    </div>
  );
}

export default function HeroChocolateMeltOverlay() {
  const anchorRef = useRef<HTMLDivElement | null>(null);
  const prefersReducedMotion = useReducedMotion();
  const { mounted, box } = useHeroAnchoredPortalBox(anchorRef);

  return (
    <>
      <div
        ref={anchorRef}
        className="pointer-events-none h-0 w-0 overflow-hidden"
        aria-hidden="true"
        data-hero-chocolate-anchor="first-container-scope"
      />

      {mounted
        ? createPortal(
            <ChocolatePortalLayer box={box} reducedMotion={prefersReducedMotion} />,
            document.body,
          )
        : null}
    </>
  );
}
''', encoding="utf-8")

# Make the chocolate overlay global through CinematicPageShell.
if shell.exists():
    shell_text = shell.read_text(encoding="utf-8-sig")
    import_line = 'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";'

    if import_line not in shell_text:
        imports = list(re.finditer(r"^import .+;$", shell_text, flags=re.MULTILINE))
        if imports:
            last_import = imports[-1]
            shell_text = shell_text[:last_import.end()] + "\n" + import_line + shell_text[last_import.end():]
        else:
            shell_text = import_line + "\n" + shell_text

    if "<HeroChocolateMeltOverlay />" not in shell_text:
        # Best placement: directly after navbar so anchor begins at first page container.
        replaced = False

        navbar_self_closing = re.compile(r"(<CinematicNavbar\b[^>]*\/>)", flags=re.DOTALL)
        if navbar_self_closing.search(shell_text):
            shell_text = navbar_self_closing.sub(r"\1\n      <HeroChocolateMeltOverlay />", shell_text, count=1)
            replaced = True

        if not replaced:
            navbar_pair = re.compile(r"(<CinematicNavbar\b[^>]*>.*?</CinematicNavbar>)", flags=re.DOTALL)
            if navbar_pair.search(shell_text):
                shell_text = navbar_pair.sub(r"\1\n      <HeroChocolateMeltOverlay />", shell_text, count=1)
                replaced = True

        if not replaced:
            shell_text = shell_text.replace("return (", "return (\n    <>\n      <HeroChocolateMeltOverlay />", 1)
            shell_text = shell_text.replace("\n  );", "\n    </>\n  );", 1)

    shell.write_text(shell_text, encoding="utf-8")

# Remove homepage-only duplicate if present.
if home.exists():
    home_text = home.read_text(encoding="utf-8-sig")
    home_text = home_text.replace(
        'import HeroChocolateMeltOverlay from "@/components/cinematic/HeroChocolateMeltOverlay";\n',
        "",
    )
    home_text = home_text.replace("      <HeroChocolateMeltOverlay />\n", "")
    home_text = home_text.replace("    <HeroChocolateMeltOverlay />\n", "")
    home.write_text(home_text, encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_r4_fix4_portal_absolute_hero_scoped_melt")
