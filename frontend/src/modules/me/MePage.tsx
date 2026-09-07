import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { ProfileResponse, ProfileUpdate, SafeDerivedAstrologyResponse, NatalResolveResponseItem } from "../../core/api/types";
import { Card, Button, Input, Badge, Avatar, Skeleton, LoadingState, ErrorState } from "../../shared/ui";

export const MePage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const [activeTab, setActiveTab] = useState<"insights" | "settings">("insights");

  // 1. Fetch User Profile
  const {
    data: profile,
    isLoading: loadingProfile,
    error: errorProfile,
  } = useQuery<ProfileResponse>({
    queryKey: ["profile", "me"],
    queryFn: API.profiles.getMyProfile,
  });

  // 2. Fetch User Safe Astrology Placements
  const {
    data: astro,
    isLoading: loadingAstro,
    error: errorAstro,
  } = useQuery<SafeDerivedAstrologyResponse>({
    queryKey: ["astrology", "me"],
    queryFn: API.astrology.getMySafeAstro,
  });

  // 3. Resolve Personal JESTER Narrative Observations (Human Interpretation First)
  const {
    data: natalObservations,
    isLoading: loadingNarrative,
    error: errorNarrative,
    refetch: refetchNarrative,
  } = useQuery<NatalResolveResponseItem[]>({
    queryKey: [
      "natal-observations",
      astro?.sun_sign,
      astro?.moon_sign,
      astro?.ascendant_sign,
      astro?.element_primary,
      astro?.modality_primary,
    ],
    queryFn: () =>
      API.interpretations.resolveNatal({
        sun_sign: astro!.sun_sign,
        moon_sign: astro?.moon_sign,
        ascendant_sign: astro?.ascendant_sign,
        element_primary: astro?.element_primary,
        modality_primary: astro?.modality_primary,
        locale: "ka",
      }),
    enabled: !!astro?.sun_sign,
  });

  // Profile Form State
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [city, setCity] = useState("");
  const [occupation, setOccupation] = useState("");
  const [isDiscoverable, setIsDiscoverable] = useState(true);
  const [formInitialized, setFormInitialized] = useState(false);

  // Sync profile form once data arrives
  if (profile && !formInitialized) {
    setDisplayName(profile.display_name || "");
    setBio(profile.bio || "");
    setCity(profile.city || "");
    setOccupation(profile.occupation || "");
    setIsDiscoverable(profile.is_discoverable ?? true);
    setFormInitialized(true);
  }

  // Mutations
  const updateMutation = useMutation({
    mutationFn: (updateData: ProfileUpdate) => API.profiles.updateMyProfile(updateData),
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile", "me"], updated);
      alert("პროფილი წარმატებით განახლდა!");
    },
  });

  const recalcMutation = useMutation({
    mutationFn: API.astrology.recalculate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
      alert("ასტროლოგიური რუკა და დაკვირვებები წარმატებით გადაითვალა!");
    },
  });

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      display_name: displayName,
      bio,
      city,
      occupation,
      is_discoverable: isDiscoverable,
    });
  };

  const getDimensionIcon = (dim: string) => {
    switch (dim) {
      case "self.identity":
        return "☀️";
      case "self.emotional":
        return "🌙";
      case "self.persona":
        return "🌅";
      case "self.element":
        return "🔥";
      case "self.modality":
        return "⚡";
      default:
        return "💡";
    }
  };

  const getSupportingSignalBadge = (dim: string) => {
    if (!astro) return null;
    switch (dim) {
      case "self.identity":
        return <Badge variant="astrology" size="sm">მზის ნიშანი: {astro.sun_sign}</Badge>;
      case "self.emotional":
        return <Badge variant="default" size="sm">მთვარის ნიშანი: {astro.moon_sign}</Badge>;
      case "self.persona":
        return astro.ascendant_sign ? (
          <Badge variant="brand" size="sm">ასცენდენტი: {astro.ascendant_sign}</Badge>
        ) : (
          <Badge variant="outline" size="sm">ასცენდენტი: უცნობი დრო</Badge>
        );
      case "self.element":
        return <Badge variant="default" size="sm">სტიქია: {astro.element_primary}</Badge>;
      case "self.modality":
        return <Badge variant="default" size="sm">მოდალობა: {astro.modality_primary}</Badge>;
      default:
        return null;
    }
  };

  const greetingName = profile?.display_name || user?.email?.split("@")[0] || "მომხმარებელი";

  if (loadingProfile && !profile) {
    return <LoadingState message="პროფილის მონაცემების ჩატვირთვა..." />;
  }

  if (errorProfile) {
    return (
      <ErrorState
        error={errorProfile as Error}
        onRetry={() => queryClient.invalidateQueries({ queryKey: ["profile", "me"] })}
      />
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
      {/* 1. Header Hero Card: Identity & Essence */}
      <Card padded style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
          <Avatar src={profile?.avatar_url} name={greetingName} size="xl" />
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
              <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 800, color: "#0f172a" }}>
                {greetingName}
              </h1>
              {astro?.sun_sign && (
                <Badge variant="astrology" size="md">
                  ☀️ {astro.sun_sign}
                </Badge>
              )}
              {profile?.is_discoverable && (
                <Badge variant="success" size="sm">
                  ✓ აღმოჩენადი
                </Badge>
              )}
            </div>

            <div style={{ fontSize: "0.875rem", color: "#64748b", marginTop: "0.3rem" }}>
              {user?.email} {[profile?.occupation, profile?.city].filter(Boolean).length > 0 && `• ${[profile?.occupation, profile?.city].filter(Boolean).join(", ")}`}
            </div>

            {profile?.bio && (
              <p style={{ margin: "0.5rem 0 0 0", color: "#334155", fontSize: "0.875rem", maxWidth: "560px", lineHeight: 1.5 }}>
                "{profile.bio}"
              </p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <Link to="/onboarding/birth-data" style={{ textDecoration: "none" }}>
            <Button variant="outline" size="sm" icon={<span>⚙️</span>}>
              დაბადების მონაცემები
            </Button>
          </Link>
          <Button
            variant="danger"
            size="sm"
            onClick={async () => {
              await signOut();
              navigate("/auth/login");
            }}
          >
            🚪 გასვლა
          </Button>
        </div>
      </Card>

      {/* 2. Mode Selector: Personal Insights (ME) vs Profile Settings */}
      <div style={{ display: "flex", borderBottom: "2px solid #e2e8f0", gap: "1.5rem" }}>
        <button
          onClick={() => setActiveTab("insights")}
          style={{
            padding: "0.75rem 0.5rem",
            background: "none",
            border: "none",
            borderBottom: activeTab === "insights" ? "3px solid #6366f1" : "3px solid transparent",
            color: activeTab === "insights" ? "#6366f1" : "#64748b",
            fontWeight: activeTab === "insights" ? 800 : 600,
            cursor: "pointer",
            fontSize: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginBottom: "-2px",
            transition: "all 0.15s ease",
          }}
        >
          <span>💡</span>
          <span>ჩემი არსი & JESTER დაკვირვებები</span>
        </button>

        <button
          onClick={() => setActiveTab("settings")}
          style={{
            padding: "0.75rem 0.5rem",
            background: "none",
            border: "none",
            borderBottom: activeTab === "settings" ? "3px solid #6366f1" : "3px solid transparent",
            color: activeTab === "settings" ? "#6366f1" : "#64748b",
            fontWeight: activeTab === "settings" ? 800 : 600,
            cursor: "pointer",
            fontSize: "1rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            marginBottom: "-2px",
            transition: "all 0.15s ease",
          }}
        >
          <span>⚙️</span>
          <span>პროფილის მართვა & პარამეტრები</span>
        </button>
      </div>

      {/* 3. TAB 1: Human-First Personal JESTER Narrative Observations */}
      {activeTab === "insights" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 800, color: "#0f172a" }}>
              ვინ ვარ მე — დეტერმინისტული დაკვირვებები
            </h2>
            <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
              JESTER-ის ინტერპრეტაციები თქვენი ხასიათის, ემოციებისა და სოციალური როლის შესახებ:
            </p>
          </div>

          {loadingAstro || loadingNarrative ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <Skeleton height="140px" borderRadius="12px" />
              <Skeleton height="140px" borderRadius="12px" />
              <Skeleton height="140px" borderRadius="12px" />
            </div>
          ) : errorAstro || errorNarrative ? (
            <ErrorState
              error={(errorAstro || errorNarrative) as Error}
              onRetry={() => {
                queryClient.invalidateQueries({ queryKey: ["astrology", "me"] });
                refetchNarrative();
              }}
            />
          ) : !astro ? (
            <Card padded style={{ textAlign: "center", padding: "2.5rem 1rem" }}>
              <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🧭</div>
              <h3 style={{ margin: "0 0 0.5rem 0", color: "#1e293b" }}>დაბადების მონაცემები არ არის შეყვანილი</h3>
              <p style={{ color: "#64748b", fontSize: "0.9rem", maxWidth: "420px", margin: "0 auto 1.5rem auto" }}>
                თქვენი პერსონალური დაკვირვებებისა და სინასტრიული რუკის გამოსათვლელად შეიყვანეთ დაბადების თარიღი და ადგილი.
              </p>
              <Link to="/onboarding/birth-data" style={{ textDecoration: "none" }}>
                <Button variant="brand" size="md">
                  🚀 მონაცემების შეყვანა
                </Button>
              </Link>
            </Card>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {(natalObservations || []).map((obs) => {
                const icon = getDimensionIcon(obs.dimension);
                const badge = getSupportingSignalBadge(obs.dimension);

                return (
                  <Card
                    key={obs.dimension}
                    padded
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.85rem",
                    }}
                  >
                    {/* Top: Title & Supporting Astrological Signal Badge */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <span style={{ fontSize: "1.25rem" }}>{icon}</span>
                        <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>
                          {obs.title}
                        </h3>
                      </div>

                      {/* Supporting Astrology Signal Chip (Below hierarchy, supporting the narrative) */}
                      {badge}
                    </div>

                    {/* Primary: Human Narrative Interpretation in JESTER Voice */}
                    <p style={{ margin: 0, color: "#334155", fontSize: "0.95rem", lineHeight: 1.65 }}>
                      {obs.interpretation?.text}
                    </p>

                    {/* Metadata footer */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #f1f5f9", paddingTop: "0.6rem", fontSize: "0.75rem", color: "#94a3b8" }}>
                      <span>ტონი: <code>{obs.interpretation?.tone || "witty"}</code></span>
                      <span>სტატუსი: <code>{obs.interpretation?.content_status || "approved"}</code></span>
                    </div>
                  </Card>
                );
              })}

              {/* Elemental & Modality Dynamics Breakdown */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem", marginTop: "0.5rem" }}>
                <Card padded>
                  <div style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                    დომინანტური სტიქია
                  </div>
                  <div style={{ fontSize: "1.3rem", fontWeight: 800, marginTop: "0.3rem", color: "#0f172a" }}>
                    🔥 {astro.element_primary}
                  </div>
                  <div style={{ fontSize: "0.825rem", color: "#64748b", marginTop: "0.2rem" }}>
                    განსაზღვრავს თქვენი ენერგიის ძირითად ბუნებასა და რეაქციებს.
                  </div>
                </Card>

                <Card padded>
                  <div style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase", fontWeight: 700 }}>
                    მოდალობა
                  </div>
                  <div style={{ fontSize: "1.3rem", fontWeight: 800, marginTop: "0.3rem", color: "#0f172a" }}>
                    ⚡ {astro.modality_primary}
                  </div>
                  <div style={{ fontSize: "0.825rem", color: "#64748b", marginTop: "0.2rem" }}>
                    ცხოვრებისეული გადაწყვეტილებების დინამიკა და ცვლილებებთან ადაპტაცია.
                  </div>
                </Card>
              </div>

              {/* Recalculate Natal Placements Action */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem" }}>
                <span style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
                  ძრავა: {astro.engine_version} • ვერსია: v{astro.source_birth_data_version} • ბოლოს გადათვლილი: {new Date(astro.updated_at).toLocaleDateString("ka-GE")}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  isLoading={recalcMutation.isPending}
                  onClick={() => recalcMutation.mutate()}
                >
                  🔄 რუკის გადათვლა
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. TAB 2: Profile & Account Settings */}
      {activeTab === "settings" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 800, color: "#0f172a" }}>
              პროფილის ინფორმაციის რედაქტირება
            </h2>
            <p style={{ margin: "0.25rem 0 0 0", color: "#64748b", fontSize: "0.9rem" }}>
              ეს მონაცემები ჩანს თქვენს საჯარო პროფილზე და აღმოჩენის გვერდზე.
            </p>
          </div>

          <Card padded>
            <form onSubmit={handleSaveProfile} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>
              <Input
                label="სახელი / Display Name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="თქვენი სახელი"
                required
              />

              <div>
                <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "#1e293b", marginBottom: "0.35rem", display: "block" }}>
                  ბიო / Bio (მოკლე აღწერა)
                </label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  rows={3}
                  style={{
                    width: "100%",
                    padding: "0.65rem",
                    border: "1px solid #cbd5e1",
                    borderRadius: "8px",
                    fontFamily: "inherit",
                    fontSize: "0.95rem",
                    boxSizing: "border-box",
                  }}
                  placeholder="რას საქმიანობთ, რა გაინტერესებთ..."
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
                <Input
                  label="ქალაქი / City"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="მაგ. თბილისი"
                />
                <Input
                  label="საქმიანობა / Occupation"
                  value={occupation}
                  onChange={(e) => setOccupation(e.target.value)}
                  placeholder="მაგ. Product Designer"
                />
              </div>

              {/* Discoverability Toggle */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                  padding: "0.85rem 1rem",
                  backgroundColor: "#f8fafc",
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  margin: "0.25rem 0",
                }}
              >
                <input
                  type="checkbox"
                  id="discoverable-checkbox"
                  checked={isDiscoverable}
                  onChange={(e) => setIsDiscoverable(e.target.checked)}
                  style={{ width: "20px", height: "20px", cursor: "pointer", accentColor: "#6366f1" }}
                />
                <div>
                  <label htmlFor="discoverable-checkbox" style={{ fontWeight: 700, fontSize: "0.9rem", color: "#0f172a", cursor: "pointer" }}>
                    პროფილი ჩანდეს აღმოჩენის სიაში (Discoverable)
                  </label>
                  <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.15rem" }}>
                    თუ გამორთავთ, სხვა მომხმარებლები ვერ დაგინახავენ Discover სიაში.
                  </div>
                </div>
              </div>

              <div>
                <Button variant="brand" size="md" isLoading={updateMutation.isPending} type="submit">
                  💾 შენახვა / Save Changes
                </Button>
              </div>
            </form>
          </Card>

          {/* Account Security & Birth Parameters Card */}
          <Card padded style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <h3 style={{ margin: "0 0 0.25rem 0", fontSize: "1.05rem", color: "#0f172a" }}>
                დაბადების პარამეტრები & ანგარიში
              </h3>
              <p style={{ margin: 0, color: "#64748b", fontSize: "0.85rem" }}>
                თქვენი დაბადების დრო, თარიღი და ადგილი დაცულია და არასდროს ჩანს საჯაროდ.
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Link to="/onboarding/birth-data" style={{ textDecoration: "none" }}>
                <Button variant="secondary" size="sm">
                  ✏️ დაბადების მონაცემების შეცვლა
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
