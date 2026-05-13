from pathlib import Path
import json
import shutil
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

# ------------------------------------------------------------
# 1. Hard-disable every root-level TS/TSX file in src/components/hershey
#    because old 17D files are still being compiled by VS Code/Next.
#    This does NOT touch subfolders like evidence / cost / fallback.
# ------------------------------------------------------------
hershey_root = root / "src" / "components" / "hershey"
archive_dest = root / "project_archive" / "disabled_src_components_hershey_root_17e"
archive_dest.mkdir(parents=True, exist_ok=True)

disabled_src_files = []

if hershey_root.exists():
    for path in list(hershey_root.glob("*.tsx")) + list(hershey_root.glob("*.ts")):
        if path.name.endswith(".d.ts"):
            continue

        dest = archive_dest / f"{path.name}.disabled.txt"
        counter = 1
        while dest.exists():
            dest = archive_dest / f"{path.stem}_{counter}{path.suffix}.disabled.txt"
            counter += 1

        shutil.move(str(path), str(dest))
        disabled_src_files.append({
            "from": str(path).replace("\\", "/"),
            "to": str(dest).replace("\\", "/"),
        })

    keep = hershey_root / ".gitkeep"
    keep.write_text("", encoding="utf-8")


# ------------------------------------------------------------
# 2. Remake canonical enrichedArtifacts.ts from scratch.
# ------------------------------------------------------------
lib_dir = root / "src" / "lib" / "hershey"
lib_dir.mkdir(parents=True, exist_ok=True)

enriched_path = lib_dir / "enrichedArtifacts.ts"

enriched_code = r'''export const ENRICHED_FRONTEND_MANIFEST_URL =
  "/data/hershey/enriched_display/enriched_frontend_manifest_v2.json";

export type HersheyFrontendManifest = {
  manifest_version?: string;
  created_at?: string;
  project?: string;
  unit?: string;
  base_public_path?: string;
  frontend_rule?: string;
  final_goal?: string;
  audit_summary?: {
    approved_display_candidates?: number;
    context_only_evidence?: number;
    rejected_evidence?: number;
    audit_status_counts?: Record<string, number>;
  };
  safe_display_rules?: string[];
  primary_artifacts: {
    evidence: string;
    packet_summary: string;
    suppliers: string;
    ingredients: string;
    cost_breakdown: string;
    graph: string;
    home_cards: string;
  };
};

export type HomeCard = {
  card_id?: string;
  title?: string;
  value?: string;
  subtitle?: string;
  display_type?: string;
  safe_note?: string;
};

export type EvidencePreview = {
  evidence_id?: string;
  file_name?: string;
  packet?: string;
  source_type?: string;
  primary_claim_role?: string;
  claim_strength?: string;
  safe_scope?: string;
  relationship_strength?: string;
  confidence_level?: string;
  strict_audit_status?: string;
  public_display_allowed?: boolean;
  context_display_allowed?: boolean;
  audited_safe_website_wording?: string;
  evidence_text_preview?: string;
};

export type GraphNode = {
  id?: string;
  type?: string;
  label?: string;
  description?: string;
  relationshipStatus?: string;
  confidenceLevel?: string;
  companyName?: string;
  material?: string;
  hoverSummary?: string;
  enrichedApprovedEvidenceCount?: number;
  enrichedEvidencePackets?: string[];
  enrichedEvidencePreview?: EvidencePreview[];
};

export type GraphEdge = {
  id?: string;
  source?: string;
  target?: string;
  flowType?: string;
  materialFlow?: string;
  relationshipStatus?: string;
  confidenceLevel?: string;
  animationType?: string;
  tooltipText?: string;
};

export type GraphPayload = {
  payload_version?: string;
  project?: string;
  unit?: string;
  safe_display_rules?: string[];
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type SupplierCard = {
  supplier_packet_id?: string;
  safe_display_name?: string;
  related_ingredient_or_stage?: string;
  relationship_level?: string;
  sku_level_confirmed?: boolean;
  confidence_level?: string;
  approved_evidence_count?: number;
  safe_website_wording?: string;
  limits?: string[];
  approved_evidence_preview?: EvidencePreview[];
};

export type IngredientCard = {
  ingredient_id?: string;
  ingredient_name?: string;
  packet?: string;
  label_order_position?: number;
  label_status?: string;
  supplier_status?: string;
  confirmed_supplier_names?: string[];
  sku_level_supplier_confirmed?: boolean;
  confidence_level?: string;
  approved_evidence_count?: number;
  origin_logic?: string;
  processing_logic?: string;
  supplier_limitations?: string[];
  approved_evidence_preview?: EvidencePreview[];
};

export type CostBreakdown = {
  display_version?: string;
  unit?: string;
  enriched_audit_note?: string;
  physical_cost?: {
    low_cents_per_bar?: number;
    base_cents_per_bar?: number;
    high_cents_per_bar?: number;
    low_usd_per_bar?: number;
    base_usd_per_bar?: number;
    high_usd_per_bar?: number;
  };
  retail_price?: {
    low_cents_per_bar?: number;
    base_cents_per_bar?: number;
    high_cents_per_bar?: number;
    low_usd_per_bar?: number;
    base_usd_per_bar?: number;
    high_usd_per_bar?: number;
    retailers_verified?: number;
  };
  residual_channel_pool?: {
    low_cents_per_bar?: number;
    base_cents_per_bar?: number;
    high_cents_per_bar?: number;
    physical_cost_share_of_retail_base_case?: number;
    safe_display_wording?: string;
  };
  enriched_evidence_by_cost_area?: Array<{
    cost_area?: string;
    packet?: string;
    approved_evidence_count?: number;
    approved_evidence_preview?: EvidencePreview[];
  }>;
};

export type PacketSummary = {
  packet?: string;
  display_name?: string;
  total_evidence_seen?: number;
  approved_display_count?: number;
  context_only_count?: number;
  rejected_count?: number;
  role_counts?: Record<string, number>;
  safe_scope_counts?: Record<string, number>;
  source_type_counts?: Record<string, number>;
  approved_evidence_ids?: string[];
  top_approved_evidence?: EvidencePreview[];
};

export type EvidenceLookup = Record<
  string,
  EvidencePreview & {
    entities?: string[];
    ingredients?: string[];
    risk_flags?: string[];
    audit_reasons?: string[];
    required_rewrites?: string[];
    evidence_text?: string;
  }
>;

export type EnrichedArtifacts = {
  manifest: HersheyFrontendManifest;
  homeCards: HomeCard[];
  graph: GraphPayload;
  suppliers: SupplierCard[];
  ingredients: IngredientCard[];
  costBreakdown: CostBreakdown;
  packetSummary: PacketSummary[];
  evidence: EvidenceLookup;
};

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function loadHersheyManifest(): Promise<HersheyFrontendManifest> {
  return fetchJson<HersheyFrontendManifest>(ENRICHED_FRONTEND_MANIFEST_URL);
}

export async function loadEnrichedArtifacts(): Promise<EnrichedArtifacts> {
  const manifest = await loadHersheyManifest();
  const artifacts = manifest.primary_artifacts;

  if (!artifacts) {
    throw new Error("Manifest is missing primary_artifacts.");
  }

  const [
    homeCards,
    graph,
    suppliers,
    ingredients,
    costBreakdown,
    packetSummary,
    evidence,
  ] = await Promise.all([
    fetchJson<HomeCard[]>(artifacts.home_cards),
    fetchJson<GraphPayload>(artifacts.graph),
    fetchJson<SupplierCard[]>(artifacts.suppliers),
    fetchJson<IngredientCard[]>(artifacts.ingredients),
    fetchJson<CostBreakdown>(artifacts.cost_breakdown),
    fetchJson<PacketSummary[]>(artifacts.packet_summary),
    fetchJson<EvidenceLookup>(artifacts.evidence),
  ]);

  return {
    manifest,
    homeCards,
    graph,
    suppliers,
    ingredients,
    costBreakdown,
    packetSummary,
    evidence,
  };
}
'''

enriched_path.write_text(enriched_code, encoding="utf-8")


# ------------------------------------------------------------
# 3. Fix tsconfig alias and remove deprecated baseUrl warning.
# ------------------------------------------------------------
tsconfig_path = root / "tsconfig.json"
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))

compiler_options = tsconfig.setdefault("compilerOptions", {})
compiler_options.pop("baseUrl", None)
compiler_options["paths"] = {
    "@/*": ["./src/*"]
}

exclude = tsconfig.get("exclude", [])
if not isinstance(exclude, list):
    exclude = []

needed_excludes = [
    "node_modules",
    ".next",
    "project_archive",
    "project_archive/**/*",
    "src/components/archive",
    "src/components/archive/**/*",
]

for item in needed_excludes:
    if item not in exclude:
        exclude.append(item)

tsconfig["exclude"] = exclude
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")


# ------------------------------------------------------------
# 4. Delete stale Next cache.
# ------------------------------------------------------------
next_dir = root / ".next"
deleted_next = False
if next_dir.exists():
    shutil.rmtree(next_dir)
    deleted_next = True


# ------------------------------------------------------------
# 5. Scan remaining root compiled Hershey files.
# ------------------------------------------------------------
remaining_hershey_root_ts = []
if hershey_root.exists():
    for path in list(hershey_root.glob("*.tsx")) + list(hershey_root.glob("*.ts")):
        if not path.name.endswith(".d.ts"):
            remaining_hershey_root_ts.append(str(path).replace("\\", "/"))

status = "pass"
if remaining_hershey_root_ts or not enriched_path.exists():
    status = "fail"

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e6g_hard_disable_hershey_root_and_remake_enriched",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "disabled_src_components_hershey_root_files": disabled_src_files,
    "remaining_src_components_hershey_root_ts_files": remaining_hershey_root_ts,
    "enriched_artifacts_remade": str(enriched_path).replace("\\", "/"),
    "enriched_artifacts_exists": enriched_path.exists(),
    "tsconfig_paths": tsconfig["compilerOptions"].get("paths"),
    "tsconfig_baseUrl_removed": "baseUrl" not in tsconfig["compilerOptions"],
    "tsconfig_exclude": tsconfig.get("exclude", []),
    "deleted_next_cache": deleted_next,
    "next_step": "Run npm build. If VS Code Problems still shows old files after build passes, reload VS Code window.",
}

report_path = report_dir / "step17e6g_hard_disable_hershey_root_and_remake_enriched_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5G HARD DISABLE + ENRICHED REMAKE COMPLETE")
print("----------------------------------------------------")
print(f"Status:                           {status}")
print(f"Root Hershey TS/TSX disabled:     {len(disabled_src_files)}")
print(f"Remaining root Hershey TS/TSX:    {len(remaining_hershey_root_ts)}")
print(f"enrichedArtifacts.ts exists:      {enriched_path.exists()}")
print(f"tsconfig baseUrl removed:         {'baseUrl' not in tsconfig['compilerOptions']}")
print(f"Deleted .next cache:              {deleted_next}")
print(f"Report JSON:                      {report_path}")
print("")