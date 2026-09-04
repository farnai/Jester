import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import {
  DailyEnergyResponse,
  DiscoveryPerson,
  ComparePreviewResponse,
  NatalResolveResponseItem,
  ResolvedInterpretationModel,
} from "../../core/api/types";
import { LoadingState, ErrorState } from "../../shared/StatusState";

type TabMode = "me" | "discovery" | "you" | "us";

export const ContentSmokeTestPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabMode>("me");
  const [selectedEnergyType, setSelectedEnergyType] = useState<string>("confidence");
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);
  const [showInspector, setShowInspector] = useState<boolean>(true);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  // 1. Fetch Today's Energy (ME)
  const {
    data: dailyEnergy,
    isLoading: loadingDaily,
    error: errorDaily,
  } = useQuery<DailyEnergyResponse>({
    queryKey: ["daily-energy", selectedEnergyType],
    queryFn: () => API.interpretations.getDailyEnergy(selectedEnergyType, "ka"),
  });

  // 2. Fetch Personal Natal Observations (ME - Alexandre: Aries Sun, Aquarius Moon, Leo Rising, Fire Element, Cardinal Modality)
  const {
    data: natalObservations,
    isLoading: loadingNatal,
    error: errorNatal,
  } = useQuery<NatalResolveResponseItem[]>({
    queryKey: ["natal-observations"],
    queryFn: () =>
      API.interpretations.resolveNatal({
        sun_sign: "Aries",
        moon_sign: "Aquarius",
        ascendant_sign: "Leo",
        element_primary: "Fire",
        modality_primary: "Cardinal",
        locale: "ka",
      }),
  });

  // 3. Fetch Discovery People (MORE PEOPLE)
  const {
    data: discoveryPeople,
    isLoading: loadingPeople,
    error: errorPeople,
  } = useQuery<DiscoveryPerson[]>({
    queryKey: ["discovery-people"],
    queryFn: () => API.interpretations.getDiscoveryPeople("26098ac8-f8f0-4cd3-9bbb-78dc8467ba07"),
  });

  // Automatically select first person if none selected
  const activePerson =
    discoveryPeople?.find((p) => p.id === selectedPersonId) ||
    discoveryPeople?.[0] ||
    null;

  // 4. Fetch Compare Preview (US - Alexandre vs Active Person)
  const {
    data: compareData,
    isLoading: loadingCompare,
    error: errorCompare,
  } = useQuery<ComparePreviewResponse>({
    queryKey: ["compare-preview", activePerson?.id],
    queryFn: () =>
      API.interpretations.comparePreview({
        source_user_id: "26098ac8-f8f0-4cd3-9bbb-78dc8467ba07",
        target_user_id: activePerson!.id,
        locale: "ka",
      }),
    enabled: !!activePerson?.id,
  });

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2500);
  };

  const renderAuditBadge = (model?: ResolvedInterpretationModel | null) => {
    if (!showInspector || !model) return null;
    const len = model.text?.length || 0;
    const hasPattern1 = model.text?.includes("ერთი შეხედვით");
    const hasPattern2 = model.text?.includes("აქ ყოველგვარი ეჭვი");
    const hasPattern3 = model.text?.includes("მოდი პირდაპირ ვთქვათ");

    return (
      <div className="audit-badge-container">
        <span className="audit-tag id-tag">ID: {model.id}</span>
        {model.content_asset_id && (
          <span className="audit-tag asset-tag">{model.content_asset_id}</span>
        )}
        <span className="audit-tag tone-tag">{model.tone || "witty"}</span>
        <span className="audit-tag status-tag">{model.content_status}</span>
        <span className={`audit-tag length-tag ${len > 180 ? "warning" : ""}`}>
          {len} სიმბოლო
        </span>
        {hasPattern1 && <span className="audit-tag flag-tag">⚠️ "ერთი შეხედვით"</span>}
        {hasPattern2 && <span className="audit-tag flag-tag">⚠️ "ყოველგვარი ეჭვი"</span>}
        {hasPattern3 && <span className="audit-tag flag-tag">⚠️ "მოდი პირდაპირ"</span>}
        <button
          className="audit-copy-btn"
          onClick={() => handleCopy(model.text, model.id)}
          title="ტექსტის კოპირება შეფასებისთვის"
        >
          {copiedText === model.id ? "✓ კოპირებულია" : "📋 გაზიარება"}
        </button>
      </div>
    );
  };

  return (
    <div className="smoke-test-container">
      {/* Top Header / Bar */}
      <header className="smoke-header">
        <div className="header-left">
          <div className="brand-logo">
            <span className="jester-icon">🃏</span>
            <span className="jester-title">JESTER</span>
            <span className="badge-live">LIVE SMOKE TEST</span>
          </div>
          <p className="header-subtitle">
            ქართული კონტენტის კორპუსის და UX ნაკადის ვიზუალური შემოწმება (Locale: <code>ka</code>)
          </p>
        </div>

        <div className="header-actions">
          <button
            className={`inspector-toggle-btn ${showInspector ? "active" : ""}`}
            onClick={() => setShowInspector(!showInspector)}
          >
            {showInspector ? "👁️ აუდიტის პანელი: ჩართული" : "🙈 აუდიტის პანელი: გამორთული"}
          </button>
        </div>
      </header>

      {/* Main Flow Navigation Tabs (ME -> YOU -> US -> MORE PEOPLE) */}
      <nav className="flow-tabs">
        <button
          className={`flow-tab-btn ${activeTab === "me" ? "active" : ""}`}
          onClick={() => setActiveTab("me")}
        >
          <span className="tab-step">1</span>
          <span className="tab-label">ME (მე)</span>
          <span className="tab-caption">ჩემი პროფილი და ენერგია</span>
        </button>

        <button
          className={`flow-tab-btn ${activeTab === "discovery" ? "active" : ""}`}
          onClick={() => setActiveTab("discovery")}
        >
          <span className="tab-step">2</span>
          <span className="tab-label">DISCOVERY (აღმოაჩინე)</span>
          <span className="tab-caption">კიდევ ვისთან ვნახოთ?</span>
        </button>

        <button
          className={`flow-tab-btn ${activeTab === "you" ? "active" : ""}`}
          onClick={() => setActiveTab("you")}
        >
          <span className="tab-step">3</span>
          <span className="tab-label">YOU (ის)</span>
          <span className="tab-caption">
            {activePerson ? activePerson.display_name : "ადამიანის ბარათი"}
          </span>
        </button>

        <button
          className={`flow-tab-btn ${activeTab === "us" ? "active" : ""}`}
          onClick={() => setActiveTab("us")}
        >
          <span className="tab-step">4</span>
          <span className="tab-label">US (ჩვენ)</span>
          <span className="tab-caption">სინასტრია & დინამიკა</span>
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="smoke-main-content">
        {/* ================================================================= */}
        {/* TAB 1: ME (მე) */}
        {/* ================================================================= */}
        {activeTab === "me" && (
          <section className="section-me">
            <div className="section-lead-banner">
              <div className="lead-tag">JESTER-ის პირადი დაკვირვება</div>
              <h1 className="lead-title">JESTER ამჩნევს რაღაცას შენზე</h1>
              <p className="lead-desc">
                მომხმარებლის პირადი JESTER გამოცდილება: დღევანდელი ვიბრაცია, თვითიდენტობა და შინაგანი დინამიკა.
              </p>
            </div>

            {/* Today's Energy / Day Vibe Widget */}
            <div className="card energy-card">
              <div className="card-header">
                <div className="card-badge">✨ TODAY'S ENERGY / DAY VIBE</div>
                <h2 className="energy-headline">
                  დღის ენერგია: <span className="highlight">{dailyEnergy?.label}</span>
                </h2>
              </div>

              {/* Archetype Switcher Pills */}
              <div className="archetype-pills-bar">
                <span className="pills-title">არქეტიპის გამოცდა:</span>
                <div className="pills-scroll">
                  {dailyEnergy?.available_archetypes?.map((arch) => (
                    <button
                      key={arch.id}
                      className={`pill-btn ${selectedEnergyType === arch.id ? "active" : ""}`}
                      onClick={() => setSelectedEnergyType(arch.id)}
                    >
                      {arch.label_ka}
                    </button>
                  ))}
                </div>
              </div>

              {loadingDaily ? (
                <LoadingState message="იტვირთება დღის ენერგია..." />
              ) : errorDaily ? (
                <ErrorState error={errorDaily as Error} />
              ) : (
                <div className="energy-content-box">
                  <p className="jester-quote-text">
                    "{dailyEnergy?.interpretation?.text}"
                  </p>
                  {renderAuditBadge(dailyEnergy?.interpretation)}
                </div>
              )}
            </div>

            {/* Relevant Personal Observations (5 Dimensions) */}
            <div className="natal-section">
              <div className="section-subheading">
                <h3>პირადი სიგნალები და შინაგანი არქიტექტურა</h3>
                <span className="subheading-note">5 ძირითადი განზომილება</span>
              </div>

              {loadingNatal ? (
                <LoadingState message="იტვირთება პირადი დაკვირვებები..." />
              ) : errorNatal ? (
                <ErrorState error={errorNatal as Error} />
              ) : (
                <div className="natal-grid">
                  {natalObservations?.map((item) => (
                    <div key={item.dimension} className="card natal-card">
                      <div className="natal-card-top">
                        <span className="natal-dim-pill">{item.title}</span>
                        <span className="natal-dim-key">{item.dimension}</span>
                      </div>
                      <p className="natal-text">{item.interpretation.text}</p>
                      {renderAuditBadge(item.interpretation)}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Bottom Transition CTA */}
            <div className="flow-continuation-banner">
              <div className="continuation-text">
                <h3>გაინტერესებს როგორ ერწყმის შენი ენერგია სხვებს?</h3>
                <p>გადადი აღმოჩენის გვერდზე და შეარჩიე ადამიანი შესადარებლად.</p>
              </div>
              <button
                className="cta-primary-btn"
                onClick={() => setActiveTab("discovery")}
              >
                აღმოაჩინე ადამიანები (DISCOVERY) →
              </button>
            </div>
          </section>
        )}

        {/* ================================================================= */}
        {/* TAB 2: DISCOVERY / MORE PEOPLE (აღმოაჩინე) */}
        {/* ================================================================= */}
        {activeTab === "discovery" && (
          <section className="section-discovery">
            <div className="section-lead-banner">
              <div className="lead-tag">PEOPLE DISCOVERY & INTELLIGENCE</div>
              <h1 className="lead-title">კიდევ ვისთან ვნახოთ?</h1>
              <p className="lead-desc">
                აღმოაჩინე რეალური ადამიანები, მათი JESTER-ის საწყისი დაკვირვებები და გამოთვლილი თავსებადობის ქულა.
              </p>
            </div>

            {loadingPeople ? (
              <LoadingState message="იტვირთება აღმოჩენის სია..." />
            ) : errorPeople ? (
              <ErrorState error={errorPeople as Error} />
            ) : (
              <div className="people-cards-grid">
                {discoveryPeople?.map((person) => {
                  const isCurrent = activePerson?.id === person.id;
                  return (
                    <div
                      key={person.id}
                      className={`card person-discovery-card ${isCurrent ? "selected" : ""}`}
                    >
                      <div className="person-card-header">
                        <div className="person-avatar">
                          {person.display_name.charAt(0)}
                        </div>
                        <div className="person-identity">
                          <h3 className="person-name">{person.display_name}</h3>
                          <div className="person-meta">
                            {person.occupation} • {person.city}
                          </div>
                        </div>
                        <div className="person-score-badge">
                          <span className="score-val">
                            {person.compatibility_score.toFixed(0)}%
                          </span>
                          <span className="score-lbl">თავსებადობა</span>
                        </div>
                      </div>

                      {/* Safe Derived Astrology Badges */}
                      <div className="astro-tags-row">
                        <span className="astro-tag sun-tag">
                          ☀️ {person.astrology.sun_sign || "მზე"}
                        </span>
                        <span className="astro-tag moon-tag">
                          🌙 {person.astrology.moon_sign || "მთვარე"}
                        </span>
                        {person.astrology.ascendant_sign && (
                          <span className="astro-tag asc-tag">
                            🏹 {person.astrology.ascendant_sign}
                          </span>
                        )}
                        <span className="astro-tag elem-tag">
                          🔥 {person.astrology.element_primary}
                        </span>
                      </div>

                      {/* Resolved Hook Observation */}
                      {person.hook_observation && (
                        <div className="person-hook-box">
                          <div className="hook-label">JESTER-ის დაკვირვება:</div>
                          <p className="hook-text">"{person.hook_observation.text}"</p>
                          {renderAuditBadge(person.hook_observation)}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="person-card-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => {
                            setSelectedPersonId(person.id);
                            setActiveTab("you");
                          }}
                        >
                          პროფილის ნახვა (YOU)
                        </button>
                        <button
                          className="btn-primary"
                          onClick={() => {
                            setSelectedPersonId(person.id);
                            setActiveTab("us");
                          }}
                        >
                          შედარება (US) →
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {/* ================================================================= */}
        {/* TAB 3: YOU (ის — ადამიანის ბარათი) */}
        {/* ================================================================= */}
        {activeTab === "you" && (
          <section className="section-you">
            {activePerson ? (
              <>
                <div className="section-lead-banner">
                  <div className="lead-tag">HUMAN INTELLIGENCE & OBSERVATION</div>
                  <h1 className="lead-title">
                    საინტერესოა... რას იტყოდა JESTER {activePerson.display_name}-ზე?
                  </h1>
                  <p className="lead-desc">
                    ადამიანის ბარათი და JESTER-ის დაკვირვების სიგნალი, რომელიც ცნობისმოყვარეობას აღძრავს.
                  </p>
                </div>

                <div className="card you-detail-card">
                  <div className="you-header">
                    <div className="you-avatar-large">
                      {activePerson.display_name.charAt(0)}
                    </div>
                    <div className="you-titles">
                      <h2>{activePerson.display_name}</h2>
                      <div className="you-meta-sub">
                        <span>💼 {activePerson.occupation}</span>
                        <span>📍 {activePerson.city}</span>
                      </div>
                      {activePerson.bio && (
                        <p className="you-bio-text">{activePerson.bio}</p>
                      )}
                    </div>

                    <div className="you-score-card">
                      <div className="score-number">
                        {activePerson.compatibility_score.toFixed(1)}%
                      </div>
                      <div className="score-desc">სავარაუდო ჰარმონია</div>
                    </div>
                  </div>

                  {/* Safe Derived Astrology Breakdown */}
                  <div className="astro-summary-grid">
                    <div className="astro-metric-box">
                      <span className="metric-label">მზე (Sun)</span>
                      <span className="metric-value">{activePerson.astrology.sun_sign}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">მთვარე (Moon)</span>
                      <span className="metric-value">{activePerson.astrology.moon_sign}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">ასცენდენტი (Rising)</span>
                      <span className="metric-value">{activePerson.astrology.ascendant_sign || "—"}</span>
                    </div>
                    <div className="metric-box">
                      <span className="metric-label">სტიქია / მოდალობა</span>
                      <span className="metric-value">
                        {activePerson.astrology.element_primary} / {activePerson.astrology.modality_primary}
                      </span>
                    </div>
                  </div>

                  {/* Hook Observation */}
                  {activePerson.hook_observation && (
                    <div className="you-observation-card">
                      <div className="obs-badge">🎯 JESTER-ის დაკვირვება ადამიანზე</div>
                      <p className="obs-quote-text">
                        "{activePerson.hook_observation.text}"
                      </p>
                      {renderAuditBadge(activePerson.hook_observation)}
                    </div>
                  )}

                  {/* Curiosity Trigger & US CTA */}
                  <div className="you-cta-box">
                    <div className="cta-prompt">
                      <h3>როგორი იქნება თქვენი დინამიკა ერთად?</h3>
                      <p>
                        გაიგე რა ხდება, როდესაც შენი ენერგია და {activePerson.display_name}-ს ხასიათი ერთ სივრცეში ხვდება.
                      </p>
                    </div>
                    <div className="cta-buttons-row">
                      <button
                        className="cta-primary-btn"
                        onClick={() => setActiveTab("us")}
                      >
                        შედარება: რას ამბობს JESTER ჩვენზე? (US) →
                      </button>
                      <button
                        className="btn-secondary"
                        onClick={() => setActiveTab("discovery")}
                      >
                        სხვა ადამიანის არჩევა
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="card empty-card">
                <h3>ადამიანი არ არის არჩეული</h3>
                <p>გთხოვთ დაბრუნდეთ აღმოჩენის სიაში და აირჩიოთ პროფილი.</p>
                <button
                  className="cta-primary-btn"
                  onClick={() => setActiveTab("discovery")}
                >
                  აღმოჩენის სიაში დაბრუნება →
                </button>
              </div>
            )}
          </section>
        )}

        {/* ================================================================= */}
        {/* TAB 4: US (ჩვენ — სინასტრია და შედარება) */}
        {/* ================================================================= */}
        {activeTab === "us" && (
          <section className="section-us">
            {activePerson ? (
              <>
                <div className="section-lead-banner">
                  <div className="lead-tag">SYNASTRY V1 DETERMINISTIC INTELLIGENCE</div>
                  <h1 className="lead-title">
                    კარგი... რას ამბობს JESTER ჩვენზე?
                  </h1>
                  <p className="lead-desc">
                    ალექსანდრე & {activePerson.display_name} — სინასტრიული კავშირის რეალური ანალიზი.
                  </p>
                </div>

                {loadingCompare ? (
                  <LoadingState message="გამოითვლება სინასტრია და წყვილის დინამიკა..." />
                ) : errorCompare ? (
                  <ErrorState error={errorCompare as Error} />
                ) : compareData ? (
                  <div className="us-dashboard">
                    {/* Overall Score & Primary Interpretation */}
                    <div className="card score-hero-card">
                      <div className="score-hero-left">
                        <div className="hero-sub">საერთო თავსებადობის ქულა</div>
                        <div className="hero-score">
                          {compareData.score.toFixed(1)}
                          <span className="hero-score-max">/ 100</span>
                        </div>
                        <div className="confidence-pill">
                          სანდოობა: {(compareData.data_quality.confidence * 100).toFixed(0)}% (ზუსტი დრო)
                        </div>
                      </div>

                      <div className="score-hero-right">
                        <div className="primary-quote-header">
                          🔮 JESTER-ის მთავარი დასკვნა
                        </div>
                        <p className="primary-interpretation-text">
                          "{compareData.interpretation.text}"
                        </p>
                        {renderAuditBadge(compareData.interpretation)}
                      </div>
                    </div>

                    {/* 4 Core Dimensions */}
                    <div className="card dimensions-card">
                      <h3 className="card-subtitle">4 ძირითადი განზომილება</h3>
                      <div className="dimensions-grid">
                        <div className="dimension-box">
                          <div className="dim-header">
                            <span className="dim-name">💚 ემოციური ჰარმონია</span>
                            <span className="dim-score">
                              {compareData.dimensions.emotional_harmony.toFixed(1)}
                            </span>
                          </div>
                          <div className="dim-progress-bg">
                            <div
                              className="dim-progress-fill harmony"
                              style={{ width: `${compareData.dimensions.emotional_harmony}%` }}
                            />
                          </div>
                        </div>

                        <div className="dimension-box">
                          <div className="dim-header">
                            <span className="dim-name">🔥 მიზიდულობა</span>
                            <span className="dim-score">
                              {compareData.dimensions.attraction.toFixed(1)}
                            </span>
                          </div>
                          <div className="dim-progress-bg">
                            <div
                              className="dim-progress-fill attraction"
                              style={{ width: `${compareData.dimensions.attraction}%` }}
                            />
                          </div>
                        </div>

                        <div className="dimension-box">
                          <div className="dim-header">
                            <span className="dim-name">💬 კომუნიკაცია</span>
                            <span className="dim-score">
                              {compareData.dimensions.communication.toFixed(1)}
                            </span>
                          </div>
                          <div className="dim-progress-bg">
                            <div
                              className="dim-progress-fill communication"
                              style={{ width: `${compareData.dimensions.communication}%` }}
                            />
                          </div>
                        </div>

                        <div className="dimension-box">
                          <div className="dim-header">
                            <span className="dim-name">🌱 ზრდა და დინამიკა</span>
                            <span className="dim-score">
                              {compareData.dimensions.growth_long_term.toFixed(1)}
                            </span>
                          </div>
                          <div className="dim-progress-bg">
                            <div
                              className="dim-progress-fill growth"
                              style={{ width: `${compareData.dimensions.growth_long_term}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Top Relationship Signals */}
                    <div className="card signals-card">
                      <h3 className="card-subtitle">
                        წამყვანი ასტროლოგიური სიგნალები და მათი ქართული თარგმანი
                      </h3>
                      <div className="signals-list">
                        {compareData.signals?.map((sig, idx) => (
                          <div key={idx} className="signal-item-card">
                            <div className="signal-item-top">
                              <span className={`signal-category-tag ${sig.category}`}>
                                {sig.category}
                              </span>
                              <span className="signal-label">{sig.label}</span>
                              <span className="signal-strength">ძალა: {sig.strength}</span>
                              {sig.source_aspects?.map((asp, i) => (
                                <span key={i} className="aspect-evidence-tag">
                                  {asp}
                                </span>
                              ))}
                            </div>
                            <p className="signal-resolved-text">
                              "{sig.interpretation?.text || "ინტერპრეტაცია არ არის"}"
                            </p>
                            {renderAuditBadge(sig.interpretation)}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Bridge Topics & Conversation Starters */}
                    <div className="two-col-grid">
                      <div className="card bridge-topics-card">
                        <h3 className="card-subtitle">🌉 საერთო თემები (Bridge Topics)</h3>
                        <ul className="topics-list">
                          {compareData.best_topics?.map((topic, i) => (
                            <li key={i} className="topic-item">
                              <span className="bullet">✦</span> {topic}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="card starters-card">
                        <h3 className="card-subtitle">
                          🗣️ საუბრის დამწყები კითხვები (Starters)
                        </h3>
                        <ul className="starters-list">
                          {compareData.conversation_starters?.map((starter, i) => (
                            <li key={i} className="starter-item">
                              <span className="starter-icon">💬</span> "{starter}"
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Structured Deep Analysis */}
                    {compareData.deep_analysis && (
                      <div className="card deep-analysis-card">
                        <div className="deep-header">
                          <span className="deep-tag">DEEP ANALYSIS ARCHITECTURE</span>
                          <h3>სიღრმისეული ანალიზი: ძირითადი დინამიკის ბლოკები</h3>
                        </div>

                        <div className="deep-blocks-grid">
                          {compareData.deep_analysis.blocks?.map((b, i) => (
                            <div key={i} className="deep-block-item">
                              <div className="deep-block-top">
                                <span className={`dim-tag ${b.dimension}`}>
                                  {b.dimension}
                                </span>
                                <span className="evidence-trace">
                                  {b.evidence_aspects?.join(", ")}
                                </span>
                              </div>
                              <p className="deep-block-text">"{b.resolved_text}"</p>
                              <div className="deep-block-footer">
                                <span className="tone-pill">{b.tone}</span>
                                <span className="asset-pill">{b.content_asset_id}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Natural Continuation / Viral Axiom */}
                    <div className="flow-continuation-banner">
                      <div className="continuation-text">
                        <h3>კიდევ ვისთან ვნახოთ?</h3>
                        <p>
                          შეადარე სხვა ადამიანებთან და ნახე, როგორ იცვლება JESTER-ის ენა სხვადასხვა წყვილში.
                        </p>
                      </div>
                      <button
                        className="cta-primary-btn"
                        onClick={() => setActiveTab("discovery")}
                      >
                        სხვა ადამიანების აღმოჩენა (MORE PEOPLE) →
                      </button>
                    </div>
                  </div>
                ) : null}
              </>
            ) : (
              <div className="card empty-card">
                <h3>შედარებისთვის აირჩიეთ ადამიანი</h3>
                <p>გადადით აღმოჩენის სიაში და აირჩიეთ ადამიანი შესადარებლად.</p>
                <button
                  className="cta-primary-btn"
                  onClick={() => setActiveTab("discovery")}
                >
                  აღმოჩენის სია →
                </button>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
};
export default ContentSmokeTestPage;
