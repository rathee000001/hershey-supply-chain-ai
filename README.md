# Hershey Supply Chain AI

**One bar. A whole supply chain.**

An independent research project that makes the ingredients, manufacturing, distribution, evidence and estimated costs behind a HERSHEY’S 1.55 oz milk chocolate bar explorable.

[Explore the website](https://hershey-supply-chain-ai.vercel.app/)

The website combines an animated supply-chain model with source-backed detail panels and an original-document reader. Its purpose is to help people understand the system around a familiar product while keeping facts, company-level context and modeled estimates distinct.

## Explore the project

| Page | What you can explore |
| --- | --- |
| **Home** | The product story, ingredient groups, the factory-to-shelf journey and the scope of the study. |
| **Supply Chain** | Ingredients, company context, production stages and the recorded connections between them. |
| **Evidence** | Research by subject, what a record supports, and the original report behind it. |
| **Cost Model** | Ingredient quantities, benchmark prices, operating allocations and low/base/high estimates. |
| **Sources** | Unique documents grouped by research family, plus a separate explanation of the illustrative artwork. |
| **How It Works** | Collection, extraction, evidence review, structured records, graph construction and the website. |

Select a subject in an animation to inspect it. Selecting another subject changes the open detail view. Section navigation lets you move through each page’s story; motion can be paused, and reduced-motion preferences are respected.

## What the research contains

The published model includes **35 subjects and 36 connections**, supported by a display collection containing **869 records approved for public explanation**. Related ingredient, supplier, cost and logistics records retain their source context.

A local retrieval index built from document text, tables and recognized image text helps locate relevant material when preparing panel context. A retrieved document is not automatically treated as direct evidence for a relationship: assigned evidence is distinguished from wider related research.

Original reports can be read with their actual page layout, page navigation and zoom. Extracted text is not substituted for a missing report. Illustrative factories, trucks, people and ingredient objects are kept separate from source evidence.

## Understanding the cost model

The estimate separates five contributions:

- Ingredients
- Packaging
- Manufacturing conversion
- Storage and warehousing
- Outbound freight

Ingredient estimates use modeled quantities and benchmark prices. Shared operating allocations are counted once, not charged again at every animation node.

Shelf-price observations are recorded separately for **CVS, Target, Walgreens and Walmart**. These are saved research observations, not current retailer quotes. The difference between a physical-cost estimate and an observed shelf price is a **channel/commercial gap—not a profit calculation**.

## Scope and limitations

This project does **not** claim to reveal:

- The exact farm, supplier allocation or shipment route for an individual bar.
- Hershey’s proprietary recipe, internal invoices or actual unit-production costs.
- Profit or margin from the difference between estimated cost and retail price.
- Live retailer prices, live shipment tracking or a newly running AI audit.

Company-level partnerships, product-label evidence, background research and benchmark assumptions answer different questions. Source documents and their qualifications should be read together. Scanned documents can contain recognition errors.

## Run locally

Use a current Node.js release compatible with the locked Next.js dependencies and npm.

```bash
npm ci
npm run dev
```

Open `http://localhost:3000`.

For a production build:

```bash
npm run build
npm start
```

The website reads the published JSON data and bundled document assets. Viewing it does not require an AI-provider API key. Rebuilding the research index or regenerating evidence artifacts is a separate research workflow requiring the original local inputs; the website does not rerun it on each visit.

## Built with

Next.js, React, TypeScript, Three.js/WebGL, CSS glass controls and PDF.js. Research tooling combines document extraction, OCR, sparse text retrieval, evidence qualification and structured graph/cost artifacts.

## Author and attribution

Created by **Praveen Rathee** as an independent academic and technical study.

This project is not affiliated with, endorsed by or sponsored by The Hershey Company. HERSHEY’S and other product or company names, logos and source materials belong to their respective owners. Generated interface artwork is illustrative, not a photograph or certification of a named facility, route or supplier.

The shared glass-control treatment adapts MIT-licensed work by the same author from Evidence Lane. Third-party code and font notices are retained with their respective assets.
