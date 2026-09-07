import React, { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate, Link } from "react-router-dom";
import { API } from "../../core/api/endpoints";
import { ProfileUpdate } from "../../core/api/types";
import { useAuth } from "../../core/auth/useAuth";
import { LoadingState, ErrorState } from "../../shared/StatusState";

export const SelfProfilePage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const { data, isLoading, error } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: API.profiles.getMyProfile,
  });

  const [displayName, setDisplayName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [bio, setBio] = useState("");
  const [city, setCity] = useState("");
  const [occupation, setOccupation] = useState("");
  const [timezone, setTimezone] = useState("");
  const [isDiscoverable, setIsDiscoverable] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (data) {
      setDisplayName(data.display_name || "");
      setAvatarUrl(data.avatar_url || "");
      setBio(data.bio || "");
      setCity(data.city || "");
      setOccupation(data.occupation || "");
      setTimezone(data.timezone || "");
      setIsDiscoverable(data.is_discoverable ?? true);
    }
  }, [data]);

  const updateMutation = useMutation({
    mutationFn: (update: ProfileUpdate) => API.profiles.updateMyProfile(update),
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile", "me"], updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      display_name: displayName,
      avatar_url: avatarUrl,
      bio,
      city,
      occupation,
      timezone,
      is_discoverable: isDiscoverable,
    });
  };

  if (isLoading) return <LoadingState message="Loading profile settings..." />;
  if (error) return <ErrorState error={error as Error} />;

  return (
    <div style={{ maxWidth: "600px" }}>
      <h2 style={{ marginTop: 0 }}>Social Profile Settings</h2>
      <p style={{ color: "#666", fontSize: "0.9rem" }}>
        Manage how other discoverable users see you across the JESTER network.
      </p>

      {saveSuccess && (
        <div
          style={{
            padding: "0.75rem",
            marginBottom: "1rem",
            background: "#f6ffed",
            border: "1px solid #b7eb8f",
            borderRadius: "4px",
            color: "#389e0d",
            fontSize: "0.85rem",
          }}
        >
          ✅ Profile updated successfully!
        </div>
      )}

      {updateMutation.isError && (
        <ErrorState error={updateMutation.error as Error} />
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Display Name
          </label>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="e.g. Alex Thorne"
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Avatar Image URL
          </label>
          <input
            type="url"
            value={avatarUrl}
            onChange={(e) => setAvatarUrl(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="https://example.com/avatar.jpg"
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
            Bio / About You
          </label>
          <textarea
            rows={3}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            placeholder="Share a short bio or your interests..."
          />
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
              City
            </label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
              placeholder="e.g. London"
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: "bold", fontSize: "0.85rem" }}>
              Occupation
            </label>
            <input
              type="text"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
              placeholder="e.g. Architect"
            />
          </div>
        </div>

        <div style={{ padding: "0.75rem", border: "1px solid #e8e8e8", borderRadius: "4px", backgroundColor: "#fafafa" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer", fontWeight: "bold" }}>
            <input
              type="checkbox"
              checked={isDiscoverable}
              onChange={(e) => setIsDiscoverable(e.target.checked)}
            />
            Make My Profile Discoverable
          </label>
          <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.3rem" }}>
            When disabled, other users cannot find your profile or view your public safe astrology placements.
          </div>
        </div>

        <button
          type="submit"
          disabled={updateMutation.isPending}
          style={{
            padding: "0.6rem 1.2rem",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            fontWeight: "bold",
            cursor: updateMutation.isPending ? "not-allowed" : "pointer",
            alignSelf: "flex-start",
          }}
        >
          {updateMutation.isPending ? "Saving..." : "Save Profile"}
        </button>
      </form>

      {/* Account & Session Management */}
      <div
        style={{
          marginTop: "2.5rem",
          paddingTop: "1.5rem",
          borderTop: "1px solid #e8e8e8",
        }}
      >
        <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.05rem" }}>ანგარიში და სესია</h3>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "1rem",
            backgroundColor: "#fff",
            border: "1px solid #e8e8e8",
            borderRadius: "6px",
            gap: "1rem",
          }}
        >
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>
              {user?.email || "მიმდინარე მომხმარებელი"}
            </div>
            <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.2rem" }}>
              სისტემიდან გასვლა და ავტორიზაციის ეკრანზე დაბრუნება
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <Link
              to="/onboarding/birth-data"
              style={{
                padding: "0.45rem 0.9rem",
                borderRadius: "4px",
                border: "1px solid #d9d9d9",
                background: "#f5f5f5",
                color: "#333",
                textDecoration: "none",
                fontSize: "0.85rem",
                fontWeight: 500,
                display: "inline-flex",
                alignItems: "center",
              }}
            >
              ⚙️ დაბადების მონაცემები
            </Link>

            <button
              type="button"
              onClick={async () => {
                await signOut();
                navigate("/auth/login");
              }}
              style={{
                padding: "0.45rem 1rem",
                background: "#ff4d4f",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                fontWeight: 600,
                fontSize: "0.85rem",
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.3rem",
              }}
            >
              🚪 გასვლა (Sign Out)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
