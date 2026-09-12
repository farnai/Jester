import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { InspectorDataResponse } from "../../core/api/types";
import { LoadingState, ErrorState } from "../../shared/StatusState";
import { RuntimeJson } from "../../shared/runtime/RuntimeJson";

type SectionTab = "all" | "natal" | "synastry" | "discovery" | "connection" | "chat" | "daily_energy";
type LangFilter = "all" | "ka" | "en";
type DailyEnergyLayer = "all" | "archetypes" | "assets" | "do" | "dont" | "neutral";

export const ContentInspectorPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<SectionTab>("all");
  const [natalSubFilter, setNatalSubFilter] = useState<string>("all");
  const [synastrySubFilter, setSynastrySubFilter] = useState<string>("all");
  const [dailyLayer, setDailyLayer] = useState<DailyEnergyLayer>("all");
  const [dailyArchetypeFilter, setDailyArchetypeFilter] = useState<string>("all");
  const [langFilter, setLangFilter] = useState<LangFilter>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [expandedCardIds, setExpandedCardIds] = useState<Record<string, boolean>>({});

  const { data, isLoading, error, refetch, isFetching } = useQuery<InspectorDataResponse>({
    queryKey: ["content-inspector-data"],
    queryFn: () => API.inspector.getData(),
  });

  const toggleCard = (id: string) => {
    setExpandedCardIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const expandAll = () => {
    const allExpanded: Record<string, boolean> = {};
    if (data) {
      data.synastry_pipeline.forEach((item) => {
        allExpanded[`synastry_${item.rule_id}`] = true;
      });
      data.natal_sections.forEach((sec) => {
        sec.assets.forEach((a) => {
          allExpanded[`natal_${a.asset_id}`] = true;
        });
      });
      data.discovery_items.forEach((item) => {
        allExpanded[`discovery_${item.asset_id}`] = true;
      });
      data.connection_items.forEach((item) => {
        allExpanded[`conn_${item.asset_id}`] = true;
      });
      data.chat_items.forEach((item) => {
        allExpanded[`chat_${item.asset_id}`] = true;
      });
      data.daily_energy.archetypes.forEach((item) => {
        allExpanded[`daily_${item.id}`] = true;
      });
    }
    setExpandedCardIds(allExpanded);
  };

  const collapseAll = () => {
    setExpandedCardIds({});
  };

  // Search filter helper
  const matchesSearch = (textOrFields: (string | undefined | null)[]) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase().trim();
    return textOrFields.some((f) => f && f.toLowerCase().includes(query));
  };

  // Filtered Synastry Pipeline
  const filteredSynastry = useMemo(() => {
    if (!data) return [];
    return data.synastry_pipeline.filter((item) => {
      if (synastrySubFilter !== "all" && item.category.toLowerCase() !== synastrySubFilter.toLowerCase()) {
        return false;
      }
      return matchesSearch([
        item.trigger,
        item.aspect,
        item.rule_id,
        item.canonical_rule,
        item.signal,
        item.category,
        item.label,
        item.contract_id,
        item.why_asset?.text,
        item.why_asset?.asset_id,
        ...(item.us_assets || []).map((u) => u.text),
        ...(item.connection_invitations || []).map((c) => c.text),
        ...(item.conversation_starters || []).map((s) => s.text),
      ]);
    });
  }, [data, synastrySubFilter, searchQuery]);

  // Filtered Natal Sections
  const filteredNatal = useMemo(() => {
    if (!data) return [];
    return data.natal_sections
      .filter((sec) => {
        if (natalSubFilter !== "all" && sec.key !== natalSubFilter) return false;
        return true;
      })
      .map((sec) => ({
        ...sec,
        assets: sec.assets.filter((a) =>
          matchesSearch([
            sec.planet,
            sec.source,
            sec.semantic_domain,
            a.asset_id,
            a.interpretation_id,
            a.text,
            a.tone,
            a.depth,
            a.category,
          ])
        ),
      }))
      .filter((sec) => sec.assets.length > 0 || !searchQuery.trim());
  }, [data, natalSubFilter, searchQuery]);

  // Filtered Discovery Items
  const filteredDiscovery = useMemo(() => {
    if (!data) return [];
    return data.discovery_items.filter((item) =>
      matchesSearch([item.sign, item.source, item.mode, item.asset_id, item.interpretation_id, item.text])
    );
  }, [data, searchQuery]);

  // Filtered Connection Items
  const filteredConnection = useMemo(() => {
    if (!data) return [];
    return data.connection_items.filter((item) =>
      matchesSearch([item.category, item.asset_id, item.interpretation_id, item.variant_key, item.text])
    );
  }, [data, searchQuery]);

  // Filtered Chat Items
  const filteredChat = useMemo(() => {
    if (!data) return [];
    return data.chat_items.filter((item) =>
      matchesSearch([
        item.category,
        item.asset_id,
        item.interpretation_id,
        item.source_signal,
        item.variant_key,
        item.text,
      ])
    );
  }, [data, searchQuery]);

  // Filtered Daily Energy Archetypes (Layer A)
  const filteredDailyEnergy = useMemo(() => {
    if (!data) return [];
    return data.daily_energy.archetypes.filter((item) => {
      if (dailyArchetypeFilter !== "all" && item.id !== dailyArchetypeFilter) {
        return false;
      }
      return matchesSearch([
        item.id,
        item.name,
        item.description,
        item.contract_id,
        item.narrative_ka,
        item.narrative_en,
        item.centralized_spec?.engine_source,
        item.centralized_spec?.detection_mode,
        ...(item.centralized_spec?.trigger_pairs || []),
        ...(item.do_tags || []),
        ...(item.dont_tags || []),
        ...(item.do_tags_ka || []),
        ...(item.dont_tags_ka || []),
      ]);
    });
  }, [data, dailyArchetypeFilter, searchQuery]);

  // Filtered Daily Energy Narrative Assets (Layer B)
  const filteredDailyAssets = useMemo(() => {
    if (!data?.daily_energy.interpretation_assets) return [];
    return data.daily_energy.interpretation_assets.filter((asset) => {
      if (dailyArchetypeFilter !== "all" && asset.archetype_id !== dailyArchetypeFilter) {
        return false;
      }
      if (langFilter !== "all" && asset.locale !== langFilter) {
        return false;
      }
      return matchesSearch([
        asset.asset_id,
        asset.interpretation_id,
        asset.archetype_id,
        asset.archetype_name,
        asset.locale,
        asset.tone,
        asset.persona,
        asset.variant_key,
        asset.text,
        asset.status,
      ]);
    });
  }, [data, dailyArchetypeFilter, langFilter, searchQuery]);

  // Filtered Daily Energy DO Tags (Layer C)
  const filteredDailyDoTags = useMemo(() => {
    if (!data?.daily_energy.do_tags) return [];
    return data.daily_energy.do_tags.filter((t) => {
      if (dailyArchetypeFilter !== "all" && t.archetype_id !== dailyArchetypeFilter) {
        return false;
      }
      return matchesSearch([
        t.tag_id,
        t.archetype_id,
        t.archetype_name,
        t.text_ka,
        t.text_en,
      ]);
    });
  }, [data, dailyArchetypeFilter, searchQuery]);

  // Filtered Daily Energy DON'T Tags (Layer D)
  const filteredDailyDontTags = useMemo(() => {
    if (!data?.daily_energy.dont_tags) return [];
    return data.daily_energy.dont_tags.filter((t) => {
      if (dailyArchetypeFilter !== "all" && t.archetype_id !== dailyArchetypeFilter) {
        return false;
      }
      return matchesSearch([
        t.tag_id,
        t.archetype_id,
        t.archetype_name,
        t.text_ka,
        t.text_en,
      ]);
    });
  }, [data, dailyArchetypeFilter, searchQuery]);

  if (isLoading) {
    return <LoadingState message="ინსპექტორის მონაცემები იტვირთება / Loading inspector projection..." />;
  }

  if (error || !data) {
    return (
      <ErrorState
        error={error instanceof Error ? error.message : "Failed to load inspector projection"}
        onRetry={() => refetch()}
      />
    );
  }

  const { summary, integrity } = data;

  return (
    <div style={{ maxWidth: "1400px", margin: "0 auto", padding: "1.5rem", fontFamily: "system-ui, sans-serif" }}>
      {/* 1. TOP HEADER & NAVIGATION */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem", borderBottom: "2px solid #e2e8f0", paddingBottom: "1rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
            <h1 style={{ fontSize: "1.75rem", fontWeight: 900, color: "#0f172a", margin: 0 }}>
              JESTER — CONTENT & LOGIC INSPECTOR
            </h1>
            <span style={{ padding: "0.25rem 0.6rem", background: "#f1f5f9", color: "#475569", borderRadius: "6px", fontSize: "0.75rem", fontWeight: 700, border: "1px solid #cbd5e1" }}>
              INTERNAL QA SURFACE
            </span>
          </div>
          <p style={{ margin: "0.35rem 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            Read-only causal projection: <code>TRIGGER → ASPECT → CANONICAL RULE → SIGNAL → CATEGORY → CONTRACT → ASSET → INVITATION → STARTER</code>
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <Link
            to="/discover"
            style={{ padding: "0.5rem 0.9rem", background: "#f8fafc", color: "#334155", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "0.85rem", textDecoration: "none", fontWeight: 600 }}
          >
            ← Back to App
          </Link>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            style={{ padding: "0.5rem 1rem", background: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", fontSize: "0.85rem", fontWeight: 600, cursor: "pointer" }}
          >
            {isFetching ? "Refreshing..." : "🔄 Refresh Cache"}
          </button>
        </div>
      </div>

      {/* 2. DYNAMIC SUMMARY STATS BANNER */}
      <div style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "10px", padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.75rem", marginBottom: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            <div>
              <span style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Frozen Assets Corpus</span>
              <div style={{ fontSize: "1.3rem", fontWeight: 800, color: "#0f172a" }}>
                {summary.actual_frozen_assets}{" "}
                <span style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 500 }}>(Expected: {summary.expected_frozen_assets})</span>
              </div>
            </div>

            <div
              style={{
                padding: "0.35rem 0.75rem",
                borderRadius: "6px",
                fontWeight: 800,
                fontSize: "0.8rem",
                background: summary.status === "OK" ? "#dcfce7" : "#fef3c7",
                color: summary.status === "OK" ? "#166534" : "#92400e",
                border: `1px solid ${summary.status === "OK" ? "#86efac" : "#fcd34d"}`,
              }}
            >
              STATUS: {summary.status} {summary.status === "MISMATCH" && `(+${summary.actual_frozen_assets - summary.expected_frozen_assets} items)`}
            </div>

            <div
              style={{
                padding: "0.35rem 0.75rem",
                borderRadius: "6px",
                fontWeight: 800,
                fontSize: "0.8rem",
                background: integrity.overall_status === "OK" ? "#dcfce7" : "#fee2e2",
                color: integrity.overall_status === "OK" ? "#166534" : "#991b1b",
                border: `1px solid ${integrity.overall_status === "OK" ? "#86efac" : "#fca5a5"}`,
              }}
            >
              INTEGRITY: {integrity.overall_status}
            </div>
          </div>

          <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
            {summary.note}
          </div>
        </div>

        {/* Section counts grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.75rem" }}>
          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Natal Assets</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.natal}</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Batches 1A-5B (9 files)</div>
          </div>

          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Synastry Assets</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.synastry}</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Batch 6 (24 contracts)</div>
          </div>

          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Discovery Presence</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.discovery}</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Batch 7 (12 zodiac signs)</div>
          </div>

          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Connection Invitations</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.connection}</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Batch 7 (6 categories)</div>
          </div>

          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Chat Starters</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.chat}</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>Batch 7 (43 starters)</div>
          </div>

          <div style={{ background: "#ffffff", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}>
            <div style={{ fontSize: "0.7rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>Daily Energy</div>
            <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#1e293b" }}>{summary.section_counts.daily_energy} Archetypes</div>
            <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>13 DO/DON'T tags pairs</div>
          </div>
        </div>
      </div>

      {/* 3. CONTROLS: SECTIONS, FILTERS, SEARCH, EXPAND/COLLAPSE */}
      <div style={{ background: "#ffffff", border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem", marginBottom: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Section Tabs */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.75rem" }}>
          {[
            { id: "all", label: "ALL CONTENT" },
            { id: "natal", label: `NATAL (${summary.section_counts.natal})` },
            { id: "synastry", label: `SYNASTRY (${summary.section_counts.synastry})` },
            { id: "discovery", label: `DISCOVERY (${summary.section_counts.discovery})` },
            { id: "connection", label: `CONNECTION (${summary.section_counts.connection})` },
            { id: "chat", label: `CHAT (${summary.section_counts.chat})` },
            { id: "daily_energy", label: `DAILY ENERGY (${summary.section_counts.daily_energy})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id as SectionTab)}
              style={{
                padding: "0.45rem 0.85rem",
                borderRadius: "6px",
                border: activeSection === tab.id ? "2px solid #2563eb" : "1px solid #cbd5e1",
                background: activeSection === tab.id ? "#eff6ff" : "#ffffff",
                color: activeSection === tab.id ? "#1d4ed8" : "#475569",
                fontWeight: activeSection === tab.id ? 800 : 600,
                fontSize: "0.85rem",
                cursor: "pointer",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Sub-Filters & Search Line */}
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap", flex: 1 }}>
            {/* Search Input */}
            <div style={{ position: "relative", minWidth: "280px", flex: 1, maxWidth: "480px" }}>
              <input
                type="text"
                placeholder="Search rule, signal, planet, text, asset ID, contract..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: "100%",
                  padding: "0.5rem 0.75rem",
                  fontSize: "0.85rem",
                  border: "1px solid #94a3b8",
                  borderRadius: "6px",
                  outline: "none",
                }}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  style={{
                    position: "absolute",
                    right: "8px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    color: "#64748b",
                    cursor: "pointer",
                    fontWeight: 700,
                  }}
                >
                  ✕
                </button>
              )}
            </div>

            {/* Natal Sub-filter (Contextual: only shown when NATAL is active) */}
            {activeSection === "natal" && (
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>Planet/Domain:</span>
                <select
                  value={natalSubFilter}
                  onChange={(e) => setNatalSubFilter(e.target.value)}
                  style={{ padding: "0.4rem 0.6rem", fontSize: "0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                >
                  <option value="all">All Natal Placements</option>
                  <option value="sun">Sun (Batch 1A)</option>
                  <option value="moon">Moon (Batch 1B)</option>
                  <option value="ascendant">Ascendant (Batch 2A)</option>
                  <option value="mercury">Mercury (Batch 2B)</option>
                  <option value="venus">Venus (Batch 3A)</option>
                  <option value="mars">Mars (Batch 3B)</option>
                  <option value="elements_modalities">Elements & Modalities (Batch 4)</option>
                  <option value="synthesis">Synthesis (Batch 5)</option>
                  <option value="life_verdicts">Life Verdicts (Batch 5B)</option>
                </select>
              </div>
            )}

            {/* Synastry Sub-filter (Contextual: only shown when SYNASTRY is active) */}
            {activeSection === "synastry" && (
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>Category:</span>
                <select
                  value={synastrySubFilter}
                  onChange={(e) => setSynastrySubFilter(e.target.value)}
                  style={{ padding: "0.4rem 0.6rem", fontSize: "0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                >
                  <option value="all">All Synastry Categories</option>
                  <option value="attraction">Attraction</option>
                  <option value="harmony">Harmony</option>
                  <option value="growth">Growth</option>
                  <option value="communication">Communication</option>
                  <option value="stability">Stability</option>
                  <option value="notice">Notice</option>
                </select>
              </div>
            )}

            {/* Daily Energy Sub-filters (Contextual: only shown when DAILY ENERGY is active) */}
            {activeSection === "daily_energy" && (
              <>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <span style={{ fontSize: "0.75rem", color: "#b45309", fontWeight: 700 }}>Layer:</span>
                  <select
                    value={dailyLayer}
                    onChange={(e) => setDailyLayer(e.target.value as DailyEnergyLayer)}
                    style={{ padding: "0.4rem 0.6rem", fontSize: "0.8rem", borderRadius: "6px", border: "1px solid #fcd34d", background: "#fffbeb", fontWeight: 600 }}
                  >
                    <option value="all">All 5 Layers</option>
                    <option value="archetypes">Layer A: Archetypes (13)</option>
                    <option value="assets">Layer B: Narrative Assets ({data?.daily_energy.interpretation_assets?.length || 831})</option>
                    <option value="do">Layer C: DO Tags (39)</option>
                    <option value="dont">Layer D: DON'T Tags (39)</option>
                    <option value="neutral">Layer E: Neutral Baseline</option>
                  </select>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <span style={{ fontSize: "0.75rem", color: "#b45309", fontWeight: 700 }}>Archetype:</span>
                  <select
                    value={dailyArchetypeFilter}
                    onChange={(e) => setDailyArchetypeFilter(e.target.value)}
                    style={{ padding: "0.4rem 0.6rem", fontSize: "0.8rem", borderRadius: "6px", border: "1px solid #fcd34d" }}
                  >
                    <option value="all">All Archetypes</option>
                    {data?.daily_energy.archetypes.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name} ({a.id})
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            {/* Language filter */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>Lang:</span>
              <select
                value={langFilter}
                onChange={(e) => setLangFilter(e.target.value as LangFilter)}
                style={{ padding: "0.4rem 0.6rem", fontSize: "0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="all">ALL</option>
                <option value="ka">KA (Georgian)</option>
                <option value="en">EN (English)</option>
              </select>
            </div>
          </div>

          {/* Expand / Collapse Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <button
              onClick={expandAll}
              style={{ padding: "0.4rem 0.75rem", background: "#f1f5f9", color: "#334155", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
            >
              [+] Expand All
            </button>
            <button
              onClick={collapseAll}
              style={{ padding: "0.4rem 0.75rem", background: "#f1f5f9", color: "#334155", border: "1px solid #cbd5e1", borderRadius: "6px", fontSize: "0.8rem", cursor: "pointer", fontWeight: 600 }}
            >
              [-] Collapse All
            </button>
          </div>
        </div>
      </div>

      {/* 4. CONTENT SECTIONS CONTAINER */}
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* ========================================================================= */}
        {/* SECTION: SYNASTRY PIPELINE (CAUSAL CHAIN: RULE -> SIGNAL -> CONTRACT -> ASSET -> INVITATION -> STARTER) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "synastry") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #9333ea", paddingBottom: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#581c87", margin: 0 }}>
                  SYNASTRY PIPELINE (49 SIGNAL DEFINITIONS & 44 CANONICAL RULES)
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#7e22ce" }}>
                  Trigger → Aspect → Canonical Rule → Signal → Category → Interpretation Contract → Interpretation Asset → Connection Invitation → Conversation Starter
                </div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#6b21a8" }}>
                Showing {filteredSynastry.length} of {data.synastry_pipeline.length} items
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {filteredSynastry.map((item) => {
                const cardKey = `synastry_${item.rule_id}`;
                const isExpanded = !!expandedCardIds[cardKey];

                return (
                  <div
                    key={item.rule_id}
                    style={{
                      background: "#ffffff",
                      border: `1px solid ${item.integrity_status === "OK" ? "#cbd5e1" : "#f87171"}`,
                      borderRadius: "8px",
                      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                      overflow: "hidden",
                    }}
                  >
                    {/* Collapsed Header / Compact Card View */}
                    <div
                      onClick={() => toggleCard(cardKey)}
                      style={{
                        padding: "0.75rem 1rem",
                        background: isExpanded ? "#faf5ff" : "#ffffff",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        flexWrap: "wrap",
                        gap: "0.5rem",
                        userSelect: "none",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                        <span style={{ fontWeight: 800, color: "#7e22ce", fontSize: "0.95rem" }}>
                          {isExpanded ? "▼" : "▶"} {item.trigger}
                        </span>

                        <span style={{ padding: "0.2rem 0.5rem", background: "#f3e8ff", color: "#6b21a8", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase" }}>
                          {item.aspect}
                        </span>

                        <span style={{ padding: "0.2rem 0.5rem", background: "#f1f5f9", color: "#334155", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700, fontFamily: "monospace" }}>
                          Rule: {item.canonical_rule}
                        </span>

                        <span style={{ padding: "0.2rem 0.5rem", background: "#e0e7ff", color: "#3730a3", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          Signal: {item.signal}
                        </span>

                        <span style={{ padding: "0.2rem 0.5rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          Category: {item.category}
                        </span>

                        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#475569" }}>
                          "{item.label}"
                        </span>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span
                          style={{
                            padding: "0.2rem 0.5rem",
                            borderRadius: "4px",
                            fontSize: "0.7rem",
                            fontWeight: 800,
                            background: item.integrity_status === "OK" ? "#dcfce7" : "#fee2e2",
                            color: item.integrity_status === "OK" ? "#166534" : "#991b1b",
                          }}
                        >
                          {item.integrity_status}
                        </span>
                        <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
                          {isExpanded ? "Collapse" : "Expand"}
                        </span>
                      </div>
                    </div>

                    {/* Full Expanded Inspection View */}
                    {isExpanded && (
                      <div style={{ padding: "1rem", borderTop: "1px solid #e2e8f0", display: "flex", flexDirection: "column", gap: "1rem" }}>
                        {/* Technical Metadata Header */}
                        <div style={{ background: "#f8fafc", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
                          <div style={{ fontSize: "0.75rem", fontWeight: 800, color: "#475569", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                            ⚙️ Technical Metadata
                          </div>
                          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.5rem", fontSize: "0.8rem" }}>
                            <div><strong>Trigger:</strong> {item.trigger}</div>
                            <div><strong>Aspect:</strong> {item.aspect}</div>
                            <div><strong>Canonical Rule ID:</strong> <code>{item.canonical_rule}</code></div>
                            <div><strong>Signal Type:</strong> <code>{item.signal}</code></div>
                            <div><strong>Category:</strong> <code>{item.category}</code></div>
                            <div><strong>Default Strength:</strong> <code>{item.default_strength}</code></div>
                            <div><strong>Contract ID:</strong> <code>{item.contract_id}</code></div>
                            <div><strong>Contract Type:</strong> <code>{item.contract_meaning.type}</code></div>
                          </div>
                        </div>

                        {/* Visible Causal Chain */}
                        <div style={{ background: "#faf5ff", padding: "0.75rem", borderRadius: "6px", border: "1px solid #e9d5ff" }}>
                          <div style={{ fontSize: "0.75rem", fontWeight: 800, color: "#6b21a8", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                            🔗 Pipeline Causal Chain
                          </div>
                          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.4rem", fontSize: "0.75rem" }}>
                            {item.causal_chain.map((step, idx) => (
                              <React.Fragment key={idx}>
                                <span style={{ padding: "0.25rem 0.5rem", background: "#ffffff", border: "1px solid #d8b4fe", borderRadius: "4px", color: "#581c87", fontWeight: 600 }}>
                                  {step}
                                </span>
                                {idx < item.causal_chain.length - 1 && <span style={{ color: "#a855f7", fontWeight: 800 }}>↓</span>}
                              </React.Fragment>
                            ))}
                          </div>
                        </div>

                        {/* Layer 1: Interpretation Layer (Why Hook + US Dynamics) */}
                        <div style={{ border: "1px solid #cbd5e1", borderRadius: "6px", padding: "0.75rem", background: "#ffffff" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.35rem" }}>
                            <span style={{ fontSize: "0.8rem", fontWeight: 800, color: "#1e293b", textTransform: "uppercase" }}>
                              1. Interpretation Layer (Relationship Insight)
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#64748b", fontFamily: "monospace" }}>
                              Contract: {item.contract_id}
                            </span>
                          </div>

                          {/* Why Hook */}
                          {item.why_asset ? (
                            <div style={{ marginBottom: "0.6rem", padding: "0.5rem", background: "#f8fafc", borderRadius: "4px", border: "1px solid #e2e8f0" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                                <strong>Surface: WHY Hook</strong>
                                <code>Asset: {item.why_asset.asset_id}</code>
                              </div>
                              <div style={{ fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.4 }}>
                                "{item.why_asset.text}"
                              </div>
                            </div>
                          ) : (
                            <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontStyle: "italic", marginBottom: "0.5rem" }}>
                              No WHY hook asset configured for this contract.
                            </div>
                          )}

                          {/* US Dynamics */}
                          {item.us_assets && item.us_assets.length > 0 ? (
                            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                              {item.us_assets.map((us: any, uIdx: number) => (
                                <div key={uIdx} style={{ padding: "0.5rem", background: "#f8fafc", borderRadius: "4px", border: "1px solid #e2e8f0" }}>
                                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                                    <strong>Surface: US Dynamic ({us.variant_key || `v${uIdx + 1}`})</strong>
                                    <code>Asset: {us.asset_id}</code>
                                  </div>
                                  <div style={{ fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.4 }}>
                                    "{us.text}"
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ fontSize: "0.8rem", color: "#94a3b8", fontStyle: "italic" }}>
                              No US dynamic assets configured for this contract.
                            </div>
                          )}
                        </div>

                        {/* Layer 2: Connection Invitation Layer */}
                        <div style={{ border: "1px solid #86efac", borderRadius: "6px", padding: "0.75rem", background: "#f0fdf4" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem", borderBottom: "1px solid #bbf7d0", paddingBottom: "0.35rem" }}>
                            <span style={{ fontSize: "0.8rem", fontWeight: 800, color: "#166534", textTransform: "uppercase" }}>
                              2. Connection Invitation Layer (Insight → Action Invitation)
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#15803d", fontFamily: "monospace" }}>
                              Category: {item.category}
                            </span>
                          </div>

                          {item.connection_invitations && item.connection_invitations.length > 0 ? (
                            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                              {item.connection_invitations.map((inv: any, iIdx: number) => (
                                <div key={iIdx} style={{ padding: "0.5rem", background: "#ffffff", borderRadius: "4px", border: "1px solid #bbf7d0" }}>
                                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#166534", marginBottom: "0.25rem" }}>
                                    <strong>Variant: {inv.variant_key || `v${iIdx + 1}`}</strong>
                                    <code>Asset: {inv.asset_id}</code>
                                  </div>
                                  <div style={{ fontSize: "0.875rem", color: "#14532d", lineHeight: 1.4 }}>
                                    "{inv.text}"
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ fontSize: "0.8rem", color: "#86efac", fontStyle: "italic" }}>
                              No connection invitation assets matching category "{item.category}".
                            </div>
                          )}
                        </div>

                        {/* Layer 3: Conversation Starter Layer */}
                        <div style={{ border: "1px solid #93c5fd", borderRadius: "6px", padding: "0.75rem", background: "#eff6ff" }}>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem", borderBottom: "1px solid #bfdbfe", paddingBottom: "0.35rem" }}>
                            <span style={{ fontSize: "0.8rem", fontWeight: 800, color: "#1e40af", textTransform: "uppercase" }}>
                              3. Conversation Starter Layer (Conversational Continuation)
                            </span>
                            <span style={{ fontSize: "0.75rem", color: "#2563eb", fontFamily: "monospace" }}>
                              Contract / Fallback Starters
                            </span>
                          </div>

                          {item.conversation_starters && item.conversation_starters.length > 0 ? (
                            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                              {item.conversation_starters.map((starter: any, sIdx: number) => (
                                <div key={sIdx} style={{ padding: "0.5rem", background: "#ffffff", borderRadius: "4px", border: "1px solid #bfdbfe" }}>
                                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#1e40af", marginBottom: "0.25rem" }}>
                                    <strong>Starter {sIdx + 1} ({starter.variant_key || "default"})</strong>
                                    <code>Asset: {starter.asset_id}</code>
                                  </div>
                                  <div style={{ fontSize: "0.875rem", color: "#1e3a8a", lineHeight: 1.4 }}>
                                    "{starter.text}"
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ fontSize: "0.8rem", color: "#93c5fd", fontStyle: "italic" }}>
                              No conversation starters matched for this contract.
                            </div>
                          )}
                        </div>

                        {/* Raw JSON block */}
                        <RuntimeJson data={item} label={`Raw Synastry Pipeline JSON (${item.rule_id})`} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION: NATAL CONTENT (BY PLANETARY SOURCE & SEMANTIC DOMAIN) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "natal") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #0284c7", paddingBottom: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#0369a1", margin: 0 }}>
                  NATAL CORPUS BY PLANETARY SOURCE & SEMANTIC DOMAIN
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#0284c7" }}>
                  Sun, Moon, Ascendant, Mercury, Venus, Mars (with Semantic Firewall), Elements/Modalities, Synthesis, Life Verdicts
                </div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#0284c7" }}>
                {filteredNatal.length} Placement Groups
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {filteredNatal.map((sec) => (
                <div key={sec.key} style={{ background: "#ffffff", border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1.25rem" }}>
                  {/* Planetary Header */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.5rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.75rem", marginBottom: "0.75rem" }}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                        <span style={{ fontSize: "1.15rem", fontWeight: 900, color: "#0f172a" }}>
                          {sec.planet.toUpperCase()}
                        </span>
                        <span style={{ padding: "0.2rem 0.5rem", background: "#f0f9ff", color: "#0369a1", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          SOURCE: {sec.source}
                        </span>
                        <span style={{ padding: "0.2rem 0.5rem", background: "#f8fafc", color: "#475569", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700, fontFamily: "monospace" }}>
                          Batch: {sec.batch_name} ({sec.count} assets)
                        </span>
                      </div>
                      <div style={{ fontSize: "0.85rem", color: "#475569", marginTop: "0.25rem" }}>
                        <strong>SEMANTIC DOMAIN:</strong> <code>{sec.semantic_domain}</code>
                      </div>
                      <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.15rem" }}>
                        {sec.description}
                      </div>
                    </div>

                    {/* Mars Semantic Firewall Callout */}
                    {sec.key === "mars" && (
                      <div
                        style={{
                          background: sec.firewall_status === "FIREWALL_PASSED" ? "#f0fdf4" : "#fef2f2",
                          border: `1px solid ${sec.firewall_status === "FIREWALL_PASSED" ? "#86efac" : "#fca5a5"}`,
                          borderRadius: "6px",
                          padding: "0.6rem 0.8rem",
                          maxWidth: "420px",
                        }}
                      >
                        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.25rem" }}>
                          <span style={{ fontSize: "0.8rem", fontWeight: 900, color: sec.firewall_status === "FIREWALL_PASSED" ? "#166534" : "#991b1b" }}>
                            🛡️ MARS SEMANTIC FIREWALL: {sec.firewall_status}
                          </span>
                        </div>
                        <div style={{ fontSize: "0.75rem", color: "#334155", lineHeight: 1.3 }}>
                          {sec.firewall_rules}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Assets Grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "0.75rem" }}>
                    {sec.assets.map((a: any) => {
                      const cardKey = `natal_${a.asset_id}`;
                      const isExpanded = !!expandedCardIds[cardKey];

                      return (
                        <div
                          key={a.asset_id}
                          style={{
                            background: "#f8fafc",
                            border: "1px solid #e2e8f0",
                            borderRadius: "6px",
                            padding: "0.75rem",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "space-between",
                          }}
                        >
                          <div>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem", flexWrap: "wrap", gap: "0.3rem" }}>
                              <code style={{ fontSize: "0.75rem", fontWeight: 700, color: "#0369a1" }}>
                                {a.asset_id}
                              </code>
                              <div style={{ display: "flex", gap: "0.3rem" }}>
                                {a.depth && (
                                  <span style={{ padding: "0.15rem 0.4rem", background: "#e2e8f0", color: "#334155", borderRadius: "3px", fontSize: "0.7rem", fontWeight: 700 }}>
                                    {a.depth}
                                  </span>
                                )}
                                {a.variant_key && (
                                  <span style={{ padding: "0.15rem 0.4rem", background: "#e0f2fe", color: "#0369a1", borderRadius: "3px", fontSize: "0.7rem", fontWeight: 700 }}>
                                    {a.variant_key}
                                  </span>
                                )}
                              </div>
                            </div>

                            <div style={{ fontSize: "0.85rem", color: "#1e293b", lineHeight: 1.45, marginBottom: "0.5rem" }}>
                              "{a.text}"
                            </div>
                          </div>

                          <div style={{ borderTop: "1px dashed #cbd5e1", paddingTop: "0.4rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#64748b" }}>
                            <span>Contract: <code>{a.interpretation_id}</code></span>
                            <button
                              onClick={() => toggleCard(cardKey)}
                              style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", fontWeight: 700, fontSize: "0.75rem" }}
                            >
                              {isExpanded ? "Hide JSON" : "Raw JSON"}
                            </button>
                          </div>

                          {isExpanded && <RuntimeJson data={a} label={`Raw Asset JSON (${a.asset_id})`} defaultOpen />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION: DISCOVERY PRESENCE (BATCH 7: 12 ZODIAC SIGNS) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "discovery") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #0284c7", paddingBottom: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#0369a1", margin: 0 }}>
                  DISCOVERY PRESENCE (12 ZODIAC SIGNS — VISIBLE PRESENCE HOOKS)
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#0284c7" }}>
                  Source: Candidate Ascendant sign (priority) or Sun sign (fallback) • Mode: visible presence
                </div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#0284c7" }}>
                {filteredDiscovery.length} Signs
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "1rem" }}>
              {filteredDiscovery.map((item) => {
                const cardKey = `discovery_${item.asset_id}`;
                const isExpanded = !!expandedCardIds[cardKey];

                return (
                  <div key={item.asset_id} style={{ background: "#ffffff", border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                        <span style={{ fontSize: "1.05rem", fontWeight: 900, color: "#0f172a" }}>
                          SIGN: {item.sign.toUpperCase()}
                        </span>
                        <span style={{ padding: "0.2rem 0.5rem", background: "#f0f9ff", color: "#0369a1", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          MODE: {item.mode}
                        </span>
                      </div>

                      <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "0.5rem" }}>
                        <strong>SOURCE:</strong> {item.source}
                      </div>

                      <div style={{ fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.45, background: "#f8fafc", padding: "0.6rem", borderRadius: "6px", border: "1px solid #e2e8f0", marginBottom: "0.5rem" }}>
                        "{item.text}"
                      </div>
                    </div>

                    <div style={{ borderTop: "1px dashed #cbd5e1", paddingTop: "0.4rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#64748b" }}>
                      <code>{item.asset_id}</code>
                      <button
                        onClick={() => toggleCard(cardKey)}
                        style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", fontWeight: 700, fontSize: "0.75rem" }}
                      >
                        {isExpanded ? "Hide JSON" : "Raw JSON"}
                      </button>
                    </div>

                    {isExpanded && <RuntimeJson data={item.raw} label={`Raw Discovery Asset (${item.asset_id})`} defaultOpen />}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION: CONNECTION INVITATIONS (BATCH 7: 11 ASSETS) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "connection") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #059669", paddingBottom: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#065f46", margin: 0 }}>
                  CONNECTION INVITATION LAYER (BATCH 7: 11 ASSETS ACROSS 6 CATEGORIES)
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#059669" }}>
                  Category Mapping: communication, harmony, attraction, stability, friction (growth), independent (notice)
                </div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#065f46" }}>
                {filteredConnection.length} Invitation Assets
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "1rem" }}>
              {filteredConnection.map((item) => {
                const cardKey = `conn_${item.asset_id}`;
                const isExpanded = !!expandedCardIds[cardKey];

                return (
                  <div key={item.asset_id} style={{ background: "#ffffff", border: "1px solid #a7f3d0", borderRadius: "8px", padding: "1rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                        <span style={{ fontSize: "1rem", fontWeight: 900, color: "#065f46", textTransform: "uppercase" }}>
                          CATEGORY: {item.category}
                        </span>
                        <span style={{ padding: "0.2rem 0.5rem", background: "#ecfdf5", color: "#047857", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          VARIANT: {item.variant_key || "default"}
                        </span>
                      </div>

                      <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "0.4rem" }}>
                        <strong>MAPPING:</strong> <code>{item.source_category_mapping}</code>
                      </div>

                      <div style={{ fontSize: "0.875rem", color: "#14532d", lineHeight: 1.45, background: "#f0fdf4", padding: "0.6rem", borderRadius: "6px", border: "1px solid #bbf7d0", marginBottom: "0.5rem" }}>
                        "{item.text}"
                      </div>
                    </div>

                    <div style={{ borderTop: "1px dashed #a7f3d0", paddingTop: "0.4rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#64748b" }}>
                      <code>{item.asset_id}</code>
                      <button
                        onClick={() => toggleCard(cardKey)}
                        style={{ background: "none", border: "none", color: "#059669", cursor: "pointer", fontWeight: 700, fontSize: "0.75rem" }}
                      >
                        {isExpanded ? "Hide JSON" : "Raw JSON"}
                      </button>
                    </div>

                    {isExpanded && <RuntimeJson data={item.raw} label={`Raw Connection Invitation (${item.asset_id})`} defaultOpen />}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION: CHAT / CONVERSATION STARTERS (BATCH 7: 43 ASSETS) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "chat") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #2563eb", paddingBottom: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#1e40af", margin: 0 }}>
                  CONVERSATION STARTERS (BATCH 7: 43 CONVERSATIONAL CONTINUATION ASSETS)
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#2563eb" }}>
                  Mapped by contract ID, source signal, and selection mode
                </div>
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e40af" }}>
                {filteredChat.length} Starters
              </span>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "1rem" }}>
              {filteredChat.map((item) => {
                const cardKey = `chat_${item.asset_id}`;
                const isExpanded = !!expandedCardIds[cardKey];

                return (
                  <div key={item.asset_id} style={{ background: "#ffffff", border: "1px solid #bfdbfe", borderRadius: "8px", padding: "1rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                        <span style={{ fontSize: "0.95rem", fontWeight: 900, color: "#1e40af" }}>
                          CATEGORY: {item.category.toUpperCase()}
                        </span>
                        <span style={{ padding: "0.2rem 0.5rem", background: "#eff6ff", color: "#1d4ed8", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                          VARIANT: {item.variant_key || "v1"}
                        </span>
                      </div>

                      <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "0.4rem" }}>
                        <strong>CONTRACT:</strong> <code>{item.interpretation_id}</code>
                      </div>

                      <div style={{ fontSize: "0.875rem", color: "#1e3a8a", lineHeight: 1.45, background: "#f0fdf4", padding: "0.6rem", borderRadius: "6px", border: "1px solid #bfdbfe", marginBottom: "0.5rem" }}>
                        "{item.text}"
                      </div>
                    </div>

                    <div style={{ borderTop: "1px dashed #bfdbfe", paddingTop: "0.4rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#64748b" }}>
                      <code>{item.asset_id}</code>
                      <button
                        onClick={() => toggleCard(cardKey)}
                        style={{ background: "none", border: "none", color: "#2563eb", cursor: "pointer", fontWeight: 700, fontSize: "0.75rem" }}
                      >
                        {isExpanded ? "Hide JSON" : "Raw JSON"}
                      </button>
                    </div>

                    {isExpanded && <RuntimeJson data={item.raw} label={`Raw Chat Starter (${item.asset_id})`} defaultOpen />}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* SECTION: DAILY ENERGY (TRANSIT PIPELINE & DO/DON'T TAGS) */}
        {/* ========================================================================= */}
        {(activeSection === "all" || activeSection === "daily_energy") && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "2px solid #d97706", paddingBottom: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
              <div>
                <h2 style={{ fontSize: "1.3rem", fontWeight: 900, color: "#b45309", margin: 0 }}>
                  DAILY ENERGY (TRANSIT ENGINE & 5-LAYER FROZEN CORPUS)
                </h2>
                <div style={{ fontSize: "0.8rem", color: "#d97706" }}>
                  Pipeline: REAL PLANETARY TRANSIT → CENTRALIZED TRIGGER SPECIFICATION → ARCHETYPE → NARRATIVE ASSET → DO/DON'T TAGS
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ padding: "0.25rem 0.5rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                  13 Archetypes
                </span>
                <span style={{ padding: "0.25rem 0.5rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                  {data.daily_energy.interpretation_assets?.length || 831} Narrative Assets
                </span>
                <span style={{ padding: "0.25rem 0.5rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                  39 DO / 39 DON'T
                </span>
              </div>
            </div>

            {/* Layer Switcher Tabs (when Daily Energy is selected) */}
            {activeSection === "daily_energy" && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "1.25rem", background: "#fffbeb", padding: "0.5rem", borderRadius: "8px", border: "1px solid #fde68a" }}>
                {[
                  { id: "all", label: "ALL 5 LAYERS" },
                  { id: "archetypes", label: "LAYER A: 13 Archetypes" },
                  { id: "assets", label: `LAYER B: ${data.daily_energy.interpretation_assets?.length || 831} Narrative Assets` },
                  { id: "do", label: "LAYER C: 39 DO Tags" },
                  { id: "dont", label: "LAYER D: 39 DON'T Tags" },
                  { id: "neutral", label: "LAYER E: Neutral Baseline" },
                ].map((l) => (
                  <button
                    key={l.id}
                    onClick={() => setDailyLayer(l.id as DailyEnergyLayer)}
                    style={{
                      padding: "0.35rem 0.75rem",
                      borderRadius: "6px",
                      border: dailyLayer === l.id ? "2px solid #b45309" : "1px solid #fcd34d",
                      background: dailyLayer === l.id ? "#f59e0b" : "#ffffff",
                      color: dailyLayer === l.id ? "#ffffff" : "#92400e",
                      fontWeight: dailyLayer === l.id ? 800 : 600,
                      fontSize: "0.8rem",
                      cursor: "pointer",
                    }}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            )}

            {/* ================================================================= */}
            {/* LAYER E: EXPLICIT NEUTRAL BASELINE CARD */}
            {/* ================================================================= */}
            {(dailyLayer === "all" || dailyLayer === "neutral") && (
              <div style={{ background: "#f8fafc", border: "2px dashed #94a3b8", borderRadius: "8px", padding: "1.25rem", marginBottom: "1.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{ fontSize: "1.1rem", fontWeight: 900, color: "#334155" }}>
                      ⚪ LAYER E: NEUTRAL BASELINE (CELESTIAL SILENCE)
                    </span>
                    <span style={{ padding: "0.2rem 0.5rem", background: "#dcfce7", color: "#166534", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 800, border: "1px solid #86efac" }}>
                      QA STATUS: {data.daily_energy.neutral_case.qa_status || "OK"}
                    </span>
                  </div>
                  <span style={{ padding: "0.25rem 0.6rem", background: "#e2e8f0", color: "#334155", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 800 }}>
                    DETECTION MODE: {data.daily_energy.neutral_case.detection_mode}
                  </span>
                </div>

                <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.5rem" }}>
                  <strong>Condition:</strong> {data.daily_energy.neutral_case.technical_note}
                </div>

                {/* Resolved Georgian Narrative */}
                <div style={{ background: "#ffffff", padding: "0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", marginBottom: "0.5rem", fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.45 }}>
                  <div style={{ fontSize: "0.7rem", color: "#64748b", fontWeight: 700, marginBottom: "0.2rem" }}>GEORGIAN FROZEN NARRATIVE (KA):</div>
                  "{data.daily_energy.neutral_case.interpretation}"
                </div>

                {/* Resolved English Narrative if available */}
                {data.daily_energy.neutral_case.interpretation_en && (
                  <div style={{ background: "#ffffff", padding: "0.75rem", borderRadius: "6px", border: "1px solid #cbd5e1", marginBottom: "0.75rem", fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.45 }}>
                    <div style={{ fontSize: "0.7rem", color: "#64748b", fontWeight: 700, marginBottom: "0.2rem" }}>ENGLISH FROZEN NARRATIVE (EN):</div>
                    "{data.daily_energy.neutral_case.interpretation_en}"
                  </div>
                )}

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "0.75rem" }}>
                  <div style={{ background: "#f0fdf4", padding: "0.6rem", borderRadius: "6px", border: "1px solid #bbf7d0" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 800, color: "#166534", marginBottom: "0.3rem" }}>✅ DO (რეკომენდებული)</div>
                    <div style={{ fontSize: "0.8rem", color: "#15803d" }}>
                      <strong>KA:</strong> {data.daily_energy.neutral_case.do_ka.join(" • ")}
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "#15803d", marginTop: "0.2rem" }}>
                      <strong>EN:</strong> {data.daily_energy.neutral_case.do_en.join(" • ")}
                    </div>
                  </div>

                  <div style={{ background: "#fef2f2", padding: "0.6rem", borderRadius: "6px", border: "1px solid #fecaca" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 800, color: "#991b1b", marginBottom: "0.3rem" }}>⛔ DON'T (თავიდან ასარიდებელი)</div>
                    <div style={{ fontSize: "0.8rem", color: "#b91c1c" }}>
                      <strong>KA:</strong> {data.daily_energy.neutral_case.dont_ka.join(" • ")}
                    </div>
                    <div style={{ fontSize: "0.8rem", color: "#b91c1c", marginTop: "0.2rem" }}>
                      <strong>EN:</strong> {data.daily_energy.neutral_case.dont_en.join(" • ")}
                    </div>
                  </div>
                </div>

                <div style={{ background: "#f1f5f9", padding: "0.5rem 0.75rem", borderRadius: "6px", fontSize: "0.75rem", color: "#475569", border: "1px solid #cbd5e1", marginBottom: "0.75rem" }}>
                  <strong>Transit Specification Notice:</strong> FROZEN CONTENT ASSET — runtime evidence not applicable (neutral baseline fallback when primary_transit is None)
                </div>

                <RuntimeJson data={data.daily_energy.neutral_case} label="Neutral Case Payload" />
              </div>
            )}

            {/* ================================================================= */}
            {/* LAYER A: 13 ARCHETYPES & CENTRALIZED SPECIFICATIONS */}
            {/* ================================================================= */}
            {(dailyLayer === "all" || dailyLayer === "archetypes") && (
              <div style={{ marginBottom: "2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#92400e", margin: 0 }}>
                    ⭐ LAYER A: 13 ARCHETYPES & CENTRALIZED ENGINE SPECS ({filteredDailyEnergy.length} / {data.daily_energy.archetypes.length})
                  </h3>
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
                    Centralized trigger rules, body-specific orbs, and resolved Georgian narratives
                  </span>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))", gap: "1rem" }}>
                  {filteredDailyEnergy.map((item) => {
                    const cardKey = `daily_${item.id}`;
                    const isExpanded = !!expandedCardIds[cardKey];

                    return (
                      <div key={item.id} style={{ background: "#ffffff", border: "1px solid #cbd5e1", borderRadius: "8px", padding: "1rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                        <div>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem", flexWrap: "wrap", gap: "0.4rem" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                              <span style={{ fontSize: "1rem", fontWeight: 900, color: "#0f172a" }}>
                                {item.name.toUpperCase()}
                              </span>
                              <code style={{ fontSize: "0.8rem", color: "#64748b" }}>({item.id})</code>
                              {item.qa_status === "OK" ? (
                                <span style={{ padding: "0.15rem 0.4rem", background: "#dcfce7", color: "#166534", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 800, border: "1px solid #86efac" }}>
                                  ✓ RESOLVED
                                </span>
                              ) : (
                                <span style={{ padding: "0.15rem 0.4rem", background: "#fee2e2", color: "#991b1b", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 800, border: "1px solid #fca5a5" }}>
                                  ⚠ MISSING FROZEN ASSET
                                </span>
                              )}
                            </div>
                            <span style={{ padding: "0.2rem 0.5rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.75rem", fontWeight: 700 }}>
                              {item.contract_id}
                            </span>
                          </div>

                          <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.5rem" }}>
                            {item.description}
                          </div>

                          {/* Narrative text */}
                          <div style={{ fontSize: "0.85rem", color: "#1e293b", lineHeight: 1.45, background: "#f8fafc", padding: "0.6rem", borderRadius: "6px", border: "1px solid #e2e8f0", marginBottom: "0.6rem" }}>
                            <div style={{ fontSize: "0.7rem", color: "#64748b", fontWeight: 700, marginBottom: "0.15rem" }}>FROZEN NARRATIVE (KA):</div>
                            "{item.narrative_ka}"
                          </div>

                          {item.narrative_en && (
                            <div style={{ fontSize: "0.8rem", color: "#334155", lineHeight: 1.4, background: "#f8fafc", padding: "0.5rem", borderRadius: "6px", border: "1px solid #e2e8f0", marginBottom: "0.6rem" }}>
                              <div style={{ fontSize: "0.7rem", color: "#64748b", fontWeight: 700, marginBottom: "0.15rem" }}>FROZEN NARRATIVE (EN):</div>
                              "{item.narrative_en}"
                            </div>
                          )}

                          {/* DO and DON'T tags */}
                          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginBottom: "0.6rem" }}>
                            <div style={{ background: "#f0fdf4", padding: "0.5rem", borderRadius: "4px", border: "1px solid #bbf7d0", fontSize: "0.75rem" }}>
                              <strong style={{ color: "#166534" }}>DO:</strong>
                              <div style={{ color: "#15803d", marginTop: "0.15rem" }}>
                                {item.do_tags_ka?.join(" • ") || item.do_tags?.join(" • ") || "N/A"}
                              </div>
                            </div>

                            <div style={{ background: "#fef2f2", padding: "0.5rem", borderRadius: "4px", border: "1px solid #fecaca", fontSize: "0.75rem" }}>
                              <strong style={{ color: "#991b1b" }}>DON'T:</strong>
                              <div style={{ color: "#b91c1c", marginTop: "0.15rem" }}>
                                {item.dont_tags_ka?.join(" • ") || item.dont_tags?.join(" • ") || "N/A"}
                              </div>
                            </div>
                          </div>

                          {/* Centralized Engine Trigger Specification */}
                          {item.centralized_spec && (
                            <div style={{ background: "#f8fafc", border: "1px solid #cbd5e1", padding: "0.6rem", borderRadius: "6px", fontSize: "0.75rem", color: "#334155" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem", flexWrap: "wrap", gap: "0.25rem" }}>
                                <strong style={{ color: "#0f172a", fontSize: "0.75rem" }}>⚡ ENGINE TRIGGER SPECIFICATION:</strong>
                                <span style={{ padding: "0.15rem 0.4rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 800 }}>
                                  {item.centralized_spec.evidence_notice}
                                </span>
                              </div>
                              <div style={{ fontSize: "0.7rem", color: "#64748b", marginBottom: "0.25rem" }}>
                                <strong>Triggers:</strong> {item.centralized_spec.trigger_pairs.join(" • ")}
                              </div>
                              <div style={{ fontSize: "0.7rem", color: "#64748b", marginBottom: "0.25rem" }}>
                                <strong>Centralized Body Orbs:</strong>{" "}
                                {item.centralized_spec.key_bodies.length > 0
                                  ? item.centralized_spec.key_bodies
                                      .map((b) => `${b.body.toUpperCase()} (Max: ${b.max_orb}°${b.transit_weight ? `, Weight: ${b.transit_weight}` : ""})`)
                                      .join(" • ")
                                  : "N/A (Baseline Fallback)"}
                              </div>
                              {item.centralized_spec.aspect_types.length > 0 && (
                                <div style={{ fontSize: "0.7rem", color: "#64748b" }}>
                                  <strong>Aspects:</strong> {item.centralized_spec.aspect_types.join(" • ")}
                                  {item.centralized_spec.applying_multiplier && (
                                    <span> • Applying: ×{item.centralized_spec.applying_multiplier}</span>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>

                        <div style={{ borderTop: "1px dashed #cbd5e1", paddingTop: "0.4rem", marginTop: "0.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.75rem", color: "#64748b" }}>
                          <span>Mode: <code>{item.centralized_spec?.detection_mode || item.technical_evidence?.detection_mode || "real_transit"}</code></span>
                          <button
                            onClick={() => toggleCard(cardKey)}
                            style={{ background: "none", border: "none", color: "#d97706", cursor: "pointer", fontWeight: 700, fontSize: "0.75rem" }}
                          >
                            {isExpanded ? "Hide JSON" : "Raw JSON"}
                          </button>
                        </div>

                        {isExpanded && <RuntimeJson data={item} label={`Raw Daily Energy JSON (${item.id})`} defaultOpen />}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ================================================================= */}
            {/* LAYER B: ALL FROZEN INTERPRETATION ASSETS (831 ASSETS) */}
            {/* ================================================================= */}
            {(dailyLayer === "all" || dailyLayer === "assets") && (
              <div style={{ marginBottom: "2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <h3 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#92400e", margin: 0 }}>
                      📖 LAYER B: FROZEN INTERPRETATION ASSETS ({filteredDailyAssets.length} / {data.daily_energy.interpretation_assets?.length || 831})
                    </h3>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      All frozen narrative assets across 12 archetypes and neutral baseline loaded from content store
                    </div>
                  </div>
                  <span style={{ fontSize: "0.75rem", color: "#92400e", fontWeight: 700 }}>
                    Filter by Search or Archetype Dropdown
                  </span>
                </div>

                <div style={{ maxHeight: "600px", overflowY: "auto", border: "1px solid #cbd5e1", borderRadius: "8px", background: "#ffffff", padding: "0.5rem" }}>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "0.75rem" }}>
                    {filteredDailyAssets.map((asset) => {
                      const cardKey = `daily_asset_${asset.asset_id}`;
                      const isExpanded = !!expandedCardIds[cardKey];

                      return (
                        <div key={asset.asset_id} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "6px", padding: "0.75rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                          <div>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem", flexWrap: "wrap", gap: "0.25rem" }}>
                              <span style={{ padding: "0.15rem 0.4rem", background: "#fef3c7", color: "#92400e", borderRadius: "4px", fontSize: "0.7rem", fontWeight: 800 }}>
                                {asset.archetype_name}
                              </span>
                              <div style={{ display: "flex", gap: "0.3rem" }}>
                                <span style={{ padding: "0.15rem 0.35rem", background: asset.locale === "ka" ? "#dbeafe" : "#dcfce7", color: asset.locale === "ka" ? "#1e40af" : "#166534", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 800 }}>
                                  {asset.locale.toUpperCase()}
                                </span>
                                <span style={{ padding: "0.15rem 0.35rem", background: "#f1f5f9", color: "#475569", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 700 }}>
                                  {asset.variant_key}
                                </span>
                              </div>
                            </div>

                            <div style={{ fontSize: "0.7rem", color: "#64748b", marginBottom: "0.3rem" }}>
                              <code>{asset.asset_id}</code>
                            </div>

                            <div style={{ fontSize: "0.8rem", color: "#1e293b", lineHeight: 1.4, background: "#ffffff", padding: "0.5rem", borderRadius: "4px", border: "1px solid #cbd5e1", marginBottom: "0.4rem" }}>
                              "{asset.text}"
                            </div>
                          </div>

                          <div style={{ borderTop: "1px dashed #e2e8f0", paddingTop: "0.3rem", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.7rem", color: "#64748b" }}>
                            <span>Tone: <code>{asset.tone}</code></span>
                            <button
                              onClick={() => toggleCard(cardKey)}
                              style={{ background: "none", border: "none", color: "#d97706", cursor: "pointer", fontWeight: 700, fontSize: "0.7rem" }}
                            >
                              {isExpanded ? "Hide JSON" : "Raw JSON"}
                            </button>
                          </div>

                          {isExpanded && <RuntimeJson data={asset} label={`Raw Asset (${asset.asset_id})`} defaultOpen />}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* ================================================================= */}
            {/* LAYER C: 39 CURATED DO TAGS */}
            {/* ================================================================= */}
            {(dailyLayer === "all" || dailyLayer === "do") && (
              <div style={{ marginBottom: "2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#166534", margin: 0 }}>
                    ✅ LAYER C: CURATED DO TAGS (39 STRINGS: 13 ARCHETYPES × 3)
                  </h3>
                  <span style={{ fontSize: "0.75rem", color: "#166534", fontWeight: 700 }}>
                    {filteredDailyDoTags.length} / 39 Tags Visible
                  </span>
                </div>

                <div style={{ overflowX: "auto", border: "1px solid #bbf7d0", borderRadius: "8px", background: "#ffffff" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                    <thead>
                      <tr style={{ background: "#f0fdf4", borderBottom: "2px solid #86efac", textAlign: "left" }}>
                        <th style={{ padding: "0.5rem 0.75rem", width: "40px" }}>#</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Archetype</th>
                        <th style={{ padding: "0.5rem 0.75rem", width: "60px" }}>Tag #</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Georgian Tag (KA)</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>English Tag (EN)</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Tag ID</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDailyDoTags.map((tag, idx) => (
                        <tr key={tag.tag_id} style={{ borderBottom: "1px solid #f0fdf4", background: idx % 2 === 0 ? "#ffffff" : "#fbfdfb" }}>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#64748b", fontWeight: 700 }}>{idx + 1}</td>
                          <td style={{ padding: "0.5rem 0.75rem", fontWeight: 700, color: "#166534" }}>{tag.archetype_name}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#64748b" }}>#{tag.index}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#0f172a", fontWeight: 600 }}>{tag.text_ka}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#475569" }}>{tag.text_en}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#94a3b8" }}><code>{tag.tag_id}</code></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* ================================================================= */}
            {/* LAYER D: 39 CURATED DON'T TAGS */}
            {/* ================================================================= */}
            {(dailyLayer === "all" || dailyLayer === "dont") && (
              <div style={{ marginBottom: "2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#991b1b", margin: 0 }}>
                    ⛔ LAYER D: CURATED DON'T TAGS (39 STRINGS: 13 ARCHETYPES × 3)
                  </h3>
                  <span style={{ fontSize: "0.75rem", color: "#991b1b", fontWeight: 700 }}>
                    {filteredDailyDontTags.length} / 39 Tags Visible
                  </span>
                </div>

                <div style={{ overflowX: "auto", border: "1px solid #fecaca", borderRadius: "8px", background: "#ffffff" }}>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                    <thead>
                      <tr style={{ background: "#fef2f2", borderBottom: "2px solid #fca5a5", textAlign: "left" }}>
                        <th style={{ padding: "0.5rem 0.75rem", width: "40px" }}>#</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Archetype</th>
                        <th style={{ padding: "0.5rem 0.75rem", width: "60px" }}>Tag #</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Georgian Tag (KA)</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>English Tag (EN)</th>
                        <th style={{ padding: "0.5rem 0.75rem" }}>Tag ID</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDailyDontTags.map((tag, idx) => (
                        <tr key={tag.tag_id} style={{ borderBottom: "1px solid #fef2f2", background: idx % 2 === 0 ? "#ffffff" : "#fffcfc" }}>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#64748b", fontWeight: 700 }}>{idx + 1}</td>
                          <td style={{ padding: "0.5rem 0.75rem", fontWeight: 700, color: "#991b1b" }}>{tag.archetype_name}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#64748b" }}>#{tag.index}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#0f172a", fontWeight: 600 }}>{tag.text_ka}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#475569" }}>{tag.text_en}</td>
                          <td style={{ padding: "0.5rem 0.75rem", color: "#94a3b8" }}><code>{tag.tag_id}</code></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
