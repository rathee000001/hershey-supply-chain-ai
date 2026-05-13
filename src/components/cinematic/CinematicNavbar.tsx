"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ExternalLink, Menu, X } from "lucide-react";
import { useEffect, useState } from "react";

type NavItem = {
  label: string;
  href: string;
};

const navItems: NavItem[] = [
  { label: "Home", href: "/" },
  { label: "Supply Chain", href: "/supply-chain" },
  { label: "Evidence", href: "/evidence-brain" },
  { label: "Cost", href: "/cost-model" },
  { label: "Sources", href: "/sources" },
  { label: "Method", href: "/methodology" },
];

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function isActiveRoute(pathname: string, href: string) {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(href + "/");
}

export default function CinematicNavbar() {
  const pathname = usePathname() || "/";
  const prefersReducedMotion = useReducedMotion();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();

    window.addEventListener("scroll", onScroll, { passive: true });

    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <>
      <header className="pointer-events-none fixed left-0 right-0 top-0 z-50 h-24">
        <motion.nav
          className="relative h-full w-full px-2 sm:px-3 lg:px-4"
          initial={prefersReducedMotion ? false : { opacity: 0, y: -12 }}
          animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
          aria-label="Primary navigation"
        >
          <Link
            href="/"
            className={cx(
              "pointer-events-auto absolute left-2 top-3 hidden rounded-full border px-4 py-2.5 text-[9px] font-black uppercase tracking-[0.28em] shadow-xl backdrop-blur-xl transition duration-300 md:left-3 lg:left-4 lg:inline-flex",
              scrolled
                ? "border-[#f7d66d]/40 bg-[#151820]/98 text-[#fff1a8] shadow-[#3a160d]/20"
                : "border-[#f7d66d]/45 bg-[#151820]/98 text-[#fff1a8] shadow-slate-950/18",
            )}
          >
            Hershey AI Lab
          </Link>

          <Link
            href="/"
            className={cx(
              "pointer-events-auto absolute left-3 top-3 flex items-center gap-3 rounded-full border px-3 py-2 shadow-xl backdrop-blur-2xl transition duration-300 sm:left-1/2 sm:-translate-x-1/2 lg:left-[350px] lg:translate-x-0",
              scrolled
                ? "border-white/95 bg-white/96 shadow-slate-300/55"
                : "border-white/90 bg-white/94 shadow-slate-200/65",
            )}
            aria-label="Hershey Supply Chain AI home"
          >
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-[#060711] text-[10px] font-black uppercase tracking-[0.08em] text-[#fff1a8] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]">
              RIL
            </span>

            <span className="hidden min-w-0 pr-1 sm:block">
              <span className="block text-[10px] font-black uppercase tracking-[0.34em] text-[#9a6a28]">
                Portfolio
              </span>
              <span className="mt-0.5 block max-w-[230px] truncate text-sm font-black leading-none tracking-tight text-[#2d0d06]">
                Hershey Supply Chain AI
              </span>
            </span>
          </Link>

          <div
            className={cx(
              "pointer-events-auto absolute right-4 top-3 hidden items-center gap-1 rounded-full border px-2 py-2 text-sm font-black shadow-xl backdrop-blur-2xl transition duration-300 xl:flex",
              scrolled
                ? "border-white/95 bg-white/96 shadow-slate-300/55"
                : "border-white/90 bg-white/94 shadow-slate-200/65",
            )}
          >
            {navItems.map((item) => {
              const active = isActiveRoute(pathname, item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cx(
                    "relative isolate overflow-hidden rounded-full px-4 py-3 transition duration-300",
                    active
                      ? "text-white"
                      : "text-[#2d0d06] hover:bg-slate-950 hover:text-white",
                  )}
                >
                  {active ? (
                    <motion.span
                      layoutId="portfolio-style-hershey-nav-active"
                      className="absolute inset-0 -z-10 rounded-full bg-[#2d0d06] shadow-[0_12px_28px_rgba(45,13,6,0.22)]"
                      transition={{ type: "spring", stiffness: 440, damping: 34 }}
                    />
                  ) : null}
                  <span className="relative z-10">{item.label}</span>
                </Link>
              );
            })}

            <a
              href="https://github.com/rathee000001/hershey-supply-chain-ai"
              target="_blank"
              rel="noreferrer"
              className="ml-1 inline-flex items-center gap-2 rounded-full bg-[#2d0d06] px-4 py-3 text-white transition duration-300 hover:-translate-y-0.5 hover:bg-[#43150b]"
            >
              Repo
              <ExternalLink size={14} strokeWidth={2.6} />
            </a>
          </div>

          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="pointer-events-auto absolute right-3 top-3 grid h-12 w-12 place-items-center rounded-full border border-slate-200 bg-white/96 text-[#2d0d06] shadow-xl shadow-slate-200/60 backdrop-blur-xl transition hover:bg-slate-950 hover:text-white xl:hidden"
            aria-label="Open navigation"
            aria-expanded={mobileOpen}
          >
            <Menu size={21} strokeWidth={2.6} />
          </button>
        </motion.nav>
      </header>

      <div className="h-24" aria-hidden="true" />

      <AnimatePresence>
        {mobileOpen ? (
          <motion.div
            className="fixed inset-0 z-[90] bg-[#090403]/62 p-3 backdrop-blur-xl xl:hidden"
            initial={prefersReducedMotion ? false : { opacity: 0 }}
            animate={prefersReducedMotion ? undefined : { opacity: 1 }}
            exit={prefersReducedMotion ? undefined : { opacity: 0 }}
          >
            <motion.div
              className="relative flex h-full flex-col overflow-hidden rounded-[2rem] border border-white/80 bg-[#fffaf2] p-5 shadow-2xl"
              initial={prefersReducedMotion ? false : { opacity: 0, y: 18, scale: 0.98 }}
              animate={prefersReducedMotion ? undefined : { opacity: 1, y: 0, scale: 1 }}
              exit={prefersReducedMotion ? undefined : { opacity: 0, y: 18, scale: 0.98 }}
              transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="pointer-events-none absolute -right-24 -top-24 h-60 w-60 rounded-full bg-[#2d0d06]/12 blur-3xl" />
              <div className="pointer-events-none absolute -bottom-24 left-8 h-64 w-64 rounded-full bg-[#f0c85a]/18 blur-3xl" />

              <div className="relative z-10 flex items-center justify-between gap-4">
                <Link href="/" className="flex items-center gap-3">
                  <span className="grid h-12 w-12 place-items-center rounded-full bg-[#060711] text-[11px] font-black uppercase text-[#fff1a8]">
                    RIL
                  </span>
                  <span>
                    <span className="block text-[10px] font-black uppercase tracking-[0.28em] text-[#9c6a27]">
                      Hershey AI Lab
                    </span>
                    <span className="mt-1 block text-lg font-black leading-none tracking-tight text-[#2d0d06]">
                      Hershey Supply Chain AI
                    </span>
                  </span>
                </Link>

                <button
                  type="button"
                  onClick={() => setMobileOpen(false)}
                  className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-[#2d0d06] text-white shadow-lg"
                  aria-label="Close navigation"
                >
                  <X size={20} strokeWidth={2.7} />
                </button>
              </div>

              <div className="relative z-10 mt-8 grid gap-3 overflow-y-auto pb-4">
                {navItems.map((item) => {
                  const active = isActiveRoute(pathname, item.href);

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileOpen(false)}
                      aria-current={active ? "page" : undefined}
                      className={cx(
                        "rounded-3xl border px-5 py-4 text-base font-black transition",
                        active
                          ? "border-[#2d0d06] bg-[#2d0d06] text-white shadow-lg shadow-[#2d0d06]/15"
                          : "border-[#2d0d06]/10 bg-white text-[#2d0d06] hover:bg-[#fff4d5]",
                      )}
                    >
                      {item.label}
                    </Link>
                  );
                })}
              </div>

              <div className="relative z-10 mt-auto rounded-[1.5rem] border border-[#2d0d06]/10 bg-white/90 p-5">
                <p className="text-[10px] font-black uppercase tracking-[0.24em] text-[#9c6a27]">
                  Academic / professional prototype
                </p>
                <p className="mt-2 text-sm font-semibold leading-6 text-[#58463d]">
                  Evidence claims remain JSON-first and public-source based. Decorative visuals do not create factual claims.
                </p>
              </div>
            </motion.div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
