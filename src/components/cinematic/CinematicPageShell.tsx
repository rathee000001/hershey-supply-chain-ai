"use client";

import type { ReactNode } from "react";
import CinematicNavbar from "@/components/cinematic/CinematicNavbar";
import ChocolateAtmosphere from "@/components/cinematic/ChocolateAtmosphere";
import ProductIdentityBadge from "@/components/cinematic/ProductIdentityBadge";

type PageMood = "portfolio" | "chocolate" | "dark";
type FooterMode = "light" | "dark";

type CinematicPageShellProps = {
  children: ReactNode;
  footerMode?: FooterMode;
  pageMood?: PageMood;
  showFloatingProductBadge?: boolean;
};

function getShellClasses(pageMood: PageMood) {
  if (pageMood === "dark") {
    return "relative min-h-screen overflow-hidden bg-[#070202] text-[#fff8ea]";
  }

  if (pageMood === "chocolate") {
    return "relative min-h-screen overflow-hidden bg-[#120503] text-[#fff8ea]";
  }

  return "relative min-h-screen overflow-hidden bg-[#f8f1e7] text-[#20100b]";
}

function getSurfaceClasses(pageMood: PageMood) {
  if (pageMood === "dark") {
    return "pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_50%_-12%,rgba(128,47,25,0.32),transparent_38%),linear-gradient(to_bottom,rgba(7,2,2,0.85),rgba(18,6,3,0.96))]";
  }

  if (pageMood === "chocolate") {
    return "pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_50%_-10%,rgba(115,35,18,0.42),transparent_40%),radial-gradient(circle_at_8%_28%,rgba(232,181,74,0.14),transparent_28%),linear-gradient(to_bottom,#1a0603,#100403_46%,#fff7eb_46%,#f8f1e7)]";
  }

  return "pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_62%_8%,rgba(105,45,25,0.13),transparent_31%),radial-gradient(circle_at_12%_14%,rgba(225,185,94,0.18),transparent_24%),linear-gradient(to_bottom,#fffaf2_0%,#f8f1e7_54%,#f6eadc_100%)]";
}

function Footer({ mode }: { mode: FooterMode }) {
  const dark = mode === "dark";

  return (
    <footer
      className={
        dark
          ? "relative z-10 border-t border-white/10 bg-[#070202]/88 px-6 py-10 text-white/64 backdrop-blur-xl"
          : "relative z-10 border-t border-[#3a160d]/10 bg-[#fffaf2]/92 px-6 py-10 text-[#5e4a3f] backdrop-blur-xl"
      }
    >
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[0.9fr_1.8fr] lg:items-start">
        <div>
          <p
            className={
              dark
                ? "text-[10px] font-black uppercase tracking-[0.28em] text-[#f4c75d]"
                : "text-[10px] font-black uppercase tracking-[0.28em] text-[#9c6a27]"
            }
          >
            Hershey AI Lab
          </p>
          <p
            className={
              dark
                ? "mt-2 text-xl font-black tracking-tight text-white"
                : "mt-2 text-xl font-black tracking-tight text-[#2d0d06]"
            }
          >
            Hershey Supply Chain AI
          </p>
          <p className="mt-2 text-sm font-semibold">
            Study project by Praveen Rathee · MGMT 780
          </p>
        </div>

        <div
          className={
            dark
              ? "rounded-[1.75rem] border border-white/10 bg-white/[0.04] p-5 text-sm leading-7 text-white/68"
              : "rounded-[1.75rem] border border-[#3a160d]/10 bg-white/72 p-5 text-sm leading-7 text-[#5d4a40] shadow-sm"
          }
        >
          <p>
            This website is an academic/professional study project using public-source evidence,
            benchmark data, and visual prototyping assets. It is not affiliated with, endorsed by,
            or sponsored by The Hershey Company, its suppliers, or any retailers shown.
          </p>
          <p className="mt-3">
            Product names, logos, trademarks, screenshots, and referenced visuals belong to their
            respective owners. Evidence claims are not made from decorative visuals; claims come from
            audited JSON evidence artifacts.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default function CinematicPageShell({
  children,
  footerMode = "light",
  pageMood = footerMode === "dark" ? "dark" : "portfolio",
  showFloatingProductBadge = false,
}: CinematicPageShellProps) {
  const atmosphereMode = pageMood === "portfolio" ? "light" : "dark";

  return (
    <main className={getShellClasses(pageMood)} data-page-mood={pageMood}>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-full focus:bg-[#2d0d06] focus:px-4 focus:py-3 focus:text-sm focus:font-black focus:text-white"
      >
        Skip to main content
      </a>

      <div className={getSurfaceClasses(pageMood)} aria-hidden="true" />
      <ChocolateAtmosphere mode={atmosphereMode} />

      <CinematicNavbar />

      {showFloatingProductBadge ? (
        <div className="pointer-events-none fixed bottom-6 left-6 z-40 hidden lg:block">
          <ProductIdentityBadge variant="floating" />
        </div>
      ) : null}

      <div id="main-content" className="relative z-10">
        {children}
      </div>

      <Footer mode={footerMode} />
    </main>
  );
}
