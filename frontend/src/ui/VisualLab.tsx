import React, { useState, useMemo } from "react";
import {
  Button,
  Input,
  Card,
  Badge,
  Avatar,
  Skeleton,
  BirthDateInput,
  CitySelector,
  JesterLogo,
} from "../shared/ui";
import {
  LoadingState,
  ErrorState,
  EmptyState,
  PrivacySafeNotFoundState,
} from "../shared/StatusState";
import { TOKEN_SECTIONS, type DesignToken } from "./tokensCatalogData";

interface PalettePreset {
  id: string;
  name: string;
  emoji: string;
  orange500: string;
  orange600: string;
  orange700: string;
}

const PALETTE_PRESETS: PalettePreset[] = [
  {
    id: "canonical",
    name: "კანონიკური სტაფილოსფერი (Canonical Orange)",
    emoji: "🥕",
    orange500: "#FF7A2F",
    orange600: "#E9681F",
    orange700: "#C95618",
  },
  {
    id: "purple",
    name: "სამეფო იისფერი (Royal Purple)",
    emoji: "💜",
    orange500: "#8B5CF6",
    orange600: "#7C3AED",
    orange700: "#6D28D9",
  },
  {
    id: "emerald",
    name: "ზურმუხტისფერი მწვანე (Emerald Green)",
    emoji: "🌿",
    orange500: "#10B981",
    orange600: "#059669",
    orange700: "#047857",
  },
  {
    id: "blue",
    name: "ასტრალური ლურჯი (Astral Blue)",
    emoji: "🔷",
    orange500: "#3B82F6",
    orange600: "#2563EB",
    orange700: "#1D4ED8",
  },
  {
    id: "crimson",
    name: "ალისფერი ვარდისფერი (Crimson Rose)",
    emoji: "🍷",
    orange500: "#E11D48",
    orange600: "#BE123C",
    orange700: "#9F1239",
  },
];

export const VisualLab: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"catalog" | "components" | "studio">("catalog");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSection, setSelectedSection] = useState<string>("all");
  const [copiedToken, setCopiedToken] = useState<string | null>(null);

  // Studio Theme Switcher State
  const [activePreset, setActivePreset] = useState<PalettePreset>(PALETTE_PRESETS[0]);
  const [customColor, setCustomColor] = useState("#FF7A2F");

  // Interactive component states
  const [demoInput, setDemoInput] = useState("JESTER Relationship Intelligence");
  const [demoBirthDate, setDemoBirthDate] = useState("1996-07-20");
  const [demoCityId, setDemoCityId] = useState<string | null>("tbilisi-ge");
  const [demoCity, setDemoCity] = useState("თბილისი, საქართველო");
  const [btnLoading, setBtnLoading] = useState(false);

  // Copy to clipboard handler
  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedToken(text);
      setTimeout(() => setCopiedToken(null), 2000);
    });
  };

  // Filter tokens based on search and section
  const filteredSections = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    return TOKEN_SECTIONS.map((sec) => {
      if (selectedSection !== "all" && sec.title !== selectedSection) {
        return { ...sec, tokens: [] };
      }
      if (!q) return sec;
      const filtered = sec.tokens.filter(
        (t) =>
          t.name.toLowerCase().includes(q) ||
          t.value.toLowerCase().includes(q) ||
          sec.title.toLowerCase().includes(q)
      );
      return { ...sec, tokens: filtered };
    }).filter((sec) => sec.tokens.length > 0);
  }, [searchQuery, selectedSection]);

  const totalFilteredTokens = useMemo(
    () => filteredSections.reduce((acc, s) => acc + s.tokens.length, 0),
    [filteredSections]
  );

  // Scoped CSS variable overrides for theme studio
  const studioOverrideStyle = useMemo<React.CSSProperties>(() => {
    return {
      "--jester-primitive-orange-500": activePreset.orange500,
      "--jester-primitive-orange-600": activePreset.orange600,
      "--jester-primitive-orange-700": activePreset.orange700,
      "--jester-color-brand-primary": activePreset.orange500,
      "--jester-color-brand-primary-hover": activePreset.orange600,
      "--jester-color-brand-primary-active": activePreset.orange700,
      "--jester-color-brand-border": activePreset.orange500,
      "--home-brand-orange": activePreset.orange500,
    } as React.CSSProperties;
  }, [activePreset]);

  return (
    <div
      id="visual-lab-root"
      style={{
        minHeight: "100vh",
        backgroundColor: "var(--jester-color-canvas, #FAF7F2)",
        color: "var(--jester-color-text-primary, #222630)",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        padding: "clamp(1rem, 3vw, 2.5rem)",
        boxSizing: "border-box",
        ...studioOverrideStyle,
      }}
    >
      <div style={{ maxWidth: "1140px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "2rem" }}>
        
        {/* HEADER BAR */}
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: "1.25rem",
            paddingBottom: "1.5rem",
            borderBottom: "1px solid var(--jester-color-border-subtle, #E6E0D7)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <JesterLogo height={36} variant="horizontal" />
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                <h1 style={{ margin: 0, fontSize: "clamp(1.25rem, 2.5vw, 1.75rem)", fontWeight: 850, letterSpacing: "-0.02em" }}>
                  Design System Living Guide
                </h1>
                <Badge variant="brand">Living Guide</Badge>
              </div>
              <p style={{ margin: "0.3rem 0 0 0", color: "var(--jester-color-text-secondary, #6A716F)", fontSize: "0.875rem" }}>
                ცოცხალი დიზაინ სახელმძღვანელო • Single Source of Truth: <code>colors.css</code> (508 ტოკენი)
              </p>
            </div>
          </div>

          {/* Preset Pill & Route Status */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.4rem" }}>
            <span
              style={{
                fontSize: "0.75rem",
                padding: "0.25rem 0.65rem",
                borderRadius: "20px",
                backgroundColor: "var(--jester-color-surface, #FFFFFF)",
                border: "1px solid var(--jester-color-border-subtle, #E6E0D7)",
                color: "var(--jester-color-text-secondary, #6A716F)",
                fontWeight: 600,
              }}
            >
              მისამართი: <strong style={{ color: "var(--jester-color-text-primary)" }}>/visual-lab</strong>
            </span>
            {activePreset.id !== "canonical" && (
              <span
                style={{
                  fontSize: "0.75rem",
                  padding: "0.2rem 0.5rem",
                  borderRadius: "6px",
                  backgroundColor: "var(--jester-color-brand-primary)",
                  color: "#FFFFFF",
                  fontWeight: 700,
                }}
              >
                აქტიური Preview: {activePreset.emoji} {activePreset.name}
              </span>
            )}
          </div>
        </header>

        {/* PRIMARY NAVIGATION TABS */}
        <nav
          style={{
            display: "flex",
            gap: "0.5rem",
            borderBottom: "1px solid var(--jester-color-border-subtle, #E6E0D7)",
            paddingBottom: "0.5rem",
            flexWrap: "wrap",
          }}
          aria-label="დიზაინ სახელმძღვანელოს სექციები"
        >
          <button
            onClick={() => setActiveTab("catalog")}
            style={{
              padding: "0.65rem 1.25rem",
              borderRadius: "10px",
              border: "none",
              backgroundColor: activeTab === "catalog" ? "var(--jester-color-brand-primary)" : "transparent",
              color: activeTab === "catalog" ? "var(--jester-color-brand-text, #222630)" : "var(--jester-color-text-primary)",
              fontWeight: 750,
              fontSize: "0.95rem",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            🎨 ფერების კატალოგი (508)
          </button>

          <button
            onClick={() => setActiveTab("components")}
            style={{
              padding: "0.65rem 1.25rem",
              borderRadius: "10px",
              border: "none",
              backgroundColor: activeTab === "components" ? "var(--jester-color-brand-primary)" : "transparent",
              color: activeTab === "components" ? "var(--jester-color-brand-text, #222630)" : "var(--jester-color-text-primary)",
              fontWeight: 750,
              fontSize: "0.95rem",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            🧩 Shared/UI კომპონენტები
          </button>

          <button
            onClick={() => setActiveTab("studio")}
            style={{
              padding: "0.65rem 1.25rem",
              borderRadius: "10px",
              border: "none",
              backgroundColor: activeTab === "studio" ? "var(--jester-color-brand-primary)" : "transparent",
              color: activeTab === "studio" ? "var(--jester-color-brand-text, #222630)" : "var(--jester-color-text-primary)",
              fontWeight: 750,
              fontSize: "0.95rem",
              cursor: "pointer",
              transition: "all 0.15s ease",
            }}
          >
            🎛️ პალიტრის Preview & Studio
          </button>
        </nav>

        {/* =========================================================================
            TAB 1: COLOR CATALOG
            ========================================================================= */}
        {activeTab === "catalog" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {/* Search & Category Filter Controls */}
            <Card padded style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                <div style={{ flex: "1 1 280px" }}>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="ძებნა ტოკენის სახელით ან მნიშვნელობით (მაგ. brand, surface, #FF7A2F, chat)..."
                    style={{
                      width: "100%",
                      padding: "0.75rem 1rem",
                      borderRadius: "10px",
                      border: "1.5px solid var(--jester-color-border-subtle, #E6E0D7)",
                      backgroundColor: "var(--jester-color-surface, #FFFFFF)",
                      color: "var(--jester-color-text-primary, #222630)",
                      fontSize: "0.95rem",
                      outline: "none",
                      boxSizing: "border-box",
                    }}
                  />
                </div>
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    style={{
                      padding: "0.65rem 1rem",
                      borderRadius: "8px",
                      border: "1px solid var(--jester-color-border-subtle)",
                      background: "transparent",
                      cursor: "pointer",
                      fontSize: "0.85rem",
                    }}
                  >
                    გასუფთავება ✕
                  </button>
                )}
                <div style={{ fontSize: "0.85rem", color: "var(--jester-color-text-secondary)", fontWeight: 600 }}>
                  ნაპოვნია: {totalFilteredTokens} ტოკენი
                </div>
              </div>

              {/* Section Filter Pills */}
              <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                <button
                  onClick={() => setSelectedSection("all")}
                  style={{
                    padding: "0.35rem 0.75rem",
                    borderRadius: "20px",
                    border: selectedSection === "all" ? "1.5px solid var(--jester-color-brand-primary)" : "1px solid var(--jester-color-border-subtle)",
                    backgroundColor: selectedSection === "all" ? "var(--jester-color-insight-peach-bg)" : "var(--jester-color-surface)",
                    color: "var(--jester-color-text-primary)",
                    fontSize: "0.8rem",
                    fontWeight: selectedSection === "all" ? 700 : 500,
                    cursor: "pointer",
                  }}
                >
                  ყველა სექცია
                </button>
                {TOKEN_SECTIONS.map((sec) => {
                  const isSel = selectedSection === sec.title;
                  return (
                    <button
                      key={sec.title}
                      onClick={() => setSelectedSection(sec.title)}
                      style={{
                        padding: "0.35rem 0.75rem",
                        borderRadius: "20px",
                        border: isSel ? "1.5px solid var(--jester-color-brand-primary)" : "1px solid var(--jester-color-border-subtle)",
                        backgroundColor: isSel ? "var(--jester-color-insight-peach-bg)" : "var(--jester-color-surface)",
                        color: "var(--jester-color-text-primary)",
                        fontSize: "0.8rem",
                        fontWeight: isSel ? 700 : 500,
                        cursor: "pointer",
                      }}
                    >
                      {sec.title.split("(")[0].trim()} ({sec.tokens.length})
                    </button>
                  );
                })}
              </div>
            </Card>

            {/* Token Section Lists */}
            {filteredSections.map((sec) => (
              <div key={sec.title} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: "0.5rem" }}>
                  <h2 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 800 }}>
                    {sec.title}
                  </h2>
                  <span style={{ fontSize: "0.8rem", color: "var(--jester-color-text-secondary)" }}>
                    ({sec.tokens.length} ტოკენი)
                  </span>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(min(260px, 100%), 1fr))",
                    gap: "0.85rem",
                  }}
                >
                  {sec.tokens.map((token: DesignToken) => {
                    const isCopied = copiedToken === token.name;
                    return (
                      <div
                        key={token.name}
                        onClick={() => handleCopy(`var(${token.name})`)}
                        style={{
                          backgroundColor: "var(--jester-color-surface, #FFFFFF)",
                          borderRadius: "12px",
                          border: "1px solid var(--jester-color-border-subtle, #E6E0D7)",
                          padding: "0.85rem",
                          display: "flex",
                          alignItems: "center",
                          gap: "0.85rem",
                          cursor: "pointer",
                          transition: "all 0.15s ease",
                          position: "relative",
                        }}
                      >
                        {/* Live Swatch Box */}
                        <div
                          style={{
                            width: "42px",
                            height: "42px",
                            borderRadius: "8px",
                            backgroundColor: `var(${token.name})`,
                            border: "1px solid rgba(0,0,0,0.1)",
                            flexShrink: 0,
                            boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.2)",
                          }}
                        />

                        {/* Token Details */}
                        <div style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
                          <div
                            style={{
                              fontSize: "0.825rem",
                              fontWeight: 700,
                              color: "var(--jester-color-text-primary)",
                              whiteSpace: "nowrap",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              fontFamily: "monospace",
                            }}
                            title={token.name}
                          >
                            {token.name}
                          </div>
                          <div
                            style={{
                              fontSize: "0.75rem",
                              color: "var(--jester-color-text-secondary)",
                              whiteSpace: "nowrap",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              marginTop: "0.15rem",
                            }}
                            title={token.value}
                          >
                            {token.value}
                          </div>
                        </div>

                        {/* Copy Badge */}
                        <span
                          style={{
                            fontSize: "0.7rem",
                            padding: "0.2rem 0.45rem",
                            borderRadius: "6px",
                            backgroundColor: isCopied ? "var(--jester-color-brand-primary)" : "var(--jester-color-surface-subtle, #F3EEE6)",
                            color: isCopied ? "#FFFFFF" : "var(--jester-color-text-secondary)",
                            fontWeight: 700,
                            flexShrink: 0,
                          }}
                        >
                          {isCopied ? "დაკოპირდა!" : "Copy"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* =========================================================================
            TAB 2: SHARED / UI COMPONENT GALLERY
            ========================================================================= */}
        {activeTab === "components" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            
            {/* 1. BUTTON SUITE */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                1. Button კომპონენტების ნაკრები
              </h2>
              <p style={{ margin: "0 0 1.25rem 0", color: "var(--jester-color-text-secondary)", fontSize: "0.875rem" }}>
                WCAG AA კონტრასტით სერტიფიცირებული ბრენდული, მეორადი, საშიშროებისა და მონახაზის ღილაკები.
              </p>
              <div style={{ display: "flex", gap: "0.85rem", flexWrap: "wrap", alignItems: "center" }}>
                <Button variant="brand" size="md">
                  🚀 Brand Action (#FF7A2F)
                </Button>
                <Button variant="secondary" size="md">
                  Secondary Action
                </Button>
                <Button variant="danger" size="md">
                  ⚠️ Danger Action
                </Button>
                <Button variant="outline" size="md">
                  Outline Variant
                </Button>
                <Button
                  variant="brand"
                  size="md"
                  isLoading={btnLoading}
                  onClick={() => {
                    setBtnLoading(true);
                    setTimeout(() => setBtnLoading(false), 2000);
                  }}
                >
                  {btnLoading ? "იტვირთება..." : "სიმულაცია Loading"}
                </Button>
                <Button variant="brand" size="md" disabled>
                  Disabled State
                </Button>
                <Button variant="brand" size="sm">
                  Small (sm)
                </Button>
                <Button variant="brand" size="lg">
                  Large (lg)
                </Button>
              </div>
            </Card>

            {/* 2. CARD ELEVATIONS */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                2. Card ზედაპირები და სიღრმის იერარქია
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(220px, 100%), 1fr))", gap: "1rem", marginTop: "1rem" }}>
                <Card padded variant="default">
                  <strong>Surface Default</strong>
                  <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.85rem", color: "var(--jester-color-text-secondary)" }}>
                    თეთრი საბაზისო ბარათი (#FFFFFF)
                  </p>
                </Card>
                <Card padded variant="elevated">
                  <strong>Elevated Card</strong>
                  <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.85rem", color: "var(--jester-color-text-secondary)" }}>
                    ჩრდილით გამოკვეთილი ზედაპირი
                  </p>
                </Card>
                <Card padded variant="accent">
                  <strong style={{ color: "var(--jester-brand-orange-800)" }}>Peach Insight Card</strong>
                  <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.85rem", color: "var(--jester-color-text-secondary)" }}>
                    ატმისფერი ინტერპრეტაციის ბარათი
                  </p>
                </Card>
                <Card padded variant="calm">
                  <strong style={{ color: "var(--jester-primitive-sage-ink)" }}>Sage Support Card</strong>
                  <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.85rem", color: "var(--jester-color-text-secondary)" }}>
                    სალბისფერი ასტროლოგიური მხარდაჭერა
                  </p>
                </Card>
              </div>
            </Card>

            {/* 3. BADGES & ASTROLOGICAL CATEGORY CHIPS */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                3. Badge & Astrological Chips
              </h2>
              <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginTop: "1rem" }}>
                <Badge variant="brand">♈ მზე ვერძში (Brand Orange)</Badge>
                <Badge variant="score">🍑 84% Synastry Score</Badge>
                <Badge variant="astrology">✦ ასტროლოგიური ასპექტი</Badge>
                <Badge variant="success">✓ Real / დადასტურებული</Badge>
                <Badge variant="warning">⚡ კარდინალური მოდალობა</Badge>
                <Badge variant="danger">⚔️ მარსი თევზებში (დაძაბულობა)</Badge>
                <Badge variant="default">◎ ნეიტრალური ინდიკატორი</Badge>
                <Badge variant="outline">◇ Outline Variant</Badge>
              </div>
            </Card>

            {/* 4. INPUTS & FORM CONTROLS */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                4. Input ველები და ვალიდაცია
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(280px, 100%), 1fr))", gap: "1.25rem", marginTop: "1rem" }}>
                <Input
                  label="მომხმარებლის სახელი / Display Name"
                  value={demoInput}
                  onChange={(e) => setDemoInput(e.target.value)}
                  placeholder="შეიყვანეთ სახელი..."
                />
                <Input
                  label="შეცდომის მდგომარეობა (Error State)"
                  value="არავალიდური მონაცემი"
                  error="მითითებული ფორმატი არასწორია"
                  readOnly
                />
              </div>
            </Card>

            {/* 5. 3-SEGMENT BIRTH DATE INPUT */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                5. BirthDateInput (დღე / თვე / წელი + 18+ ვალიდაცია)
              </h2>
              <p style={{ margin: "0 0 1rem 0", color: "var(--jester-color-text-secondary)", fontSize: "0.875rem" }}>
                ქართული ლოკალიზაციით, თაობების ფილტრითა და ზუსტი კალენდარული ასაკის დაცვით.
              </p>
              <div style={{ maxWidth: "480px" }}>
                <BirthDateInput
                  label="დაბადების თარიღი"
                  required
                  value={demoBirthDate}
                  onChange={(val) => setDemoBirthDate(val)}
                  helperText="შეამოწმეთ დღის, თვის და წლის შერჩევა"
                />
                <div style={{ marginTop: "0.75rem", fontSize: "0.8rem", color: "var(--jester-color-text-secondary)" }}>
                  მიმდინარე მნიშვნელობა: <code>{demoBirthDate || "(ცარიელია)"}</code>
                </div>
              </div>
            </Card>

            {/* 6. CANONICAL CITY SELECTOR */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                6. CitySelector (კანონიკური ქალაქის შერჩევა)
              </h2>
              <div style={{ maxWidth: "480px" }}>
                <CitySelector
                  value={demoCityId}
                  initialDisplayLabel={demoCity}
                  onChange={(item) => {
                    setDemoCityId(item.city_id);
                    setDemoCity(`${item.display_name}, ${item.country_name}`);
                  }}
                  onClear={() => {
                    setDemoCityId(null);
                    setDemoCity("");
                  }}
                  label="დაბადების ქალაქი"
                  placeholder="მაგ. თბილისი, ბათუმი, London..."
                />
              </div>
            </Card>

            {/* 7. AVATARS & SKELETON LOADING */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                7. Avatar & Skeleton Shimmer
              </h2>
              <div style={{ display: "flex", gap: "1.5rem", alignItems: "center", flexWrap: "wrap", marginTop: "1rem" }}>
                <Avatar size="sm" name="Ana B" />
                <Avatar size="md" name="Davit B" />
                <Avatar size="lg" name="Nino K" />
                <Avatar size="xl" name="Jester Master" />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", marginTop: "1.5rem" }}>
                <Skeleton width="40%" height="24px" borderRadius="6px" />
                <Skeleton width="100%" height="16px" borderRadius="4px" />
                <Skeleton width="85%" height="16px" borderRadius="4px" />
              </div>
            </Card>

            {/* 8. STATUS STATE SUITE */}
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.2rem", fontWeight: 800 }}>
                8. StatusState უკუკავშირის კომპონენტები
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(280px, 100%), 1fr))", gap: "1rem", marginTop: "1rem" }}>
                <LoadingState message="იტვირთება ასტროლოგიური მონაცემები..." />
                <ErrorState error="დაფიქსირდა სერვერთან კავშირის შეცდომა." onRetry={() => alert("Retried!")} />
                <EmptyState title="შეტყობინებები არ არის" description="აქ გამოჩნდება თქვენი ახალი შეტყობინებები." />
                <PrivacySafeNotFoundState message="მოთხოვნილი პროფილი დაცულია ან მიუწვდომელია." />
              </div>
            </Card>

          </div>
        )}

        {/* =========================================================================
            TAB 3: ISOLATED PALETTE PREVIEW & THEME STUDIO
            ========================================================================= */}
        {activeTab === "studio" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            <Card padded>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.25rem", fontWeight: 800 }}>
                🎛️ ბრენდის პალიტრის ცოცხალი Preview (Theme Studio)
              </h2>
              <p style={{ margin: "0 0 1.25rem 0", color: "var(--jester-color-text-secondary)", fontSize: "0.9rem" }}>
                შეცვალეთ ბრენდის ძირითადი ფერი და დააკვირდით, როგორ გავრცელდება ცვლილება მყისიერად ბრენდულ ღილაკებსა და ელემენტებზე,
                ხოლო <strong>სტატუსები (Success/Danger), Stars (ოქროსფერი) და Chat ბაბლები დარჩება 100%-ით დამოუკიდებელი და უცვლელი</strong>.
              </p>

              {/* Preset Selector Buttons */}
              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
                {PALETTE_PRESETS.map((preset) => {
                  const isSel = activePreset.id === preset.id;
                  return (
                    <button
                      key={preset.id}
                      onClick={() => {
                        setActivePreset(preset);
                        setCustomColor(preset.orange500);
                      }}
                      style={{
                        padding: "0.75rem 1rem",
                        borderRadius: "12px",
                        border: isSel ? `2px solid ${preset.orange500}` : "1px solid var(--jester-color-border-subtle)",
                        backgroundColor: isSel ? "var(--jester-color-surface)" : "var(--jester-color-surface-subtle)",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.6rem",
                        cursor: "pointer",
                        fontWeight: 700,
                        fontSize: "0.9rem",
                        boxShadow: isSel ? `0 4px 12px ${preset.orange500}33` : "none",
                        transition: "all 0.15s ease",
                      }}
                    >
                      <span
                        style={{
                          width: "20px",
                          height: "20px",
                          borderRadius: "50%",
                          backgroundColor: preset.orange500,
                          border: "1px solid rgba(0,0,0,0.15)",
                        }}
                      />
                      <span>{preset.emoji} {preset.name.split("(")[0]}</span>
                    </button>
                  );
                })}
              </div>

              {/* Custom Color Override */}
              <div style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "1rem", borderRadius: "10px", backgroundColor: "var(--jester-color-surface-subtle)" }}>
                <label style={{ fontSize: "0.85rem", fontWeight: 700 }}>საკუთარი ფერის არჩევა (Custom Hex):</label>
                <input
                  type="color"
                  value={customColor}
                  onChange={(e) => {
                    const c = e.target.value;
                    setCustomColor(c);
                    setActivePreset({
                      id: "custom",
                      name: `Custom (${c})`,
                      emoji: "🎨",
                      orange500: c,
                      orange600: c,
                      orange700: c,
                    });
                  }}
                  style={{ width: "40px", height: "36px", border: "none", cursor: "pointer", borderRadius: "6px" }}
                />
                <code style={{ fontSize: "0.9rem", fontWeight: 700 }}>{customColor}</code>

                <button
                  onClick={() => {
                    setActivePreset(PALETTE_PRESETS[0]);
                    setCustomColor(PALETTE_PRESETS[0].orange500);
                  }}
                  style={{
                    marginLeft: "auto",
                    padding: "0.5rem 0.85rem",
                    borderRadius: "8px",
                    border: "1px solid var(--jester-color-border-subtle)",
                    backgroundColor: "var(--jester-color-surface)",
                    fontSize: "0.8rem",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  კანონიკურზე დაბრუნება (Reset)
                </button>
              </div>
            </Card>

            {/* LIVE PREVIEW COMPARISON: PROPAGATED VS INDEPENDENT */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(340px, 100%), 1fr))", gap: "1.5rem" }}>
              
              {/* Box A: What changes dynamically */}
              <Card padded style={{ borderTop: `4px solid ${activePreset.orange500}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <span style={{ fontSize: "1.2rem" }}>🎯</span>
                  <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800 }}>
                    ბრენდის ტოკენები (ავტომატურად იცვლება)
                  </h3>
                </div>
                <p style={{ margin: "0 0 1rem 0", color: "var(--jester-color-text-secondary)", fontSize: "0.85rem" }}>
                  ერთი წყაროდან გავრცელებული ახალი ფერი:
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                  <Button variant="brand" size="md">
                    Brand Action Button
                  </Button>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    <Badge variant="brand">Brand Badge</Badge>
                    <span style={{ fontSize: "0.85rem", color: "var(--jester-color-brand-primary)", fontWeight: 700 }}>
                      ბრენდული აქცენტის ტექსტი
                    </span>
                  </div>
                  <div
                    style={{
                      padding: "0.75rem 1rem",
                      borderRadius: "8px",
                      border: "1.5px solid var(--jester-color-brand-primary)",
                      backgroundColor: "var(--jester-color-surface)",
                      fontSize: "0.85rem",
                    }}
                  >
                    აქტიური ინპუტის ან ბარათის ფოკუსის საზღვარი
                  </div>
                </div>
              </Card>

              {/* Box B: What remains strictly independent */}
              <Card padded style={{ borderTop: "4px solid #10B981" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <span style={{ fontSize: "1.2rem" }}>🛡️</span>
                  <h3 style={{ margin: 0, fontSize: "1.05rem", fontWeight: 800 }}>
                    იზოლირებული როლები (რჩება უცვლელი)
                  </h3>
                </div>
                <p style={{ margin: "0 0 1rem 0", color: "var(--jester-color-text-secondary)", fontSize: "0.85rem" }}>
                  სტატუსები, მონეტარული სისტემა და შეტყობინებები არ იცვლება:
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                  {/* Stars / Wallet */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0.75rem", borderRadius: "8px", backgroundColor: "var(--jester-color-stars-pill-bg-start, #FFFDF8)", border: "1px solid #FDE68A" }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--jester-color-wallet-free-text, #2D5231)" }}>⭐ Stars Balance</span>
                    <strong style={{ color: "#D97706" }}>120 Stars</strong>
                  </div>

                  {/* Status Danger */}
                  <div style={{ padding: "0.5rem 0.75rem", borderRadius: "8px", backgroundColor: "var(--jester-color-status-danger-bg, #FEF2F2)", border: "1px solid var(--jester-color-status-danger-border, #FECACA)", color: "var(--jester-color-status-danger-text, #B91C1C)", fontSize: "0.825rem", fontWeight: 600 }}>
                    ⚠️ შეცდომის სტატუსი (დარჩა Rose-700)
                  </div>

                  {/* Notification Blue */}
                  <div style={{ padding: "0.5rem 0.75rem", borderRadius: "8px", backgroundColor: "var(--jester-color-notification-unread-bg, #EFF6FF)", border: "1px solid var(--jester-color-notification-unread-border, #93C5FD)", color: "var(--jester-color-notification-unread-action, #2563EB)", fontSize: "0.825rem", fontWeight: 600 }}>
                    🔔 შეტყობინების ლურჯი აქცენტი (დარჩა Blue-600)
                  </div>

                  {/* Chat Bubbles */}
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <div style={{ flex: 1, padding: "0.4rem 0.6rem", borderRadius: "8px", backgroundColor: "var(--jester-color-chat-bubble-received-bg, #FAF8F5)", border: "1px solid var(--jester-color-chat-bubble-received-border, #EFEAE3)", fontSize: "0.75rem" }}>
                      მიღებული ბაბლი
                    </div>
                    <div style={{ flex: 1, padding: "0.4rem 0.6rem", borderRadius: "8px", backgroundColor: "var(--jester-color-chat-bubble-sent-bg, #F5DDD1)", fontSize: "0.75rem" }}>
                      გაგზავნილი ბაბლი
                    </div>
                  </div>
                </div>
              </Card>

            </div>
          </div>
        )}

      </div>
    </div>
  );
};
