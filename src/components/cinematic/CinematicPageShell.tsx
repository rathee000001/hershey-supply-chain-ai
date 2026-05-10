"use client";

import { ReactNode } from "react";
import CinematicNavbar from "@/components/cinematic/CinematicNavbar";

type CinematicPageShellProps = {
  children: ReactNode;
  footerMode?: "light" | "dark";
};

export default function CinematicPageShell({
  children,
  footerMode = "light",
}: CinematicPageShellProps) {
  const dark = footerMode === "dark";

  return (
    <main
      className={
        dark
          ? "min-h-screen overflow-hidden bg-[#080202] text-white"
          : "min-h-screen overflow-hidden bg-[#f8f4ed] text-[#110706]"
      }
    >
      <CinematicNavbar />

      {children}

      <footer
        className={
          dark
            ? "border-t border-white/10 bg-black/30 px-6 py-8 text-white/55"
            : "border-t border-[#2a0805]/10 bg-[#fffaf3] px-6 py-8 text-[#51433d]"
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