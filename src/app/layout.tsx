import type { Metadata } from "next";
import "./globals.css";
import "@/components/hershey/frosted-surfaces.css";
import "@/components/hershey/navigation-glass.css";
import "@/components/hershey/story-objects.css";
import "@/components/hershey/object-selector-cleanup.css";
import "@/components/hershey/reference-control-skin.css";
import "@/components/hershey/panel-interaction-fixes.css";
import "@/components/hershey/panel-fit.css";
import "@/components/hershey/interaction-affordance.css";
import "@/components/hershey/story-questions.css";
import { SceneSessionProvider } from "@/components/hershey/SceneSession";
import ReadingBoundary from "@/components/hershey/ReadingBoundary";
import GlassControlLighting from "@/components/hershey/GlassControlLighting";

export const metadata: Metadata = {
  title: "Hershey Supply Chain Intelligence",
  description: "Public-evidence benchmark supply chain and cost model for HERSHEY'S 1.55 oz milk chocolate bar.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-scroll-behavior="smooth" suppressHydrationWarning>
      <body suppressHydrationWarning><SceneSessionProvider><ReadingBoundary/><GlassControlLighting/>{children}</SceneSessionProvider></body>
    </html>
  );
}
