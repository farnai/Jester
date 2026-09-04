import { apiRequest } from "./client";
import { supabase } from "../realtime/supabase";
import {
  BirthDataPayload,
  ComparePreviewRequest,
  ComparePreviewResponse,
  ConnectionResponse,
  ConnectionTransitionPayload,
  ConversationResponse,
  DailyEnergyResponse,
  DiscoveryPerson,
  MessageResponse,
  NatalResolveRequest,
  NatalResolveResponseItem,
  NotificationResponse,
  ProfileResponse,
  ProfileUpdate,
  SafeDerivedAstrologyResponse,
  StructuredCompatibilityResponse,
  UserResponse,
} from "./types";

export const API = {
  // Users & Identity
  users: {
    getMe: () => apiRequest<UserResponse>("/v1/users/me"),
  },

  // Profiles
  profiles: {
    getMyProfile: () => apiRequest<ProfileResponse>("/v1/profiles/me"),
    updateMyProfile: (data: ProfileUpdate) =>
      apiRequest<ProfileResponse>("/v1/profiles/me", {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    getProfileById: (profileId: string) =>
      apiRequest<ProfileResponse>(`/v1/profiles/${profileId}`),
  },

  // Astrology & Birth Data (Official /v1/astrology/... namespace)
  astrology: {
    getMySafeAstro: () =>
      apiRequest<SafeDerivedAstrologyResponse>("/v1/astrology/profile/safe-astro"),
    recalculate: () =>
      apiRequest<SafeDerivedAstrologyResponse>("/v1/astrology/profile/recalculate", {
        method: "POST",
      }),
    getPersonSafeAstro: (targetUserId: string) =>
      apiRequest<SafeDerivedAstrologyResponse>(
        `/v1/astrology/people/${targetUserId}/safe-astro`
      ),
    // Direct birth data persistence through Supabase client with owner RLS
    saveBirthData: async (userId: string, data: BirthDataPayload) => {
      const { error } = await supabase.from("birth_data").upsert({
        user_id: userId,
        birth_date: data.birth_date,
        birth_time: data.birth_time || null,
        birth_time_precision: data.birth_time_precision,
        birth_timezone: data.birth_timezone,
        latitude: data.latitude || null,
        longitude: data.longitude || null,
        place_label: data.place_label || null,
        updated_at: new Date().toISOString(),
      });
      if (error) {
        throw new Error(error.message);
      }
      // Trigger Swiss Ephemeris recalculation immediately after saving birth data
      return apiRequest<SafeDerivedAstrologyResponse>(
        "/v1/astrology/profile/recalculate",
        { method: "POST" }
      );
    },
    checkHasBirthData: async (userId: string): Promise<boolean> => {
      const { data, error } = await supabase
        .from("birth_data")
        .select("user_id")
        .eq("user_id", userId)
        .maybeSingle();
      if (error) return false;
      return !!data;
    },
  },

  // Connections
  connections: {
    list: () => apiRequest<ConnectionResponse[]>("/v1/connections"),
    create: (targetUserId: string) =>
      apiRequest<ConnectionResponse>("/v1/connections", {
        method: "POST",
        body: JSON.stringify({ target_user_id: targetUserId }),
      }),
    transition: (connectionId: string, action: ConnectionTransitionPayload["action"]) =>
      apiRequest<ConnectionResponse>(`/v1/connections/${connectionId}/transition`, {
        method: "POST",
        body: JSON.stringify({ action }),
      }),
  },

  // Comparisons / Compatibility
  compatibility: {
    compare: (targetUserId: string) =>
      apiRequest<StructuredCompatibilityResponse>("/v1/compare", {
        method: "POST",
        body: JSON.stringify({ target_user_id: targetUserId }),
      }),
    why: (targetUserId: string) =>
      apiRequest<StructuredCompatibilityResponse>(`/v1/people/${targetUserId}/why`),
  },

  // Messaging & Conversations
  conversations: {
    createOrGetDirect: (targetUserId: string) =>
      apiRequest<ConversationResponse>("/v1/conversations", {
        method: "POST",
        body: JSON.stringify({ target_user_id: targetUserId }),
      }),
    listMessages: (conversationId: string) =>
      apiRequest<MessageResponse[]>(`/v1/conversations/${conversationId}/messages`),
    sendMessage: (conversationId: string, body: string) =>
      apiRequest<MessageResponse>(`/v1/conversations/${conversationId}/messages`, {
        method: "POST",
        body: JSON.stringify({ body }),
      }),
  },

  // Notifications
  notifications: {
    list: () => apiRequest<NotificationResponse[]>("/v1/notifications"),
    markRead: (notificationId: string) =>
      apiRequest<NotificationResponse>(`/v1/notifications/${notificationId}/read`, {
        method: "PATCH",
      }),
  },

  // Interpretation Architecture V2 & Content Exposure
  interpretations: {
    getDailyEnergy: (energyType: string = "confidence", locale: string = "ka", tone?: string) => {
      const params = new URLSearchParams({ energy_type: energyType, locale });
      if (tone) params.append("tone", tone);
      return apiRequest<DailyEnergyResponse>(`/v1/interpretations/daily-energy?${params.toString()}`);
    },
    resolveNatal: (payload: NatalResolveRequest) =>
      apiRequest<NatalResolveResponseItem[]>("/v1/interpretations/resolve-natal", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    getDiscoveryPeople: (viewerId?: string) => {
      const params = viewerId ? `?viewer_id=${viewerId}` : "";
      return apiRequest<DiscoveryPerson[]>(`/v1/interpretations/discovery-people${params}`);
    },
    comparePreview: (payload: ComparePreviewRequest) =>
      apiRequest<ComparePreviewResponse>("/v1/interpretations/compare-preview", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    getContract: (interpretationId: string, locale: string = "ka") =>
      apiRequest<Record<string, any>>(`/v1/interpretations/${interpretationId}?locale=${locale}`),
  },
};
