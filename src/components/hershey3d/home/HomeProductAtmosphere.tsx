"use client";

import { Sparkles, Stars } from "@react-three/drei";

export default function HomeProductAtmosphere() {
  return (
    <>
      <Stars radius={86} depth={34} count={420} factor={1.75} fade speed={0.1} />

      <Sparkles
        count={58}
        scale={[4.8, 2.8, 2.2]}
        size={1.95}
        speed={0.18}
        color="#f4c75d"
        opacity={0.26}
      />

      <Sparkles
        count={22}
        scale={[3.9, 2.2, 1.8]}
        size={2.5}
        speed={0.1}
        color="#8b2d18"
        opacity={0.12}
      />

      <mesh position={[1.15, -1.05, -0.7]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[2.1, 96]} />
        <meshBasicMaterial color="#f4c75d" transparent opacity={0.04} />
      </mesh>
    </>
  );
}
