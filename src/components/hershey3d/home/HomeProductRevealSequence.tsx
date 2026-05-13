"use client";

import { Float } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";
import ProductWrapperPlane from "@/components/hershey3d/home/ProductWrapperPlane";
import UnwrappedBarPlane from "@/components/hershey3d/home/UnwrappedBarPlane";
import WrapperPeelPanels from "@/components/hershey3d/home/WrapperPeelPanels";

const PRODUCT_ASSETS = {
  wrapperFront: "/data/hershey/visual_assets/source_assets/hershey_wrapper_front.webp",
  wrapperBack: "/data/hershey/visual_assets/source_assets/hershey_wrapper_back.webp",
  unwrappedBar: "/data/hershey/visual_assets/source_assets/hershey_unwrapped_bar.png",
};

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

function smoothstep(edge0: number, edge1: number, value: number) {
  const t = clamp((value - edge0) / (edge1 - edge0));
  return t * t * (3 - 2 * t);
}

function setGroupOpacity(object: THREE.Object3D | null, opacity: number) {
  if (!object) return;

  object.visible = opacity > 0.01;

  object.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) return;

    const materials = Array.isArray(child.material) ? child.material : [child.material];

    materials.forEach((item) => {
      const material = item as THREE.Material & { opacity?: number };
      material.transparent = true;
      material.opacity = opacity;
      material.needsUpdate = true;
    });
  });
}

export default function HomeProductRevealSequence() {
  const master = useRef<THREE.Group | null>(null);
  const wrapperFront = useRef<THREE.Group | null>(null);
  const wrapperBack = useRef<THREE.Group | null>(null);
  const wrapperPeel = useRef<THREE.Group | null>(null);
  const unwrappedBar = useRef<THREE.Group | null>(null);

  useFrame((state) => {
    const elapsed = state.clock.elapsedTime;
    const cycle = elapsed % 13.2;

    const intro = smoothstep(0.2, 1.4, cycle);
    const flipToBack = smoothstep(1.7, 3.0, cycle);
    const peelOpen = smoothstep(3.0, 5.0, cycle);
    const barReveal = smoothstep(4.0, 6.4, cycle);
    const heroHold = smoothstep(6.2, 7.4, cycle);
    const fadeOut = smoothstep(11.2, 12.8, cycle);

    const floatY = Math.sin(elapsed * 0.42) * 0.04;
    const subtleYaw = Math.sin(elapsed * 0.18) * 0.04;

    if (master.current) {
      master.current.position.set(1.08, -0.06 + floatY, 0);
      master.current.rotation.y = subtleYaw;
      master.current.rotation.x = Math.sin(elapsed * 0.13) * 0.014;
      master.current.scale.setScalar(0.82);
    }

    const frontOpacity = intro * (1 - flipToBack) * (1 - fadeOut);
    const backOpacity = flipToBack * (1 - peelOpen * 0.94) * (1 - fadeOut);
    const peelOpacity = peelOpen * (1 - fadeOut);
    const barOpacity = barReveal * (1 - fadeOut);

    if (wrapperFront.current) {
      wrapperFront.current.position.set(-0.05, 0.34, 0.38);
      wrapperFront.current.rotation.set(0.02, -0.14 + flipToBack * 1.2, -0.02);
      wrapperFront.current.scale.setScalar(0.82 + intro * 0.18);
      setGroupOpacity(wrapperFront.current, frontOpacity);
    }

    if (wrapperBack.current) {
      wrapperBack.current.position.set(0.02, 0.34, 0.36);
      wrapperBack.current.rotation.set(0.02, 0.78 - peelOpen * 0.28, 0.015);
      wrapperBack.current.scale.setScalar(0.96);
      setGroupOpacity(wrapperBack.current, backOpacity);
    }

    if (wrapperPeel.current) {
      wrapperPeel.current.position.set(peelOpen * 0.16, 0.18 - peelOpen * 0.08, 0.42);
      wrapperPeel.current.rotation.set(0.03, -0.12 + peelOpen * 0.18, 0.02);
      wrapperPeel.current.scale.setScalar(0.96 + peelOpen * 0.18);
      setGroupOpacity(wrapperPeel.current, peelOpacity * 0.9);
    }

    if (unwrappedBar.current) {
      unwrappedBar.current.position.set(-0.08 + barReveal * 0.14, -0.48 + barReveal * 0.24, 0.72);
      unwrappedBar.current.rotation.set(-0.05, -0.1 + heroHold * 0.08, 0.02);
      unwrappedBar.current.scale.setScalar(0.64 + barReveal * 0.36);
      setGroupOpacity(unwrappedBar.current, barOpacity * 0.92);
    }
  });

  return (
    <group ref={master} data-home-product-sequence="right-side-front-back-peel-unwrapped">
      <Float speed={0.62} rotationIntensity={0.025} floatIntensity={0.06}>
        <group ref={wrapperFront}>
          <ProductWrapperPlane
            url={PRODUCT_ASSETS.wrapperFront}
            side="front"
            position={[0, 0, 0]}
            rotation={[0, 0, 0]}
            scale={[3.6, 0.94, 1]}
            opacity={1}
          />
        </group>
      </Float>

      <Float speed={0.58} rotationIntensity={0.022} floatIntensity={0.052}>
        <group ref={wrapperBack}>
          <ProductWrapperPlane
            url={PRODUCT_ASSETS.wrapperBack}
            side="back"
            position={[0, 0, 0]}
            rotation={[0, 0, 0]}
            scale={[3.46, 0.9, 1]}
            opacity={0}
          />
        </group>
      </Float>

      <group ref={wrapperPeel}>
        <WrapperPeelPanels
          frontUrl={PRODUCT_ASSETS.wrapperFront}
          backUrl={PRODUCT_ASSETS.wrapperBack}
        />
      </group>

      <Float speed={0.72} rotationIntensity={0.038} floatIntensity={0.1}>
        <group ref={unwrappedBar}>
          <UnwrappedBarPlane
            url={PRODUCT_ASSETS.unwrappedBar}
            position={[0, 0, 0]}
            rotation={[0, 0, 0]}
            scale={[3.55, 1.18, 1]}
            opacity={0}
          />
        </group>
      </Float>
    </group>
  );
}
