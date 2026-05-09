from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


ROOT = Path("D:/HersheySupplyChainAI").resolve()


FILES = {
    "package.json": {
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint"
        },
        "dependencies": {
            "@react-three/drei": "latest",
            "@react-three/fiber": "latest",
            "framer-motion": "latest",
            "lucide-react": "latest",
            "next": "latest",
            "react": "latest",
            "react-dom": "latest",
            "recharts": "latest",
            "three": "latest"
        },
        "devDependencies": {
            "@types/node": "latest",
            "@types/react": "latest",
            "@types/react-dom": "latest",
            "autoprefixer": "latest",
            "postcss": "latest",
            "tailwindcss": "latest",
            "typescript": "latest"
        }
    },
    "tsconfig.json": {
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./src/*"]}
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    },
    "postcss.config.js": """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""",
    "tailwind.config.ts": """import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
""",
    "next.config.ts": """import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
""",
    "src/app/globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --hershey-dark: #2b0909;
  --hershey-brown: #4b1d16;
  --cream: #fff7ed;
}

html {
  scroll-behavior: smooth;
}

body {
  background: #fff7ed;
  color: #24100c;
}

* {
  box-sizing: border-box;
}
""",
    "src/app/layout.tsx": """import type { Metadata } from "next";
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
""",
    "src/app/page.tsx": """"use client";

import Link from "next/link";
import { ArrowRight, Boxes, LineChart, Network } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-[#fff7ed] via-[#f8eadb] to-[#ead0bd] text-[#24100c]">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 py-16">
        <div className="max-w-4xl">
          <p className="mb-4 inline-flex rounded-full border border-[#4b1d16]/20 bg-white/60 px-4 py-2 text-sm font-semibold uppercase tracking-[0.25em] text-[#4b1d16]">
            Public-Evidence Benchmark Model
          </p>

          <h1 className="text-5xl font-black tracking-tight md:text-7xl">
            Hershey 1.55 oz Milk Chocolate Supply Chain Intelligence
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-[#5a3328]">
            Interactive artifact-driven supply chain model for ingredient sourcing,
            supplier confidence, manufacturing flow, logistics, verified retail price,
            and benchmark cost breakdown.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/supply-chain"
              className="inline-flex items-center gap-2 rounded-2xl bg-[#4b1d16] px-6 py-4 font-bold text-white shadow-xl transition hover:scale-[1.02]"
            >
              Open Supply Chain Model <ArrowRight size={20} />
            </Link>
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-3">
          {[
            ["JSON-First", "Frontend reads only public artifacts.", Boxes],
            ["Interactive Graph", "35 nodes and 36 edges prepared.", Network],
            ["Cost Intelligence", "Physical cost, retail price, and residual pool.", LineChart],
          ].map(([title, text, Icon]) => (
            <div key={String(title)} className="rounded-3xl border border-[#4b1d16]/10 bg-white/60 p-6 shadow-lg backdrop-blur">
              <Icon className="mb-4 text-[#4b1d16]" size={28} />
              <h2 className="text-xl font-black">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-[#6f4a3d]">{text}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
"""
}


def write_file_if_missing(relative_path: str, content) -> str:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        return "exists_skipped"

    if isinstance(content, dict):
        path.write_text(json.dumps(content, indent=2), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")

    return "created"


def main() -> None:
    results = []

    for rel_path, content in FILES.items():
        status = write_file_if_missing(rel_path, content)
        results.append({"file": rel_path, "status": status})

    report_dir = ROOT / "artifacts" / "10_run_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "run_name": "step17a_frontend_scaffold_guard",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT).replace("\\", "/"),
        "files": results,
        "next_step": "Run npm install, then Step 17B build the /supply-chain artifact-driven page.",
    }

    report_path = report_dir / "step17a_frontend_scaffold_guard_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("")
    print("STEP 17A FRONTEND SCAFFOLD GUARD COMPLETE")
    print("-----------------------------------------")
    for item in results:
        print(f"{item['status']}: {item['file']}")
    print("")
    print(f"Report JSON: {report_path}")
    print("")


if __name__ == "__main__":
    main()