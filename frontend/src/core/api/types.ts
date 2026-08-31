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
  category: "harmony" | "attraction" | "communication" | "growth" | "stability" | "notice";
  strength: "low" | "medium" | "high";
  source_aspects: string[];
  label: string;
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

export interface StructuredCompatibilityResponse {
  id: string;
  target_user_id: string;
  score: number;
  dimensions: Dimensions;
  signals: Signal[];
  best_topics: string[];
  conversation_starters: string[];
  data_quality: DataQuality;
  engine_version: string;
  calculated_at: string;
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
