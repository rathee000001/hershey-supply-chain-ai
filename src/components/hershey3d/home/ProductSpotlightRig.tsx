"use client";

export default function ProductSpotlightRig() {
  return (
    <>
      <ambientLight intensity={0.88} />
      <directionalLight position={[4.8, 5.2, 5.6]} intensity={2.35} color="#fff4d2" />
      <pointLight position={[-3.8, 2.2, 3.4]} intensity={3.2} color="#f4c75d" />
      <pointLight position={[3.8, -1.9, 3.1]} intensity={2.2} color="#8a2e18" />
      <spotLight
        position={[0, 4.8, 4.6]}
        angle={0.42}
        penumbra={0.72}
        intensity={2.85}
        color="#ffe2a5"
      />
    </>
  );
}
