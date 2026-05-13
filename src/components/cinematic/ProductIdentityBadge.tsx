"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { PackageCheck } from "lucide-react";

type ProductIdentityBadgeProps = {
  variant?: "hero" | "floating";
};

type VisualAsset = {
  asset_key: string;
  label: string;
  url: string;
  source_kind?: string;
};

type VisualAssetManifest = {
  assets?: Record<string, VisualAsset>;
};

const MANIFEST_URL = "/data/hershey/visual_assets/hershey_visual_assets_manifest.json";

export default function ProductIdentityBadge({
  variant = "hero",
}: ProductIdentityBadgeProps) {
  const prefersReducedMotion = useReducedMotion();
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  useEffect(() => {
    fetch(MANIFEST_URL, { cache: "no-store" })
      .then((response) => response.json())
      .then((manifest: VisualAssetManifest) => {
        const wrapper = manifest.assets?.hershey_wrapper_front?.url;
        setImageUrl(wrapper || null);
      })
      .catch(() => setImageUrl(null));
  }, []);

  const content = (
    <>
      <div className="flex h-16 w-28 shrink-0 items-center justify-center overflow-hidden rounded-2xl border border-[#2a0805]/10 bg-white">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Hershey 1.55 oz wrapper front"
            className="h-full w-full object-contain"
            onError={() => setImageUrl(null)}
          />
        ) : (
          <PackageCheck size={24} className="text-[#7b2a15]" />
        )}
      </div>

      <div>
        <p className="text-[10px] font-black uppercase tracking-[0.22em] text-[#9c6a27]">
          Target SKU
        </p>
        <p className="text-base font-black leading-tight text-[#2a0805]">
          Hershey 1.55 oz Milk Chocolate
        </p>
        <p className="mt-1 text-xs font-semibold text-[#6a5a52]">
          Public-evidence study model
        </p>
      </div>
    </>
  );

  if (variant === "floating") {
    return (
      <motion.aside
        className="fixed bottom-5 left-5 z-40 hidden max-w-[330px] items-center gap-3 rounded-[1.35rem] border border-[#2a0805]/10 bg-[#fffaf3]/90 p-3 text-[#2a0805] shadow-2xl backdrop-blur-xl md:flex"
        initial={prefersReducedMotion ? false : { opacity: 0, y: 18, scale: 0.96 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0, scale: 1 }}
        transition={{ delay: 0.45, duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
      >
        {content}
      </motion.aside>
    );
  }

  return (
    <motion.div
      className="inline-flex max-w-[430px] items-center gap-4 rounded-[1.5rem] border border-[#2a0805]/10 bg-white/75 p-3 pr-5 text-[#2a0805] shadow-sm backdrop-blur"
      initial={prefersReducedMotion ? false : { opacity: 0, y: 14, scale: 0.98 }}
      animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: 0.2, duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
    >
      {content}
    </motion.div>
  );
}