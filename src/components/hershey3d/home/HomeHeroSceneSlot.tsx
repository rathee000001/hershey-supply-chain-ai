"use client";

import dynamic from "next/dynamic";

const HomeHeroScene = dynamic(
  () => import("@/components/hershey3d/home/HomeHeroScene"),
  {
    ssr: false,
    loading: () => null,
  },
);

export default function HomeHeroSceneSlot() {
  return <HomeHeroScene />;
}
