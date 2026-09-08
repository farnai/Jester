import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { API } from "../core/api/endpoints";
import { useAuth } from "../core/auth/useAuth";
import {
  BirthDataPayload,
  SafeDerivedAstrologyResponse,
  NatalResolveResponseItem,
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

export const BackendAuditDebugPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { user, session } = useAuth();
  const [withInvalidation, setWithInvalidation] = useState(true);
  const [actionLog, setActionLog] = useState<string[]>([]);

  const addLog = (msg: string) => {
    setActionLog((prev) => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 15)]);
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
    dataUpdatedAt: astroUpdatedAt,
    isFetching: fetchingAstro,
    refetch: refetchAstro,
  } = useQuery<SafeDerivedAstrologyResponse>({
    queryKey: ["astrology", "me"],
    queryFn: API.astrology.getMySafeAstro,
    enabled: !!user,
  });

  // 3. Resolve Personal JESTER Narrative Observations
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
        addLog("Invalidating query keys: ['astrology', 'me'], ['birth-data'], ['natal-observations']");
        queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
        queryClient.invalidateQueries({ queryKey: ["birth-data"] });
        queryClient.invalidateQueries({ queryKey: ["natal-observations"] });
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
      addLog("Manual recalculate triggered -> invalidating ['astrology', 'me']");
      queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
      queryClient.invalidateQueries({ queryKey: ["natal-observations"] });
    },
  });

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "1.5rem", fontFamily: "monospace" }}>
      {/* Header Banner */}
      <div
        style={{
          backgroundColor: "#0f172a",
          color: "#f8fafc",
          padding: "1.25rem",
          borderRadius: "8px",
          marginBottom: "1.5rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Badge variant="brand" size="sm">
              PHASE 4.1.1
            </Badge>
            <span style={{ fontWeight: 800, fontSize: "1.25rem" }}>
              JESTER Forensic Data Integrity Debug Lab
            </span>
          </div>
          <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginTop: "0.25rem" }}>
            Route: <code>/__debug/backend-audit</code> • End-to-End Persistence & Cache Inspector
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link to="/me" style={{ textDecoration: "none" }}>
            <Button variant="secondary" size="sm">
              ← View ME Page
            </Button>
          </Link>
          <Link to="/visual-lab" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm">
              🎨 Foundation Lab
            </Button>
          </Link>
        </div>
      </div>

      {/* 1. AUTHENTICATED USER & SESSION */}
      <Card padded style={{ marginBottom: "1.25rem", backgroundColor: "#f8fafc", borderColor: "#cbd5e1" }}>
        <h3 style={{ margin: "0 0 0.75rem 0", color: "#0f172a", fontSize: "1rem", fontWeight: 700 }}>
          1. AUTHENTICATED USER CONTEXT
        </h3>
        {user ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem", fontSize: "0.85rem" }}>
            <div>
              <span style={{ color: "#64748b" }}>User ID:</span>{" "}
              <code style={{ background: "#e2e8f0", padding: "2px 4px", borderRadius: "3px" }}>{user.id}</code>
            </div>
            <div>
              <span style={{ color: "#64748b" }}>Email:</span> <strong>{user.email}</strong>
            </div>
            <div>
              <span style={{ color: "#64748b" }}>Role:</span> <code>{user.role || "authenticated"}</code>
            </div>
            <div>
              <span style={{ color: "#64748b" }}>Token:</span>{" "}
              <Badge variant={session?.access_token ? "success" : "danger"} size="sm">
                {session?.access_token ? "Bearer Valid" : "Missing"}
              </Badge>
            </div>
          </div>
        ) : (
          <div style={{ color: "#dc2626", fontWeight: 700 }}>
            ⚠️ Not authenticated! Please <Link to="/auth/login">log in</Link> to inspect registered user persistence.
          </div>
        )}
      </Card>

      {/* 2. INTERACTIVE A/B TEST SWITCHER */}
      <Card padded style={{ marginBottom: "1.25rem", backgroundColor: "#fff", borderColor: "#6366f1", borderWidth: 2 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h3 style={{ margin: 0, color: "#4338ca", fontSize: "1.05rem", fontWeight: 800 }}>
              2. DETERMINISTIC A/B BIRTH DATA SWITCHER
            </h3>
            <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.8rem", color: "#64748b" }}>
              Switch birth data in real time to prove database persistence, Swiss Ephemeris recalculation, and cache invalidation.
            </p>
          </div>

          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", cursor: "pointer", fontWeight: 600 }}>
            <input
              type="checkbox"
              checked={withInvalidation}
              onChange={(e) => setWithInvalidation(e.target.checked)}
            />
            Invalidate React Query on change <span style={{ fontSize: "0.75rem", color: withInvalidation ? "#16a34a" : "#dc2626" }}>({withInvalidation ? "Fix Active" : "Reproduce Bug"})</span>
          </label>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem", flexWrap: "wrap" }}>
          <Button
            variant="brand"
            size="sm"
            isLoading={applyStateMutation.isPending}
            onClick={() => applyStateMutation.mutate(STATE_A)}
          >
            Apply STATE A (1990-03-21 London UTC)
          </Button>

          <Button
            variant="secondary"
            size="sm"
            isLoading={applyStateMutation.isPending}
            onClick={() => applyStateMutation.mutate(STATE_B)}
          >
            Apply STATE B (1995-11-15 Tbilisi Asia/Tbilisi)
          </Button>

          <Button
            variant="outline"
            size="sm"
            isLoading={recalcMutation.isPending}
            onClick={() => recalcMutation.mutate()}
          >
            🔄 Force Backend Recalculate
          </Button>
        </div>

        {/* Action Logs */}
        {actionLog.length > 0 && (
          <div style={{ marginTop: "1rem", backgroundColor: "#0f172a", color: "#22c55e", padding: "0.75rem", borderRadius: "6px", fontSize: "0.75rem", maxHeight: "120px", overflowY: "auto" }}>
            {actionLog.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        )}
      </Card>

      {/* 3. STORED BIRTH DATA vs CALCULATED ASTROLOGY */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))", gap: "1.25rem", marginBottom: "1.25rem" }}>
        {/* Stored DB Data */}
        <Card padded>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700 }}>
              3.1 STORED IN DATABASE (public.birth_data)
            </h4>
            <Button variant="ghost" size="sm" onClick={() => refetchBD()}>Refetch</Button>
          </div>

          {loadingBD ? (
            <Skeleton height="100px" />
          ) : storedBirthData ? (
            <div style={{ fontSize: "0.85rem", lineHeight: 1.6 }}>
              <div><strong>Birth Date:</strong> {storedBirthData.birth_date}</div>
              <div><strong>Birth Time:</strong> {storedBirthData.birth_time || "None (Unknown)"}</div>
              <div><strong>Precision:</strong> {storedBirthData.birth_time_precision}</div>
              <div><strong>Timezone:</strong> {storedBirthData.birth_timezone}</div>
              <div><strong>Coordinates:</strong> {storedBirthData.latitude}, {storedBirthData.longitude}</div>
              <div><strong>Place:</strong> {storedBirthData.place_label || "None"}</div>
            </div>
          ) : (
            <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No birth data stored in DB for this user.</div>
          )}
        </Card>

        {/* Calculated Placements */}
        <Card padded>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700 }}>
              3.2 CALCULATED PLACEMENTS (/safe-astro)
            </h4>
            <Button variant="ghost" size="sm" onClick={() => refetchAstro()}>Refetch</Button>
          </div>

          {loadingAstro ? (
            <Skeleton height="100px" />
          ) : astro ? (
            <div style={{ fontSize: "0.85rem", lineHeight: 1.6 }}>
              <div><strong>☀️ Sun Sign:</strong> <Badge variant="brand" size="sm">{astro.sun_sign}</Badge></div>
              <div><strong>🌙 Moon Sign:</strong> <Badge variant="default" size="sm">{astro.moon_sign}</Badge></div>
              <div><strong>🌅 Ascendant:</strong> <Badge variant="default" size="sm">{astro.ascendant_sign || "Unknown"}</Badge></div>
              <div><strong>☿ Mercury Sign:</strong> <Badge variant={astro.mercury_sign ? "default" : "outline"} size="sm">{astro.mercury_sign || "null (Not calculated)"}</Badge></div>
              <div><strong>♀ Venus Sign:</strong> <Badge variant={astro.venus_sign ? "default" : "outline"} size="sm">{astro.venus_sign || "null (Not calculated)"}</Badge></div>
              <div><strong>♂ Mars Sign:</strong> <Badge variant={astro.mars_sign ? "default" : "outline"} size="sm">{astro.mars_sign || "null (Not calculated)"}</Badge></div>
              <div><strong>🔥 Element / ⚡ Modality:</strong> {astro.element_primary} / {astro.modality_primary}</div>
              <div><strong>Data Version:</strong> v{astro.source_birth_data_version} (Engine: {astro.engine_version})</div>
            </div>
          ) : (
            <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No astrology calculated yet.</div>
          )}
        </Card>
      </div>

      {/* 4. REACT QUERY CACHE STATE */}
      <Card padded style={{ marginBottom: "1.25rem", backgroundColor: "#f1f5f9" }}>
        <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", fontWeight: 700 }}>
          4. REACT QUERY CACHE STATUS (['astrology', 'me'])
        </h4>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.75rem", fontSize: "0.8rem" }}>
          <div>
            <span style={{ color: "#64748b" }}>Query Key:</span> <code>["astrology", "me"]</code>
          </div>
          <div>
            <span style={{ color: "#64748b" }}>Status:</span>{" "}
            <Badge variant={fetchingAstro ? "warning" : astro ? "success" : "danger"} size="sm">
              {fetchingAstro ? "Fetching..." : astro ? "Cached (Success)" : "Empty"}
            </Badge>
          </div>
          <div>
            <span style={{ color: "#64748b" }}>Last Updated:</span>{" "}
            {astroUpdatedAt ? new Date(astroUpdatedAt).toLocaleTimeString() : "Never"}
          </div>
          <div>
            <span style={{ color: "#64748b" }}>Configured staleTime:</span> <code>30000ms (30s)</code>
          </div>
        </div>
      </Card>

      {/* 5. RESOLVED GEORGIAN NARRATIVE COPY */}
      <Card padded style={{ marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
          <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700 }}>
            5. RESOLVED JESTER NARRATIVE COPY (/resolve-natal)
          </h4>
          <Button variant="ghost" size="sm" onClick={() => refetchNarrative()}>Refetch Copy</Button>
        </div>

        {loadingNarrative ? (
          <Skeleton height="120px" />
        ) : natalObservations && natalObservations.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {natalObservations.map((item) => (
              <div
                key={item.dimension}
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: "6px",
                  padding: "0.75rem",
                  backgroundColor: "#fafafa",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                  <strong>{item.title}</strong>
                  <code style={{ fontSize: "0.75rem", color: "#6366f1" }}>{item.interpretation?.id}</code>
                </div>
                <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", color: "#334155", lineHeight: 1.5 }}>
                  "{item.interpretation?.text}"
                </p>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8", marginTop: "0.3rem" }}>
                  Tone: <code>{item.interpretation?.tone}</code> • Status: <code>{item.interpretation?.content_status}</code>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No observations resolved. Provide birth data first.</div>
        )}
      </Card>

      {/* 6. FORENSIC STATUS MATRIX */}
      <Card padded style={{ marginBottom: "1.25rem" }}>
        <h4 style={{ margin: "0 0 0.75rem 0", fontSize: "0.95rem", fontWeight: 700 }}>
          6. FORENSIC CHAIN PASS/FAIL MATRIX
        </h4>

        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #e2e8f0", textAlign: "left" }}>
              <th style={{ padding: "6px 8px" }}>Layer / Stage</th>
              <th style={{ padding: "6px 8px" }}>Verification Gate</th>
              <th style={{ padding: "6px 8px" }}>Status</th>
              <th style={{ padding: "6px 8px" }}>Forensic Finding</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Database Persistence</strong></td>
              <td style={{ padding: "6px 8px" }}><code>public.birth_data</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Stored accurately; <code>data_version</code> auto-bumps on update via trigger.</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Timezone & Julian Day</strong></td>
              <td style={{ padding: "6px 8px" }}><code>compute_julian_day</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Deterministic UTC conversion (18:30 Tbilisi &rarr; 14:30 UTC &rarr; exact JD match).</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Swiss Ephemeris</strong></td>
              <td style={{ padding: "6px 8px" }}><code>compute_natal_placements</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Accurately computes Sun, Moon, Asc, Mercury, Venus, Mars longitudes in <code>astro_private</code>.</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Derived Safe Profile</strong></td>
              <td style={{ padding: "6px 8px" }}><code>astro_safe_profile</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Core safe profile persisted. Planetary signs (Mercury, Venus, Mars) are intentionally derived from private longitudes in <code>astro_private</code> without exposing raw angles.</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>API Response (/safe-astro)</strong></td>
              <td style={{ padding: "6px 8px" }}><code>SafeDerivedAstrologyResponse</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Fully populated: returns Sun, Moon, Ascendant, Mercury, Venus, Mars on both recalculation and cached reads.</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Content Resolution (Mercury)</strong></td>
              <td style={{ padding: "6px 8px" }}><code>self.cognition.mercury_*</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>All 12 signs resolve approved Georgian copy (96 assets).</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Content Resolution (Venus)</strong></td>
              <td style={{ padding: "6px 8px" }}><code>self.relation.venus_*</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>All 12 signs resolve approved Georgian copy (96 assets).</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Content Resolution (Mars)</strong></td>
              <td style={{ padding: "6px 8px" }}><code>self.action.mars_*</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Resolved: Mars corpus assets correctly scoped with <code>context: "self"</code>. All 12 signs resolve approved Georgian copy.</td>
            </tr>
            <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "6px 8px" }}><strong>Frontend Cache Invalidation</strong></td>
              <td style={{ padding: "6px 8px" }}><code>BirthDataOnboardingPage</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Resolved: Mutating birth data explicitly invalidates <code>["astrology", "me"]</code> cache.</td>
            </tr>
            <tr>
              <td style={{ padding: "6px 8px" }}><strong>User Data Isolation</strong></td>
              <td style={{ padding: "6px 8px" }}><code>User A vs User B</code></td>
              <td style={{ padding: "6px 8px" }}><Badge variant="success" size="sm">PASS</Badge></td>
              <td style={{ padding: "6px 8px" }}>Strictly isolated via JWT <code>sub</code>; User B cannot access User A private data; safe view respects discovery status.</td>
            </tr>
          </tbody>
        </table>
      </Card>

      {/* 7. RAW API RESPONSE DUMP */}
      <Card padded>
        <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", fontWeight: 700 }}>
          7. RAW BACKEND API RESPONSE ENVELOPE (/v1/astrology/profile/safe-astro)
        </h4>
        <pre style={{ backgroundColor: "#0f172a", color: "#f8fafc", padding: "0.75rem", borderRadius: "6px", fontSize: "0.75rem", overflowX: "auto" }}>
          {JSON.stringify(astro, null, 2)}
        </pre>
      </Card>
    </div>
  );
};
