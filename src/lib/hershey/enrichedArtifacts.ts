export const ENRICHED_FRONTEND_MANIFEST_URL =
  "/data/hershey/enriched_display/enriched_frontend_manifest_v2.json";

export type HersheyFrontendManifest = {
  supplemental_artifacts?: { calculation_details: string };
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
  cost?: { low: number | null; base: number | null; high: number | null };
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
  logo_path?: string;
  logo_allowed?: boolean;
  display_allowed?: boolean;
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
  records?: CostRecord[];
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

export type CostRecord = {
  ingredient_story?: { origin: string | null; processing: string | null; process_steps: string[]; supplier_scope: string | null; limitations: string[] } | null;
  family?: string;
  model_ingredient_id?: string | null;
  calculation_inputs?: Record<string, number | string> | null;
  calculation_reference_ids?: string[];
  current_context_reference_ids?: string[];
  cost_bucket_id: string;
  label: string;
  cost_type: string;
  low_cents_per_bar: number;
  base_cents_per_bar: number;
  high_cents_per_bar: number;
  confidence_level?: string;
  evidence_type?: string;
  notes?: string;
  cost_logic?: string;
  safe_display?: boolean;
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
  panelResearch: PanelResearchContext;
  calculationDetails: CalculationDetails;
  manifest: HersheyFrontendManifest;
  homeCards: HomeCard[];
  graph: GraphPayload;
  suppliers: SupplierCard[];
  ingredients: IngredientCard[];
  costBreakdown: CostBreakdown;
  packetSummary: PacketSummary[];
  evidence: EvidenceLookup;
};

export type PanelResearchContext={version:string;retrieval_engine:string;node_contexts:Record<string,{query:string;incoming_edge_ids:string[];outgoing_edge_ids:string[];graph_assigned_evidence_ids:string[];packet_evidence_ids:string[];ordered_evidence_ids:string[];retrieved_document_context_ids:string[];retrieved_public_documents:string[];retrieved_chunk_count:number;scope:string}>;coverage:{graph_nodes:number;graph_edges:number;nodes_with_graph_assigned_evidence:number;nodes_with_packet_evidence:number;nodes_with_retrieved_approved_document_context:number;nodes_without_direct_evidence:string[];boundary:string}};

export type CalculationDetails = {
  version: string;
  canonical_cost_version: string;
  buckets: CostRecord[];
  ingredient_links: Array<{ display_ingredient_id: string; model_ingredient_id: string | null; role: string; cost_bucket_ids: string[]; shared_bucket: boolean; join_note: string | null }>;
  verified_retailers: Array<{ retailer: string; price_cents_per_bar: number; review_id: string; source_file: string; observation_date: string | null; store_or_zip: string | null; related_current_evidence_ids: string[] }>;
  family_totals: Record<string,{ cost_bucket_ids: string[]; low_cents_per_bar: number; base_cents_per_bar: number; high_cents_per_bar: number }>;
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
    calculationDetails,
    panelResearch,
  ] = await Promise.all([
    fetchJson<HomeCard[]>(artifacts.home_cards),
    fetchJson<GraphPayload>(artifacts.graph),
    fetchJson<SupplierCard[]>(artifacts.suppliers),
    fetchJson<IngredientCard[]>(artifacts.ingredients),
    fetchJson<CostBreakdown>(artifacts.cost_breakdown),
    fetchJson<PacketSummary[]>(artifacts.packet_summary),
    fetchJson<EvidenceLookup>(artifacts.evidence),
    fetchJson<CalculationDetails>(manifest.supplemental_artifacts?.calculation_details ?? "/data/hershey/enriched_display/enriched_calculation_details_v2.json"),
    fetchJson<PanelResearchContext>("/data/hershey/enriched_display/panel_research_context_v1.json"),
  ]);

  if (calculationDetails.canonical_cost_version !== costBreakdown.display_version) {
    throw new Error("Calculation details do not match the published cost version.");
  }
  const detailedCosts = new Map(calculationDetails.buckets.map(row => [row.cost_bucket_id, row]));
  costBreakdown.records = costBreakdown.records?.map(row => {
    const detail = detailedCosts.get(row.cost_bucket_id);
    if (!detail || detail.low_cents_per_bar !== row.low_cents_per_bar ||
      detail.base_cents_per_bar !== row.base_cents_per_bar ||
      detail.high_cents_per_bar !== row.high_cents_per_bar) {
      throw new Error("Calculation detail mismatch: " + row.cost_bucket_id);
    }
    return { ...row, ...detail };
  });

  return {
    panelResearch,
    calculationDetails,
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
