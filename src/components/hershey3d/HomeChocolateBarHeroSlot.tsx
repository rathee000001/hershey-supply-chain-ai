"use client";

import dynamic from "next/dynamic";

const HomeChocolateBarHero = dynamic(
  () => import("@/components/hershey3d/HomeChocolateBarHero"),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-[560px] rounded-[2.8rem] border border-[#2a0805]/10 bg-[#170504] p-8 text-white shadow-2xl">
        <p className="text-[10px] font-black uppercase tracking-[0.28em] text-amber-100/55">
          Loading 3D hero
        </p>
        <h2 className="mt-4 text-3xl font-black">Preparing Hershey product scene...</h2>
        <p className="mt-3 max-w-xl text-sm leading-6 text-white/60">
          The homepage hero uses the collected wrapper and unwrapped Hershey bar assets.
        </p>
      </div>
    ),
  }
);

export default function HomeChocolateBarHeroSlot() {
  return <HomeChocolateBarHero />;
}
