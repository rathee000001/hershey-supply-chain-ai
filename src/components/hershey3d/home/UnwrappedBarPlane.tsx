"use client";

import { useTexture } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";

type UnwrappedBarPlaneProps = {
  url: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: [number, number, number];
  opacity?: number;
};

export default function UnwrappedBarPlane({
  url,
  position,
  rotation = [0, 0, 0],
  scale = [1, 1, 1],
  opacity = 1,
}: UnwrappedBarPlaneProps) {
  const texture = useTexture(url);

  useMemo(() => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;
  }, [texture]);

  return (
    <mesh position={position} rotation={rotation} scale={scale} data-product-plane="unwrapped-bar">
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial
        map={texture}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
        toneMapped={false}
        depthWrite={false}
      />
    </mesh>
  );
}
