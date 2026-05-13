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

const VIDEO_PLAYBACK_RATE = 0.68;
const FINAL_IDLE_LOOP_SECONDS = 1.45;

function useDocumentTopHeroBox() {
  const [mounted, setMounted] = useState(false);
  const [height, setHeight] = useState(460);

  useEffect(() => {
    setMounted(true);

    const syncHeight = () => {
      /*
        This layer is intentionally scoped to the first hero zone only.
        It starts at document top = 0, flows over the nav, and scrolls away.
      */
      const nextHeight = Math.round(
        Math.min(520, Math.max(390, window.innerHeight * 0.48)),
      );
      setHeight(nextHeight);
    };

    syncHeight();
    window.addEventListener("resize", syncHeight);

    return () => {
      window.removeEventListener("resize", syncHeight);
    };
  }, []);

  return { mounted, height };
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
      uOpacity: { value: reducedMotion ? 0.78 : 0.96 },
      uContainerAspect: { value: size.width / Math.max(size.height, 1) },
      uKeyColor: { value: new THREE.Color("#00ff00") },
      uSimilarity: { value: 0.245 },
      uSmoothness: { value: 0.145 },
      uSpill: { value: 0.94 },
      uContrast: { value: 1.66 },
      uSaturation: { value: 1.52 },
      uBrightness: { value: 0.86 },
      uGlossBoost: { value: 0.8 },
      uWarmth: { value: 0.38 },
      uDepth: { value: 0.28 },
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
              Keep the real video starting from the document top.
              Crop only enough vertically to prevent lower-page takeover.
            */
            vec2 result = uv;
            result.y = mix(0.0, 0.86, uv.y);
            return result;
          }

          vec3 saturateColor(vec3 color, float amount) {
            float luma = dot(color, vec3(0.299, 0.587, 0.114));
            return mix(vec3(luma), color, amount);
          }

          vec3 contrastColor(vec3 color, float amount) {
            return (color - 0.5) * amount + 0.5;
          }

          float heroScopeMask(vec2 uv) {
            /*
              Top chocolate sheet remains broad.
              Below that, visible energy leans toward the product-card side.
            */
            float topSheet = smoothstep(0.55, 0.88, uv.y);

            float diagonalCenter = 0.82 - (uv.x * 0.33);
            float diagonalFlow = 1.0 - smoothstep(0.14, 0.38, abs(uv.y - diagonalCenter));
            diagonalFlow *= smoothstep(0.18, 0.5, uv.x);
            diagonalFlow *= 1.0 - smoothstep(0.94, 1.0, uv.x);

            float productApproach = 1.0 - smoothstep(0.08, 0.34, uv.y);
            productApproach *= smoothstep(0.46, 0.72, uv.x);
            productApproach *= 1.0 - smoothstep(0.95, 1.0, uv.x);

            return clamp(max(topSheet, max(diagonalFlow * 0.82, productApproach * 0.62)), 0.0, 1.0);
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
              HDR-style chocolate remap.
            */
            vec3 darkChocolate = vec3(0.05, 0.011, 0.006);
            vec3 deepMaroon = vec3(0.18, 0.043, 0.018);
            vec3 warmChocolate = vec3(0.35, 0.088, 0.034);
            vec3 goldenSpecular = vec3(1.0, 0.78, 0.42);

            float luminance = dot(rgb, vec3(0.299, 0.587, 0.114));
            vec3 chocolateRamp = mix(darkChocolate, warmChocolate, smoothstep(0.05, 0.64, luminance));
            chocolateRamp = mix(chocolateRamp, deepMaroon, smoothstep(0.1, 0.38, luminance) * 0.42);

            rgb = mix(rgb, chocolateRamp, uWarmth);
            rgb = contrastColor(rgb, uContrast);
            rgb = saturateColor(rgb, uSaturation);
            rgb *= uBrightness;

            /*
              Moving wet gloss.
            */
            float glossA = sin((uv.x * 19.0) - (uTime * 1.45)) * 0.5 + 0.5;
            float glossB = sin(((uv.x * 0.8 + uv.y * 1.25) * 29.0) + (uTime * 1.06)) * 0.5 + 0.5;
            float glossC = sin(((uv.x - uv.y) * 17.0) - (uTime * 0.82)) * 0.5 + 0.5;

            float wetGloss =
              pow(glossA, 11.0) * 0.3 +
              pow(glossB, 14.0) * 0.26 +
              pow(glossC, 9.0) * 0.16;

            float navBand = smoothstep(0.73, 0.98, vUv.y);
            float lowerDepth = smoothstep(0.24, 0.8, 1.0 - uv.y);
            float scope = heroScopeMask(vUv);

            rgb = mix(rgb, darkChocolate, uDepth * lowerDepth);
            rgb += goldenSpecular * wetGloss * uGlossBoost * max(navBand * 0.76, scope);

            /*
              It flows over nav visually, but does not block nav clicks.
            */
            float navReadability = mix(1.0, 0.74, navBand);

            /*
              Fade at the bottom of the hero-only layer.
            */
            float heroBottomFade = 1.0 - smoothstep(0.05, 0.22, vUv.y);
            float topFade = smoothstep(0.0, 0.01, uv.y);

            gl_FragColor = vec4(
              rgb,
              alpha * uOpacity * navReadability * heroBottomFade * topFade * scope
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
    <ChromaKeyChocolatePlane
      texture={texture}
      reducedMotion={reducedMotion}
      idleMode={idleMode}
    />
  );
}

function ChocolatePortalLayer({
  height,
  reducedMotion,
}: {
  height: number;
  reducedMotion: boolean | null;
}) {
  const portalStyle: CSSProperties = {
    position: "absolute",
    left: 0,
    top: 0,
    width: "100vw",
    height: `${height}px`,
    zIndex: 2147483000,
    pointerEvents: "none",
    overflow: "hidden",
    opacity: 1,
    contain: "layout paint style",
  };

  return (
    <div
      style={portalStyle}
      aria-hidden="true"
      data-hero-chocolate-melt-overlay="portal-document-top-hero-only-video-melt"
    >
      <motion.div
        className="absolute inset-x-0 top-0 h-full"
        initial={
          reducedMotion
            ? false
            : {
                opacity: 0,
                y: -8,
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
          duration: 1.8,
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

      <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#170302]/10 via-transparent to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent via-[#fff8ee]/18 to-[#fff8ee]/0" />
    </div>
  );
}

export default function HeroChocolateMeltOverlay() {
  const prefersReducedMotion = useReducedMotion();
  const { mounted, height } = useDocumentTopHeroBox();

  if (!mounted) return null;

  return createPortal(
    <ChocolatePortalLayer height={height} reducedMotion={prefersReducedMotion} />,
    document.body,
  );
}
''', encoding="utf-8")

# Ensure global shell layer exists.
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

print("PATCH_APPLIED: step17e_b6g2a_r4_fix5_document_top_hero_only_melt")
