/**
 * Backend API DTOs & Models for JESTER.
 * Strictly mirrors FastAPI Pydantic responses.
 */

export interface UserResponse {
  id: string;
  email: string | null;
  role: string;
}

export interface ProfileResponse {
  id: string;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  city: string | null;
  occupation: string | null;
  timezone: string;
  is_discoverable: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdate {
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  city?: string;
  occupation?: string;
  timezone?: string;
  is_discoverable?: boolean;
}

export interface SafeDerivedAstrologyResponse {
  user_id: string;
  sun_sign: string;
  moon_sign: string;
  ascendant_sign: string | null;
  mercury_sign?: string | null;
  venus_sign?: string | null;
  mars_sign?: string | null;
  element_primary: string;
  modality_primary: string;
  source_birth_data_version: number;
  engine_version: string;
  updated_at: string;
}

export interface BirthDataPayload {
  birth_date: string; // YYYY-MM-DD
  birth_time?: string | null; // HH:MM:SS
  birth_time_precision: "exact" | "approximate" | "unknown";
  birth_timezone: string;
  latitude?: number | null;
  longitude?: number | null;
  place_label?: string | null;
  data_version?: number;
}

export type ConnectionStatus = "pending" | "accepted" | "declined" | "blocked" | "removed";

export interface ConnectionResponse {
  id: string;
  user_a_id: string;
  user_b_id: string;
  status: ConnectionStatus;
  initiated_by: string;
  blocked_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConnectionTransitionPayload {
  action: "accept" | "decline" | "block" | "unblock" | "remove";
}

export interface Signal {
  type: string;
  category: "harmony" | "attraction" | "communication" | "growth" | "stability" | "notice" | string;
  strength: "low" | "medium" | "high" | string;
  source_aspects: string[];
  label: string;
  importance?: number;
  planet_pair?: string;
  aspect?: string;
  source_aspect?: string;
  rule_id?: string;
  interpretation?: ResolvedInterpretationModel;
}

export interface Dimensions {
  emotional_harmony: number;
  communication: number;
  attraction: number;
  growth_long_term: number;
}

export interface DataQuality {
  time_precision: "exact" | "approximate" | "unknown";
  confidence: number;
  houses_used: boolean;
  ascendant_used: boolean;
}

export interface ConversationStarterDetail {
  text: string;
  contract_id: string;
  category: string;
  source_signal: string;
  asset_id: string;
  variant_key?: string | null;
  selection_mode: string;
}

export interface StructuredCompatibilityResponse {
  id: string;
  target_user_id: string;
  score: number;
  dimensions: Dimensions;
  signals: Signal[];
  best_topics: string[];
  conversation_starters: string[];
  conversation_starter_details?: ConversationStarterDetail[];
  data_quality: DataQuality;
  engine_version: string;
  calculated_at: string;
  interpretation?: ResolvedInterpretationModel | null;
  connection_invitation?: ResolvedInterpretationModel | null;
  deep_analysis?: DeepAnalysisPayload | null;
}

export interface ConversationResponse {
  id: string;
  conversation_type: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  other_member_id?: string;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  sender_user_id: string;
  body: string;
  created_at: string;
}

export interface NotificationResponse {
  id: string;
  user_id: string;
  type?: string;
  notification_type: "connection_request" | "connection_accepted" | "message_received" | "daily_energy" | "system";
  payload: Record<string, any>;
  read_at: string | null;
  created_at: string;
}


export interface ApiError {
  status_code: number;
  error_code: string;
  message: string;
}

// =============================================================================
// Interpretation Architecture V2 & Discovery Smoke Test Types
// =============================================================================

export interface ResolvedInterpretationModel {
  id: string;
  text: string;
  content_status: string;
  language: string;
  content_asset_id?: string;
  asset_id?: string;
  category?: string;
  context?: string;
  locale: string;
  tone?: string;
  persona?: string;
  variant_key?: string;
  title?: string;
  hook?: string;
  source?: string;
}

export interface DailyEnergyArchetype {
  id: string;
  label_ka: string;
  transit: string;
}

export interface ActiveTransitSignal {
  transit_planet: string;
  natal_point: string;
  aspect_type: string;
  actual_distance: number;
  target_angle: number;
  orb_diff: number;
  max_orb: number;
  aspect_strength: number;
  is_applying: boolean;
  transit_retrograde: boolean;
  archetype_id: string;
  ranking_score?: number;
  context_label_ka: string;
}

export interface DailyEnergyResponse {
  date?: string;
  archetype?: string;
  energy_type: string;
  label: string;
  interpretation: ResolvedInterpretationModel | null;
  contract?: Record<string, any>;
  available_archetypes: DailyEnergyArchetype[];
  primary_transit?: ActiveTransitSignal | null;
  supporting_transits?: ActiveTransitSignal[];
  detection_mode?: string;
  do?: string[] | string;
  dont?: string[] | string;
}

export interface NatalResolveRequest {
  sun_sign: string;
  moon_sign?: string | null;
  ascendant_sign?: string | null;
  mercury_sign?: string | null;
  venus_sign?: string | null;
  mars_sign?: string | null;
  element_primary?: string | null;
  modality_primary?: string | null;
  locale?: string;
  tone?: string | null;
}

export interface NatalResolveResponseItem {
  dimension: string;
  title: string;
  interpretation: ResolvedInterpretationModel;
  contract?: Record<string, any>;
}

export interface DiscoveryPerson {
  id: string;
  display_name: string;
  bio?: string | null;
  city?: string | null;
  occupation?: string | null;
  avatar_url?: string | null;
  astrology: {
    sun_sign: string | null;
    moon_sign: string | null;
    ascendant_sign: string | null;
    element_primary: string | null;
    modality_primary: string | null;
  };
  compatibility_score: number;
  hook_observation?: ResolvedInterpretationModel | null;
  presence_sign_source?: string;
  presence_sign?: string;
}

export interface ComparePreviewRequest {
  target_user_id: string;
  source_user_id?: string | null;
  locale?: string;
  tone?: string | null;
}

export interface DeepAnalysisBlock {
  interpretation_id: string;
  dimension: string;
  resolved_text: string;
  evidence_aspects: string[];
  content_status: string;
  content_asset_id?: string;
  tone: string;
}

export interface DeepAnalysisPayload {
  primary_interpretation: ResolvedInterpretationModel;
  blocks: DeepAnalysisBlock[];
  overall_score: number;
  data_confidence: number;
  title?: string;
  summary?: string;
  core_dynamic?: {
    headline: string;
    text: string;
  };
}

export interface ComparePreviewResponse {
  source_user_id: string;
  target_user_id: string;
  score: number;
  dimensions: {
    emotional_harmony: number;
    communication: number;
    attraction: number;
    growth_long_term: number;
  };
  signals: Signal[];
  interpretation: ResolvedInterpretationModel;
  connection_invitation?: ResolvedInterpretationModel;
  best_topics: string[];
  conversation_starters: string[];
  conversation_starter_details?: ConversationStarterDetail[];
  data_quality: {
    confidence: number;
    time_precision: string;
    houses_used: boolean;
    ascendant_used: boolean;
  };
  deep_analysis: DeepAnalysisPayload;
  engine_version: string;
  calculated_at: string;
}

// =============================================================================
// Inspector Data Types
// =============================================================================

export interface InspectorBatchSummary {
  stem: string;
  filename: string;
  count: number;
  domains: string[];
  surfaces: string[];
}

export interface InspectorSummary {
  expected_frozen_assets: number;
  actual_frozen_assets: number;
  status: "OK" | "MISMATCH";
  note: string;
  batches: InspectorBatchSummary[];
  section_counts: {
    natal: number;
    synastry: number;
    discovery: number;
    connection: number;
    chat: number;
    daily_energy: number;
  };
}

export interface InspectorSynastryItem {
  trigger: string;
  planet_a: string;
  planet_b: string;
  aspect: string;
  rule_id: string;
  canonical_rule: string;
  is_canonical_primary: boolean;
  signal: string;
  category: string;
  default_strength: string;
  label: string;
  contract_id: string;
  contract_meaning: {
    type: string;
    intensity: string;
    human_meaning: string[];
  };
  why_asset: any | null;
  us_assets: any[];
  connection_invitations: any[];
  conversation_starters: any[];
  causal_chain: string[];
  integrity_status: "OK" | "UNRESOLVED";
}

export interface InspectorNatalSection {
  key: string;
  planet: string;
  source: string;
  semantic_domain: string;
  description: string;
  firewall_rules?: string;
  firewall_violations?: Array<{ asset_id: string; word: string }>;
  firewall_status?: string;
  batch_name: string;
  count: number;
  assets: any[];
}

export interface InspectorDiscoveryItem {
  asset_id: string;
  sign: string;
  source: string;
  mode: string;
  interpretation_id: string;
  category: string;
  text: string;
  raw: any;
}

export interface InspectorConnectionItem {
  asset_id: string;
  interpretation_id: string;
  category: string;
  variant_key?: string;
  source_category_mapping: string;
  selection_mode: string;
  text: string;
  raw: any;
}

export interface InspectorChatItem {
  asset_id: string;
  interpretation_id: string;
  category: string;
  variant_key?: string;
  source_signal: string;
  selection_mode: string;
  text: string;
  raw: any;
}

export interface InspectorDailyEnergyCentralizedSpec {
  engine_source: string;
  detection_mode: string;
  trigger_pairs: string[];
  key_bodies: Array<{ body: string; max_orb: number; transit_weight?: number; weight?: number }>;
  aspect_types: string[];
  applying_multiplier: number;
  evidence_notice: string;
}

export interface InspectorDailyEnergyTagItem {
  tag_id: string;
  archetype_id: string;
  archetype_name: string;
  index: number;
  text_ka: string;
  text_en: string;
}

export interface InspectorDailyEnergyNarrativeAsset {
  asset_id: string;
  interpretation_id: string;
  archetype_id: string;
  archetype_name: string;
  locale: string;
  tone: string;
  persona?: string;
  variant_key: string;
  text: string;
  status: string;
  source?: string;
}

export interface InspectorDailyEnergyArchetype {
  id: string;
  name: string;
  description: string;
  contract_id: string;
  narrative_ka: string;
  narrative_en?: string;
  qa_status: string;
  do_tags: string[];
  dont_tags: string[];
  do_tags_ka: string[];
  dont_tags_ka: string[];
  centralized_spec: InspectorDailyEnergyCentralizedSpec;
  technical_evidence: {
    transit_body: string;
    natal_body: string;
    aspect: string;
    max_orb: number;
    aspect_strength: number;
    ranking_score: number;
    archetype_id: string;
    detection_mode: string;
    evidence_status: string;
    is_centralized_spec?: boolean;
    orb_diff?: number;
    is_applying?: boolean;
    transit_retrograde?: boolean;
  };
  is_neutral_case: boolean;
}

export interface InspectorIntegrityReport {
  overall_status: string;
  synastry_rules_total: number;
  synastry_canonical_unique: number;
  synastry_unresolved_count: number;
  synastry_unresolved_rules: string[];
  mars_semantic_firewall: string;
  discovery_signs_coverage: string;
  connection_categories_coverage: string;
  chat_starters_coverage: string;
  daily_energy_archetypes_coverage: string;
}

export interface InspectorDataResponse {
  summary: InspectorSummary;
  synastry_pipeline: InspectorSynastryItem[];
  synastry_verdicts_and_notice: any[];
  natal_sections: InspectorNatalSection[];
  discovery_items: InspectorDiscoveryItem[];
  connection_items: InspectorConnectionItem[];
  chat_items: InspectorChatItem[];
  daily_energy: {
    archetypes: InspectorDailyEnergyArchetype[];
    interpretation_assets: InspectorDailyEnergyNarrativeAsset[];
    do_tags: InspectorDailyEnergyTagItem[];
    dont_tags: InspectorDailyEnergyTagItem[];
    neutral_case: {
      detection_mode: string;
      primary_transit: any;
      supporting_transits: any[];
      archetype: string;
      interpretation: string;
      interpretation_en?: string;
      qa_status?: string;
      do_ka: string[];
      dont_ka: string[];
      do_en: string[];
      dont_en: string[];
      technical_note: string;
      centralized_spec?: InspectorDailyEnergyCentralizedSpec;
    };
    summary?: {
      archetypes_count: number;
      interpretation_assets_count: number;
      do_tags_count: number;
      dont_tags_count: number;
      missing_assets_count: number;
    };
  };
  integrity: InspectorIntegrityReport;
}

