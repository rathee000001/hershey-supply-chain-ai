"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Line, Stars } from "@react-three/drei";
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

function getVerticalFunnelPoint(t: number, lane: number) {
  const eased = t * t * (3 - 2 * t);
  const y = 1.45 - eased * 2.85;
  const radius = 0.64 * (1 - eased) + 0.12;
  const angle = t * Math.PI * 6.4 + lane * 1.22;
  const x = Math.cos(angle) * radius;
  const z = Math.sin(angle) * radius * 0.62;

  return new THREE.Vector3(x, y, z);
}

function getOutputPoint(t: number, lane: number) {
  const x = 0.1 + t * 0.88;
  const y = -1.15 + Math.sin(t * Math.PI + lane) * 0.16;
  const z = Math.cos(t * Math.PI * 1.2 + lane) * 0.15;

  return new THREE.Vector3(x, y, z);
}

function makeVerticalFunnelLine(lane: number) {
  return Array.from({ length: 120 }, (_, index) => {
    const t = index / 119;
    const point = getVerticalFunnelPoint(t, lane);
    return [point.x, point.y, point.z] as [number, number, number];
  });
}

function makeOutputLine(lane: number) {
  return Array.from({ length: 62 }, (_, index) => {
    const t = index / 61;
    const point = getOutputPoint(t, lane);
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

function RawInputCard({ card, index }: { card: InputCard; index: number }) {
  return (
    <Float speed={0.62 + index * 0.04} rotationIntensity={0.07} floatIntensity={0.1}>
      <group position={card.position} rotation={card.rotation} scale={card.scale}>
        <mesh>
          <boxGeometry args={[1, 0.62, 0.018]} />
          <meshStandardMaterial
            color={card.color}
            emissive={card.color}
            emissiveIntensity={0.025}
            transparent
            opacity={card.opacity}
            roughness={0.38}
            metalness={0.03}
          />
        </mesh>

        <mesh position={[-0.25, 0.1, 0.016]}>
          <boxGeometry args={[0.34, 0.035, 0.012]} />
          <meshStandardMaterial color="#6f1d12" transparent opacity={0.16} />
        </mesh>

        <mesh position={[0.18, 0.1, 0.016]}>
          <boxGeometry args={[0.42, 0.035, 0.012]} />
          <meshStandardMaterial color="#d8a533" transparent opacity={0.16} />
        </mesh>

        <mesh position={[-0.18, -0.08, 0.016]}>
          <boxGeometry args={[0.52, 0.035, 0.012]} />
          <meshStandardMaterial color="#222222" transparent opacity={0.08} />
        </mesh>

        <mesh position={[0.24, -0.2, 0.016]}>
          <boxGeometry args={[0.24, 0.035, 0.012]} />
          <meshStandardMaterial color="#38bdf8" transparent opacity={0.13} />
        </mesh>
      </group>
    </Float>
  );
}

function CleanOutputCard({ index }: { index: number }) {
  const positions: Array<[number, number, number]> = [
    [0.88, -0.96, -0.06],
    [1.02, -1.28, 0.05],
    [0.68, -1.55, -0.04],
  ];

  const rotations: Array<[number, number, number]> = [
    [0.04, -0.22, 0.08],
    [-0.04, 0.18, -0.06],
    [0.08, 0.14, 0.1],
  ];

  return (
    <Float speed={0.72 + index * 0.05} rotationIntensity={0.07} floatIntensity={0.1}>
      <group position={positions[index]} rotation={rotations[index]} scale={[0.34, 0.34, 1]}>
        <mesh>
          <boxGeometry args={[1, 0.5, 0.03]} />
          <meshStandardMaterial
            color={index === 1 ? "#fff1d0" : "#fff7ed"}
            emissive="#f4c75d"
            emissiveIntensity={0.07}
            transparent
            opacity={0.44}
            roughness={0.26}
            metalness={0.1}
          />
        </mesh>

        <mesh position={[-0.24, 0.08, 0.025]}>
          <boxGeometry args={[0.36, 0.04, 0.012]} />
          <meshStandardMaterial color="#d8a533" emissive="#d8a533" emissiveIntensity={0.1} transparent opacity={0.34} />
        </mesh>

        <mesh position={[0.16, -0.08, 0.025]}>
          <boxGeometry args={[0.48, 0.04, 0.012]} />
          <meshStandardMaterial color="#6f1d12" emissive="#6f1d12" emissiveIntensity={0.08} transparent opacity={0.22} />
        </mesh>
      </group>
    </Float>
  );
}

function HersheyEvidenceFunnelWorld() {
  const worldRef = useRef<THREE.Group | null>(null);
  const funnelRef = useRef<THREE.Group | null>(null);
  const coreRef = useRef<THREE.Group | null>(null);
  const particleRefs = useRef<Array<THREE.Mesh | null>>([]);

  const funnelLines = useMemo(() => [0, 1, 2, 3, 4].map(makeVerticalFunnelLine), []);
  const outputLines = useMemo(() => [0, 1, 2].map(makeOutputLine), []);

  const streamParticles = useMemo<StreamParticle[]>(() => {
    return Array.from({ length: 118 }, (_, index) => {
      const lane = index % 5;
      return {
        id: `stream-${index}`,
        offset: (index * 0.037) % 1,
        lane,
        color: funnelColors[lane],
        size: lane === 2 ? 0.016 : 0.013 + (index % 3) * 0.003,
      };
    });
  }, []);

  const inputCards = useMemo<InputCard[]>(() => {
    return [
      {
        id: "input-01",
        position: [-0.76, 1.58, -0.08],
        rotation: [0.1, -0.26, 0.16],
        scale: [0.38, 0.38, 1],
        color: "#fff7ed",
        opacity: 0.32,
      },
      {
        id: "input-02",
        position: [0.12, 1.72, 0.08],
        rotation: [-0.05, 0.18, -0.12],
        scale: [0.36, 0.36, 1],
        color: "#f9e7bd",
        opacity: 0.3,
      },
      {
        id: "input-03",
        position: [0.76, 1.42, 0.02],
        rotation: [0.08, 0.12, 0.08],
        scale: [0.38, 0.38, 1],
        color: "#fff1d0",
        opacity: 0.28,
      },
      {
        id: "input-04",
        position: [-0.14, 1.25, -0.12],
        rotation: [-0.08, -0.22, -0.18],
        scale: [0.32, 0.32, 1],
        color: "#fff7ed",
        opacity: 0.24,
      },
    ];
  }, []);

  useFrame((state) => {
    const elapsed = state.clock.elapsedTime;

    if (worldRef.current) {
      worldRef.current.rotation.y = Math.sin(elapsed * 0.12) * 0.055;
      worldRef.current.rotation.x = Math.sin(elapsed * 0.1) * 0.016;
      worldRef.current.position.y = Math.sin(elapsed * 0.28) * 0.024;
    }

    if (funnelRef.current) {
      funnelRef.current.rotation.y = elapsed * 0.12;
      funnelRef.current.rotation.z = Math.sin(elapsed * 0.18) * 0.035;
    }

    if (coreRef.current) {
      coreRef.current.rotation.y = elapsed * 0.4;
      coreRef.current.rotation.z = elapsed * 0.18;
    }

    particleRefs.current.forEach((particle, index) => {
      if (!particle) return;

      const item = streamParticles[index];
      const t = (item.offset + elapsed * 0.078) % 1;
      const point = getVerticalFunnelPoint(t, item.lane);

      particle.position.set(point.x, point.y, point.z);

      const fadeIn = THREE.MathUtils.smoothstep(t, 0, 0.18);
      const fadeOut = 1 - THREE.MathUtils.smoothstep(t, 0.78, 1);
      const opacity = Math.max(0.05, fadeIn * fadeOut * 0.84);
      const pulse = 0.8 + Math.sin(elapsed * 3 + index) * 0.18;

      particle.scale.setScalar(pulse);
      setOpacity(particle, opacity);
    });
  });

  return (
    <group
      ref={worldRef}
      position={[1.52, 0.08, 0]}
      scale={0.92}
      data-hershey-scene-world="vertical-evidence-funnel-intelligence-field"
    >
      <group>
        {inputCards.map((card, index) => (
          <RawInputCard key={card.id} card={card} index={index} />
        ))}
      </group>

      <group ref={funnelRef}>
        {funnelLines.map((points, index) => (
          <Line
            key={`funnel-line-${index}`}
            points={points}
            color={funnelColors[index]}
            lineWidth={index === 1 ? 1.55 : 1.05}
            transparent
            opacity={index === 2 ? 0.4 : 0.32}
          />
        ))}

        {[0, 1, 2, 3, 4, 5].map((ringIndex) => {
          const t = ringIndex / 5;
          const point = getVerticalFunnelPoint(t, ringIndex % 5);
          const radius = 0.64 * (1 - t) + 0.14;

          return (
            <mesh
              key={`funnel-ring-${ringIndex}`}
              position={[0, point.y, 0]}
              rotation={[Math.PI / 2, 0, 0]}
            >
              <torusGeometry args={[radius, 0.0055, 16, 120]} />
              <meshStandardMaterial
                color={ringIndex % 2 === 0 ? "#d8a533" : "#6f1d12"}
                emissive={ringIndex % 2 === 0 ? "#d8a533" : "#6f1d12"}
                emissiveIntensity={0.22}
                transparent
                opacity={0.24}
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
            emissiveIntensity={0.58}
            transparent
            opacity={0.7}
            roughness={0.28}
            metalness={0.18}
          />
        </mesh>
      ))}

      <Float speed={1.02} rotationIntensity={0.08} floatIntensity={0.14}>
        <group ref={coreRef} position={[0, -0.4, 0.16]}>
          <mesh>
            <sphereGeometry args={[0.28, 64, 64]} />
            <meshStandardMaterial
              color="#d8a533"
              emissive="#d8a533"
              emissiveIntensity={0.46}
              metalness={0.72}
              roughness={0.16}
              transparent
              opacity={0.86}
            />
          </mesh>

          <mesh rotation={[Math.PI / 2.35, 0, 0]}>
            <torusGeometry args={[0.68, 0.007, 18, 170]} />
            <meshStandardMaterial
              color="#6f1d12"
              emissive="#6f1d12"
              emissiveIntensity={0.34}
              transparent
              opacity={0.62}
            />
          </mesh>

          <mesh rotation={[0.52, Math.PI / 2.45, 0.18]}>
            <torusGeometry args={[0.98, 0.005, 18, 180]} />
            <meshStandardMaterial
              color="#f4c75d"
              emissive="#f4c75d"
              emissiveIntensity={0.28}
              transparent
              opacity={0.5}
            />
          </mesh>

          <mesh rotation={[0.18, 0.3, Math.PI / 2.15]}>
            <torusGeometry args={[1.22, 0.004, 18, 200]} />
            <meshStandardMaterial
              color="#fff1d0"
              emissive="#fff1d0"
              emissiveIntensity={0.2}
              transparent
              opacity={0.32}
            />
          </mesh>
        </group>
      </Float>

      <group>
        {outputLines.map((points, index) => (
          <Line
            key={`output-line-${index}`}
            points={points}
            color={index === 0 ? "#d8a533" : index === 1 ? "#fff1d0" : "#38bdf8"}
            lineWidth={1.05}
            transparent
            opacity={0.2}
          />
        ))}

        {[0, 1, 2].map((index) => (
          <CleanOutputCard key={`clean-output-${index}`} index={index} />
        ))}
      </group>
    </group>
  );
}

export default function HersheySupplyChainFieldScene() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <section
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden"
      aria-hidden="true"
      data-hershey-home-background="vertical-evidence-funnel-intelligence-field"
    >
      <motion.div
        className="absolute inset-y-0 right-0 w-[42vw] min-w-[560px]"
        initial={prefersReducedMotion ? false : { opacity: 0 }}
        animate={prefersReducedMotion ? undefined : { opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      >
        <Canvas camera={{ position: [0, 0, 6.3], fov: 42 }} dpr={[1, 1.65]}>
          <color attach="background" args={["#fffaf2"]} />

          <ambientLight intensity={0.66} />
          <pointLight position={[3.5, 4, 5]} intensity={1.65} color="#f4c75d" />
          <pointLight position={[-2, -2, 4]} intensity={1.0} color="#6f1d12" />
          <pointLight position={[1.5, -3, 3]} intensity={0.75} color="#fff1d0" />
          <pointLight position={[2.4, 1.8, 2.4]} intensity={0.45} color="#38bdf8" />

          <Stars radius={88} depth={44} count={360} factor={1.35} fade speed={0.08} />
          <HersheyEvidenceFunnelWorld />
        </Canvas>
      </motion.div>

      <div className="absolute inset-y-0 right-0 w-[42vw] min-w-[560px] bg-[radial-gradient(circle_at_58%_34%,rgba(111,29,18,0.07),transparent_29%),radial-gradient(circle_at_56%_52%,rgba(244,199,93,0.08),transparent_34%),radial-gradient(circle_at_78%_70%,rgba(255,241,208,0.12),transparent_28%)]" />
    </section>
  );
}
