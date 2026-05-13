"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Box, Rotate3D, ShieldCheck } from "lucide-react";
import { useState } from "react";

const WRAPPER_FRONT =
  "/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp";

const WRAPPER_BACK =
  "/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp";

export default function HomeProductShowcase() {
  const prefersReducedMotion = useReducedMotion();
  const [showBack, setShowBack] = useState(false);

  return (
    <aside
      className="relative mx-auto min-h-[460px] w-full max-w-[760px]"
      aria-label="Hershey product visual showcase"
      data-home-product-showcase="restored-large-wrapper-hover"
      onMouseEnter={() => setShowBack(true)}
      onMouseLeave={() => setShowBack(false)}
      onFocus={() => setShowBack(true)}
      onBlur={() => setShowBack(false)}
    >
      <motion.div
        className="absolute inset-0 rounded-[2.5rem] border border-[#3a160d]/10 bg-white/80 shadow-2xl shadow-[#3a160d]/10 backdrop-blur-xl"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 18, scale: 0.98 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.72, ease: [0.22, 1, 0.36, 1] }}
      />

      <div className="absolute inset-0 overflow-hidden rounded-[2.5rem]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_52%_34%,rgba(244,199,93,0.16),transparent_34%),radial-gradient(circle_at_76%_66%,rgba(111,29,18,0.10),transparent_34%),linear-gradient(135deg,rgba(255,250,242,0.92),rgba(255,247,237,0.68))]" />

        <motion.div
          className="absolute right-[-10%] top-[4%] h-64 w-64 rounded-full bg-[#6f1d12]/10 blur-3xl"
          initial={prefersReducedMotion ? false : { opacity: 0.22, scale: 0.92 }}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  opacity: [0.16, 0.3, 0.16],
                  scale: [0.92, 1.06, 0.92],
                }
          }
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.div
          className="absolute bottom-[-20%] left-[14%] h-72 w-72 rounded-full bg-[#f4c75d]/12 blur-3xl"
          initial={prefersReducedMotion ? false : { opacity: 0.18, scale: 0.96 }}
          animate={
            prefersReducedMotion
              ? undefined
              : {
                  opacity: [0.14, 0.28, 0.14],
                  scale: [0.96, 1.08, 0.96],
                }
          }
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <div className="relative z-10 flex min-h-[460px] flex-col justify-between p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <motion.div
            className="inline-flex items-center gap-2 rounded-full border border-[#3a160d]/10 bg-white/88 px-4 py-2 text-[10px] font-black uppercase tracking-[0.22em] text-[#6f1d12] shadow-sm backdrop-blur-xl"
            initial={prefersReducedMotion ? false : { opacity: 0, y: 10 }}
            animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ delay: 0.18, duration: 0.55 }}
          >
            <Box size={13} />
            Product Study Anchor
          </motion.div>

          <motion.div
            className="inline-flex items-center gap-2 rounded-full border border-[#3a160d]/10 bg-[#2d0d06] px-4 py-2 text-[10px] font-black uppercase tracking-[0.2em] text-[#fff1d0] shadow-sm"
            initial={prefersReducedMotion ? false : { opacity: 0, y: 10 }}
            animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ delay: 0.24, duration: 0.55 }}
          >
            <Rotate3D size={13} />
            Hover to inspect back
          </motion.div>
        </div>

        <div className="relative flex flex-1 items-center justify-center py-2">
          <motion.div
            className="relative w-full max-w-[640px]"
            initial={prefersReducedMotion ? false : { opacity: 0, x: 28, rotate: -1.5 }}
            animate={
              prefersReducedMotion
                ? undefined
                : {
                    opacity: 1,
                    x: 0,
                    rotate: showBack ? 0.7 : [-0.9, 0.7, -0.9],
                    y: showBack ? -3 : [0, -6, 0],
                  }
            }
            transition={{
              opacity: { duration: 0.7, delay: 0.18, ease: [0.22, 1, 0.36, 1] },
              x: { duration: 0.7, delay: 0.18, ease: [0.22, 1, 0.36, 1] },
              rotate: { duration: showBack ? 0.35 : 8, repeat: showBack ? 0 : Infinity, ease: "easeInOut" },
              y: { duration: showBack ? 0.35 : 7, repeat: showBack ? 0 : Infinity, ease: "easeInOut" },
            }}
            tabIndex={0}
          >
            <div className="absolute -inset-x-6 bottom-[-22%] h-24 rounded-full bg-[#2d0d06]/13 blur-2xl" />

            <div className="relative aspect-[5.8/2] overflow-hidden rounded-[1.8rem] border border-white/70 bg-white/44 p-4 shadow-2xl shadow-[#3a160d]/14 backdrop-blur-md">
              <AnimatePresence mode="wait">
                <motion.img
                  key={showBack ? "wrapper-back" : "wrapper-front"}
                  src={showBack ? WRAPPER_BACK : WRAPPER_FRONT}
                  alt={
                    showBack
                      ? "Hershey 1.55 oz milk chocolate wrapper back visual"
                      : "Hershey 1.55 oz milk chocolate wrapper front visual"
                  }
                  className="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain drop-shadow-2xl"
                  draggable={false}
                  initial={prefersReducedMotion ? false : { opacity: 0, rotateY: showBack ? -12 : 12, scale: 1.92 }}
                  animate={prefersReducedMotion ? undefined : { opacity: 1, rotateY: 0, scale: 2.08 }}
                  exit={prefersReducedMotion ? undefined : { opacity: 0, rotateY: showBack ? 12 : -12, scale: 1.92 }}
                  transition={{ duration: 0.34, ease: [0.22, 1, 0.36, 1] }}
                />
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        <motion.div
          className="grid gap-3 sm:grid-cols-[1fr_auto]"
          initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
          animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ delay: 0.36, duration: 0.55 }}
        >
          <div className="rounded-[1.35rem] border border-[#3a160d]/10 bg-white/86 p-4 shadow-sm backdrop-blur-xl">
            <p className="text-[10px] font-black uppercase tracking-[0.24em] text-[#9c6a27]">
              Study product
            </p>
            <p className="mt-1.5 text-lg font-black tracking-tight text-[#2d0d06]">
              1.55 oz milk chocolate bar
            </p>
            <p className="mt-1.5 text-sm font-semibold leading-6 text-[#5c4a40]">
              Product visuals support identification only; evidence claims remain JSON-first.
            </p>
          </div>

          <div className="flex items-center justify-center rounded-[1.35rem] border border-[#3a160d]/10 bg-[#fff7df] px-5 py-4 text-[#2d0d06] shadow-sm">
            <ShieldCheck size={20} />
            <ArrowRight className="ml-3" size={18} />
          </div>
        </motion.div>
      </div>
    </aside>
  );
}
