"use client";

import ProductWrapperPlane from "@/components/hershey3d/home/ProductWrapperPlane";

type WrapperPeelPanelsProps = {
  frontUrl: string;
  backUrl: string;
};

export default function WrapperPeelPanels({ frontUrl, backUrl }: WrapperPeelPanelsProps) {
  return (
    <group data-home-product-sequence="cropped-wrapper-peel-panels">
      <ProductWrapperPlane
        url={frontUrl}
        side="peel"
        crop="left-half"
        position={[-0.62, 0.08, 0.06]}
        rotation={[0.03, 0.52, -0.18]}
        scale={[1.78, 0.94, 1]}
        opacity={0.95}
      />

      <ProductWrapperPlane
        url={frontUrl}
        side="peel"
        crop="right-half"
        position={[0.72, 0.08, 0.07]}
        rotation={[0.03, -0.58, 0.18]}
        scale={[1.78, 0.94, 1]}
        opacity={0.94}
      />

      <ProductWrapperPlane
        url={backUrl}
        side="peel"
        crop="left-half"
        position={[-0.48, -0.42, -0.02]}
        rotation={[-0.09, -0.24, 0.2]}
        scale={[1.34, 0.72, 1]}
        opacity={0.5}
      />

      <ProductWrapperPlane
        url={backUrl}
        side="peel"
        crop="right-half"
        position={[0.62, -0.44, -0.03]}
        rotation={[-0.08, 0.26, -0.18]}
        scale={[1.34, 0.72, 1]}
        opacity={0.5}
      />
    </group>
  );
}
