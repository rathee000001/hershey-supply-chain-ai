"use client";

import { motion, useReducedMotion } from "framer-motion";

type ChocolateAtmosphereProps = {
  mode?: "light" | "dark";
};

const floatingDrops = [
  { left: "8%", top: "18%", size: 78, delay: 0 },
  { left: "18%", top: "64%", size: 42, delay: 0.6 },
  { left: "36%", top: "28%", size: 58, delay: 1.1 },
  { left: "62%", top: "14%", size: 88, delay: 0.35 },
  { left: "78%", top: "62%", size: 46, delay: 1.5 },
  { left: "91%", top: "32%", size: 66, delay: 0.9 },
];

export default function ChocolateAtmosphere({
  mode = "light",
}: ChocolateAtmosphereProps) {
  const prefersReducedMotion = useReducedMotion();
  const dark = mode === "dark";

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <div
        className={
          dark
            ? "absolute inset-0 bg-[radial-gradient(circle_at_78%_12%,rgba(120,44,22,0.35),transparent_34%),radial-gradient(circle_at_10%_90%,rgba(214,165,38,0.10),transparent_36%)]"
            : "absolute inset-0 bg-[radial-gradient(circle_at_78%_12%,rgba(123,42,21,0.14),transparent_34%),radial-gradient(circle_at_10%_90%,rgba(214,165,38,0.18),transparent_36%)]"
        }
      />

      <motion.div
        className="absolute left-[-8%] top-[-5.5rem] h-36 w-[116%] rounded-b-[48%] bg-gradient-to-r from-[#1a0503] via-[#5a1e0f] to-[#260805] opacity-90 shadow-2xl"
        initial={prefersReducedMotion ? false : { y: -36, opacity: 0.72 }}
        animate={prefersReducedMotion ? undefined : { y: [-18, -8, -18], opacity: [0.78, 0.94, 0.78] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />

      <motion.div
        className="absolute left-[-4%] top-5 h-6 w-[108%] rounded-full bg-gradient-to-r from-transparent via-amber-100/20 to-transparent blur-md"
        initial={prefersReducedMotion ? false : { x: "-25%" }}
        animate={prefersReducedMotion ? undefined : { x: ["-25%", "35%", "-25%"] }}
        transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
      />

      {floatingDrops.map((drop) => (
        <motion.div
          key={`${drop.left}-${drop.top}`}
          className="absolute rounded-full bg-[radial-gradient(circle_at_34%_22%,#9d5733_0%,#4a160a_48%,#180403_100%)] opacity-20 blur-[1px]"
          style={{
            left: drop.left,
            top: drop.top,
            width: drop.size,
            height: drop.size * 1.32,
            borderRadius: "56% 44% 58% 42%",
          }}
          initial={prefersReducedMotion ? false : { y: 0, rotate: -8, scale: 0.96 }}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  y: [0, -18, 0],
                  rotate: [-8, 7, -8],
                  scale: [0.96, 1.04, 0.96],
                }
          }
          transition={{
            duration: 8 + drop.delay,
            delay: drop.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      <div
        className={
          dark
            ? "absolute inset-0 bg-[linear-gradient(to_bottom,rgba(8,2,2,0.18),transparent_22%,rgba(8,2,2,0.38))]"
            : "absolute inset-0 bg-[linear-gradient(to_bottom,rgba(255,250,243,0.28),transparent_24%,rgba(255,250,243,0.48))]"
        }
      />
    </div>
  );
}