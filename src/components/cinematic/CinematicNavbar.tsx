"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Factory, Menu, ShieldCheck, X } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
  { label: "HOME", href: "/" },
  { label: "SUPPLY CHAIN", href: "/supply-chain" },
  { label: "EVIDENCE BRAIN", href: "/evidence-brain" },
  { label: "COST MODEL", href: "/cost-model" },
  { label: "SOURCES", href: "/sources" },
  { label: "METHODOLOGY", href: "/methodology" },
];

export default function CinematicNavbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      <nav className="sticky top-0 z-50 border-b border-[#2a0805]/10 bg-[#fffaf3]/88 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2a0805] text-amber-100 shadow-lg">
              <Factory size={21} />
            </div>
            <div>
              <p className="text-lg font-black leading-none tracking-tight text-[#2a0805]">
                HERSHEY
              </p>
              <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                Supply Chain AI
              </p>
            </div>
          </Link>

          <div className="hidden items-center gap-1 rounded-full border border-[#1d0b06]/10 bg-white/75 p-1 shadow-sm xl:flex">
            {navItems.map((item) => {
              const active =
                item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative rounded-full px-4 py-2 text-[11px] font-black uppercase tracking-[0.16em] transition ${
                    active
                      ? "bg-[#2a0805] text-amber-50 shadow-md"
                      : "text-[#4d3a31] hover:bg-[#2a0805]/8 hover:text-[#2a0805]"
                  }`}
                >
                  {item.label}
                  {active && (
                    <motion.span
                      layoutId="hershey-navbar-active"
                      className="absolute inset-0 -z-10 rounded-full bg-[#2a0805]"
                      transition={{ type: "spring", stiffness: 380, damping: 32 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>

          <div className="hidden items-center gap-3 lg:flex">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-50 px-4 py-2 text-[11px] font-black uppercase tracking-[0.18em] text-emerald-700">
              <ShieldCheck size={14} />
              JSON-first
            </div>
            <div className="rounded-full border border-[#1d0b06]/10 bg-[#2a0805] px-4 py-2 text-[11px] font-black uppercase tracking-[0.18em] text-amber-100">
              Study Project
            </div>
          </div>

          <button
            type="button"
            onClick={() => setOpen(true)}
            className="flex h-11 w-11 items-center justify-center rounded-2xl border border-[#2a0805]/10 bg-white text-[#2a0805] xl:hidden"
            aria-label="Open navigation"
          >
            <Menu size={20} />
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed inset-0 z-[80] bg-[#080202]/80 p-4 backdrop-blur-xl xl:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="h-full rounded-[2rem] border border-white/10 bg-[#fffaf3] p-6 text-[#2a0805] shadow-2xl"
              initial={{ opacity: 0, y: 18, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 18, scale: 0.98 }}
              transition={{ duration: 0.28 }}
            >
              <div className="mb-8 flex items-center justify-between">
                <div>
                  <p className="text-xl font-black">HERSHEY</p>
                  <p className="text-[10px] font-black uppercase tracking-[0.25em] text-[#9c6a27]">
                    Supply Chain AI
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#2a0805] text-amber-100"
                  aria-label="Close navigation"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="grid gap-3">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className="rounded-3xl border border-[#2a0805]/10 bg-white px-5 py-4 text-sm font-black uppercase tracking-[0.18em]"
                  >
                    {item.label}
                  </Link>
                ))}
              </div>

              <div className="mt-8 rounded-3xl border border-[#2a0805]/10 bg-[#f8f4ed] p-5 text-sm leading-6 text-[#51433d]">
                Academic/professional study project. Evidence claims remain JSON-first and
                public-source based.
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}