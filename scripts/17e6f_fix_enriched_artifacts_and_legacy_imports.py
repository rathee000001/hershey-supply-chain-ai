from pathlib import Path
import json
import shutil
from datetime import datetime

root = Path("D:/HersheySupplyChainAI")

# 1. Ensure canonical file path exists.
lib_dir = root / "src" / "lib" / "hershey"
lib_dir.mkdir(parents=True, exist_ok=True)

canonical_path = lib_dir / "enrichedArtifacts.ts"

canonical_code = r'''export const ENRICHED_FRONTEND_MANIFEST_URL =
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

canonical_path.write_text(canonical_code, encoding="utf-8")

# 2. Ensure tsconfig path alias is correct.
tsconfig_path = root / "tsconfig.json"
tsconfig = json.loads(tsconfig_path.read_text(encoding="utf-8"))

compiler_options = tsconfig.setdefault("compilerOptions", {})
compiler_options["baseUrl"] = "."
paths = compiler_options.setdefault("paths", {})
paths["@/*"] = ["./src/*"]

exclude = tsconfig.get("exclude", [])
if not isinstance(exclude, list):
    exclude = []

for item in [
    "node_modules",
    ".next",
    "project_archive",
    "project_archive/**/*",
    "src/components/archive",
    "src/components/archive/**/*",
]:
    if item not in exclude:
        exclude.append(item)

tsconfig["exclude"] = exclude
tsconfig_path.write_text(json.dumps(tsconfig, indent=2), encoding="utf-8")

# 3. Move old legacy root Hershey TSX files out of src if still present.
legacy_names = {
    "CinematicAssetScene.tsx",
    "CinematicConnectedMap.tsx",
    "CinematicSupplyChainStoryboard.tsx",
    "HersheyCinematicHero.tsx",
    "ChocolateDripOverlay.tsx",
}

moved_legacy = []
hershey_root = root / "src" / "components" / "hershey"
archive_dest = root / "project_archive" / "legacy_hershey_components_disabled"
archive_dest.mkdir(parents=True, exist_ok=True)

if hershey_root.exists():
    for name in legacy_names:
        path = hershey_root / name
        if path.exists():
            dest = archive_dest / f"{name}.archive.txt"
            counter = 1
            while dest.exists():
                dest = archive_dest / f"{name}.archive_{counter}.txt"
                counter += 1
            shutil.move(str(path), str(dest))
            moved_legacy.append({
                "from": str(path).replace("\\", "/"),
                "to": str(dest).replace("\\", "/"),
            })

# 4. Rename any TS/TSX in project_archive so TypeScript cannot compile it.
renamed_archive = []
project_archive = root / "project_archive"

if project_archive.exists():
    for path in list(project_archive.rglob("*.tsx")) + list(project_archive.rglob("*.ts")):
        if path.name.endswith(".d.ts"):
            continue
        new_path = path.with_name(path.name + ".archive.txt")
        counter = 1
        while new_path.exists():
            new_path = path.with_name(path.name + f".archive_{counter}.txt")
            counter += 1
        path.rename(new_path)
        renamed_archive.append({
            "from": str(path).replace("\\", "/"),
            "to": str(new_path).replace("\\", "/"),
        })

# 5. Delete stale Next cache.
next_dir = root / ".next"
deleted_next = False
if next_dir.exists():
    shutil.rmtree(next_dir)
    deleted_next = True

# 6. Scan current state.
remaining_legacy_src = []
if hershey_root.exists():
    for name in legacy_names:
        if (hershey_root / name).exists():
            remaining_legacy_src.append(str(hershey_root / name).replace("\\", "/"))

remaining_archive_ts = []
if project_archive.exists():
    for path in list(project_archive.rglob("*.tsx")) + list(project_archive.rglob("*.ts")):
        if not path.name.endswith(".d.ts"):
            remaining_archive_ts.append(str(path).replace("\\", "/"))

status = "pass"
if not canonical_path.exists() or remaining_legacy_src or remaining_archive_ts:
    status = "fail"

report_dir = root / "artifacts" / "10_run_reports"
report_dir.mkdir(parents=True, exist_ok=True)

report = {
    "run_name": "step17e6f_fix_enriched_artifacts_and_legacy_imports",
    "run_time": datetime.now().isoformat(timespec="seconds"),
    "status": status,
    "canonical_enriched_artifacts_path": str(canonical_path).replace("\\", "/"),
    "canonical_file_exists": canonical_path.exists(),
    "tsconfig_paths": tsconfig.get("compilerOptions", {}).get("paths"),
    "moved_legacy_src_files": moved_legacy,
    "renamed_archive_ts_files": renamed_archive,
    "deleted_next_cache": deleted_next,
    "remaining_legacy_src_files": remaining_legacy_src,
    "remaining_archive_ts_files": remaining_archive_ts,
    "next_step": "Run npm build and then reload VS Code if Problems panel is stale.",
}

report_path = report_dir / "step17e6f_enriched_artifacts_import_fix_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("")
print("STEP 17E-B5F ENRICHED ARTIFACTS IMPORT FIX COMPLETE")
print("---------------------------------------------------")
print(f"Status:                      {status}")
print(f"Canonical file exists:       {canonical_path.exists()}")
print(f"Legacy src files moved:      {len(moved_legacy)}")
print(f"Archive TS files renamed:    {len(renamed_archive)}")
print(f"Remaining legacy src files:  {len(remaining_legacy_src)}")
print(f"Remaining archive TS files:  {len(remaining_archive_ts)}")
print(f"Deleted .next cache:         {deleted_next}")
print(f"Report JSON:                 {report_path}")
print("")