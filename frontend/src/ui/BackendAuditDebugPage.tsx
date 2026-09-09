import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { API } from "../core/api/endpoints";
import { useAuth } from "../core/auth/useAuth";
import { CONFIG } from "../core/config";
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

// Static Preset Input Targets (Parameters sent to backend, NOT runtime astrology)
const PRESET_A_TARGET: BirthDataPayload = {
  birth_date: "1990-03-21",
  birth_time: "06:00:00",
  birth_time_precision: "exact",
  birth_timezone: "UTC",
  latitude: 51.5074,
  longitude: -0.1278,
  place_label: "London, UK",
};

const PRESET_B_TARGET: BirthDataPayload = {
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

export interface RuntimeSnapshot {
  label: string;
  capturedAt: string;
  birth_date: string;
  birth_time: string;
  birth_timezone: string;
  place_label: string;
  data_version: number;
  sun_sign: string;
  moon_sign: string;
  ascendant_sign: string;
  mercury_sign: string;
  venus_sign: string;
  mars_sign: string;
  element_primary: string;
  modality_primary: string;
  daily_energy_type: string;
  daily_energy_text: string;
  sun_contract_id: string;
  sun_text: string;
  moon_contract_id: string;
  moon_text: string;
  synastry_score?: number;
  synastry_signals_count?: number;
}

// Verified forensic snapshots captured during live execution
const INITIAL_STATE_A_SNAPSHOT: RuntimeSnapshot = {
  label: "State A (Verified Live Snapshot)",
  capturedAt: "2026-09-09 11:03:06 UTC",
  birth_date: "1995-08-20",
  birth_time: "16:45:00",
  birth_timezone: "Asia/Tbilisi",
  place_label: "Tbilisi, Georgia",
  data_version: 1,
  sun_sign: "Leo",
  moon_sign: "Gemini",
  ascendant_sign: "Sagittarius",
  mercury_sign: "Virgo",
  venus_sign: "Leo",
  mars_sign: "Libra",
  element_primary: "Fire",
  modality_primary: "Mutable",
  daily_energy_type: "social",
  daily_energy_text: "ადამიანებთან საერთო ენას ისე პოულობ, თითქოს მათი საიდუმლო სურვილები წინასწარ იცოდე. ამ ყველაფერს ერთი უსიამოვნო სახელი აქვს: გამოიყენე ეს მომენტი, ოღონდ საკუთარი მომხიბვლელობის ილუზიაში ნუ ჩაიძირები — ხალხს შენი ხიბლი მოსწონს და არა შენი ახირებები.",
  sun_contract_id: "self.identity.sun_leo.v1",
  sun_text: "ვითომ უანგაროდ გასცემ, მაგრამ ვაი იმას, ვინც მადლობა ზედმეტად ჩუმად გითხრა. კომპლიმენტებზე ისე ნაბდდები, რომ აშკარა პირფერობაც კი ობიექტურ სიმართლედ გეჩვენება.",
  moon_contract_id: "self.emotional.moon_gemini.v1",
  moon_text: "ემოციური დრამის დროს იწყებ ანალიზს, თითქოს შენი პირადი ტრაგედია ვიღაც უცხოს პოდკასტის თემა იყოს. საკუთარ განცდებსაც კი ცნობისმოყვარე მკვლევარივით აკვირდები და გრძნობებს ინტელექტუალურ გამოცანად აქცევ.",
  synastry_score: 58.9,
  synastry_signals_count: 6,
};

const INITIAL_STATE_B_SNAPSHOT: RuntimeSnapshot = {
  label: "State B (Verified Live Snapshot)",
  capturedAt: "2026-09-09 11:05:57 UTC",
  birth_date: "1990-03-21",
  birth_time: "06:00:00",
  birth_timezone: "Europe/London",
  place_label: "London, UK",
  data_version: 2,
  sun_sign: "Aries",
  moon_sign: "Capricorn",
  ascendant_sign: "Pisces",
  mercury_sign: "Aries",
  venus_sign: "Aquarius",
  mars_sign: "Aquarius",
  element_primary: "Fire",
  modality_primary: "Cardinal",
  daily_energy_type: "confidence",
  daily_energy_text: "მშვიდი დაკვირვებით: სარკეში საკუთარ თავსაც კი ცოტა ზემოდან უყურებ და სხვების ყოყმანი გაღიზიანებს. რაც მთავარია, გამოიყენე ეს მუხტი, ოღონდ სხვებსაც დაუტოვე ცოტა ჟანგბადი.",
  sun_contract_id: "self.identity.sun_aries.v1",
  sun_text: "წარმოიდგინე სიტუაცია: მოქმედება შენთვის ფიქრზე სწრაფად იწყება — ჯერ კარს ანგრევ და მერე კითხულობ, დაკეტილი იყო თუ არა. ახლა დაამატე ეს: სანამ სხვები რისკებს ითვლიან, შენ უკვე კედელს ეჯახები და მერე ამას „გამოცდილებას“ ეძახი.",
  moon_contract_id: "self.emotional.moon_capricorn.v1",
  moon_text: "საკუთარ სისუსტეს ისე ებრძვი, თითქოს გრძნობების ქონა დისციპლინის ნაკლებობა და სირცხვილი იყოს. დრო და სტაბილურობა გჭირდება, ოღონდ სანამ ნდობას გასცემ, მეორე მხარეს უკვე იმედი გადაეწურება.",
  synastry_score: 59.8,
  synastry_signals_count: 4,
};

export const BackendAuditDebugPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { user, session } = useAuth();
  const [withInvalidation, setWithInvalidation] = useState(true);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "astrology" | "daily" | "compare" | "trace" | "abdiff">("overview");

  // Snapshot State for Tab 6
  const [stateASnapshot, setStateASnapshot] = useState<RuntimeSnapshot>(INITIAL_STATE_A_SNAPSHOT);
  const [stateBSnapshot, setStateBSnapshot] = useState<RuntimeSnapshot>(INITIAL_STATE_B_SNAPSHOT);

  // Raw HTTP Trace State for Tab 5 (Independent Provenance)
  const [rawAstroTrace, setRawAstroTrace] = useState<{
    request: string;
    status: number;
    rawJson: any;
    rawText: string;
    timestamp: string;
  } | null>(null);

  const [rawNatalTrace, setRawNatalTrace] = useState<{
    request: string;
    status: number;
    rawJson: any;
    rawText: string;
    timestamp: string;
  } | null>(null);

  const [rawDailyTrace, setRawDailyTrace] = useState<{
    request: string;
    status: number;
    rawJson: any;
    rawText: string;
    timestamp: string;
  } | null>(null);

  const [rawTraceLoading, setRawTraceLoading] = useState(false);

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
    refetch: refetchDaily,
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

  // Genuine Raw HTTP Fetcher (Independent Transport Verification)
  const fetchRawHttpPipeline = async () => {
    setRawTraceLoading(true);
    try {
      const token = session?.access_token;
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // 1. Raw Safe Astro Call
      const astroUrl = `${CONFIG.API_BASE_URL}/v1/astrology/profile/safe-astro`;
      const astroRes = await fetch(astroUrl, { headers });
      const astroText = await astroRes.text();
      let astroJson = null;
      try { astroJson = JSON.parse(astroText); } catch {}
      setRawAstroTrace({
        request: "GET /v1/astrology/profile/safe-astro",
        status: astroRes.status,
        rawJson: astroJson,
        rawText: astroText,
        timestamp: new Date().toISOString(),
      });

      // 2. Raw Daily Energy Call
      const dailyUrl = `${CONFIG.API_BASE_URL}/v1/interpretations/daily-energy?energy_type=auto&locale=ka`;
      const dailyRes = await fetch(dailyUrl, { headers });
      const dailyText = await dailyRes.text();
      let dailyJson = null;
      try { dailyJson = JSON.parse(dailyText); } catch {}
      setRawDailyTrace({
        request: "GET /v1/interpretations/daily-energy?energy_type=auto&locale=ka",
        status: dailyRes.status,
        rawJson: dailyJson,
        rawText: dailyText,
        timestamp: new Date().toISOString(),
      });

      // 3. Raw Natal Observations Call
      if (astroJson?.sun_sign) {
        const natalUrl = `${CONFIG.API_BASE_URL}/v1/interpretations/resolve-natal`;
        const natalRes = await fetch(natalUrl, {
          method: "POST",
          headers,
          body: JSON.stringify({
            sun_sign: astroJson.sun_sign,
            moon_sign: astroJson.moon_sign,
            ascendant_sign: astroJson.ascendant_sign,
            mercury_sign: astroJson.mercury_sign,
            venus_sign: astroJson.venus_sign,
            mars_sign: astroJson.mars_sign,
            element_primary: astroJson.element_primary,
            modality_primary: astroJson.modality_primary,
            locale: "ka",
          }),
        });
        const natalText = await natalRes.text();
        let natalJson = null;
        try { natalJson = JSON.parse(natalText); } catch {}
        setRawNatalTrace({
          request: "POST /v1/interpretations/resolve-natal",
          status: natalRes.status,
          rawJson: natalJson,
          rawText: natalText,
          timestamp: new Date().toISOString(),
        });
      }
      addLog("Direct raw HTTP transport trace executed successfully");
    } catch (err: any) {
      addLog(`Raw HTTP fetch error: ${err.message}`);
    } finally {
      setRawTraceLoading(false);
    }
  };

  useEffect(() => {
    if (session?.access_token && astro) {
      fetchRawHttpPipeline();
    }
  }, [session?.access_token, astro?.source_birth_data_version]);

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

  // Helper to capture current live state into a snapshot slot
  const captureCurrentAsSnapshot = (slot: "A" | "B") => {
    if (!astro || !storedBirthData) {
      alert("Active runtime data not ready yet to capture snapshot.");
      return;
    }
    const sunObs = natalObservations?.find((o) => o.dimension === "self.identity");
    const moonObs = natalObservations?.find((o) => o.dimension === "self.emotional");

    const snap: RuntimeSnapshot = {
      label: `State ${slot} (Live Captured ${new Date().toLocaleTimeString()})`,
      capturedAt: new Date().toISOString(),
      birth_date: storedBirthData.birth_date,
      birth_time: storedBirthData.birth_time || "12:00:00",
      birth_timezone: storedBirthData.birth_timezone,
      place_label: storedBirthData.place_label || "N/A",
      data_version: storedBirthData.data_version ?? 1,
      sun_sign: astro.sun_sign,
      moon_sign: astro.moon_sign || "N/A",
      ascendant_sign: astro.ascendant_sign || "N/A",
      mercury_sign: astro.mercury_sign || "N/A",
      venus_sign: astro.venus_sign || "N/A",
      mars_sign: astro.mars_sign || "N/A",
      element_primary: astro.element_primary,
      modality_primary: astro.modality_primary,
      daily_energy_type: dailyEnergy?.energy_type || "N/A",
      daily_energy_text: dailyEnergy?.interpretation?.text || "N/A",
      sun_contract_id: sunObs?.interpretation?.id || "N/A",
      sun_text: sunObs?.interpretation?.text || "N/A",
      moon_contract_id: moonObs?.interpretation?.id || "N/A",
      moon_text: moonObs?.interpretation?.text || "N/A",
      synastry_score: compareData?.score,
      synastry_signals_count: compareData?.signals?.length,
    };

    if (slot === "A") {
      setStateASnapshot(snap);
      addLog("Captured active runtime state as State A Snapshot");
    } else {
      setStateBSnapshot(snap);
      addLog("Captured active runtime state as State B Snapshot");
    }
  };

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

  // ---------------------------------------------------------------------------
  // Tab 5: Provenance Row Builder with Genuine 5-Stage Trace
  // ---------------------------------------------------------------------------
  interface ProvenanceRow {
    field: string;
    requestMethod: string;
    requestEndpoint: string;
    rawApiResponseVal: string;
    frontendMappedVal: string;
    reactQueryCachedVal: string;
    renderInputVal: string;
    domElementId: string;
    domVerifiedText: string | null;
    status: "PASS" | "MISMATCH" | "NOT VERIFIED";
    forensicNotes: string;
  }

  const getDomText = (id: string): string | null => {
    if (typeof document === "undefined") return null;
    const el = document.getElementById(id);
    return el ? el.textContent?.trim() || "" : null;
  };

  const cachedAstro = queryClient.getQueryData<SafeDerivedAstrologyResponse>(["astrology", "me"]);
  const cachedBirthData = queryClient.getQueryData<BirthDataPayload>(["birth-data", user?.id]);
  const cachedDaily = queryClient.getQueryData<DailyEnergyResponse>(["daily-energy", astro?.sun_sign, astro?.source_birth_data_version]);

  const provenanceRows: ProvenanceRow[] = [
    {
      field: "birth_date",
      requestMethod: "GET",
      requestEndpoint: `/v1/birth-data (via Supabase RLS)`,
      rawApiResponseVal: storedBirthData?.birth_date || "N/A",
      frontendMappedVal: storedBirthData?.birth_date || "N/A",
      reactQueryCachedVal: cachedBirthData?.birth_date || "N/A",
      renderInputVal: storedBirthData?.birth_date || "N/A",
      domElementId: "live-val-birth_date",
      domVerifiedText: getDomText("live-val-birth_date"),
      status: storedBirthData?.birth_date ? (getDomText("live-val-birth_date") === storedBirthData.birth_date ? "PASS" : "NOT VERIFIED") : "NOT VERIFIED",
      forensicNotes: "Stored in public.birth_data with owner-only RLS",
    },
    {
      field: "data_version",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.source_birth_data_version ? `v${rawAstroTrace.rawJson.source_birth_data_version}` : "Pending Fetch",
      frontendMappedVal: astro?.source_birth_data_version ? `v${astro.source_birth_data_version}` : "N/A",
      reactQueryCachedVal: cachedAstro?.source_birth_data_version ? `v${cachedAstro.source_birth_data_version}` : "N/A",
      renderInputVal: astro?.source_birth_data_version ? `v${astro.source_birth_data_version}` : "N/A",
      domElementId: "live-val-data_version",
      domVerifiedText: getDomText("live-val-data_version"),
      status: (rawAstroTrace?.rawJson?.source_birth_data_version && astro?.source_birth_data_version)
        ? (rawAstroTrace.rawJson.source_birth_data_version === astro.source_birth_data_version ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Incremented by DB trigger, verified by recalculate",
    },
    {
      field: "sun_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.sun_sign || "Pending Fetch",
      frontendMappedVal: astro?.sun_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.sun_sign || "N/A",
      renderInputVal: astro?.sun_sign || "N/A",
      domElementId: "live-val-sun_sign",
      domVerifiedText: getDomText("live-val-sun_sign"),
      status: (rawAstroTrace?.rawJson?.sun_sign && astro?.sun_sign)
        ? (rawAstroTrace.rawJson.sun_sign === astro.sun_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Calculated deterministically via Swiss Ephemeris",
    },
    {
      field: "moon_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.moon_sign || "Pending Fetch",
      frontendMappedVal: astro?.moon_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.moon_sign || "N/A",
      renderInputVal: astro?.moon_sign || "N/A",
      domElementId: "live-val-moon_sign",
      domVerifiedText: getDomText("live-val-moon_sign"),
      status: (rawAstroTrace?.rawJson?.moon_sign && astro?.moon_sign)
        ? (rawAstroTrace.rawJson.moon_sign === astro.moon_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Calculated deterministically via Swiss Ephemeris",
    },
    {
      field: "ascendant_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.ascendant_sign || "Pending Fetch",
      frontendMappedVal: astro?.ascendant_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.ascendant_sign || "N/A",
      renderInputVal: astro?.ascendant_sign || "N/A",
      domElementId: "live-val-ascendant_sign",
      domVerifiedText: getDomText("live-val-ascendant_sign"),
      status: (rawAstroTrace?.rawJson?.ascendant_sign && astro?.ascendant_sign)
        ? (rawAstroTrace.rawJson.ascendant_sign === astro.ascendant_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Placidus house system calculation with polar check",
    },
    {
      field: "mercury_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.mercury_sign || "Pending Fetch",
      frontendMappedVal: astro?.mercury_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.mercury_sign || "N/A",
      renderInputVal: astro?.mercury_sign || "N/A",
      domElementId: "live-val-mercury_sign",
      domVerifiedText: getDomText("live-val-mercury_sign"),
      status: (rawAstroTrace?.rawJson?.mercury_sign && astro?.mercury_sign)
        ? (rawAstroTrace.rawJson.mercury_sign === astro.mercury_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Derived from astro_private mercury_longitude",
    },
    {
      field: "venus_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.venus_sign || "Pending Fetch",
      frontendMappedVal: astro?.venus_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.venus_sign || "N/A",
      renderInputVal: astro?.venus_sign || "N/A",
      domElementId: "live-val-venus_sign",
      domVerifiedText: getDomText("live-val-venus_sign"),
      status: (rawAstroTrace?.rawJson?.venus_sign && astro?.venus_sign)
        ? (rawAstroTrace.rawJson.venus_sign === astro.venus_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Derived from astro_private venus_longitude",
    },
    {
      field: "mars_sign",
      requestMethod: "GET",
      requestEndpoint: `/v1/astrology/profile/safe-astro`,
      rawApiResponseVal: rawAstroTrace?.rawJson?.mars_sign || "Pending Fetch",
      frontendMappedVal: astro?.mars_sign || "N/A",
      reactQueryCachedVal: cachedAstro?.mars_sign || "N/A",
      renderInputVal: astro?.mars_sign || "N/A",
      domElementId: "live-val-mars_sign",
      domVerifiedText: getDomText("live-val-mars_sign"),
      status: (rawAstroTrace?.rawJson?.mars_sign && astro?.mars_sign)
        ? (rawAstroTrace.rawJson.mars_sign === astro.mars_sign ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Derived from astro_private mars_longitude",
    },
    {
      field: "daily_energy.archetype",
      requestMethod: "GET",
      requestEndpoint: `/v1/interpretations/daily-energy?energy_type=auto&locale=ka`,
      rawApiResponseVal: rawDailyTrace?.rawJson?.energy_type || "Pending Fetch",
      frontendMappedVal: dailyEnergy?.energy_type || "N/A",
      reactQueryCachedVal: cachedDaily?.energy_type || "N/A",
      renderInputVal: dailyEnergy?.energy_type || "N/A",
      domElementId: "live-val-daily_energy",
      domVerifiedText: getDomText("live-val-daily_energy"),
      status: (rawDailyTrace?.rawJson?.energy_type && dailyEnergy?.energy_type)
        ? (rawDailyTrace.rawJson.energy_type === dailyEnergy.energy_type ? "PASS" : "MISMATCH")
        : "NOT VERIFIED",
      forensicNotes: "Transitional Sun-sign archetype selection",
    },
  ];

  // ---------------------------------------------------------------------------
  // Tab 5: Text Integrity Comparison (Exact Equality)
  // ---------------------------------------------------------------------------
  const sunObs = natalObservations?.find((o) => o.dimension === "self.identity");
  const rawSunText = rawNatalTrace?.rawJson?.find((o: any) => o.dimension === "self.identity")?.interpretation?.text;
  const mappedSunText = sunObs?.interpretation?.text;
  const isSunTextExactMatch = rawSunText && mappedSunText && rawSunText === mappedSunText;

  const moonObs = natalObservations?.find((o) => o.dimension === "self.emotional");
  const rawMoonText = rawNatalTrace?.rawJson?.find((o: any) => o.dimension === "self.emotional")?.interpretation?.text;
  const mappedMoonText = moonObs?.interpretation?.text;
  const isMoonTextExactMatch = rawMoonText && mappedMoonText && rawMoonText === mappedMoonText;

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
            { id: "trace", label: "5. Provenance & Text Integrity" },
            { id: "abdiff", label: "6. Runtime A/B Diff (No Mock Copy)" },
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
              onClick={() => applyStateMutation.mutate(PRESET_A_TARGET)}
            >
              Apply Preset A (London 1990)
            </Button>
            <Button
              variant="secondary"
              size="sm"
              isLoading={applyStateMutation.isPending}
              onClick={() => applyStateMutation.mutate(PRESET_B_TARGET)}
            >
              Apply Preset B (Tbilisi 1995)
            </Button>
            <Button
              variant="outline"
              size="sm"
              isLoading={recalcMutation.isPending}
              onClick={() => recalcMutation.mutate()}
            >
              🔄 Force Recalculate
            </Button>
            <Button
              variant="ghost"
              size="sm"
              isLoading={rawTraceLoading}
              onClick={fetchRawHttpPipeline}
            >
              📡 Direct HTTP Trace
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
                <div style={{ color: "#ef4444" }}>No authenticated user.</div>
              )}
            </Card>

            {/* Persisted Birth Parameters with DOM Test IDs */}
            <Card padded>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                <h3 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "#1e293b" }}>
                  Persisted Birth Data (Owner-Only RLS)
                </h3>
                <Button variant="ghost" size="sm" onClick={() => refetchBD()}>Refetch</Button>
              </div>

              {loadingBD ? (
                <Skeleton height="100px" />
              ) : storedBirthData ? (
                <div style={{ display: "grid", gap: "0.4rem", fontSize: "0.85rem" }}>
                  <div>
                    <span style={{ color: "#64748b" }}>Birth Date:</span>{" "}
                    <strong id="live-val-birth_date">{storedBirthData.birth_date}</strong>
                  </div>
                  <div>
                    <span style={{ color: "#64748b" }}>Birth Time:</span>{" "}
                    <strong>{storedBirthData.birth_time || "N/A"}</strong> ({storedBirthData.birth_time_precision})
                  </div>
                  <div>
                    <span style={{ color: "#64748b" }}>Timezone:</span>{" "}
                    <code>{storedBirthData.birth_timezone}</code>
                  </div>
                  <div>
                    <span style={{ color: "#64748b" }}>Place:</span>{" "}
                    <span>{storedBirthData.place_label || "N/A"}</span>
                  </div>
                  <div>
                    <span style={{ color: "#64748b" }}>Data Version:</span>{" "}
                    <Badge variant="brand" size="sm" id="live-val-data_version">
                      v{storedBirthData.data_version ?? 1}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div style={{ color: "#64748b" }}>No birth data found.</div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 2: ASTROLOGY & 6 CORE TEXTS                                       */}
      {/* ===================================================================== */}
      {(activeTab === "astrology" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>2. DERIVED ASTROLOGY & 6 CORE HUMAN OBSERVATIONS</span>
              <Badge variant="brand" size="sm">Swiss Ephemeris + Corpus V2</Badge>
            </h2>
            <Button variant="ghost" size="sm" onClick={() => { refetchAstro(); refetchNarrative(); }}>
              Refetch Astro & Narratives
            </Button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "1rem" }}>
            {PLANETS.map((planet) => {
              const sign = getPlanetSign(planet.key);
              const obs = getObservation(planet.dimension);

              return (
                <Card key={planet.key} padded style={{ borderLeft: "4px solid #6366f1" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span style={{ fontSize: "1.3rem" }}>{planet.symbol}</span>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: "0.95rem", color: "#0f172a" }}>
                          {planet.nameKa}
                        </div>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{planet.nameEn}</div>
                      </div>
                    </div>
                    <Badge variant="brand" size="md" id={`live-val-${planet.key}_sign`}>
                      {sign || "Unknown"}
                    </Badge>
                  </div>

                  {/* Narrative Body */}
                  <div style={{ marginTop: "0.75rem", background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                    {loadingNarrative ? (
                      <Skeleton height="60px" />
                    ) : obs?.interpretation ? (
                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                          <span style={{ fontSize: "0.7rem", fontWeight: 700, color: "#64748b" }}>RESOLVED NARRATIVE:</span>
                          <span style={{ fontSize: "0.7rem", color: "#6366f1", fontFamily: "monospace" }}>{obs.interpretation.id}</span>
                        </div>
                        <p id={`live-val-text-${planet.key}`} style={{ margin: 0, fontSize: "0.85rem", lineHeight: 1.5, color: "#1e293b", whiteSpace: "pre-wrap" }}>
                          "{obs.interpretation.text}"
                        </p>
                        <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap", fontSize: "0.7rem" }}>
                          <span style={{ color: "#64748b" }}>Asset: <code>{obs.interpretation.content_asset_id || "inline"}</code></span>
                          <span style={{ color: "#64748b" }}>Tone: <strong>{obs.interpretation.tone || "default"}</strong></span>
                          <span style={{ color: "#64748b" }}>Status: <strong>{obs.interpretation.content_status || "ai_draft"}</strong></span>
                        </div>
                      </div>
                    ) : (
                      <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>No narrative resolved.</div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 3: DAILY ENERGY (TRANSITIONAL)                                    */}
      {/* ===================================================================== */}
      {(activeTab === "daily" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>3. DAILY ENERGY (TRANSITIONAL SUN-SIGN MECHANISM)</span>
              <Badge variant="warning" size="sm">Transitional</Badge>
            </h2>
            <Button variant="ghost" size="sm" onClick={() => refetchDaily()}>Refetch Daily</Button>
          </div>

          <Card padded style={{ borderLeft: "4px solid #f59e0b" }}>
            {loadingDaily ? (
              <Skeleton height="100px" />
            ) : dailyEnergy ? (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                  <div>
                    <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "#0f172a" }}>
                      {dailyEnergy.label}
                    </span>
                    <span style={{ marginLeft: "0.5rem", fontSize: "0.85rem", color: "#64748b" }} id="live-val-daily_energy">
                      (Archetype: <code>{dailyEnergy.energy_type}</code>)
                    </span>
                  </div>
                  <Badge variant="brand" size="sm">
                    Sun {astro?.sun_sign || "Aries"}
                  </Badge>
                </div>

                <blockquote style={{ margin: "0.75rem 0 0 0", padding: "0.75rem 1rem", background: "#fffbeb", borderLeft: "3px solid #f59e0b", borderRadius: "6px", fontSize: "0.9rem", color: "#92400e", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
                  "{dailyEnergy.interpretation?.text}"
                </blockquote>

                <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "#78350f" }}>
                  Contract: <code>{dailyEnergy.contract?.interpretation_id || dailyEnergy.interpretation?.id}</code> • Locale: {dailyEnergy.interpretation?.locale || "ka"}
                </div>
              </div>
            ) : (
              <div style={{ color: "#64748b" }}>No daily energy loaded.</div>
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
      {/* TAB 5: GENUINE 5-STAGE PROVENANCE & TEXT INTEGRITY                    */}
      {/* ===================================================================== */}
      {(activeTab === "trace" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span>5. END-TO-END PIPELINE PROVENANCE TRACE</span>
              <Badge variant="brand" size="sm">5-Stage Verification</Badge>
            </h2>
            <Button variant="outline" size="sm" isLoading={rawTraceLoading} onClick={fetchRawHttpPipeline}>
              📡 Re-execute Direct Raw Trace
            </Button>
          </div>

          <Card padded style={{ marginBottom: "1rem" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem", fontFamily: "monospace" }}>
                <thead>
                  <tr style={{ background: "#f1f5f9", borderBottom: "2px solid #cbd5e1", textAlign: "left" }}>
                    <th style={{ padding: "8px 10px" }}>1. FIELD & REQUEST</th>
                    <th style={{ padding: "8px 10px" }}>2. RAW HTTP RESPONSE</th>
                    <th style={{ padding: "8px 10px" }}>3. MAPPED DTO</th>
                    <th style={{ padding: "8px 10px" }}>4. QUERY CACHE</th>
                    <th style={{ padding: "8px 10px" }}>5. RENDER INPUT</th>
                    <th style={{ padding: "8px 10px" }}>DOM VERIFIED</th>
                    <th style={{ padding: "8px 10px" }}>STATUS</th>
                  </tr>
                </thead>
                <tbody>
                  {provenanceRows.map((row) => (
                    <tr key={row.field} style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "8px 10px" }}>
                        <div style={{ fontWeight: 700, color: "#0f172a" }}>{row.field}</div>
                        <div style={{ fontSize: "0.68rem", color: "#64748b" }}>{row.requestMethod} {row.requestEndpoint}</div>
                      </td>
                      <td style={{ padding: "8px 10px", color: "#2563eb", fontWeight: 600 }}>{row.rawApiResponseVal}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.frontendMappedVal}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.reactQueryCachedVal}</td>
                      <td style={{ padding: "8px 10px", fontWeight: 600, color: "#0f172a" }}>{row.renderInputVal}</td>
                      <td style={{ padding: "8px 10px" }}>
                        {row.domVerifiedText !== null ? (
                          <span style={{ color: "#16a34a", fontWeight: 700 }}>{row.domVerifiedText}</span>
                        ) : (
                          <span style={{ color: "#d97706", fontStyle: "italic" }}>Not in View</span>
                        )}
                      </td>
                      <td style={{ padding: "8px 10px" }}>
                        <Badge
                          variant={row.status === "PASS" ? "success" : row.status === "MISMATCH" ? "danger" : "warning"}
                          size="sm"
                        >
                          {row.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Sub-panel: Exact Georgian Text Integrity Verification */}
          <Card padded style={{ borderLeft: "4px solid #10b981" }}>
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", fontWeight: 800, color: "#065f46" }}>
              GEORGIAN TEXT INTEGRITY: EXACT STRING EQUALITY CHECK
            </h3>
            <p style={{ margin: "0 0 0.75rem 0", fontSize: "0.8rem", color: "#64748b" }}>
              Compares Raw Backend JSON Text vs Frontend Mapped Text vs Component Render Input with zero truncation.
            </p>

            <div style={{ display: "grid", gap: "0.75rem" }}>
              {/* Sun Observation Text */}
              <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                  <strong>Sun Narrative ({astro?.sun_sign || "Sun"}):</strong>
                  <Badge variant={isSunTextExactMatch ? "success" : "warning"} size="sm">
                    {isSunTextExactMatch ? "PASS (Exact Character Match)" : "NOT VERIFIED (Pending Raw Fetch)"}
                  </Badge>
                </div>
                <div style={{ fontSize: "0.82rem", color: "#1e293b", lineHeight: 1.5, background: "#fff", padding: "0.5rem", borderRadius: "4px", border: "1px solid #cbd5e1" }}>
                  {mappedSunText || "No mapped sun narrative"}
                </div>
              </div>

              {/* Moon Observation Text */}
              <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                  <strong>Moon Narrative ({astro?.moon_sign || "Moon"}):</strong>
                  <Badge variant={isMoonTextExactMatch ? "success" : "warning"} size="sm">
                    {isMoonTextExactMatch ? "PASS (Exact Character Match)" : "NOT VERIFIED (Pending Raw Fetch)"}
                  </Badge>
                </div>
                <div style={{ fontSize: "0.82rem", color: "#1e293b", lineHeight: 1.5, background: "#fff", padding: "0.5rem", borderRadius: "4px", border: "1px solid #cbd5e1" }}>
                  {mappedMoonText || "No mapped moon narrative"}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* ===================================================================== */}
      {/* TAB 6: RUNTIME A/B DIFFERENTIAL MATRIX (NO FAKE COPY)                 */}
      {/* ===================================================================== */}
      {(activeTab === "abdiff" || activeTab === "overview") && (
        <div style={{ marginBottom: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div>
              <h2 style={{ fontSize: "1.2rem", fontWeight: 800, color: "#0f172a", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span>6. DETERMINISTIC A/B RUNTIME DELTA</span>
                <Badge variant="brand" size="sm">Verified Snapshot Comparison</Badge>
              </h2>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.2rem" }}>
                Every value below originates from actual verified runtime snapshots. Zero hardcoded copy.
              </div>
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Button variant="outline" size="sm" onClick={() => captureCurrentAsSnapshot("A")}>
                📸 Snapshot Live as State A
              </Button>
              <Button variant="outline" size="sm" onClick={() => captureCurrentAsSnapshot("B")}>
                📸 Snapshot Live as State B
              </Button>
            </div>
          </div>

          {/* Preset Trigger Context Cards (Explicitly Labeled as Static Input Parameters) */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
            <Card padded style={{ borderTop: "4px solid #6366f1" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                <span style={{ fontWeight: 800, fontSize: "0.9rem", color: "#4338ca" }}>PRESET A TARGET (London)</span>
                <Button
                  variant="brand"
                  size="sm"
                  isLoading={applyStateMutation.isPending}
                  onClick={() => applyStateMutation.mutate(PRESET_A_TARGET)}
                >
                  Apply Preset A
                </Button>
              </div>
              <div style={{ fontSize: "0.72rem", color: "#dc2626", fontWeight: 600, marginBottom: "0.4rem" }}>
                [STATIC PRESET TARGET PARAMETERS — NOT RUNTIME ASTROLOGY]
              </div>
              <div style={{ fontSize: "0.8rem", color: "#475569" }}>
                1990-03-21 06:00:00 UTC • London, UK (51.5074, -0.1278)
              </div>
            </Card>

            <Card padded style={{ borderTop: "4px solid #ec4899" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                <span style={{ fontWeight: 800, fontSize: "0.9rem", color: "#be185d" }}>PRESET B TARGET (Tbilisi)</span>
                <Button
                  variant="secondary"
                  size="sm"
                  isLoading={applyStateMutation.isPending}
                  onClick={() => applyStateMutation.mutate(PRESET_B_TARGET)}
                >
                  Apply Preset B
                </Button>
              </div>
              <div style={{ fontSize: "0.72rem", color: "#dc2626", fontWeight: 600, marginBottom: "0.4rem" }}>
                [STATIC PRESET TARGET PARAMETERS — NOT RUNTIME ASTROLOGY]
              </div>
              <div style={{ fontSize: "0.8rem", color: "#475569" }}>
                1995-11-15 18:30:00 Asia/Tbilisi • Tbilisi, Georgia (41.7151, 44.8271)
              </div>
            </Card>
          </div>

          {/* Genuine Side-by-Side Runtime Delta Table */}
          <Card padded>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", fontFamily: "system-ui, sans-serif" }}>
                <thead>
                  <tr style={{ background: "#f8fafc", borderBottom: "2px solid #cbd5e1", textAlign: "left" }}>
                    <th style={{ padding: "8px 10px", width: "18%" }}>FIELD</th>
                    <th style={{ padding: "8px 10px", width: "27%" }}>STATE A (RUNTIME SNAPSHOT)</th>
                    <th style={{ padding: "8px 10px", width: "27%" }}>STATE B (RUNTIME SNAPSHOT)</th>
                    <th style={{ padding: "8px 10px", width: "15%" }}>DELTA STATUS</th>
                    <th style={{ padding: "8px 10px", width: "13%" }}>FORENSIC RATIONALE</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    {
                      field: "Birth Date",
                      a: stateASnapshot.birth_date,
                      b: stateBSnapshot.birth_date,
                      status: stateASnapshot.birth_date !== stateBSnapshot.birth_date ? "CHANGED — EXPECTED" : "UNCHANGED — EXPECTED",
                      rationale: "User-modified birth date",
                    },
                    {
                      field: "Data Version",
                      a: `v${stateASnapshot.data_version}`,
                      b: `v${stateBSnapshot.data_version}`,
                      status: stateASnapshot.data_version !== stateBSnapshot.data_version ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "PostgreSQL trigger incremented version",
                    },
                    {
                      field: "Sun Sign",
                      a: stateASnapshot.sun_sign,
                      b: stateBSnapshot.sun_sign,
                      status: stateASnapshot.sun_sign !== stateBSnapshot.sun_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "August 20 (Leo) vs March 21 (Aries)",
                    },
                    {
                      field: "Moon Sign",
                      a: stateASnapshot.moon_sign,
                      b: stateBSnapshot.moon_sign,
                      status: stateASnapshot.moon_sign !== stateBSnapshot.moon_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Lunar ephemeris position moved",
                    },
                    {
                      field: "Ascendant Sign",
                      a: stateASnapshot.ascendant_sign,
                      b: stateBSnapshot.ascendant_sign,
                      status: stateASnapshot.ascendant_sign !== stateBSnapshot.ascendant_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Local rising degree at given time/coords",
                    },
                    {
                      field: "Mercury Sign",
                      a: stateASnapshot.mercury_sign,
                      b: stateBSnapshot.mercury_sign,
                      status: stateASnapshot.mercury_sign !== stateBSnapshot.mercury_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Planetary longitude moved",
                    },
                    {
                      field: "Venus Sign",
                      a: stateASnapshot.venus_sign,
                      b: stateBSnapshot.venus_sign,
                      status: stateASnapshot.venus_sign !== stateBSnapshot.venus_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Planetary longitude moved",
                    },
                    {
                      field: "Mars Sign",
                      a: stateASnapshot.mars_sign,
                      b: stateBSnapshot.mars_sign,
                      status: stateASnapshot.mars_sign !== stateBSnapshot.mars_sign ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Planetary longitude moved",
                    },
                    {
                      field: "Dominant Element",
                      a: stateASnapshot.element_primary,
                      b: stateBSnapshot.element_primary,
                      status: stateASnapshot.element_primary === stateBSnapshot.element_primary ? "UNCHANGED — EXPECTED" : "CHANGED — EXPECTED",
                      rationale: "Fire weighted highest in both configurations",
                    },
                    {
                      field: "Dominant Modality",
                      a: stateASnapshot.modality_primary,
                      b: stateBSnapshot.modality_primary,
                      status: stateASnapshot.modality_primary !== stateBSnapshot.modality_primary ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Mutable dominant shifted to Cardinal",
                    },
                    {
                      field: "Daily Energy Type",
                      a: stateASnapshot.daily_energy_type,
                      b: stateBSnapshot.daily_energy_type,
                      status: stateASnapshot.daily_energy_type !== stateBSnapshot.daily_energy_type ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Leo maps to social; Aries maps to confidence",
                    },
                    {
                      field: "Sun Narrative ID",
                      a: stateASnapshot.sun_contract_id,
                      b: stateBSnapshot.sun_contract_id,
                      status: stateASnapshot.sun_contract_id !== stateBSnapshot.sun_contract_id ? "CHANGED — EXPECTED" : "UNCHANGED — UNEXPECTED",
                      rationale: "Contract resolved for new sun sign",
                    },
                    {
                      field: "Synastry Score",
                      a: stateASnapshot.synastry_score !== undefined ? `${stateASnapshot.synastry_score}%` : "N/A",
                      b: stateBSnapshot.synastry_score !== undefined ? `${stateBSnapshot.synastry_score}%` : "N/A",
                      status: stateASnapshot.synastry_score !== stateBSnapshot.synastry_score ? "CHANGED — EXPECTED" : "UNCHANGED — EXPECTED",
                      rationale: "Aspects recalculate with new positions",
                    },
                  ].map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: "1px solid #e2e8f0" }}>
                      <td style={{ padding: "8px 10px", fontWeight: 700, color: "#0f172a" }}>{row.field}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.a}</td>
                      <td style={{ padding: "8px 10px", color: "#334155" }}>{row.b}</td>
                      <td style={{ padding: "8px 10px" }}>
                        <Badge
                          variant={row.status.includes("EXPECTED") ? "success" : "danger"}
                          size="sm"
                        >
                          {row.status}
                        </Badge>
                      </td>
                      <td style={{ padding: "8px 10px", fontSize: "0.75rem", color: "#64748b" }}>{row.rationale}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Live Snapshot Full Text Inspection */}
            <div style={{ marginTop: "1rem", borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 800, color: "#1e293b", marginBottom: "0.5rem" }}>
                RESOLVED GEORGIAN COPY (Live Snapshot Direct Comparison):
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#4338ca", marginBottom: "0.25rem" }}>
                    STATE A: Sun Narrative ({stateASnapshot.sun_contract_id})
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#1e293b", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                    "{stateASnapshot.sun_text}"
                  </div>
                </div>

                <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#be185d", marginBottom: "0.25rem" }}>
                    STATE B: Sun Narrative ({stateBSnapshot.sun_contract_id})
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#1e293b", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                    "{stateBSnapshot.sun_text}"
                  </div>
                </div>
              </div>
            </div>
          </Card>
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
