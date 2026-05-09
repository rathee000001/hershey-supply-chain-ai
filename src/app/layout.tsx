import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
