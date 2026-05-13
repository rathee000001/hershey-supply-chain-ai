"use client";

import dynamic from "next/dynamic";

const HersheyHomeLabScene = dynamic(
  () => import("@/components/hershey3d/home/HersheyHomeLabScene"),
  {
    ssr: false,
    loading: () => null,
  },
);

export default function HersheyHomeLabSceneSlot() {
  return <HersheyHomeLabScene />;
}
