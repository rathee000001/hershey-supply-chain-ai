"use client";

import { motion, useReducedMotion } from "framer-motion";

type ChocolateAtmosphereProps = {
  mode?: "light" | "dark";
};

const goldParticles = [
  { left: "7%", top: "18%", size: 3, delay: 0.1, duration: 8 },
  { left: "18%", top: "62%", size: 2, delay: 1.4, duration: 10 },
  { left: "31%", top: "28%", size: 3, delay: 0.8, duration: 9 },
  { left: "46%", top: "72%", size: 2, delay: 2.1, duration: 11 },
  { left: "61%", top: "16%", size: 4, delay: 0.4, duration: 10 },
  { left: "77%", top: "54%", size: 2, delay: 1.8, duration: 8 },
  { left: "91%", top: "26%", size: 3, delay: 1.1, duration: 9 },
];

const chocolateDust = [
  { left: "14%", top: "38%", size: 140, opacity: 0.12 },
  { left: "67%", top: "18%", size: 190, opacity: 0.1 },
  { left: "82%", top: "72%", size: 150, opacity: 0.08 },
];

export default function ChocolateAtmosphere({ mode = "light" }: ChocolateAtmosphereProps) {
  const prefersReducedMotion = useReducedMotion();
  const dark = mode === "dark";

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div
        className={
          dark
            ? "absolute inset-0 bg-[radial-gradient(circle_at_82%_12%,rgba(129,45,22,0.20),transparent_32%),radial-gradient(circle_at_12%_86%,rgba(224,174,66,0.10),transparent_34%)]"
            : "absolute inset-0 bg-[radial-gradient(circle_at_82%_12%,rgba(129,45,22,0.10),transparent_32%),radial-gradient(circle_at_12%_86%,rgba(224,174,66,0.15),transparent_34%)]"
        }
      />

      {chocolateDust.map((dust) => (
        <motion.div
          key={`${dust.left}-${dust.top}`}
          className="absolute rounded-full bg-[#5c2113] blur-3xl"
          style={{
            left: dust.left,
            top: dust.top,
            width: dust.size,
            height: dust.size,
            opacity: dark ? dust.opacity * 1.4 : dust.opacity,
          }}
          initial={prefersReducedMotion ? false : { scale: 0.92, x: 0, y: 0 }}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  scale: [0.92, 1.06, 0.92],
                  x: [0, 14, 0],
                  y: [0, -10, 0],
                }
          }
          transition={{
            duration: 13,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      {goldParticles.map((particle) => (
        <motion.span
          key={`${particle.left}-${particle.top}`}
          className={
            dark
              ? "absolute rounded-full bg-[#f5c75f] shadow-[0_0_18px_rgba(245,199,95,0.78)]"
              : "absolute rounded-full bg-[#dfaa39] shadow-[0_0_14px_rgba(223,170,57,0.42)]"
          }
          style={{
            left: particle.left,
            top: particle.top,
            width: particle.size,
            height: particle.size,
          }}
          initial={prefersReducedMotion ? false : { opacity: 0.35, y: 0 }}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  opacity: [0.22, 0.9, 0.22],
                  y: [0, -18, 0],
                }
          }
          transition={{
            duration: particle.duration,
            delay: particle.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      <motion.div
        className={
          dark
            ? "absolute left-1/2 top-[-18rem] h-[34rem] w-[72rem] -translate-x-1/2 rounded-full bg-[#4a160a]/24 blur-3xl"
            : "absolute left-1/2 top-[-18rem] h-[34rem] w-[72rem] -translate-x-1/2 rounded-full bg-[#6b2114]/10 blur-3xl"
        }
        initial={prefersReducedMotion ? false : { opacity: 0.72 }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.55, 0.84, 0.55] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      />

      <div
        className={
          dark
            ? "absolute inset-0 bg-[linear-gradient(to_bottom,rgba(7,2,2,0.26),transparent_30%,rgba(7,2,2,0.38))]"
            : "absolute inset-0 bg-[linear-gradient(to_bottom,rgba(255,250,242,0.42),transparent_34%,rgba(248,241,231,0.54))]"
        }
      />
    </div>
  );
}
