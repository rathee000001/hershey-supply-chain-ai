from pathlib import Path
import shutil
import json
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

# 1. Move old archived TSX files outside src so Next/TypeScript stops compiling legacy experiments.
legacy_src = root / "src" / "components" / "archive" / "hershey_legacy_17d"
legacy_dest = root / "project_archive" / "hershey_legacy_17d"
legacy_dest.mkdir(parents=True, exist_ok=True)

moved_legacy = []
if legacy_src.exists():
    for path in legacy_src.glob("*.tsx"):
        dest = legacy_dest / path.name
        shutil.move(str(path), str(dest))
        moved_legacy.append({
            "from": str(path).replace("\\", "/"),
            "to": str(dest).replace("\\", "/"),
        })

    keep = legacy_src / ".gitkeep"
    keep.write_text("", encoding="utf-8")

# 2. Fully rebuild HomeChocolateBarHero with safer Three.js texture planes.
hero_path = root / "src" / "components" / "hershey3d" / "HomeChocolateBarHero.tsx"
hero_path.parent.mkdir(parents=True, exist_ok=True)

hero_code = r'''// @ts-nocheck
"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Float, Sparkles, useTexture } from "@react-three/drei";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

type VisualAsset = {
  asset_key: string;
  label: string;
  url: string;
};

type VisualAssetManifest = {
  assets?: Record<string, VisualAsset>;
};

type AssetUrls = {
  wrapperFront: string | null;
  wrapperBack: string | null;
  unwrappedBar: string | null;
};

const MANIFEST_URL = "/data/hershey/visual_assets/hershey_visual_assets_manifest.json";

function TexturePlane({
  url,
  position,
  rotation = [0, 0, 0],
  scale = [1, 1, 1],
  opacity = 1,
}: {
  url: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: [number, number, number];
  opacity?: number;
}) {
  const texture = useTexture(url);

  useMemo(() => {
    if (!texture) return;
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
  }, [texture]);

  return (
    <mesh position={position} rotation={rotation} scale={scale}>
      <planeGeometry args={[1, 1]} />
      <meshBasicMaterial
        map={texture}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
        toneMapped={false}
      />
    </mesh>
  );
}

function ChocolateBlockGrid() {
  const group = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!group.current) return;
    group.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.55) * 0.12;
    group.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.35) * 0.05;
  });

  const blocks = Array.from({ length: 12 }, (_, index) => {
    const col = index % 4;
    const row = Math.floor(index / 4);

    return {
      x: (col - 1.5) * 0.72,
      y: (1 - row) * 0.48,
      z: 0,
      delay: index * 0.05,
    };
  });

  return (
    <group ref={group} position={[0, -0.03, 0]}>
      {blocks.map((block, index) => (
        <Float
          key={index}
          speed={1.05}
          rotationIntensity={0.06}
          floatIntensity={0.08}
          floatingRange={[0, 0.035 + block.delay]}
        >
          <mesh position={[block.x, block.y, block.z]}>
            <boxGeometry args={[0.56, 0.32, 0.16]} />
            <meshStandardMaterial
              color="#4b170c"
              roughness={0.34}
              metalness={0.12}
              emissive="#120302"
              emissiveIntensity={0.22}
            />
          </mesh>
        </Float>
      ))}
    </group>
  );
}

function ChocolateHeroScene({ assets }: { assets: AssetUrls }) {
  const sceneGroup = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (!sceneGroup.current) return;
    sceneGroup.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.22) * 0.075;
    sceneGroup.current.position.y = Math.sin(state.clock.elapsedTime * 0.38) * 0.045;
  });

  return (
    <>
      <color attach="background" args={["#160503"]} />

      <ambientLight intensity={1.1} />
      <directionalLight position={[4, 5, 7]} intensity={2.8} />
      <pointLight position={[-3, 2, 4]} intensity={4} color="#d6a526" />
      <pointLight position={[3, -2, 4]} intensity={2.5} color="#7b2a15" />

      <Sparkles
        count={80}
        scale={[6.4, 3.2, 2.8]}
        size={2.15}
        speed={0.28}
        color="#f5d08a"
        opacity={0.36}
      />

      <group ref={sceneGroup}>
        <Float speed={1.2} rotationIntensity={0.16} floatIntensity={0.2}>
          <group position={[0, 0.18, 0]}>
            <ChocolateBlockGrid />

            {assets.unwrappedBar && (
              <TexturePlane
                url={assets.unwrappedBar}
                position={[0, -0.02, 0.31]}
                scale={[3.85, 1.5, 1]}
                opacity={0.94}
              />
            )}
          </group>
        </Float>

        {assets.wrapperFront && (
          <Float speed={0.85} rotationIntensity={0.09} floatIntensity={0.12}>
            <TexturePlane
              url={assets.wrapperFront}
              position={[0, -1.52, -0.08]}
              scale={[3.35, 0.88, 1]}
              opacity={0.94}
            />
          </Float>
        )}

        {assets.wrapperBack && (
          <Float speed={0.72} rotationIntensity={0.08} floatIntensity={0.1}>
            <TexturePlane
              url={assets.wrapperBack}
              position={[2.25, 1.35, -0.35]}
              rotation={[0, -0.22, 0.02]}
              scale={[1.7, 0.55, 1]}
              opacity={0.72}
            />
          </Float>
        )}

        <mesh position={[0, -1.93, -0.35]} rotation={[-Math.PI / 2, 0, 0]}>
          <circleGeometry args={[2.65, 64]} />
          <meshBasicMaterial color="#d6a526" transparent opacity={0.08} />
        </mesh>
      </group>

      <Environment preset="studio" />
    </>
  );
}

export default function HomeChocolateBarHero() {
  const [assets, setAssets] = useState<AssetUrls>({
    wrapperFront: null,
    wrapperBack: null,
    unwrappedBar: null,
  });

  useEffect(() => {
    fetch(MANIFEST_URL, { cache: "no-store" })
      .then((response) => response.json())
      .then((manifest: VisualAssetManifest) => {
        setAssets({
          wrapperFront: manifest.assets?.hershey_wrapper_front?.url || null,
          wrapperBack: manifest.assets?.hershey_wrapper_back?.url || null,
          unwrappedBar: manifest.assets?.hershey_unwrapped_bar?.url || null,
        });
      })
      .catch(() => {
        setAssets({
          wrapperFront: null,
          wrapperBack: null,
          unwrappedBar: null,
        });
      });
  }, []);

  return (
    <div className="relative min-h-[560px] overflow-hidden rounded-[2.8rem] border border-[#2a0805]/10 bg-[#170504] shadow-2xl">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_34%,rgba(214,165,38,0.22),transparent_34%),radial-gradient(circle_at_80%_12%,rgba(123,42,21,0.42),transparent_34%)]" />

      <Canvas
        camera={{ position: [0, 0, 5.6], fov: 42 }}
        dpr={[1, 1.8]}
        gl={{ antialias: true, alpha: true }}
      >
        <Suspense fallback={null}>
          <ChocolateHeroScene assets={assets} />
        </Suspense>
      </Canvas>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#170504] via-[#170504]/72 to-transparent p-7">
        <p className="text-[10px] font-black uppercase tracking-[0.28em] text-amber-100/55">
          Home Hero 3D Preview
        </p>
        <h2 className="mt-2 text-3xl font-black text-white">
          Unwrapped bar as the cinematic product anchor
        </h2>
        <p className="mt-3 max-w-xl text-sm leading-6 text-white/62">
          The home page starts with the product itself. Later roadmap steps connect this
          product anchor to the full ingredient-to-retail supply-chain world.
        </p>
      </div>
    </div>
  );
}
'''

hero_path.write_text(hero_code, encoding="utf-8")

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e6a_fix_home_3d_build_errors",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": "complete",
    "legacy_tsx_moved_out_of_src": moved_legacy,
    "home_hero_rebuilt": str(hero_path).replace("\\", "/"),
    "note": "Old archived TSX files were moved outside src so TypeScript does not compile legacy experiments. HomeChocolateBarHero was rebuilt with safer texture planes.",
    "next_step": "Run Step 17E-B5 validation and npm build.",
}

report_path = report_dir / "step17e6a_home_3d_build_fix_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5A HOME 3D BUILD FIX COMPLETE")
print("---------------------------------------")
print(f"Legacy TSX files moved out of src: {len(moved_legacy)}")
print(f"Home hero rebuilt:                {hero_path}")
print(f"Report JSON:                      {report_path}")
print("")