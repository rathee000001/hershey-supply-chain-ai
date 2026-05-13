"use client";

import { motion, useReducedMotion } from "framer-motion";

type ChocolateDripHeaderProps = {
  className?: string;
  height?: number;
  intensity?: "soft" | "hero";
};

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export default function ChocolateDripHeader({
  className,
  height = 168,
  intensity = "hero",
}: ChocolateDripHeaderProps) {
  const prefersReducedMotion = useReducedMotion();
  const strong = intensity === "hero";

  return (
    <div
      className={cx(
        "pointer-events-none absolute inset-x-0 top-0 z-20 overflow-hidden",
        className,
      )}
      style={{ height }}
      aria-hidden="true"
      data-chocolate-animation="drip-header"
    >
      <motion.svg
        viewBox="0 0 1440 260"
        preserveAspectRatio="none"
        className="h-full w-full"
        initial={prefersReducedMotion ? false : { y: -14, opacity: 0.96 }}
        animate={prefersReducedMotion ? undefined : { y: [-8, -2, -8], opacity: [0.96, 1, 0.96] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      >
        <defs>
          <linearGradient id="hershey-drip-main" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#1a0503" />
            <stop offset="26%" stopColor="#3a1008" />
            <stop offset="54%" stopColor="#6b2411" />
            <stop offset="78%" stopColor="#3a1008" />
            <stop offset="100%" stopColor="#140302" />
          </linearGradient>

          <linearGradient id="hershey-drip-gloss" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="rgba(255,232,168,0)" />
            <stop offset="28%" stopColor="rgba(255,232,168,0.34)" />
            <stop offset="52%" stopColor="rgba(255,232,168,0.10)" />
            <stop offset="80%" stopColor="rgba(255,232,168,0.28)" />
            <stop offset="100%" stopColor="rgba(255,232,168,0)" />
          </linearGradient>

          <radialGradient id="hershey-drip-depth" cx="50%" cy="18%" r="90%">
            <stop offset="0%" stopColor="rgba(255,220,145,0.22)" />
            <stop offset="42%" stopColor="rgba(91,28,13,0.34)" />
            <stop offset="100%" stopColor="rgba(15,3,2,0.88)" />
          </radialGradient>

          <filter id="hershey-drip-shadow" x="-10%" y="-20%" width="120%" height="150%">
            <feDropShadow dx="0" dy="18" stdDeviation="16" floodColor="#2a0804" floodOpacity="0.34" />
            <feDropShadow dx="0" dy="4" stdDeviation="3" floodColor="#080101" floodOpacity="0.24" />
          </filter>
        </defs>

        <motion.path
          d="
            M0 0 H1440 V54
            C1378 48 1321 42 1266 52
            C1208 63 1183 97 1135 88
            C1098 81 1098 48 1058 43
            C1007 37 978 83 932 84
            C884 85 857 42 807 41
            C753 39 724 92 671 91
            C619 91 588 38 533 43
            C486 47 463 91 420 89
            C371 87 345 42 292 45
            C236 49 221 96 174 92
            C133 88 107 50 59 48
            C32 47 13 52 0 58
            Z
          "
          fill="url(#hershey-drip-main)"
          filter="url(#hershey-drip-shadow)"
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  d: [
                    `
                      M0 0 H1440 V54
                      C1378 48 1321 42 1266 52
                      C1208 63 1183 97 1135 88
                      C1098 81 1098 48 1058 43
                      C1007 37 978 83 932 84
                      C884 85 857 42 807 41
                      C753 39 724 92 671 91
                      C619 91 588 38 533 43
                      C486 47 463 91 420 89
                      C371 87 345 42 292 45
                      C236 49 221 96 174 92
                      C133 88 107 50 59 48
                      C32 47 13 52 0 58
                      Z
                    `,
                    `
                      M0 0 H1440 V58
                      C1379 54 1325 46 1268 57
                      C1211 68 1186 100 1136 91
                      C1096 84 1095 52 1054 48
                      C1004 44 977 88 929 89
                      C879 89 855 48 804 47
                      C748 45 727 95 670 94
                      C616 93 588 43 532 48
                      C485 52 461 96 418 93
                      C369 90 347 47 293 51
                      C237 55 224 101 175 96
                      C132 92 108 55 58 54
                      C31 53 12 56 0 62
                      Z
                    `,
                    `
                      M0 0 H1440 V54
                      C1378 48 1321 42 1266 52
                      C1208 63 1183 97 1135 88
                      C1098 81 1098 48 1058 43
                      C1007 37 978 83 932 84
                      C884 85 857 42 807 41
                      C753 39 724 92 671 91
                      C619 91 588 38 533 43
                      C486 47 463 91 420 89
                      C371 87 345 42 292 45
                      C236 49 221 96 174 92
                      C133 88 107 50 59 48
                      C32 47 13 52 0 58
                      Z
                    `,
                  ],
                }
          }
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />

        <path
          d="
            M0 0 H1440 V54
            C1378 48 1321 42 1266 52
            C1208 63 1183 97 1135 88
            C1098 81 1098 48 1058 43
            C1007 37 978 83 932 84
            C884 85 857 42 807 41
            C753 39 724 92 671 91
            C619 91 588 38 533 43
            C486 47 463 91 420 89
            C371 87 345 42 292 45
            C236 49 221 96 174 92
            C133 88 107 50 59 48
            C32 47 13 52 0 58
            Z
          "
          fill="url(#hershey-drip-depth)"
          opacity={strong ? 0.72 : 0.52}
        />

        <motion.g
          initial={prefersReducedMotion ? false : { opacity: 0.9 }}
          animate={prefersReducedMotion ? undefined : { opacity: [0.72, 1, 0.72] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        >
          <path
            d="M55 47 C96 55 123 71 168 70 C218 69 236 39 287 38"
            stroke="url(#hershey-drip-gloss)"
            strokeWidth="9"
            strokeLinecap="round"
            fill="none"
            opacity="0.82"
          />
          <path
            d="M492 43 C540 36 579 74 624 75 C665 76 698 44 741 43"
            stroke="url(#hershey-drip-gloss)"
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
            opacity="0.76"
          />
          <path
            d="M904 51 C952 54 973 31 1025 37 C1081 43 1098 73 1143 75"
            stroke="url(#hershey-drip-gloss)"
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
            opacity="0.72"
          />
          <path
            d="M1198 55 C1246 38 1308 45 1368 37"
            stroke="url(#hershey-drip-gloss)"
            strokeWidth="7"
            strokeLinecap="round"
            fill="none"
            opacity="0.68"
          />
        </motion.g>

        <g fill="url(#hershey-drip-main)" filter="url(#hershey-drip-shadow)">
          <motion.path
            d="M182 72 C164 102 166 128 181 142 C198 126 202 99 182 72 Z"
            animate={prefersReducedMotion ? undefined : { y: [0, 5, 0] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.path
            d="M386 74 C367 119 367 172 388 201 C412 170 412 118 386 74 Z"
            animate={prefersReducedMotion ? undefined : { y: [0, 8, 0] }}
            transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.path
            d="M659 80 C641 116 643 151 661 169 C683 147 682 113 659 80 Z"
            animate={prefersReducedMotion ? undefined : { y: [0, 4, 0] }}
            transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.path
            d="M1008 66 C991 103 995 133 1010 149 C1029 129 1029 99 1008 66 Z"
            animate={prefersReducedMotion ? undefined : { y: [0, 6, 0] }}
            transition={{ duration: 8.5, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.path
            d="M1287 70 C1265 121 1268 168 1290 191 C1314 164 1312 119 1287 70 Z"
            animate={prefersReducedMotion ? undefined : { y: [0, 7, 0] }}
            transition={{ duration: 9.5, repeat: Infinity, ease: "easeInOut" }}
          />
        </g>

        <g opacity="0.54">
          <path d="M384 91 C377 129 379 158 388 181" stroke="rgba(255,227,161,0.38)" strokeWidth="4" strokeLinecap="round" />
          <path d="M1286 88 C1278 124 1280 154 1290 176" stroke="rgba(255,227,161,0.32)" strokeWidth="4" strokeLinecap="round" />
          <path d="M181 87 C176 107 177 124 181 134" stroke="rgba(255,227,161,0.28)" strokeWidth="3" strokeLinecap="round" />
        </g>
      </motion.svg>

      <div className="absolute inset-x-0 top-0 h-10 bg-gradient-to-b from-[#120302]/80 to-transparent" />
    </div>
  );
}
