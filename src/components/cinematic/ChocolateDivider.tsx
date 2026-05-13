"use client";

import ChocolateFlowDivider from "@/components/cinematic/ChocolateFlowDivider";

type ChocolateDividerProps = {
  className?: string;
  height?: number;
  variant?: "cream-to-chocolate" | "chocolate-to-cream";
};

export default function ChocolateDivider({
  className,
  height,
  variant,
}: ChocolateDividerProps) {
  return (
    <ChocolateFlowDivider
      className={className}
      height={height}
      variant={variant}
    />
  );
}
