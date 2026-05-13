"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ShieldCheck, Sparkles } from "lucide-react";

type ChocolateDripRibbonProps = {
  variant?: "heroTop" | "divider";
};

const heroDrips = [
  { id: "d1", x: 86, y: 53, h: 82, w: 18, delay: 0.1 },
  { id: "d2", x: 222, y: 58, h: 55, w: 14, delay: 0.35 },
  { id: "d3", x: 390, y: 48, h: 112, w: 20, delay: 0.65 },
  { id: "d4", x: 612, y: 55, h: 68, w: 15, delay: 0.25 },
  { id: "d5", x: 840, y: 52, h: 96, w: 19, delay: 0.55 },
  { id: "d6", x: 1050, y: 54, h: 70, w: 16, delay: 0.8 },
];

const dividerDrips = [
  { id: "sd1", x: 168, y: 37, h: 38, w: 11, delay: 0.1 },
  { id: "sd2", x: 516, y: 40, h: 54, w: 13, delay: 0.35 },
  { id: "sd3", x: 930, y: 36, h: 42, w: 12, delay: 0.6 },
];

function DripShape({
  x,
  y,
  h,
  w,
  delay,
  prefersReducedMotion,
}: {
  x: number;
  y: number;
  h: number;
  w: number;
  delay: number;
  prefersReducedMotion: boolean | null;
}) {
  const d = `
    M ${x - w / 2} ${y}
    C ${x - w * 0.65} ${y + h * 0.24}, ${x - w * 0.46} ${y + h * 0.62}, ${x - w * 0.18} ${y + h * 0.82}
    C ${x - w * 0.06} ${y + h * 0.94}, ${x - w * 0.1} ${y + h}, ${x} ${y + h}
    C ${x + w * 0.1} ${y + h}, ${x + w * 0.06} ${y + h * 0.94}, ${x + w * 0.18} ${y + h * 0.82}
    C ${x + w * 0.46} ${y + h * 0.62}, ${x + w * 0.65} ${y + h * 0.24}, ${x + w / 2} ${y}
    Z
  `;

  return (
    <motion.path
      d={d}
      fill="url(#chocolateBodyGradient)"
      stroke="rgba(255,241,208,0.26)"
      strokeWidth="1.1"
      initial={false}
      animate={
        prefersReducedMotion
          ? undefined
          : {
              y: [0, 5, 0],
              opacity: [0.82, 1, 0.82],
            }
      }
      transition={{
        duration: 5.6,
        delay,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}

export function ChocolateDripRibbon({ variant = "heroTop" }: ChocolateDripRibbonProps) {
  const prefersReducedMotion = useReducedMotion();
  const isHeroTop = variant === "heroTop";
  const drips = isHeroTop ? heroDrips : dividerDrips;

  return (
    <div
      className={[
        "pointer-events-none overflow-hidden",
        isHeroTop
          ? "absolute left-0 right-0 top-0 z-[1] h-[150px] opacity-[0.72]"
          : "absolute left-0 right-0 top-0 z-[1] h-[105px] opacity-[0.82]",
      ].join(" ")}
      aria-hidden="true"
      data-chocolate-drip-ribbon={variant}
    >
      <motion.svg
        className="h-full w-full"
        viewBox={isHeroTop ? "0 0 1200 220" : "0 0 1200 130"}
        preserveAspectRatio="none"
        initial={false}
        animate={
          prefersReducedMotion
            ? undefined
            : {
                y: isHeroTop ? [0, -3, 0] : [0, 2, 0],
              }
        }
        transition={{
          duration: isHeroTop ? 8.5 : 7,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <defs>
          <linearGradient id="chocolateBodyGradient" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#2a0805" />
            <stop offset="32%" stopColor="#5b180d" />
            <stop offset="68%" stopColor="#7b2a15" />
            <stop offset="100%" stopColor="#2a0805" />
          </linearGradient>

          <linearGradient id="chocolateGlossGradient" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="rgba(255,241,208,0)" />
            <stop offset="35%" stopColor="rgba(255,241,208,0.4)" />
            <stop offset="62%" stopColor="rgba(255,241,208,0.12)" />
            <stop offset="100%" stopColor="rgba(255,241,208,0)" />
          </linearGradient>

          <filter id="chocolateSoftShadow" x="-10%" y="-20%" width="120%" height="150%">
            <feDropShadow dx="0" dy="12" stdDeviation="11" floodColor="#2a0805" floodOpacity="0.22" />
          </filter>
        </defs>

        <path
          d={
            isHeroTop
              ? "M0 0 H1200 V42 C1110 50 1045 25 946 42 C850 59 796 81 706 52 C620 24 540 27 450 49 C356 72 294 60 210 44 C130 29 72 51 0 39 Z"
              : "M0 0 H1200 V30 C1088 43 1008 24 888 35 C752 48 705 60 580 38 C462 17 386 28 268 43 C166 56 82 41 0 35 Z"
          }
          fill="url(#chocolateBodyGradient)"
          filter="url(#chocolateSoftShadow)"
        />

        {drips.map((drip) => (
          <DripShape
            key={drip.id}
            x={drip.x}
            y={drip.y}
            h={drip.h}
            w={drip.w}
            delay={drip.delay}
            prefersReducedMotion={prefersReducedMotion}
          />
        ))}

        <motion.path
          d={
            isHeroTop
              ? "M20 22 C130 9 197 25 302 20 C425 14 510 4 640 21 C795 42 874 15 1012 22 C1090 26 1138 18 1190 15"
              : "M28 17 C132 8 240 18 350 15 C472 12 560 5 690 18 C836 32 960 12 1175 16"
          }
          stroke="url(#chocolateGlossGradient)"
          strokeWidth={isHeroTop ? "8" : "6"}
          strokeLinecap="round"
          fill="none"
          initial={false}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  pathLength: [0.35, 0.92, 0.35],
                  opacity: [0.38, 0.78, 0.38],
                }
          }
          transition={{
            duration: isHeroTop ? 6.6 : 5.8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </motion.svg>
    </div>
  );
}

export function ChocolateFlowDivider() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section
      className="relative px-6 py-10"
      data-home-chocolate-flow-divider="json-safe-decorative-chocolate-flow"
    >
      <motion.div
        className="relative mx-auto max-w-7xl overflow-hidden rounded-[2.4rem] border border-[#3a160d]/10 bg-white/82 p-6 shadow-2xl shadow-[#3a160d]/8 backdrop-blur-xl md:p-8"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 18 }}
        whileInView={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.58, ease: [0.22, 1, 0.36, 1] }}
      >
        <ChocolateDripRibbon variant="divider" />

        <div className="relative z-10 grid gap-6 pt-16 md:grid-cols-[1fr_1.2fr] md:items-end">
          <div>
            <p className="text-[11px] font-black uppercase tracking-[0.28em] text-[#9c6a27]">
              Chocolate motion layer
            </p>
            <h2 className="mt-3 max-w-2xl text-3xl font-black leading-tight tracking-tight text-[#120807] md:text-4xl">
              Cinematic visuals support the story; audited JSON artifacts control the claims.
            </h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            {[
              "Decorative flow",
              "Evidence-safe wording",
              "Reusable site layer",
            ].map((item, index) => (
              <motion.div
                key={item}
                className="rounded-[1.35rem] border border-[#3a160d]/10 bg-[#fffaf0]/86 p-4 shadow-sm"
                initial={false}
                animate={
                  prefersReducedMotion
                    ? undefined
                    : {
                        y: [0, -4, 0],
                      }
                }
                transition={{
                  duration: 4.8,
                  delay: index * 0.35,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-[#3a160d]/10 bg-white text-[#6f1d12]">
                  {index === 1 ? <ShieldCheck size={18} /> : <Sparkles size={18} />}
                </div>
                <p className="text-sm font-black text-[#2a0805]">{item}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </section>
  );
}
