"use client";

import { ReactNode } from "react";
import CinematicNavbar from "@/components/cinematic/CinematicNavbar";
import ChocolateAtmosphere from "@/components/cinematic/ChocolateAtmosphere";
import ProductIdentityBadge from "@/components/cinematic/ProductIdentityBadge";

type CinematicPageShellProps = {
  children: ReactNode;
  footerMode?: "light" | "dark";
  showFloatingProductBadge?: boolean;
};

export default function CinematicPageShell({
  children,
  footerMode = "light",
  showFloatingProductBadge = false,
}: CinematicPageShellProps) {
  const dark = footerMode === "dark";

  return (
    <main
      className={
        dark
          ? "relative min-h-screen overflow-hidden bg-[#080202] text-white"
          : "relative min-h-screen overflow-hidden bg-[#f8f4ed] text-[#110706]"
      }
    >
      <ChocolateAtmosphere mode={dark ? "dark" : "light"} />
      <CinematicNavbar />

      {showFloatingProductBadge && <ProductIdentityBadge variant="floating" />}

      <div className="relative z-10">{children}</div>

      <footer
        className={
          dark
            ? "relative z-10 border-t border-white/10 bg-black/30 px-6 py-8 text-white/55"
            : "relative z-10 border-t border-[#2a0805]/10 bg-[#fffaf3]/80 px-6 py-8 text-[#51433d] backdrop-blur"
        }
      >
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm lg:flex-row lg:items-center lg:justify-between">
          <p>© 2026 Hershey Supply Chain AI · Study project by Praveen Rathee</p>
          <p className="max-w-3xl text-xs leading-5">
            Academic/professional study project using public-source evidence and benchmark
            modeling. Not affiliated with, endorsed by, or sponsored by The Hershey Company.
          </p>
        </div>
      </footer>
    </main>
  );
}
