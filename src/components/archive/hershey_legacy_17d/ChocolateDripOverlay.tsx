"use client";

type ChocolateDripOverlayProps = {
  variant?: "hero" | "section";
};

const CHOCOLATE_MELT_URL =
  "/data/hershey/visual_assets/source_assets/chocolate_melt_drip.webp";

export default function ChocolateDripOverlay({
  variant = "hero",
}: ChocolateDripOverlayProps) {
  const heightClass = variant === "hero" ? "h-48 md:h-56" : "h-32 md:h-40";

  return (
    <div
      className={`pointer-events-none absolute inset-x-0 top-0 z-30 overflow-hidden ${heightClass}`}
      aria-hidden="true"
    >
      <style>{`
        @keyframes chocolateImageFloat {
          0%, 100% {
            transform: translateX(-1.5%) translateY(-4px) scaleX(1.04);
          }
          50% {
            transform: translateX(1%) translateY(3px) scaleX(1.055);
          }
        }

        @keyframes chocolateGlossSweep {
          0% {
            transform: translateX(-35%);
            opacity: 0.12;
          }
          45% {
            opacity: 0.38;
          }
          100% {
            transform: translateX(135%);
            opacity: 0.1;
          }
        }

        .real-chocolate-melt {
          animation: chocolateImageFloat 9s ease-in-out infinite;
          filter:
            drop-shadow(0 18px 18px rgba(0, 0, 0, 0.45))
            drop-shadow(0 4px 8px rgba(60, 14, 5, 0.55));
        }

        .chocolate-gloss-sweep {
          animation: chocolateGlossSweep 8s ease-in-out infinite;
        }
      `}</style>

      <div className="relative h-full w-full">
        <img
          src={CHOCOLATE_MELT_URL}
          alt=""
          className="real-chocolate-melt absolute left-[-3%] top-[-18px] h-full w-[108%] object-fill"
          draggable={false}
        />

        <div className="chocolate-gloss-sweep absolute left-0 top-5 h-8 w-1/2 rotate-[-2deg] rounded-full bg-gradient-to-r from-transparent via-amber-100/20 to-transparent blur-md" />

        <div className="absolute inset-x-0 top-0 h-10 bg-gradient-to-b from-[#210705]/70 to-transparent" />
      </div>
    </div>
  );
}