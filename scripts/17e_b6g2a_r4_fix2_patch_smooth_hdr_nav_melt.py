from pathlib import Path

ROOT = Path.cwd()
overlay = ROOT / "src/components/cinematic/HeroChocolateMeltOverlay.tsx"

overlay.write_text(r'''"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { motion, useReducedMotion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

const CHOCOLATE_VIDEO_SRC =
  "/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4";

/*
  Slow but smooth:
  0.2 was too slow and looked frozen.
  0.55 keeps the melt cinematic without making the video feel stuck.
*/
const VIDEO_PLAYBACK_RATE = 0.55;

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
      uOpacity: { value: reducedMotion ? 0.72 : 0.84 },
      uVideoAspect: { value: 2560 / 1440 },
      uContainerAspect: { value: size.width / Math.max(size.height, 1) },
      uKeyColor: { value: new THREE.Color("#00ff00") },
      uSimilarity: { value: 0.24 },
      uSmoothness: { value: 0.16 },
      uSpill: { value: 0.9 },
      uContrast: { value: 1.46 },
      uSaturation: { value: 1.36 },
      uBrightness: { value: 0.9 },
      uGlossBoost: { value: 0.58 },
      uWarmth: { value: 0.24 },
      uDepth: { value: 0.18 },
    }),
    [texture, reducedMotion, size.width, size.height],
  );

  useFrame(({ clock }) => {
    if (!materialRef.current) return;

    materialRef.current.uniforms.uTime.value = reducedMotion
      ? 1.2
      : clock.elapsedTime * 0.55;

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
          uniform float uDepth;

          varying vec2 vUv;

          vec2 fitWideTopUv(vec2 uv) {
            /*
              Keep the video full-width and top-flowing.
              Slight vertical compression keeps drips rich but avoids giant page takeover.
            */
            vec2 result = uv;
            result.y = mix(0.08, 0.92, uv.y);
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
            vec2 uv = fitWideTopUv(vUv);

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
            float greenCut = smoothstep(0.045, 0.31, greenDominance);
            float alpha = baseAlpha * (1.0 - greenCut * 0.96);

            rgb.g = mix(rgb.g, (rgb.r + rgb.b) * 0.42, greenCut * uSpill);

            /*
              Chocolate HDR-style remap.
            */
            vec3 darkChocolate = vec3(0.075, 0.018, 0.009);
            vec3 warmChocolate = vec3(0.30, 0.078, 0.032);
            vec3 redChocolate = vec3(0.42, 0.105, 0.045);
            vec3 goldenSpecular = vec3(1.0, 0.78, 0.42);

            float luminance = dot(rgb, vec3(0.299, 0.587, 0.114));
            vec3 chocolateRamp = mix(darkChocolate, warmChocolate, smoothstep(0.05, 0.62, luminance));
            chocolateRamp = mix(chocolateRamp, redChocolate, smoothstep(0.36, 0.92, luminance) * 0.35);

            rgb = mix(rgb, chocolateRamp, uWarmth);
            rgb = contrastColor(rgb, uContrast);
            rgb = saturateColor(rgb, uSaturation);
            rgb *= uBrightness;

            /*
              Moving wet gloss: stronger and smoother than prior version.
            */
            float glossA = sin((uv.x * 18.0) - (uTime * 1.45)) * 0.5 + 0.5;
            float glossB = sin(((uv.x * 0.8 + uv.y * 1.2) * 28.0) + (uTime * 1.1)) * 0.5 + 0.5;
            float glossC = sin(((uv.x - uv.y) * 16.0) - (uTime * 0.9)) * 0.5 + 0.5;

            float wetGloss =
              pow(glossA, 11.0) * 0.28 +
              pow(glossB, 14.0) * 0.23 +
              pow(glossC, 9.0) * 0.14;

            float topLiquid = smoothstep(0.02, 0.26, 1.0 - uv.y);
            float navFlowBand = smoothstep(0.74, 0.92, vUv.y);
            float lowerDepth = smoothstep(0.22, 0.8, 1.0 - uv.y);

            rgb = mix(rgb, darkChocolate, uDepth * lowerDepth);
            rgb += goldenSpecular * wetGloss * uGlossBoost * max(topLiquid, navFlowBand * 0.7);

            /*
              Important:
              Chocolate must visibly pass over navbar pills, but text still readable.
              So nav band alpha is softened, not removed.
            */
            float navReadability = mix(1.0, 0.72, navFlowBand);

            /*
              Fade before it becomes a full-page takeover.
            */
            float heroBottomFade = 1.0 - smoothstep(0.78, 1.0, vUv.y);
            float topFade = smoothstep(0.0, 0.025, uv.y);

            gl_FragColor = vec4(rgb, alpha * uOpacity * navReadability * heroBottomFade * topFade);
          }
        `}
      />
    </mesh>
  );
}

function ChocolateVideoShaderLayer({ reducedMotion }: { reducedMotion: boolean | null }) {
  const [texture, setTexture] = useState<THREE.VideoTexture | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

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
    videoRef.current = video;

    const videoTexture = new THREE.VideoTexture(video);
    videoTexture.colorSpace = THREE.SRGBColorSpace;
    videoTexture.minFilter = THREE.LinearFilter;
    videoTexture.magFilter = THREE.LinearFilter;
    videoTexture.generateMipmaps = false;
    videoTexture.needsUpdate = true;

    setTexture(videoTexture);

    const play = async () => {
      try {
        video.playbackRate = VIDEO_PLAYBACK_RATE;
        await video.play();
      } catch {
        // Muted + playsInline normally allows autoplay.
      }
    };

    if (video.readyState >= 2) {
      play();
    } else {
      video.addEventListener("canplay", play, { once: true });
      video.load();
    }

    return () => {
      video.pause();
      video.removeEventListener("canplay", play);
      video.removeAttribute("src");
      video.load();
      videoTexture.dispose();
      videoRef.current = null;
    };
  }, []);

  if (!texture) return null;

  return <ChromaKeyChocolatePlane texture={texture} reducedMotion={reducedMotion} />;
}

export default function HeroChocolateMeltOverlay() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div
      className="pointer-events-none fixed inset-x-0 top-[-40px] h-[470px] overflow-hidden"
      style={{ zIndex: 2147483000 }}
      aria-hidden="true"
      data-hero-chocolate-melt-overlay="smooth-hdr-video-melt-over-navbar-pills"
    >
      <motion.div
        className="absolute inset-x-0 top-0 h-full"
        initial={
          prefersReducedMotion
            ? false
            : {
                y: -92,
                opacity: 0,
                clipPath: "inset(0% 0% 72% 0%)",
              }
        }
        animate={
          prefersReducedMotion
            ? undefined
            : {
                y: 0,
                opacity: 1,
                clipPath: [
                  "inset(0% 0% 72% 0%)",
                  "inset(0% 0% 50% 0%)",
                  "inset(0% 0% 24% 0%)",
                  "inset(0% 0% 0% 0%)",
                ],
              }
        }
        transition={{
          duration: 7.5,
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
          <ChocolateVideoShaderLayer reducedMotion={prefersReducedMotion} />
        </Canvas>
      </motion.div>

      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-[#170302]/18 via-transparent to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-b from-transparent via-[#fff8ee]/18 to-[#fff8ee]/0" />
    </div>
  );
}
''', encoding="utf-8")

print("PATCH_APPLIED: step17e_b6g2a_r4_fix2_smooth_hdr_nav_melt")
