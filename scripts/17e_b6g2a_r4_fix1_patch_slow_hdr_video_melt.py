from pathlib import Path
import re

ROOT = Path.cwd()

# 1) Fix known build blocker if still present.
overview = ROOT / "src/components/home/HomeProjectOverviewSection.tsx"
if overview.exists():
    text = overview.read_text(encoding="utf-8-sig")
    text = re.sub(r"(\n\s*opacity:\s*1,\s*)\n\s*opacity:\s*1,", r"\1", text)
    overview.write_text(text, encoding="utf-8")

# 2) Replace chocolate melt overlay with slow video + HDR shader tune.
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"

overlay.write_text(r'''"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { motion, useReducedMotion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

const CHOCOLATE_VIDEO_SRC =
  "/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4";

const VIDEO_PLAYBACK_RATE = 0.2;

function ChromaKeyChocolatePlane({
  texture,
  reducedMotion,
}: {
  texture: THREE.VideoTexture;
  reducedMotion: boolean | null;
}) {
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const { viewport, size } = useThree();

  const uniforms = useMemo(
    () => ({
      uTexture: { value: texture },
      uTime: { value: 0 },
      uOpacity: { value: reducedMotion ? 0.62 : 0.72 },
      uVideoAspect: { value: 2560 / 1440 },
      uContainerAspect: { value: size.width / Math.max(size.height, 1) },
      uKeyColor: { value: new THREE.Color("#00ff00") },
      uSimilarity: { value: 0.23 },
      uSmoothness: { value: 0.18 },
      uSpill: { value: 0.82 },
      uContrast: { value: 1.23 },
      uSaturation: { value: 1.22 },
      uBrightness: { value: 0.96 },
      uGlossBoost: { value: 0.32 },
      uWarmth: { value: 0.12 },
    }),
    [texture, reducedMotion, size.width, size.height],
  );

  useFrame(({ clock }) => {
    if (!materialRef.current) return;

    materialRef.current.uniforms.uTime.value = reducedMotion
      ? 1.5
      : clock.elapsedTime * 0.34;

    materialRef.current.uniforms.uContainerAspect.value =
      size.width / Math.max(size.height, 1);
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
          uniform float uOpacity;
          uniform float uVideoAspect;
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

          varying vec2 vUv;

          vec2 heroVideoUv(vec2 uv) {
            /*
              Intentional non-cover mapping:
              - keep full width so it feels like top-page overflow
              - sample upper video area so drips remain natural but less absurdly huge
              - keep the video visually entering from top, not left-to-right
            */
            vec2 result = uv;
            result.y = mix(0.18, 1.0, uv.y);
            return result;
          }

          vec3 boostSaturation(vec3 color, float amount) {
            float luma = dot(color, vec3(0.299, 0.587, 0.114));
            return mix(vec3(luma), color, amount);
          }

          void main() {
            vec2 uv = heroVideoUv(vUv);

            if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
              discard;
            }

            vec4 tex = texture2D(uTexture, uv);
            vec3 rgb = tex.rgb;

            float chromaDistance = distance(rgb, uKeyColor);
            float baseAlpha = smoothstep(uSimilarity, uSimilarity + uSmoothness, chromaDistance);

            float greenDominance = max(rgb.g - max(rgb.r, rgb.b), 0.0);
            float greenCut = smoothstep(0.055, 0.34, greenDominance);
            float alpha = baseAlpha * (1.0 - greenCut * 0.94);

            rgb.g = mix(rgb.g, (rgb.r + rgb.b) * 0.46, greenCut * uSpill);

            vec3 warmChocolate = vec3(0.16, 0.042, 0.018);
            vec3 deepChocolate = vec3(0.075, 0.016, 0.008);
            vec3 goldenSpecular = vec3(1.0, 0.78, 0.46);

            rgb = mix(rgb, warmChocolate, uWarmth);
            rgb = (rgb - 0.5) * uContrast + 0.5;
            rgb = boostSaturation(rgb, uSaturation);
            rgb *= uBrightness;

            float navBand = smoothstep(0.76, 0.92, vUv.y);
            float liquidTop = smoothstep(0.04, 0.28, 1.0 - uv.y);
            float movingGlossA = sin((uv.x * 18.0) - (uTime * 1.4)) * 0.5 + 0.5;
            float movingGlossB = sin(((uv.x + uv.y) * 26.0) + (uTime * 0.9)) * 0.5 + 0.5;
            float wetGloss = pow(movingGlossA, 9.0) * 0.18 + pow(movingGlossB, 12.0) * 0.16;

            /*
              Keep the transparent navbar readable:
              chocolate still flows above it visually, but the shader softens alpha in the nav band.
            */
            float navReadability = mix(1.0, 0.62, navBand);

            rgb = mix(rgb, deepChocolate, 0.08);
            rgb += goldenSpecular * wetGloss * uGlossBoost * max(liquidTop, navBand * 0.7);

            float topFade = smoothstep(0.0, 0.035, uv.y);
            float heroBottomFade = 1.0 - smoothstep(0.82, 1.0, vUv.y);

            gl_FragColor = vec4(rgb, alpha * uOpacity * navReadability * topFade * heroBottomFade);
          }
        `}
      />
    </mesh>
  );
}

function ChocolateVideoShaderLayer({ reducedMotion }: { reducedMotion: boolean | null }) {
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);

  useEffect(() => {
    const video = document.createElement("video");
    video.src = CHOCOLATE_VIDEO_SRC;
    video.muted = true;
    video.loop = true;
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

    setTexture(videoTexture);

    const playPromise = video.play();
    if (playPromise) {
      playPromise.catch(() => {
        // Muted + playsInline normally allows autoplay; browser may defer in rare cases.
      });
    }

    return () => {
      video.pause();
      video.removeAttribute("src");
      video.load();
      videoTexture.dispose();
    };
  }, []);

  if (!texture) return null;

  return <ChromaKeyChocolatePlane texture={texture} reducedMotion={reducedMotion} />;
}

export default function HeroChocolateMeltOverlay() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div
      className="pointer-events-none absolute inset-x-0 top-[-72px] z-[9999] h-[500px] overflow-hidden"
      aria-hidden="true"
      data-hero-chocolate-melt-overlay="slow-hdr-video-melt-over-transparent-navbar"
    >
      <motion.div
        className="absolute inset-x-0 top-0 h-full"
        initial={
          prefersReducedMotion
            ? false
            : {
                y: -150,
                opacity: 0,
                clipPath: "inset(0% 0% 84% 0%)",
              }
        }
        animate={
          prefersReducedMotion
            ? undefined
            : {
                y: 0,
                opacity: 1,
                clipPath: [
                  "inset(0% 0% 84% 0%)",
                  "inset(0% 0% 66% 0%)",
                  "inset(0% 0% 40% 0%)",
                  "inset(0% 0% 12% 0%)",
                  "inset(0% 0% 0% 0%)",
                ],
              }
        }
        transition={{
          duration: 18,
          ease: [0.22, 1, 0.36, 1],
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
          <ChocolateVideoShaderLayer reducedMotion={prefersReducedMotion} />
        </Canvas>
      </motion.div>

      <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-[#210604]/18 via-[#210604]/6 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-56 bg-gradient-to-b from-transparent via-[#fff8ee]/14 to-[#fff8ee]/0" />
    </div>
  );
}
''', encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_r4_fix1_slow_hdr_video_melt")
