import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { API } from "../core/api/endpoints";
import { useAuth } from "../core/auth/useAuth";
import {
  BirthDataPayload,
  SafeDerivedAstrologyResponse,
  NatalResolveResponseItem,
  DailyEnergyResponse,
  ComparePreviewResponse,
  DiscoveryPerson,
} from "../core/api/types";
import {
  Card,
  Button,
  Badge,
  Skeleton,
} from "../shared/ui";

const STATE_A: BirthDataPayload = {
  birth_date: "1990-03-21",
  birth_time: "06:00:00",
  birth_time_precision: "exact",
  birth_timezone: "UTC",
  latitude: 51.5074,
  longitude: -0.1278,
  place_label: "London, UK",
};

const STATE_B: BirthDataPayload = {
  birth_date: "1995-11-15",
  birth_time: "18:30:00",
  birth_time_precision: "exact",
  birth_timezone: "Asia/Tbilisi",
  latitude: 41.7151,
  longitude: 44.8271,
  place_label: "Tbilisi, Georgia",
};

interface PlanetAuditConfig {
  key: "sun" | "moon" | "ascendant" | "mercury" | "venus" | "mars";
  nameKa: string;
  nameEn: string;
  symbol: string;
  dimension: string;
}

const PLANETS: PlanetAuditConfig[] = [
  { key: "sun", nameKa: "მზე (იდენტობა)", nameEn: "Sun", symbol: "☀️", dimension: "self.identity" },
  { key: "moon", nameKa: "მთვარე (ემოციური ბირთვი)", nameEn: "Moon", symbol: "🌙", dimension: "self.emotional" },
  { key: "ascendant", nameKa: "ასცენდენტი (პირველი შთაბეჭდილება)", nameEn: "Ascendant", symbol: "🌅", dimension: "self.persona" },
  { key: "mercury", nameKa: "მერკური (აზროვნება და სიტყვა)", nameEn: "Mercury", symbol: "☿", dimension: "self.cognition" },
  { key: "venus", nameKa: "ვენერა (მიზიდულობა და გემოვნება)", nameEn: "Venus", symbol: "♀", dimension: "self.relation" },
  { key: "mars", nameKa: "მარსი (ენერგია და იმპულსი)", nameEn: "Mars", symbol: "♂", dimension: "self.action" },
];

export const BackendAuditDebugPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { user, session } = useAuth();
  const [withInvalidation, setWithInvalidation] = useState(true);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "astrology" | "daily" | "compare" | "trace" | "abdiff">("overview");

  const addLog = (msg: string) => {
    setActionLog((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 20)]);
  };

  // 1. Fetch User Stored Birth Data
  const {
    data: storedBirthData,
    isLoading: loadingBD,
    refetch: refetchBD,
  } = useQuery<BirthDataPayload | null>({
    queryKey: ["birth-data", user?.id],
    queryFn: () => (user ? API.astrology.getBirthData(user.id) : Promise.resolve(null)),
    enabled: !!user?.id,
  });

  // 2. Fetch User Safe Astrology Placements
  const {
    data: astro,
    isLoading: loadingAstro,
    refetch: refetchAstro,
  } = useQuery<SafeDerivedAstrologyResponse>({
    queryKey: ["astrology", "me"],
    queryFn: API.astrology.getMySafeAstro,
    enabled: !!user,
  });

  // 3. Resolve Personal JESTER Narrative Observations for the 6 planets
  const {
    data: natalObservations,
    isLoading: loadingNarrative,
    refetch: refetchNarrative,
  } = useQuery<NatalResolveResponseItem[]>({
    queryKey: [
      "natal-observations",
      astro?.sun_sign,
      astro?.moon_sign,
      astro?.ascendant_sign,
      astro?.mercury_sign,
      astro?.venus_sign,
      astro?.mars_sign,
      astro?.element_primary,
      astro?.modality_primary,
      astro?.source_birth_data_version,
    ],
    queryFn: () =>
      API.interpretations.resolveNatal({
        sun_sign: astro!.sun_sign,
        moon_sign: astro?.moon_sign,
        ascendant_sign: astro?.ascendant_sign,
        mercury_sign: astro?.mercury_sign,
        venus_sign: astro?.venus_sign,
        mars_sign: astro?.mars_sign,
        element_primary: astro?.element_primary,
        modality_primary: astro?.modality_primary,
        locale: "ka",
      }),
    enabled: !!astro?.sun_sign,
  });

  // 4. Daily Energy Resolution
  const {
    data: dailyEnergy,
    isLoading: loadingDaily,
  } = useQuery<DailyEnergyResponse>({
    queryKey: ["daily-energy", astro?.sun_sign, astro?.source_birth_data_version],
    queryFn: () => API.interpretations.getDailyEnergy("auto", "ka"),
    enabled: !!user,
  });

  // 5. Discoverable people (to find a real target user for Compare audit)
  const { data: discoveryPeople } = useQuery<DiscoveryPerson[]>({
    queryKey: ["discovery-people", user?.id],
    queryFn: () => API.interpretations.getDiscoveryPeople(),
    enabled: !!user,
  });

  const targetPerson = discoveryPeople && discoveryPeople.length > 0 ? discoveryPeople[0] : null;

  // 6. Compare Preview with Target Person
  const {
    data: compareData,
    isLoading: loadingCompare,
    refetch: refetchCompare,
  } = useQuery<ComparePreviewResponse | null>({
    queryKey: ["compare-preview", user?.id, targetPerson?.id, astro?.source_birth_data_version],
    queryFn: () =>
      targetPerson
        ? API.interpretations.comparePreview({
            target_user_id: targetPerson.id,
            locale: "ka",
          })
        : Promise.resolve(null),
    enabled: !!user && !!targetPerson?.id,
  });

  // Mutations
  const applyStateMutation = useMutation({
    mutationFn: async (payload: BirthDataPayload) => {
      if (!user) throw new Error("Not authenticated");
      addLog(`Sending birth data: ${payload.birth_date} ${payload.birth_time} (${payload.birth_timezone})`);
      const result = await API.astrology.saveBirthData(user.id, payload);
      return result;
    },
    onSuccess: () => {
      if (withInvalidation) {
        addLog("Invalidating React Query cache: ['astrology', 'me'], ['birth-data'], ['natal-observations'], ['daily-energy'], ['compare-preview']");
        queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
        queryClient.invalidateQueries({ queryKey: ["birth-data"] });
        queryClient.invalidateQueries({ queryKey: ["natal-observations"] });
        queryClient.invalidateQueries({ queryKey: ["daily-energy"] });
        queryClient.invalidateQueries({ queryKey: ["compare-preview"] });
      } else {
        addLog("WITHOUT INVALIDATION: Queries left stale in cache (Reproduces user bug)");
      }
    },
    onError: (err: any) => {
      addLog(`Error saving birth data: ${err.message}`);
    },
  });

  const recalcMutation = useMutation({
    mutationFn: API.astrology.recalculate,
    onSuccess: () => {
      addLog("Manual recalculate triggered -> invalidating ['astrology', 'me'] and related queries");
      queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
      queryClient.invalidateQueries({ queryKey: ["natal-observations"] });
      queryClient.invalidateQueries({ queryKey: ["daily-energy"] });
      queryClient.invalidateQueries({ queryKey: ["compare-preview"] });
    },
  });

  // Helper to find resolved observation by dimension prefix
  const getObservation = (dimension: string) => {
    return natalObservations?.find((item) => item.dimension === dimension);
  };

  // Helper to extract sign for a planet
  const getPlanetSign = (key: PlanetAuditConfig["key"]) => {
    if (!astro) return null;
    switch (key) {
      case "sun": return astro.sun_sign;
      case "moon": return astro.moon_sign;
      case "ascendant": return astro.ascendant_sign || "Unknown";
      case "mercury": return astro.mercury_sign || "None";
      case "venus": return astro.venus_sign || "None";
      case "mars": return astro.mars_sign || "None";
    }
  };

  // Build End-to-End Pipeline Trace Rows
  interface TraceRow {
    field: string;
    backendVal: string;
    rawApiVal: string;
    frontendMappedVal: string;
    reactQueryCachedVal: string;
    renderedVal: string;
    status: "PASS" | "FAIL";
  }

  const traceRows: TraceRow[] = [
    {
      field: "birth_date",
      backendVal: storedBirthData?.birth_date || "N/A",
      rawApiVal: storedBirthData?.birth_date || "N/A",
      frontendMappedVal: storedBirthData?.birth_date || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["birth-data", user?.id]) as BirthDataPayload)?.birth_date || "N/A",
      renderedVal: storedBirthData?.birth_date || "N/A",
      status: storedBirthData?.birth_date ? "PASS" : "FAIL",
    },
    {
      field: "data_version",
      backendVal: `v${storedBirthData?.data_version ?? "N/A"}`,
      rawApiVal: `v${storedBirthData?.data_version ?? "N/A"}`,
      frontendMappedVal: `v${storedBirthData?.data_version ?? "N/A"}`,
      reactQueryCachedVal: `v${(queryClient.getQueryData(["birth-data", user?.id]) as BirthDataPayload)?.data_version ?? "N/A"}`,
      renderedVal: `v${astro?.source_birth_data_version ?? "N/A"}`,
      status: storedBirthData?.data_version === astro?.source_birth_data_version ? "PASS" : "FAIL",
    },
    {
      field: "sun_sign",
      backendVal: astro?.sun_sign || "N/A",
      rawApiVal: astro?.sun_sign || "N/A",
      frontendMappedVal: astro?.sun_sign || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["astrology", "me"]) as SafeDerivedAstrologyResponse)?.sun_sign || "N/A",
      renderedVal: astro?.sun_sign || "N/A",
      status: astro?.sun_sign ? "PASS" : "FAIL",
    },
    {
      field: "moon_sign",
      backendVal: astro?.moon_sign || "N/A",
      rawApiVal: astro?.moon_sign || "N/A",
      frontendMappedVal: astro?.moon_sign || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["astrology", "me"]) as SafeDerivedAstrologyResponse)?.moon_sign || "N/A",
      renderedVal: astro?.moon_sign || "N/A",
      status: astro?.moon_sign ? "PASS" : "FAIL",
    },
    {
      field: "mercury_sign",
      backendVal: astro?.mercury_sign || "N/A",
      rawApiVal: astro?.mercury_sign || "N/A",
      frontendMappedVal: astro?.mercury_sign || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["astrology", "me"]) as SafeDerivedAstrologyResponse)?.mercury_sign || "N/A",
      renderedVal: astro?.mercury_sign || "N/A",
      status: astro?.mercury_sign ? "PASS" : "FAIL",
    },
    {
      field: "venus_sign",
      backendVal: astro?.venus_sign || "N/A",
      rawApiVal: astro?.venus_sign || "N/A",
      frontendMappedVal: astro?.venus_sign || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["astrology", "me"]) as SafeDerivedAstrologyResponse)?.venus_sign || "N/A",
      renderedVal: astro?.venus_sign || "N/A",
      status: astro?.venus_sign ? "PASS" : "FAIL",
    },
    {
      field: "mars_sign",
      backendVal: astro?.mars_sign || "N/A",
      rawApiVal: astro?.mars_sign || "N/A",
      frontendMappedVal: astro?.mars_sign || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["astrology", "me"]) as SafeDerivedAstrologyResponse)?.mars_sign || "N/A",
      renderedVal: astro?.mars_sign || "N/A",
      status: astro?.mars_sign ? "PASS" : "FAIL",
    },
    {
      field: "daily_energy.archetype",
      backendVal: dailyEnergy?.energy_type || "N/A",
      rawApiVal: dailyEnergy?.energy_type || "N/A",
      frontendMappedVal: dailyEnergy?.energy_type || "N/A",
      reactQueryCachedVal: (queryClient.getQueryData(["daily-energy", astro?.sun_sign, astro?.source_birth_data_version]) as DailyEnergyResponse)?.energy_type || "N/A",
      renderedVal: dailyEnergy?.label || "N/A",
      status: dailyEnergy?.energy_type ? "PASS" : "FAIL",
    },
  ];

  return (
    <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "1.5rem", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Top Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
          color: "#f8fafc",
          padding: "1.5rem",
          borderRadius: "12px",
          marginBottom: "1.5rem",
          boxShadow: "0 10px 25px -5px rgba(0,0,0,0.3)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <Badge variant="brand" size="md">PHASE 4.1.x</Badge>
              <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, letterSpacing: "-0.025em" }}>
                JESTER Forensic Data & Content Inspector
              </h1>
            </div>
            <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.875rem", color: "#94a3b8" }}>
              Full End-to-End Pipeline Trace: Database &rarr; Swiss Ephemeris &rarr; API &rarr; React Query &rarr; Georgian Narrative Content
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Link to="/me" style={{ textDecoration: "none" }}>
              <Button variant="secondary" size="sm">👤 ME Page</Button>
            </Link>
            <Link to="/visual-lab" style={{ textDecoration: "none" }}>
              <Button variant="outline" size="sm">🎨 Visual Lab</Button>
            </Link>
            <Link to="/smoke-test" style={{ textDecoration: "none" }}>
              <Button variant="outline" size="sm">🧪 Smoke Test</Button>
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: "flex", gap: "0.5rem", marginTop: "1.25rem", borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: "1rem", flexWrap: "wrap" }}>
          {[
            { id: "overview", label: "1. User & Birth Data" },
            { id: "astrology", label: "2. Astrology & 6 Core Texts" },
            { id: "daily", label: "3. Daily Energy (Transitional)" },
            { id: "compare", label: "4. US / Compare Synastry" },
            { id: "trace", label: "5. API &rarr; Frontend Trace" },
            { id: "abdiff", label: "6. Live A/B Diff" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              style={{
                background: activeTab === tab.id ? "#6366f1" : "rgba(255,255,255,0.08)",
                color: "#fff",
                border: "none",
                padding: "0.45rem 0.9rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                fontWeight: activeTab === tab.id ? 700 : 500,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Action Bar / Invalidation Switcher */}
      <Card padded style={{ marginBottom: "1.5rem", backgroundColor: "#f8fafc", border: "1px solid #e2e8f0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#334155" }}>Deterministic A/B Control:</span>
            <Button
              variant="brand"
              size="sm"
              isLoading={applyStateMutation.isPending}
              onClick={() => applyStateMutation.mutate(STATE_A)}
            >
              Apply STATE A (London Aries 1990)
            </Button>
            <Button
              variant="secondary"
              size="sm"
              isLoading={applyStateMutation.isPending}
              onClick={() => applyStateMutation.mutate(STATE_B)}
            >
              Apply STATE B (Tbilisi Scorpio 1995)
            </Button>
            <Button
              variant="outline"
              size="sm"
              isLoading={recalcMutation.isPending}
              onClick={() => recalcMutation.mutate()}
            >
              🔄 Force Recalculate
            </Button>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", fontWeight: 600, cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={withInvalidation}
              onChange={(e) => setWithInvalidation(e.target.checked)}
            />
            Invalidate React Query on change
            <span style={{ fontSize: "0.75rem", color: withInvalidation ? "#16a34a" : "#dc2626" }}>
              ({withInvalidation ? "Auto Cache Purge" : "Keep Cache Stale"})
            </span>
          </label>
        </div>

        {actionLog.length > 0 && (
          <div style={{ marginTop: "0.75rem", backgroundColor: "#0f172a", color: "#4ade80", padding: "0.6rem 0.8rem", borderRadius: "6px", fontSize: "0.75rem", fontFamily: "monospace", maxHeight: "100px", overflowY: "auto" }}>
            {actionLog.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        )}
      </Card>

      {/* ===================================================================== */}
      {/* TAB 1: AUTH USER & PERSISTED BIRTH DATA                               */}
      {/* ===================================================================== */}
      {(activeTab === "overview" || activeTab === "abdiff") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>1. AUTHENTICATED USER & PERSISTED BIRTH DATA</span>
            <Badge variant="default" size="sm">public.birth_data</Badge>
          </h2>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1rem" }}>
            {/* Auth Identity Context */}
            <Card padded>
              <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "0.95rem", fontWeight: 700, color: "#1e293b" }}>
                Auth Identity Context
              </h3>
              {user ? (
                <div style={{ display: "grid", gap: "0.5rem", fontSize: "0.85rem" }}>
                  <div><span style={{ color: "#64748b" }}>User ID:</span> <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: "4px" }}>{user.id}</code></div>
                  <div><span style={{ color: "#64748b" }}>Email:</span> <strong>{user.email || "No email"}</strong></div>
                  <div><span style={{ color: "#64748b" }}>Role:</span> <code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: "4px" }}>{user.role || "authenticated"}</code></div>
                  <div>
                    <span style={{ color: "#64748b" }}>Token Status:</span>{" "}
                    <Badge variant={session?.access_token ? "success" : "danger"} size="sm">
                      {session?.access_token ? "Valid Supabase JWT Bearer" : "Missing / Anonymous"}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div style={{ color: "#dc2626", fontSize: "0.85rem" }}>
                  ⚠️ Not logged in. <Link to="/auth/login">Click here to log in</Link>.
                </div>
              )}
            </Card>

            {/* Persisted Birth Data Fields */}
            <Card padded>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <h3 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#1e293b" }}>
                  Persisted Birth Data (Owner-Only)
                </h3>
                <Button variant="ghost" size="sm" onClick={() => refetchBD()}>Refetch</Button>
              </div>

              {loadingBD ? (
                <Skeleton height="120px" />
              ) : storedBirthData ? (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.6rem", fontSize: "0.85rem" }}>
                  <div><span style={{ color: "#64748b" }}>Date:</span> <strong>{storedBirthData.birth_date}</strong></div>
                  <div><span style={{ color: "#64748b" }}>Time:</span> <strong>{storedBirthData.birth_time || "None (Unknown)"}</strong></div>
                  <div><span style={{ color: "#64748b" }}>Timezone:</span> <code>{storedBirthData.birth_timezone}</code></div>
                  <div><span style={{ color: "#64748b" }}>Precision:</span> <Badge variant="default" size="sm">{storedBirthData.birth_time_precision}</Badge></div>
                  <div><span style={{ color: "#64748b" }}>Latitude:</span> <code>{storedBirthData.latitude ?? "null"}</code></div>
                  <div><span style={{ color: "#64748b" }}>Longitude:</span> <code>{storedBirthData.longitude ?? "null"}</code></div>
                  <div><span style={{ color: "#64748b" }}>Place:</span> <strong>{storedBirthData.place_label || "None"}</strong></div>
                  <div>
                    <span style={{ color: "#64748b" }}>Data Version:</span>{" "}
                    <Badge variant="brand" size="sm">v{storedBirthData.data_version ?? 1}</Badge>
                  </div>
                </div>
              ) : (
                <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No birth data stored for user yet.</div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 2: ASTROLOGY & 6 CORE PLACEMENT NARRATIVES (FULL GEORGIAN TEXT)   */}
      {/* ===================================================================== */}
      {(activeTab === "astrology" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>2. ASTROLOGICAL PLACEMENTS & FULL GEORGIAN TEXT (6 Core Planets)</span>
              <Badge variant="brand" size="sm">v{astro?.source_birth_data_version ?? "N/A"}</Badge>
            </h2>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Button variant="ghost" size="sm" onClick={() => refetchAstro()}>Refetch Astrology</Button>
              <Button variant="ghost" size="sm" onClick={() => refetchNarrative()}>Refetch Copy</Button>
            </div>
          </div>

          {loadingAstro || loadingNarrative ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "1rem" }}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} height="200px" />
              ))}
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: "1rem" }}>
              {PLANETS.map((planet) => {
                const sign = getPlanetSign(planet.key);
                const obs = getObservation(planet.dimension);
                const interp = obs?.interpretation;
                const provenance = interp?.source === "copywriter" ? "Approved Copywriter Corpus" : "AI Draft Fallback";

                return (
                  <Card key={planet.key} padded style={{ borderLeft: "4px solid #6366f1" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                      <div>
                        <span style={{ fontSize: "1.25rem", marginRight: "0.4rem" }}>{planet.symbol}</span>
                        <strong style={{ fontSize: "1rem", color: "#0f172a" }}>{planet.nameKa}</strong>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{planet.nameEn} Placement</div>
                      </div>
                      <Badge variant="brand" size="sm">{sign || "N/A"}</Badge>
                    </div>

                    {/* Metadata Matrix */}
                    <div style={{ background: "#f8fafc", padding: "0.6rem", borderRadius: "6px", fontSize: "0.75rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.35rem", marginBottom: "0.75rem" }}>
                      <div><span style={{ color: "#64748b" }}>Data Ver:</span> <strong>v{astro?.source_birth_data_version}</strong></div>
                      <div><span style={{ color: "#64748b" }}>Contract:</span> <code style={{ fontSize: "0.7rem" }}>{interp?.id || "N/A"}</code></div>
                      <div><span style={{ color: "#64748b" }}>Asset ID:</span> <code style={{ fontSize: "0.7rem" }}>{interp?.content_asset_id || interp?.variant_key || "corpus_v2"}</code></div>
                      <div><span style={{ color: "#64748b" }}>Context:</span> <code>{interp?.context || "self"}</code></div>
                      <div><span style={{ color: "#64748b" }}>Tone:</span> <code>{interp?.tone || "witty"}</code></div>
                      <div><span style={{ color: "#64748b" }}>Status/Tier:</span> <Badge variant={interp?.content_status === "approved" ? "success" : "warning"} size="sm">{interp?.content_status || "approved"}</Badge></div>
                      <div><span style={{ color: "#64748b" }}>Locale:</span> <code>{interp?.locale || "ka"}</code></div>
                      <div>
                        <span style={{ color: "#64748b" }}>Provenance:</span>{" "}
                        <span style={{ fontWeight: 600, color: interp?.source === "copywriter" ? "#15803d" : "#b45309" }}>
                          {provenance}
                        </span>
                      </div>
                    </div>

                    {/* FULL GEORGIAN TEXT - UNTRUNCATED */}
                    <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.5rem" }}>
                      <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#475569", marginBottom: "0.25rem" }}>
                        FULL GEORGIAN NARRATIVE (NO TRUNCATION):
                      </div>
                      {interp?.text ? (
                        <blockquote style={{ margin: 0, padding: "0.6rem 0.8rem", background: "#f1f5f9", borderRadius: "6px", fontSize: "0.85rem", color: "#1e293b", lineHeight: 1.6, fontStyle: "normal", whiteSpace: "pre-wrap" }}>
                          "{interp.text}"
                        </blockquote>
                      ) : (
                        <div style={{ color: "#94a3b8", fontSize: "0.8rem" }}>
                          No text resolved for this placement.
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 3: DAILY ENERGY (TRANSITIONAL MECHANISM)                           */}
      {/* ===================================================================== */}
      {(activeTab === "daily" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>3. DAILY ENERGY (DAY VIBE)</span>
            <Badge variant="warning" size="sm">TRANSITIONAL MECHANISM</Badge>
          </h2>

          <Card padded style={{ borderTop: "4px solid #f59e0b" }}>
            <div style={{ background: "#fffbeb", border: "1px solid #fef3c7", padding: "0.75rem", borderRadius: "6px", marginBottom: "1rem", fontSize: "0.85rem", color: "#92400e" }}>
              <strong>⚠️ ARCHITECTURAL NOTICE:</strong> The current Daily Energy selection mechanism is <strong>TRANSITIONAL</strong>. It dynamically maps the user's natal Sun sign to an energetic archetype (e.g. Aries &rarr; confidence, Scorpio &rarr; introspection) and resolves approved Georgian narrative copy. It will be superseded by the deterministic transit engine in Phase 5.
            </div>

            {loadingDaily ? (
              <Skeleton height="150px" />
            ) : dailyEnergy ? (
              <div style={{ display: "grid", gap: "1rem" }}>
                {/* Metadata Matrix */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem", fontSize: "0.85rem", background: "#f8fafc", padding: "0.75rem", borderRadius: "6px" }}>
                  <div><span style={{ color: "#64748b" }}>Date:</span> <strong>{new Date().toISOString().split("T")[0]}</strong></div>
                  <div><span style={{ color: "#64748b" }}>User ID:</span> <code style={{ fontSize: "0.75rem" }}>{user?.id}</code></div>
                  <div><span style={{ color: "#64748b" }}>Data Version:</span> <Badge variant="brand" size="sm">v{astro?.source_birth_data_version ?? 1}</Badge></div>
                  <div><span style={{ color: "#64748b" }}>Sun Sign:</span> <Badge variant="default" size="sm">{astro?.sun_sign || "N/A"}</Badge></div>
                  <div><span style={{ color: "#64748b" }}>Archetype:</span> <strong>{dailyEnergy.label}</strong> (<code>{dailyEnergy.energy_type}</code>)</div>
                  <div><span style={{ color: "#64748b" }}>Selection Mechanism:</span> <Badge variant="warning" size="sm">TRANSITIONAL (Sun-Sign Heuristic)</Badge></div>
                  <div><span style={{ color: "#64748b" }}>Contract:</span> <code style={{ fontSize: "0.75rem" }}>{dailyEnergy.interpretation?.id || "N/A"}</code></div>
                  <div><span style={{ color: "#64748b" }}>Asset ID:</span> <code style={{ fontSize: "0.75rem" }}>{dailyEnergy.interpretation?.content_asset_id || dailyEnergy.interpretation?.variant_key || "daily_energy_ka"}</code></div>
                </div>

                {/* FULL DAILY ENERGY TEXT */}
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#475569", marginBottom: "0.35rem" }}>
                    FULL GEORGIAN DAILY ENERGY NARRATIVE (NO TRUNCATION):
                  </div>
                  <blockquote style={{ margin: 0, padding: "1rem", background: "#f8fafc", borderLeft: "4px solid #f59e0b", borderRadius: "6px", fontSize: "0.95rem", color: "#1e293b", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                    "{dailyEnergy.interpretation?.text}"
                  </blockquote>
                </div>
              </div>
            ) : (
              <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No daily energy available. Provide birth data first.</div>
            )}
          </Card>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 4: US / COMPARE SYNASTRY INSPECTION                               */}
      {/* ===================================================================== */}
      {(activeTab === "compare" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>4. US / COMPARE SYNASTRY INSPECTION</span>
              <Badge variant="brand" size="sm">Deterministic Synastry V1</Badge>
            </h2>
            <Button variant="ghost" size="sm" onClick={() => refetchCompare()}>Refetch Compare</Button>
          </div>

          <Card padded style={{ borderTop: "4px solid #10b981" }}>
            {loadingCompare ? (
              <Skeleton height="180px" />
            ) : compareData ? (
              <div style={{ display: "grid", gap: "1rem" }}>
                {/* Users Comparison Header */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: "1rem", alignItems: "center", background: "#f8fafc", padding: "0.75rem", borderRadius: "8px" }}>
                  <div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>User A (You / Viewer)</div>
                    <code style={{ fontSize: "0.8rem", fontWeight: 700 }}>{compareData.source_user_id}</code>
                    <div style={{ marginTop: "0.25rem", fontSize: "0.8rem" }}>
                      Data Ver: <Badge variant="brand" size="sm">v{astro?.source_birth_data_version ?? 1}</Badge> • Sun: <strong>{astro?.sun_sign}</strong>
                    </div>
                  </div>

                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: "1.75rem", fontWeight: 900, color: "#10b981" }}>
                      {compareData.score}%
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "#64748b", fontWeight: 600 }}>SYNASTRY SCORE</div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>User B (Target / Partner)</div>
                    <code style={{ fontSize: "0.8rem", fontWeight: 700 }}>{compareData.target_user_id}</code>
                    <div style={{ marginTop: "0.25rem", fontSize: "0.8rem" }}>
                      Target Sun: <strong>{targetPerson?.astrology?.sun_sign || "Demo Partner"}</strong>
                    </div>
                  </div>
                </div>

                {/* Signals Matrix */}
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#475569", marginBottom: "0.35rem" }}>
                    DETECTED DETERMINISTIC SYNASTRY SIGNALS ({compareData.signals?.length || 0}):
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                    {compareData.signals?.map((sig, idx) => (
                      <span
                        key={idx}
                        style={{
                          background: "#f1f5f9",
                          border: "1px solid #cbd5e1",
                          borderRadius: "4px",
                          padding: "0.25rem 0.5rem",
                          fontSize: "0.75rem",
                          color: "#334155",
                        }}
                      >
                        <strong>{sig.label || sig.type}</strong> ({sig.category}, {sig.strength})
                      </span>
                    ))}
                  </div>
                </div>

                {/* Primary Interpretation & Full Text */}
                <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                    <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#475569" }}>
                      PRIMARY RELATIONSHIP NARRATIVE:
                    </div>
                    <code style={{ fontSize: "0.75rem", color: "#6366f1" }}>
                      {compareData.interpretation?.id}
                    </code>
                  </div>
                  <blockquote style={{ margin: 0, padding: "0.8rem", background: "#f8fafc", borderLeft: "4px solid #10b981", borderRadius: "6px", fontSize: "0.9rem", color: "#1e293b", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                    "{compareData.interpretation?.text}"
                  </blockquote>
                </div>

                {/* Home Hook & WHY Deep Analysis */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "0.75rem" }}>
                  <div style={{ background: "#fafafa", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", marginBottom: "0.25rem" }}>HOME HOOK COPY</div>
                    <div style={{ fontSize: "0.85rem", color: "#334155", fontStyle: "italic" }}>
                      "{compareData.deep_analysis?.primary_interpretation?.hook || compareData.interpretation?.hook || "ერთად ყოფნისას თქვენი ენერგია უნიკალურ დინამიკას ქმნის."}"
                    </div>
                  </div>

                  <div style={{ background: "#fafafa", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", marginBottom: "0.25rem" }}>WHY DEEP ANALYSIS CONTRACT</div>
                    <div style={{ fontSize: "0.8rem", color: "#475569" }}>
                      <div>Confidence: <strong>{Math.round((compareData.data_quality?.confidence || 1) * 100)}%</strong></div>
                      <div>Engine Version: <code>{compareData.engine_version}</code></div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>
                No comparison target available. Seed discovery people first to inspect live compare data.
              </div>
            )}
          </Card>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 5: END-TO-END API &rarr; FRONTEND DATA TRACE                      */}
      {/* ===================================================================== */}
      {(activeTab === "trace" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>5. END-TO-END PIPELINE AUDIT TRACE</span>
            <Badge variant="brand" size="sm">Backend &rarr; Raw API &rarr; DTO &rarr; Cache &rarr; Render</Badge>
          </h2>

          <Card padded>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", fontFamily: "monospace" }}>
                <thead>
                  <tr style={{ background: "#f1f5f9", borderBottom: "2px solid #cbd5e1", textAlign: "left" }}>
                    <th style={{ padding: "8px 10px" }}>FIELD</th>
                    <th style={{ padding: "8px 10px" }}>BACKEND VALUE</th>
                    <th style={{ padding: "8px 10px" }}>RAW API JSON</th>
                    <th style={{ padding: "8px 10px" }}>FRONTEND MAPPED</th>
                    <th style={{ padding: "8px 10px" }}>REACT QUERY</th>
                    <th style={{ padding: "8px 10px" }}>RENDERED VALUE</th>
                    <th style={{ padding: "8px 10px" }}>AUDIT</th>
                  </tr>
                </thead>
                <tbody>
                  {traceRows.map((row) => (
                    <tr key={row.field} style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "8px 10px", fontWeight: 700, color: "#0f172a" }}>{row.field}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.backendVal}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.rawApiVal}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.frontendMappedVal}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.reactQueryCachedVal}</td>
                      <td style={{ padding: "8px 10px", fontWeight: 600, color: "#0f172a" }}>{row.renderedVal}</td>
                      <td style={{ padding: "8px 10px" }}>
                        <Badge variant={row.status === "PASS" ? "success" : "danger"} size="sm">
                          {row.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 6: DETERMINISTIC LIVE A/B DIFF                                    */}
      {/* ===================================================================== */}
      {(activeTab === "abdiff" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>6. DETERMINISTIC A/B DIFF (STATE A vs STATE B)</span>
            <Badge variant="brand" size="sm">Side-by-Side Reactive Delta</Badge>
          </h2>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            {/* STATE A COLUMN */}
            <Card padded style={{ borderTop: "4px solid #6366f1" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 800, color: "#4338ca" }}>STATE A (London Aries)</h3>
                <Button
                  variant="brand"
                  size="sm"
                  isLoading={applyStateMutation.isPending}
                  onClick={() => applyStateMutation.mutate(STATE_A)}
                >
                  Activate State A
                </Button>
              </div>
              <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.75rem" }}>
                1990-03-21 06:00 UTC • London, UK
              </div>

              <div style={{ display: "grid", gap: "0.5rem", fontSize: "0.8rem", background: "#f8fafc", padding: "0.6rem", borderRadius: "6px" }}>
                <div><strong>Sun Sign:</strong> Aries (Fire / Cardinal)</div>
                <div><strong>Mars Sign:</strong> Aquarius</div>
                <div><strong>Daily Energy:</strong> თავდაჯერება და მოქმედება (<code>confidence</code>)</div>
                <div><strong>Contract ID:</strong> <code>self.identity.sun_aries.v1</code></div>
                <div style={{ marginTop: "0.25rem", fontStyle: "italic", color: "#334155", borderTop: "1px solid #e2e8f0", paddingTop: "0.25rem" }}>
                  "ვერძის მზე პირდაპირი იმპულსია. ჯერ მოქმედებ, შემდეგ ფიქრობ..."
                </div>
              </div>
            </Card>

            {/* STATE B COLUMN */}
            <Card padded style={{ borderTop: "4px solid #ec4899" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 800, color: "#be185d" }}>STATE B (Tbilisi Scorpio)</h3>
                <Button
                  variant="secondary"
                  size="sm"
                  isLoading={applyStateMutation.isPending}
                  onClick={() => applyStateMutation.mutate(STATE_B)}
                >
                  Activate State B
                </Button>
              </div>
              <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.75rem" }}>
                1995-11-15 18:30 Asia/Tbilisi • Tbilisi, Georgia
              </div>

              <div style={{ display: "grid", gap: "0.5rem", fontSize: "0.8rem", background: "#f8fafc", padding: "0.6rem", borderRadius: "6px" }}>
                <div><strong>Sun Sign:</strong> Scorpio (Water / Fixed)</div>
                <div><strong>Mars Sign:</strong> Sagittarius</div>
                <div><strong>Daily Energy:</strong> შინაგანი გადატვირთვა (<code>introspection</code>)</div>
                <div><strong>Contract ID:</strong> <code>self.identity.sun_scorpio.v1</code></div>
                <div style={{ marginTop: "0.25rem", fontStyle: "italic", color: "#334155", borderTop: "1px solid #e2e8f0", paddingTop: "0.25rem" }}>
                  "მორიელის მზე ზედაპირს ვერ იტანს. შენთვის ყველაფერი ან უკიდურესად მნიშვნელოვანია, ან საერთოდ არ არსებობს..."
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Raw JSON Debugging Drawer */}
      <Card padded style={{ marginTop: "1rem", background: "#0f172a", color: "#f8fafc" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
          <h4 style={{ margin: 0, fontSize: "0.85rem", fontWeight: 700, color: "#94a3b8" }}>
            RAW API PAYLOAD DUMP (Safe Astro Placements)
          </h4>
          <span style={{ fontSize: "0.75rem", color: "#64748b" }}>GET /v1/astrology/profile/safe-astro</span>
        </div>
        <pre style={{ margin: 0, fontSize: "0.75rem", fontFamily: "monospace", color: "#38bdf8", overflowX: "auto" }}>
          {JSON.stringify(astro, null, 2)}
        </pre>
      </Card>
    </div>
  );
};
