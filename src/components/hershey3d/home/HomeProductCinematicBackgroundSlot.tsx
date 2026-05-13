"use client";

import dynamic from "next/dynamic";

const HomeProductCinematicBackground = dynamic(
  () => import("@/components/hershey3d/home/HomeProductCinematicBackground"),
  {
    ssr: false,
    loading: () => null,
  },
);

export default function HomeProductCinematicBackgroundSlot() {
  return <HomeProductCinematicBackground />;
}
