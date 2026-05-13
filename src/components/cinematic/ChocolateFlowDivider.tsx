"use client";

import { motion, useReducedMotion } from "framer-motion";

type ChocolateFlowDividerProps = {
  className?: string;
  variant?: "cream-to-chocolate" | "chocolate-to-cream";
  height?: number;
};

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export default function ChocolateFlowDivider({
  className,
  variant = "chocolate-to-cream",
  height = 118,
}: ChocolateFlowDividerProps) {
  const prefersReducedMotion = useReducedMotion();
  const reverse = variant === "cream-to-chocolate";

  return (
    <div
      className={cx("pointer-events-none relative z-10 overflow-hidden", className)}
      style={{ height }}
      aria-hidden="true"
      data-chocolate-animation="flow-divider"
      data-flow-variant={variant}
    >
      <motion.svg
        viewBox="0 0 1440 180"
        preserveAspectRatio="none"
        className="h-full w-full"
        initial={prefersReducedMotion ? false : { opacity: 0.96 }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.92, 1, 0.92] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      >
        <defs>
          <linearGradient id="hershey-flow-main" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#190503" />
            <stop offset="35%" stopColor="#5a1d0d" />
            <stop offset="70%" stopColor="#2b0d06" />
            <stop offset="100%" stopColor="#100302" />
          </linearGradient>

          <linearGradient id="hershey-flow-highlight" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="rgba(255,229,164,0)" />
            <stop offset="38%" stopColor="rgba(255,229,164,0.34)" />
            <stop offset="56%" stopColor="rgba(255,229,164,0.08)" />
            <stop offset="100%" stopColor="rgba(255,229,164,0)" />
          </linearGradient>

          <filter id="hershey-flow-shadow" x="-10%" y="-20%" width="120%" height="150%">
            <feDropShadow dx="0" dy="12" stdDeviation="13" floodColor="#2a0804" floodOpacity="0.24" />
          </filter>
        </defs>

        <rect
          x="0"
          y="0"
          width="1440"
          height="180"
          fill={reverse ? "#fff7ed" : "#f8f1e7"}
        />

        <motion.path
          d="
            M0 58
            C126 32 224 82 348 61
            C488 37 587 17 718 54
            C851 92 962 96 1092 63
            C1230 27 1330 42 1440 65
            V180 H0 Z
          "
          fill="url(#hershey-flow-main)"
          filter="url(#hershey-flow-shadow)"
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  d: [
                    `
                      M0 58
                      C126 32 224 82 348 61
                      C488 37 587 17 718 54
                      C851 92 962 96 1092 63
                      C1230 27 1330 42 1440 65
                      V180 H0 Z
                    `,
                    `
                      M0 64
                      C132 44 226 88 352 66
                      C489 42 591 24 720 60
                      C850 96 969 86 1094 58
                      C1233 26 1332 50 1440 72
                      V180 H0 Z
                    `,
                    `
                      M0 58
                      C126 32 224 82 348 61
                      C488 37 587 17 718 54
                      C851 92 962 96 1092 63
                      C1230 27 1330 42 1440 65
                      V180 H0 Z
                    `,
                  ],
                }
          }
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.path
          d="M67 69 C172 48 252 83 356 65 C471 45 564 29 689 58 C802 84 923 97 1051 70 C1190 40 1302 47 1392 66"
          stroke="url(#hershey-flow-highlight)"
          strokeWidth="10"
          strokeLinecap="round"
          fill="none"
          animate={prefersReducedMotion ? undefined : { x: [-16, 18, -16] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        />

        <path
          d="M0 72 C160 44 262 92 402 72 C554 50 644 38 776 72 C918 108 1048 100 1190 69 C1302 45 1374 58 1440 76"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="2"
          fill="none"
        />

        <path
          d="M0 156 C170 137 284 160 436 144 C596 127 713 130 868 150 C1034 172 1182 150 1440 160 V180 H0 Z"
          fill="rgba(12,3,2,0.28)"
        />
      </motion.svg>
    </div>
  );
}
