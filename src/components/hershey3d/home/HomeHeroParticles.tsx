"use client";

import { Sparkles } from "@react-three/drei";

export default function HomeHeroParticles() {
  return (
    <>
      <Sparkles
        count={92}
        scale={[7.2, 4.1, 3.2]}
        size={2.25}
        speed={0.24}
        color="#f4c75d"
        opacity={0.42}
      />

      <Sparkles
        count={36}
        scale={[5.8, 2.8, 2.1]}
        size={3.2}
        speed={0.16}
        color="#8b2d18"
        opacity={0.22}
      />
    </>
  );
}
