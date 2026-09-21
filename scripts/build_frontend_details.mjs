import { readFile, mkdir, writeFile, rename } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourcePaths = {
  costs: "artifacts/07_cost_model_blobs/cost_model_records_with_retail.json",
  ingredients: "artifacts/07_cost_model_blobs/ingredient_packets_costed.json",
  assumptions: "artifacts/07_cost_model_blobs/cost_assumptions_v1.json",
  retailers: "artifacts/07_cost_model_blobs/retail_price_verified.json",
  publicCosts: "public/data/hershey/enriched_display/enriched_cost_breakdown_display_v2.json",
  publicIngredients: "public/data/hershey/enriched_display/enriched_ingredient_cards_v2.json",
  evidence: "public/data/hershey/enriched_display/enriched_evidence_panel_lookup_v2.json",
};
const inputs = {}, hashes = {};
for (const [key, path] of Object.entries(sourcePaths)) {
  const bytes = await readFile(resolve(root, path));
  inputs[key] = JSON.parse(bytes.toString("utf8"));
  hashes[key] = createHash("sha256").update(bytes).digest("hex");
}
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const scenarios = ["low", "base", "high"];
const families = {
  sugar: ["COST_ING_SUGAR"],
  cocoa: ["COST_ING_COCOA_CHOCOLATE", "COST_ING_COCOA_BUTTER"],
  dairy: ["COST_ING_MILK", "COST_ING_SKIM_MILK", "COST_ING_MILK_FAT"],
  minor: ["COST_ING_SOY_LECITHIN", "COST_ING_PGPR", "COST_ING_NATURAL_FLAVOR"],
  packaging: ["COST_PACKAGING_PRIMARY_SECONDARY"],
  manufacturing: ["COST_MANUFACTURING_CONVERSION"],
  logistics: ["COST_STORAGE_WAREHOUSING", "COST_OUTBOUND_FREIGHT"],
  retail: ["COST_RETAIL_PRICE_VERIFIED"],
  residual: ["COST_RESIDUAL_CHANNEL_COMMERCIAL_POOL"],
};
const allowed = inputs.publicCosts.records.filter(row => row.safe_display === true);
const modelById = new Map(inputs.costs.map(row => [row.cost_bucket_id, row]));
assert(modelById.size === inputs.costs.length, "Duplicate cost bucket ID");
const exported = [];
let formulaChecks = 0;
for (const canonical of allowed) {
  const model = modelById.get(canonical.cost_bucket_id);
  assert(model, "Missing calculation owner: " + canonical.cost_bucket_id);
  for (const scenario of scenarios) {
    const key = scenario + "_cents_per_bar";
    assert(Number.isFinite(model[key]) && model[key] === canonical[key], "Cost drift: " + canonical.cost_bucket_id + "/" + scenario);
    if (model.cost_type === "ingredient") {
      const input = model.calculation_inputs;
      const calculated = input["grams_" + scenario] * input["price_" + scenario + "_per_lb"] / 453.59237 * 100;
      assert(Math.abs(calculated - model[key]) <= 0.000051, "Formula mismatch: " + canonical.cost_bucket_id + "/" + scenario);
      formulaChecks++;
    }
  }
  const family = Object.keys(families).find(key => families[key].includes(canonical.cost_bucket_id));
  assert(family, "Unclassified cost bucket: " + canonical.cost_bucket_id);
  const assumptionEntry = Object.entries(inputs.assumptions.ingredient_cost_assumptions).find(([, value]) => value.cost_bucket_id === canonical.cost_bucket_id);
  const modelIngredient = assumptionEntry ? inputs.ingredients.find(row => row.ingredient_id === assumptionEntry[0]) : null;
  if (modelIngredient) for (const scenario of scenarios) {
    assert(modelIngredient["estimated_cost_" + scenario + "_cents"] === canonical[scenario + "_cents_per_bar"], "Ingredient/cost mismatch: " + modelIngredient.ingredient_id);
  }
  exported.push({
    cost_bucket_id: canonical.cost_bucket_id,
    label: canonical.label,
    cost_type: canonical.cost_type,
    family,
    unit: "cents_per_bar",
    low_cents_per_bar: canonical.low_cents_per_bar,
    base_cents_per_bar: canonical.base_cents_per_bar,
    high_cents_per_bar: canonical.high_cents_per_bar,
    calculation_inputs: model.calculation_inputs || null,
    model_ingredient_id: modelIngredient?.ingredient_id || null,
    price_input_unit: modelIngredient ? "USD_per_pound" : null,
    quantity_input_unit: modelIngredient ? "grams_per_bar" : null,
    ingredient_story: modelIngredient ? {
      origin: modelIngredient.origin_logic || null,
      processing: modelIngredient.processing_logic || null,
      process_steps: (modelIngredient.processing_logic || "").split("→").map(value => value.trim()).filter(Boolean),
      supplier_scope: modelIngredient.supplier_status || null,
      limitations: modelIngredient.supplier_limitations || [],
    } : null,
    calculation_reference_namespace: "legacy_EV",
    calculation_reference_ids: model.source_evidence_ids || [],
    current_context_reference_namespace: "enriched_EEVID",
    current_context_reference_ids: assumptionEntry
      ? Object.values(inputs.evidence).filter(e => e.public_display_allowed === true && e.packet === assumptionEntry[1].evidence_packet).map(e => e.evidence_id)
      : [],
    confidence_level: canonical.confidence_level,
    cost_logic: canonical.cost_logic,
    notes: canonical.notes,
  });
}
const ids = new Set(exported.map(r => r.cost_bucket_id));
const aliases = {
  ING_CHOCOLATE: "ING_COCOA_CHOCOLATE",
  ING_COCOA: "ING_COCOA_CHOCOLATE",
  ING_PACKAGING__WRAPPER: "ING_PACKAGING_WRAPPER",
};
const ingredientLinks = inputs.publicIngredients.map(card => {
  const modelId = aliases[card.ingredient_id] || card.ingredient_id;
  const model = inputs.ingredients.find(r => r.ingredient_id === modelId);
  const matching = exported.filter(row => row.model_ingredient_id === modelId).map(row => row.cost_bucket_id);
  const role = card.ingredient_id === "ING_TARGET_SKU__PRODUCT_LABEL" ? "product" : modelId === "ING_PACKAGING_WRAPPER" ? "packaging" : "ingredient";
  if (role === "packaging") matching.push("COST_PACKAGING_PRIMARY_SECONDARY");
  if (role === "ingredient") assert(model && matching.length === 1, "Missing explicit ingredient join: " + card.ingredient_id);
  return { display_ingredient_id: card.ingredient_id, model_ingredient_id: model?.ingredient_id || null, role, cost_bucket_ids: matching, shared_bucket: modelId === "ING_COCOA_CHOCOLATE", join_note: modelId === "ING_COCOA_CHOCOLATE" ? "Chocolate and Cocoa reference one combined modeled bucket. Count it once." : null };
});
const retailers = inputs.retailers.verified_retail_prices.filter(r => r.validation_passed === true && r.verification_status === "verified").map(row => {
  assert(Math.abs(row.verified_price_usd * 100 - row.verified_price_cents) < 0.00001, "Retail unit mismatch: " + row.retailer);
  const related = Object.values(inputs.evidence).filter(e => e.public_display_allowed === true && e.file_name === row.file_name);
  assert(related.length, "No current approved source context: " + row.retailer);
  return { retailer: row.retailer, price_cents_per_bar: row.verified_price_cents, review_id: row.review_id, source_file: row.file_name, product_name: row.verified_product_name, pack_size: row.verified_pack_size, observation_date: row.verified_date_visible || null, store_or_zip: row.verified_store_or_zip_visible || null, verification_status: row.verification_status, related_current_evidence_ids: related.map(e => e.evidence_id) };
});
assert(retailers.length > 0, "No eligible retailer observations");
const mean = retailers.reduce((sum, row) => sum + row.price_cents_per_bar, 0) / retailers.length;
assert(mean === inputs.publicCosts.retail_price.base_cents_per_bar, "Retail mean does not match published model");
const familyTotals = Object.fromEntries(Object.entries(families).map(([family, members]) => [family, {
  cost_bucket_ids: members.filter(id => ids.has(id)),
  ...Object.fromEntries(scenarios.map(scenario => [scenario + "_cents_per_bar", Number(exported.filter(r => members.includes(r.cost_bucket_id)).reduce((sum, r) => sum + r[scenario + "_cents_per_bar"], 0).toFixed(4))])),
}]));
for (const scenario of scenarios) {
  const physical = exported.filter(r => !["retail", "residual"].includes(r.family)).reduce((sum, r) => sum + r[scenario + "_cents_per_bar"], 0);
  assert(Math.abs(physical - inputs.publicCosts.physical_cost[scenario + "_cents_per_bar"]) < 0.000051, "Physical cost total mismatch");
}
const output = {
  version: "frontend_detail_adapter_v1",
  canonical_cost_version: inputs.publicCosts.display_version,
  unit: inputs.publicCosts.unit,
  source_sha256: hashes,
  buckets: exported,
  ingredient_links: ingredientLinks,
  family_totals: familyTotals,
  verified_retailers: retailers,
  retail_mean_cents_per_bar: mean,
  evidence_lineage_note: "Legacy calculation references and current approved context are separate namespaces; no ID equivalence is asserted.",
};
const serialized = JSON.stringify(output, null, 2) + "\n";
assert(!/[A-Za-z]:[\\/]/.test(serialized), "Local filesystem path would leak into public export");
const destination = resolve(root, "public/data/hershey/enriched_display/enriched_calculation_details_v2.json");
if (process.argv.includes("--check")) {
  assert(await readFile(destination, "utf8") === serialized, "Detail export is stale");
} else {
  await mkdir(dirname(destination), { recursive: true });
  const temporary = destination + ".tmp";
  await writeFile(temporary, serialized);
  await rename(temporary, destination);
}
console.log(JSON.stringify({ mode: process.argv.includes("--check") ? "verified" : "exported", buckets: exported.length, ingredient_links: ingredientLinks.length, formula_checks: formulaChecks, verified_retailers: retailers.length, sha256: createHash("sha256").update(serialized).digest("hex") }, null, 2));
