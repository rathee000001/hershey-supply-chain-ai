from pathlib import Path
import re

ROOT = Path.cwd()

overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"
shell = ROOT / "src/components/cinematic/CinematicPageShell.tsx"
home = ROOT / "src/app/page.tsx"

overlay.write_text(r'''"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { motion, useReducedMotion } from "framer-motion";
import { type CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import * as THREE from "three";

const CHOCOLATE_VIDEO_SRC =
  "/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4";

const VIDEO_PLAYBACK_RATE = 0.78;
const FINAL_IDLE_LOOP_SECONDS = 1.35;

function useHeroTopScrollAwayBox() {
  const [mounted, setMounted] = useState(false);
  const [state, setState] = useState({
    height: 430,
    scrollY: 0,
    visible: true,
  });

  useEffect(() => {
    setMounted(true);

    let raf = 0;

    const sync = () => {
      window.cancelAnimationFrame(raf);

      raf = window.requestAnimationFrame(() => {
        const height = Math.round(
          Math.min(470, Math.max(380, window.innerHeight * 0.44)),
        );

        const scrollY = window.scrollY || 0;

        /*
          This is the corrected behavior:
          - portal is fixed for z-index and navbar-overflow correctness
          - transform moves it upward with scroll
          - after hero zone it is hidden, so it does not cover the whole site
        */
        setState({
          height,
          scrollY,
          visible: scrollY < height + 90,
        });
      });
    };

    sync();

    window.addEventListener("scroll", sync, { passive: true });
    window.addEventListener("resize", sync);
    window.addEventListener("load", sync);

    return () => {
      window.cancelAnimationFrame(raf);
      window.removeEventListener("scroll", sync);
      window.removeEventListener("resize", sync);
      window.removeEventListener("load", sync);
    };
  }, []);

  return { mounted, ...state };
}

function ChocolateShaderPlane({
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
      uOpacity: { value: reducedMotion ? 0.74 : 0.92 },
      uContainerAspect: { value: size.width / Math.max(size.height, 1) },
      uKeyColor: { value: new THREE.Color("#00ff00") },
      uSimilarity: { value: 0.24 },
      uSmoothness: { value: 0.15 },
      uSpill: { value: 0.92 },
      uContrast: { value: 1.58 },
      uSaturation: { value: 1.44 },
      uBrightness: { value: 0.88 },
      uGlossBoost: { value: 0.66 },
      uWarmth: { value: 0.34 },
      uDepth: { value: 0.22 },
    }),
    [texture, reducedMotion, size.width, size.height, idleMode],
  );

  useFrame(({ clock }) => {
    if (!materialRef.current) return;

    materialRef.current.uniforms.uTime.value = reducedMotion
      ? 1.0
      : clock.elapsedTime * 0.8;

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
              Rollback correction:
              do not over-mask or anchor low.
              Use the real video from the top so the chocolate starts at page top.
            */
            vec2 result = uv;
            result.y = mix(0.0, 0.94, uv.y);
            return result;
          }

          vec3 saturateColor(vec3 color, float amount) {
            float luma = dot(color, vec3(0.299, 0.587, 0.114));
            return mix(vec3(luma), color, amount);
          }

          vec3 contrastColor(vec3 color, float amount) {
            return (color - 0.5) * amount + 0.5;
          }

          void main() {
            vec2 uv = chocolateVideoUv(vUv);

            if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
              discard;
            }

            vec4 tex = texture2D(uTexture, uv);
            vec3 rgb = tex.rgb;

            /*
              Green-screen removal.
            */
            float chromaDistance = distance(rgb, uKeyColor);
            float baseAlpha = smoothstep(uSimilarity, uSimilarity + uSmoothness, chromaDistance);

            float greenDominance = max(rgb.g - max(rgb.r, rgb.b), 0.0);
            float greenCut = smoothstep(0.04, 0.31, greenDominance);
            float alpha = baseAlpha * (1.0 - greenCut * 0.97);

            rgb.g = mix(rgb.g, (rgb.r + rgb.b) * 0.4, greenCut * uSpill);

            /*
              Rich chocolate remap.
            */
            vec3 darkChocolate = vec3(0.052, 0.012, 0.006);
            vec3 deepBrown = vec3(0.18, 0.043, 0.018);
            vec3 warmChocolate = vec3(0.34, 0.086, 0.034);
            vec3 goldenSpecular = vec3(1.0, 0.78, 0.42);

            float luminance = dot(rgb, vec3(0.299, 0.587, 0.114));
            vec3 chocolateRamp = mix(darkChocolate, warmChocolate, smoothstep(0.05, 0.62, luminance));
            chocolateRamp = mix(chocolateRamp, deepBrown, smoothstep(0.08, 0.38, luminance) * 0.38);

            rgb = mix(rgb, chocolateRamp, uWarmth);
            rgb = contrastColor(rgb, uContrast);
            rgb = saturateColor(rgb, uSaturation);
            rgb *= uBrightness;

            /*
              Soft 3D-style gloss movement.
            */
            float glossA = sin((uv.x * 18.0) - (uTime * 1.35)) * 0.5 + 0.5;
            float glossB = sin(((uv.x * 0.9 + uv.y * 1.2) * 28.0) + (uTime * 1.0)) * 0.5 + 0.5;
            float wetGloss = pow(glossA, 11.0) * 0.26 + pow(glossB, 14.0) * 0.22;

            float navBand = smoothstep(0.74, 0.98, vUv.y);
            float lowerDepth = smoothstep(0.2, 0.86, 1.0 - uv.y);

            rgb = mix(rgb, darkChocolate, uDepth * lowerDepth);
            rgb += goldenSpecular * wetGloss * uGlossBoost * max(navBand, 0.35);

            /*
              Hero scope:
              visible at top and over nav/product hero, then fades out before lower sections.
            */
            float bottomFade = 1.0 - smoothstep(0.02, 0.2, vUv.y);
            float topFade = smoothstep(0.0, 0.012, uv.y);

            /*
              Let it pass over navbar visually, but keep nav readable.
            */
            float navReadability = mix(1.0, 0.76, navBand);

            gl_FragColor = vec4(
              rgb,
              alpha * uOpacity * bottomFade * topFade * navReadability
            );
          }
        `}
      />
    </mesh>
  );
}

function ChocolateVideoLayer({ reducedMotion }: { reducedMotion: boolean | null }) {
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
          Muted autoplay normally works. If blocked, user interaction resumes it.
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
    <ChocolateShaderPlane
      texture={texture}
      reducedMotion={reducedMotion}
      idleMode={idleMode}
    />
  );
}

function ChocolatePortalLayer({
  height,
  scrollY,
  visible,
  reducedMotion,
}: {
  height: number;
  scrollY: number;
  visible: boolean;
  reducedMotion: boolean | null;
}) {
  const portalStyle: CSSProperties = {
    position: "fixed",
    left: 0,
    top: 0,
    width: "100vw",
    height: `${height}px`,
    transform: `translate3d(0, ${-scrollY}px, 0)`,
    zIndex: 2147483000,
    pointerEvents: "none",
    overflow: "hidden",
    opacity: visible ? 1 : 0,
    contain: "layout paint style",
    transition: "opacity 240ms ease",
  };

  return (
    <div
      style={portalStyle}
      aria-hidden="true"
      data-hero-chocolate-melt-overlay="rollback-fixed-scrollaway-top-video-melt"
    >
      <motion.div
        className="absolute inset-x-0 top-0 h-full"
        initial={
          reducedMotion
            ? false
            : {
                opacity: 0,
                y: -10,
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
          duration: 1.4,
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
          <ChocolateVideoLayer reducedMotion={reducedMotion} />
        </Canvas>
      </motion.div>

      <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#170302]/10 via-transparent to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-b from-transparent via-[#fff8ee]/16 to-[#fff8ee]/0" />
    </div>
  );
}

export default function HeroChocolateMeltOverlay() {
  const prefersReducedMotion = useReducedMotion();
  const { mounted, height, scrollY, visible } = useHeroTopScrollAwayBox();

  if (!mounted) return null;

  return createPortal(
    <ChocolatePortalLayer
      height={height}
      scrollY={scrollY}
      visible={visible}
      reducedMotion={prefersReducedMotion}
    />,
    document.body,
  );
}
''', encoding="utf-8")

# Ensure global shell layer exists exactly once.
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

    # Remove duplicates first.
    shell_text = re.sub(r"\n\s*<HeroChocolateMeltOverlay\s*/>", "", shell_text)

    navbar_self_closing = re.compile(r"(<CinematicNavbar\b[^>]*\/>)", flags=re.DOTALL)
    if navbar_self_closing.search(shell_text):
        shell_text = navbar_self_closing.sub(r"\1\n      <HeroChocolateMeltOverlay />", shell_text, count=1)
    else:
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

print("PATCH_APPLIED: step17e_b6g2a_r4_fix6_rollback_fixed_scrollaway_top_melt")
