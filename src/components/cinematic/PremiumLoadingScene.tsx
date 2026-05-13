"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Sparkles } from "lucide-react";

type PremiumLoadingSceneProps = {
  label?: string;
  sublabel?: string;
};

export default function PremiumLoadingScene({
  label = "Loading cinematic supply-chain intelligence",
  sublabel = "Preparing audited evidence, visual assets, and animation layers.",
}: PremiumLoadingSceneProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#080202] px-6 text-white">
      <div className="absolute inset-0 opacity-70">
        <div className="absolute left-[-10rem] top-20 h-[34rem] w-[34rem] rounded-full bg-[#5c1f12] blur-3xl" />
        <div className="absolute right-[-10rem] bottom-10 h-[38rem] w-[38rem] rounded-full bg-amber-300/10 blur-3xl" />
      </div>

      <motion.div
        initial={prefersReducedMotion ? false : { opacity: 0, scale: 0.96, y: 18 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative w-full max-w-xl rounded-[2rem] border border-white/10 bg-white/[0.06] p-8 shadow-2xl backdrop-blur"
      >
        <div className="mb-6 inline-flex rounded-full border border-amber-100/20 bg-black/25 p-3">
          <Sparkles className="text-amber-200" />
        </div>

        <p className="text-xs font-black uppercase tracking-[0.25em] text-amber-100/55">
          Hershey Supply Chain AI
        </p>

        <h1 className="mt-4 text-3xl font-black leading-tight">{label}</h1>

        <p className="mt-4 text-sm leading-6 text-white/60">{sublabel}</p>

        <div className="mt-7 h-2 overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-amber-200 via-orange-300 to-amber-100"
            initial={prefersReducedMotion ? false : { x: "-100%" }}
            animate={prefersReducedMotion ? undefined : { x: "100%" }}
            transition={{
              duration: 1.6,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>
      </motion.div>
    </main>
  );
}