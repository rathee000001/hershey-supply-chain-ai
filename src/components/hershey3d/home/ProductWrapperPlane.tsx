"use client";

import { useTexture } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";

type TextureCrop = "full" | "left-half" | "right-half";

type ProductWrapperPlaneProps = {
  url: string;
  side?: "front" | "back" | "peel";
  crop?: TextureCrop;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: [number, number, number];
  opacity?: number;
};

function prepareTexture(texture: THREE.Texture, crop: TextureCrop) {
  const prepared = crop === "full" ? texture : texture.clone();

  prepared.colorSpace = THREE.SRGBColorSpace;
  prepared.anisotropy = 8;
  prepared.wrapS = THREE.ClampToEdgeWrapping;
  prepared.wrapT = THREE.ClampToEdgeWrapping;

  if (crop === "left-half") {
    prepared.repeat.set(0.5, 1);
    prepared.offset.set(0, 0);
  }

  if (crop === "right-half") {
    prepared.repeat.set(0.5, 1);
    prepared.offset.set(0.5, 0);
  }

  prepared.needsUpdate = true;

  return prepared;
}

export default function ProductWrapperPlane({
  url,
  side = "front",
  crop = "full",
  position,
  rotation = [0, 0, 0],
  scale = [1, 1, 1],
  opacity = 1,
}: ProductWrapperPlaneProps) {
  const texture = useTexture(url);

  const preparedTexture = useMemo(() => {
    return prepareTexture(texture, crop);
  }, [texture, crop]);

  return (
    <mesh position={position} rotation={rotation} scale={scale} data-product-plane={side}>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial
        map={preparedTexture}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
        toneMapped={false}
        depthWrite={false}
      />
    </mesh>
  );
}
