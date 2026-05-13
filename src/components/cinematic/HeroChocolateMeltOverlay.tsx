"use client";

import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { motion, useReducedMotion } from "framer-motion";
import { type CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import * as THREE from "three";

const CHOCOLATE_VIDEO_SRC =
  "/data/hershey/visual_assets/motion/chocolate_drip_green_screen.mp4";

const VIDEO_PLAYBACK_RATE = 0.78;
const FINAL_IDLE_LOOP_SECONDS = 1.35;

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
    node.style.mixBlendMode = "normal";
    node.style.transform = "translateZ(0)";
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
      uOpacity: { value: reducedMotion ? 0.72 : 0.88 },
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
    position: "absolute",
    left: 0,
    top: 0,
    width: "100vw",
    height: `${height}px`,
    transform: `translate3d(0, ${-scrollY}px, 0)`,
    zIndex: 1,
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
      data-hero-chocolate-melt-overlay="top-layer-video-plus-nav-spill-melt"
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

      <ChocolateNavSpillLayer scrollY={scrollY} visible={visible} />
      <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#170302]/10 via-transparent to-transparent" />
      <div className="absolute inset-x-0 bottom-0 h-36 bg-gradient-to-b from-transparent via-[#fff8ee]/16 to-[#fff8ee]/0" />
    </div>
  );
}

export default function HeroChocolateMeltOverlay() {
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
}
