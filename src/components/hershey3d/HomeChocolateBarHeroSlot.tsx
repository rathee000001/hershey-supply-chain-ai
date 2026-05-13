"use client";

import dynamic from "next/dynamic";

const HomeChocolateBarHero = dynamic(
  () => import("@/components/hershey3d/HomeChocolateBarHero"),
  {
    ssr: false,
    loading: () => null,
  },
);

export default function HomeChocolateBarHeroSlot() {
  return <HomeChocolateBarHero />;
}
