"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Line } from "@react-three/drei";
import { motion, useReducedMotion } from "framer-motion";
import { useMemo, useRef } from "react";
import * as THREE from "three";

type StreamParticle = {
  id: string;
  offset: number;
  lane: number;
  color: string;
  size: number;
};

type InputCard = {
  id: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  color: string;
  opacity: number;
};

const funnelColors = ["#6f1d12", "#d8a533", "#fff1d0", "#38bdf8", "#f59e0b"];

function getFunnelPoint(t: number, lane: number) {
  const eased = t * t * (3 - 2 * t);
  const y = 1.48 - eased * 2.92;
  const radius = 0.58 * (1 - eased) + 0.1;
  const angle = t * Math.PI * 6.25 + lane * 1.18;
  const x = Math.cos(angle) * radius;
  const z = Math.sin(angle) * radius * 0.58;

  return new THREE.Vector3(x, y, z);
}

function makeFunnelLine(lane: number) {
  return Array.from({ length: 124 }, (_, index) => {
    const t = index / 123;
    const point = getFunnelPoint(t, lane);
    return [point.x, point.y, point.z] as [number, number, number];
  });
}

function setOpacity(object: THREE.Object3D | null, opacity: number) {
  if (!object) return;

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

function EvidenceCard({ card, index }: { card: InputCard; index: number }) {
  return (
    <Float speed={0.65 + index * 0.05} rotationIntensity={0.08} floatIntensity={0.12}>
      <group position={card.position} rotation={card.rotation} scale={card.scale}>
        <mesh>
          <boxGeometry args={[1, 0.62, 0.02]} />
          <meshStandardMaterial
            color={card.color}
            emissive={card.color}
            emissiveIntensity={0.035}
            transparent
            opacity={card.opacity}
            roughness={0.34}
            metalness={0.04}
          />
        </mesh>

        <mesh position={[-0.23, 0.1, 0.016]}>
          <boxGeometry args={[0.36, 0.035, 0.012]} />
          <meshStandardMaterial color="#6f1d12" transparent opacity={0.16} />
        </mesh>

        <mesh position={[0.18, -0.07, 0.016]}>
          <boxGeometry args={[0.48, 0.035, 0.012]} />
          <meshStandardMaterial color="#38bdf8" transparent opacity={0.14} />
        </mesh>
      </group>
    </Float>
  );
}

function BackgroundFunnelWorld() {
  const worldRef = useRef<THREE.Group | null>(null);
  const funnelRef = useRef<THREE.Group | null>(null);
  const coreRef = useRef<THREE.Group | null>(null);
  const particleRefs = useRef<Array<THREE.Mesh | null>>([]);

  const funnelLines = useMemo(() => [0, 1, 2, 3, 4].map(makeFunnelLine), []);

  const streamParticles = useMemo<StreamParticle[]>(() => {
    return Array.from({ length: 86 }, (_, index) => {
      const lane = index % funnelColors.length;

      return {
        id: `particle-${index}`,
        offset: (index * 0.043) % 1,
        lane,
        color: funnelColors[lane],
        size: lane === 2 ? 0.014 : 0.011 + (index % 3) * 0.002,
      };
    });
  }, []);

  const inputCards = useMemo<InputCard[]>(() => {
    return [
      {
        id: "source-card-01",
        position: [-0.58, 1.48, -0.06],
        rotation: [0.1, -0.24, 0.15],
        scale: [0.3, 0.3, 1],
        color: "#fff7ed",
        opacity: 0.3,
      },
      {
        id: "source-card-02",
        position: [0.1, 1.66, 0.08],
        rotation: [-0.05, 0.18, -0.1],
        scale: [0.29, 0.29, 1],
        color: "#f9e7bd",
        opacity: 0.28,
      },
      {
        id: "source-card-03",
        position: [0.66, 1.35, 0.02],
        rotation: [0.08, 0.12, 0.08],
        scale: [0.3, 0.3, 1],
        color: "#fff1d0",
        opacity: 0.27,
      },
    ];
  }, []);

  useFrame((state) => {
    const elapsed = state.clock.elapsedTime;

    if (worldRef.current) {
      worldRef.current.rotation.y = Math.sin(elapsed * 0.12) * 0.045;
      worldRef.current.rotation.x = Math.sin(elapsed * 0.11) * 0.014;
      worldRef.current.position.y = Math.sin(elapsed * 0.3) * 0.028;
    }

    if (funnelRef.current) {
      funnelRef.current.rotation.y = elapsed * 0.11;
      funnelRef.current.rotation.z = Math.sin(elapsed * 0.18) * 0.028;
    }

    if (coreRef.current) {
      coreRef.current.rotation.y = elapsed * 0.34;
      coreRef.current.rotation.z = elapsed * 0.12;
    }

    particleRefs.current.forEach((particle, index) => {
      if (!particle) return;

      const item = streamParticles[index];
      const t = (item.offset + elapsed * 0.072) % 1;
      const point = getFunnelPoint(t, item.lane);

      particle.position.set(point.x, point.y, point.z);

      const fadeIn = THREE.MathUtils.smoothstep(t, 0, 0.18);
      const fadeOut = 1 - THREE.MathUtils.smoothstep(t, 0.78, 1);
      const opacity = Math.max(0.04, fadeIn * fadeOut * 0.78);
      const pulse = 0.82 + Math.sin(elapsed * 3 + index) * 0.16;

      particle.scale.setScalar(pulse);
      setOpacity(particle, opacity);
    });
  });

  return (
    <group
      ref={worldRef}
      position={[0.3, 0.08, 0]}
      scale={0.9}
      data-hershey-scene-world="portfolio-right-background-funnel-bigger-solid-core"
    >
      <group>
        {inputCards.map((card, index) => (
          <EvidenceCard key={card.id} card={card} index={index} />
        ))}
      </group>

      <group ref={funnelRef}>
        {funnelLines.map((points, index) => (
          <Line
            key={`funnel-line-${index}`}
            points={points}
            color={funnelColors[index]}
            lineWidth={index === 1 ? 1.5 : 1.05}
            transparent
            opacity={index === 2 ? 0.34 : 0.28}
          />
        ))}

        {[0, 1, 2, 3, 4].map((ringIndex) => {
          const t = ringIndex / 4;
          const point = getFunnelPoint(t, ringIndex % 5);
          const radius = 0.58 * (1 - t) + 0.12;

          return (
            <mesh
              key={`funnel-ring-${ringIndex}`}
              position={[0, point.y, 0]}
              rotation={[Math.PI / 2, 0, 0]}
            >
              <torusGeometry args={[radius, 0.005, 16, 120]} />
              <meshStandardMaterial
                color={ringIndex % 2 === 0 ? "#d8a533" : "#6f1d12"}
                emissive={ringIndex % 2 === 0 ? "#d8a533" : "#6f1d12"}
                emissiveIntensity={0.18}
                transparent
                opacity={0.22}
              />
            </mesh>
          );
        })}
      </group>

      {streamParticles.map((particle, index) => (
        <mesh
          key={particle.id}
          ref={(node) => {
            particleRefs.current[index] = node;
          }}
        >
          <sphereGeometry args={[particle.size, 12, 12]} />
          <meshStandardMaterial
            color={particle.color}
            emissive={particle.color}
            emissiveIntensity={0.48}
            transparent
            opacity={0.62}
            roughness={0.28}
            metalness={0.14}
          />
        </mesh>
      ))}

      <Float speed={0.95} rotationIntensity={0.08} floatIntensity={0.14}>
        <group ref={coreRef} position={[0, -0.38, 0.14]}>
          <mesh>
            <sphereGeometry args={[0.31, 64, 64]} />
            <meshStandardMaterial
              color="#d8a533"
              emissive="#a66f10"
              emissiveIntensity={0.18}
              metalness={0.58}
              roughness={0.2}
            />
          </mesh>

          <group data-solid-core-color-variance="true">
            <mesh position={[0.09, 0.13, 0.27]}>
              <sphereGeometry args={[0.038, 18, 18]} />
              <meshStandardMaterial color="#fff1d0" emissive="#fff1d0" emissiveIntensity={0.22} roughness={0.18} metalness={0.35} />
            </mesh>

            <mesh position={[-0.18, -0.07, 0.23]}>
              <sphereGeometry args={[0.032, 18, 18]} />
              <meshStandardMaterial color="#7b2a15" emissive="#7b2a15" emissiveIntensity={0.12} roughness={0.22} metalness={0.28} />
            </mesh>

            <mesh position={[0.19, -0.16, -0.19]}>
              <sphereGeometry args={[0.03, 18, 18]} />
              <meshStandardMaterial color="#f4c75d" emissive="#f4c75d" emissiveIntensity={0.18} roughness={0.2} metalness={0.3} />
            </mesh>
          </group>

          <mesh rotation={[Math.PI / 2.35, 0, 0]}>
            <torusGeometry args={[0.66, 0.006, 18, 150]} />
            <meshStandardMaterial
              color="#6f1d12"
              emissive="#6f1d12"
              emissiveIntensity={0.28}
              transparent
              opacity={0.5}
            />
          </mesh>

          <mesh rotation={[0.52, Math.PI / 2.45, 0.18]}>
            <torusGeometry args={[0.94, 0.0045, 18, 160]} />
            <meshStandardMaterial
              color="#f4c75d"
              emissive="#f4c75d"
              emissiveIntensity={0.22}
              transparent
              opacity={0.38}
            />
          </mesh>
        </group>
      </Float>
    </group>
  );
}

export default function HersheySupplyChainFieldScene() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section
      className="pointer-events-none fixed inset-y-0 right-[-2vw] z-0 hidden w-[36vw] min-w-[460px] overflow-visible lg:block"
      aria-hidden="true"
      data-hershey-home-background="portfolio-right-background-funnel-bigger-solid-core"
    >
      <motion.div
        className="absolute inset-0"
        initial={prefersReducedMotion ? false : { opacity: 0 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      >
        <Canvas
          className="h-full w-full"
          camera={{ position: [0, 0, 6.15], fov: 35 }}
          dpr={[1, 1.45]}
          gl={{ alpha: true, antialias: true }}
        >
          <ambientLight intensity={0.7} />
          <pointLight position={[3.5, 4, 5]} intensity={1.4} color="#f4c75d" />
          <pointLight position={[-2, -2, 4]} intensity={0.82} color="#6f1d12" />
          <pointLight position={[1.5, -3, 3]} intensity={0.55} color="#fff1d0" />
          <BackgroundFunnelWorld />
        </Canvas>
      </motion.div>

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_52%_42%,rgba(216,165,38,0.055),transparent_32%),radial-gradient(circle_at_48%_54%,rgba(111,29,18,0.04),transparent_40%)]" />
    </section>
  );
}
