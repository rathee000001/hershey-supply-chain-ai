export const ENRICHED_FRONTEND_MANIFEST_URL =
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
