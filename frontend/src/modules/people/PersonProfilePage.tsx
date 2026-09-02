import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { API } from "../../core/api/endpoints";
import { useAuth } from "../../core/auth/useAuth";
import { supabase } from "../../core/realtime/supabase";
import { LoadingState, PrivacySafeNotFoundState, ErrorState } from "../../shared/StatusState";

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const PersonProfilePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();

  const [lookupId, setLookupId] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  const targetId = (id || "").trim();
  const isValidUUID = UUID_REGEX.test(targetId);

  // Fetch Discoverable Users for the directory view when no ID is selected
  const discoverableUsersQuery = useQuery({
    queryKey: ["discoverable_profiles"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("profiles")
        .select("id, display_name, city, occupation, bio")
        .eq("is_discoverable", true)
        .limit(20);
      if (error) throw new Error(error.message);
      return data || [];
    },
    enabled: !targetId || !isValidUUID,
  });

  // 1. Fetch Target Profile (only if valid UUID format)
  const profileQuery = useQuery({
    queryKey: ["profile", targetId],
    queryFn: () => API.profiles.getProfileById(targetId),
    enabled: !!targetId && isValidUUID,
    retry: false,
  });

  // 2. Fetch Target Safe Astrology (only if valid UUID format and profile exists)
  const astroQuery = useQuery({
    queryKey: ["astrology", targetId],
    queryFn: () => API.astrology.getPersonSafeAstro(targetId),
    enabled: !!targetId && isValidUUID && !profileQuery.isError && !!profileQuery.data,
    retry: false,
  });

  // 3. Fetch Connections to determine state
  const connectionsQuery = useQuery({
    queryKey: ["connections"],
    queryFn: API.connections.list,
    enabled: !!targetId && isValidUUID,
  });

  // Determine relationship state
  const myConnection = connectionsQuery.data?.find(
    (c) =>
      (c.user_a_id === user?.id && c.user_b_id === targetId) ||
      (c.user_b_id === user?.id && c.user_a_id === targetId)
  );

  let relState: "none" | "pending_out" | "pending_in" | "accepted" | "blocked" | "removed" = "none";
  if (myConnection) {
    if (myConnection.status === "pending") {
      relState = myConnection.initiated_by === user?.id ? "pending_out" : "pending_in";
    } else if (myConnection.status === "accepted") {
      relState = "accepted";
    } else if (myConnection.status === "blocked") {
      relState = "blocked";
    } else if (myConnection.status === "declined" || myConnection.status === "removed") {
      relState = "none";
    }
  }

  // Mutations
  const connectMutation = useMutation({
    mutationFn: () => API.connections.create(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  const transitionMutation = useMutation({
    mutationFn: (action: "accept" | "decline" | "block" | "remove") => {
      if (!myConnection) throw new Error("No active connection ID");
      return API.connections.transition(myConnection.id, action);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });

  const handleCreateChat = async () => {
    try {
      const conv = await API.conversations.createOrGetDirect(targetId);
      navigate(`/chat/${conv.id}`);
    } catch (err: any) {
      alert(err.message || "Failed to start direct conversation");
    }
  };

  const handleLookupSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = lookupId.trim();
    if (!cleanId) {
      setValidationError("Please enter a User ID.");
      return;
    }
    if (!UUID_REGEX.test(cleanId)) {
      setValidationError("Please enter a valid UUID format (e.g. 58b57ed8-6824-47e5-abf6-57fd42584654).");
      return;
    }
    setValidationError(null);
    navigate(`/people/${cleanId}`);
  };

  // If no target ID is in the URL or invalid UUID format -> Render Directory + Lookup Form
  if (!targetId || !isValidUUID) {
    const otherUsers = (discoverableUsersQuery.data || []).filter((u) => u.id !== user?.id);

    return (
      <div style={{ maxWidth: "680px", margin: "1.5rem auto" }}>
        {/* Discoverable People Directory */}
        <div style={{ padding: "1.5rem", background: "#fff", border: "1px solid #d9d9d9", borderRadius: "6px", marginBottom: "1.5rem" }}>
          <h3 style={{ marginTop: 0 }}>👥 Discoverable Users Directory</h3>
          <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Click on any discoverable person below to view their profile, safe astrology placements, and connect:
          </p>

          {discoverableUsersQuery.isLoading ? (
            <div style={{ color: "#888", fontSize: "0.9rem" }}>Loading discoverable users...</div>
          ) : otherUsers.length === 0 ? (
            <div style={{ padding: "1rem", background: "#fafafa", borderRadius: "4px", color: "#666", fontSize: "0.9rem" }}>
              No other discoverable users registered in your local database yet. You can register a second test user in an incognito window or use the manual ID lookup below.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {otherUsers.map((u) => (
                <div
                  key={u.id}
                  style={{
                    padding: "0.9rem 1rem",
                    border: "1px solid #e8e8e8",
                    borderRadius: "6px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    backgroundColor: "#fafafa",
                  }}
                >
                  <div>
                    <strong>{u.display_name || "Anonymous User"}</strong>
                    <div style={{ fontSize: "0.75rem", color: "#888", marginTop: "0.1rem" }}>
                      ID: <code>{u.id}</code>
                    </div>
                    {u.city && <span style={{ fontSize: "0.8rem", color: "#555" }}>📍 {u.city}</span>}
                  </div>
                  <button
                    onClick={() => navigate(`/people/${u.id}`)}
                    style={{
                      padding: "0.4rem 0.9rem",
                      background: "#1890ff",
                      color: "#fff",
                      border: "none",
                      borderRadius: "4px",
                      fontWeight: "bold",
                      cursor: "pointer",
                      fontSize: "0.85rem",
                    }}
                  >
                    View Profile →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Manual ID Lookup Box */}
        <div style={{ padding: "1.5rem", background: "#fff", border: "1px solid #d9d9d9", borderRadius: "6px" }}>
          <h4 style={{ marginTop: 0, marginBottom: "0.5rem" }}>🔍 Manual UUID Lookup</h4>
          <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Paste a specific user's 36-character UUID:
          </p>

          {targetId && !isValidUUID && (
            <div style={{ padding: "0.75rem", marginBottom: "1rem", background: "#fff2f0", border: "1px solid #ffccc7", borderRadius: "4px", color: "#cf1322", fontSize: "0.85rem" }}>
              ❌ <strong>Invalid ID Format:</strong> "<code>{targetId}</code>" is not a valid UUID.
            </div>
          )}

          {validationError && (
            <div style={{ padding: "0.75rem", marginBottom: "1rem", background: "#fff2f0", border: "1px solid #ffccc7", borderRadius: "4px", color: "#cf1322", fontSize: "0.85rem" }}>
              ⚠️ {validationError}
            </div>
          )}

          <form onSubmit={handleLookupSubmit} style={{ display: "flex", gap: "0.5rem" }}>
            <input
              type="text"
              required
              value={lookupId}
              onChange={(e) => {
                setLookupId(e.target.value);
                setValidationError(null);
              }}
              placeholder="e.g. 58b57ed8-6824-47e5-abf6-57fd42584654"
              style={{ flex: 1, padding: "0.6rem", border: "1px solid #d9d9d9", borderRadius: "4px" }}
            />
            <button
              type="submit"
              style={{
                padding: "0.6rem 1.2rem",
                background: "#1890ff",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              Open Profile
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (profileQuery.isLoading) return <LoadingState message="Loading person profile..." />;
  if (profileQuery.error) {
    const err = profileQuery.error as any;
    if (err.statusCode === 404 || err.statusCode === 422) {
      return (
        <div>
          <PrivacySafeNotFoundState />
          <div style={{ textAlign: "center", marginTop: "1rem" }}>
            <Link to="/people" style={{ color: "#1890ff", fontWeight: "bold" }}>
              ← Return to People Directory
            </Link>
          </div>
        </div>
      );
    }
    return <ErrorState error={profileQuery.error as Error} />;
  }

  const profile = profileQuery.data;
  const astro = astroQuery.data;

  return (
    <div>
      <div style={{ marginBottom: "1rem" }}>
        <Link to="/people" style={{ textDecoration: "none", color: "#1890ff", fontSize: "0.85rem" }}>
          ← Back to People Directory
        </Link>
      </div>

      <div style={{ padding: "1.5rem", border: "1px solid #e8e8e8", borderRadius: "6px", backgroundColor: "#fff", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h2 style={{ margin: 0 }}>{profile?.display_name || "Anonymous Person"}</h2>
            <div style={{ color: "#666", fontSize: "0.9rem", marginTop: "0.2rem" }}>
              {profile?.city && <span>📍 {profile.city}</span>}
              {profile?.occupation && <span style={{ marginLeft: "1rem" }}>💼 {profile.occupation}</span>}
            </div>
            {profile?.bio && <p style={{ marginTop: "0.8rem", color: "#444" }}>{profile.bio}</p>}
          </div>

          {/* Relationship Action Controls */}
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
            {relState === "none" && (
              <button
                onClick={() => connectMutation.mutate()}
                disabled={connectMutation.isPending}
                style={{ padding: "0.5rem 1rem", background: "#1890ff", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
              >
                {connectMutation.isPending ? "Connecting..." : "Connect"}
              </button>
            )}

            {relState === "pending_out" && (
              <div style={{ padding: "0.4rem 0.8rem", background: "#fff7e6", border: "1px solid #ffd591", borderRadius: "4px", color: "#d46b08", fontSize: "0.85rem" }}>
                ⏳ Connection Request Pending
              </div>
            )}

            {relState === "pending_in" && (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <button
                  onClick={() => transitionMutation.mutate("accept")}
                  style={{ padding: "0.4rem 0.8rem", background: "#52c41a", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                >
                  Accept
                </button>
                <button
                  onClick={() => transitionMutation.mutate("decline")}
                  style={{ padding: "0.4rem 0.8rem", background: "#f5222d", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                >
                  Decline
                </button>
              </div>
            )}

            {relState === "accepted" && (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Link
                  to={`/compare/${targetId}`}
                  style={{ padding: "0.5rem 1rem", background: "#722ed1", color: "#fff", textDecoration: "none", borderRadius: "4px", fontWeight: "bold", fontSize: "0.85rem" }}
                >
                  🔮 Compare Synastry
                </Link>
                <button
                  onClick={handleCreateChat}
                  style={{ padding: "0.5rem 1rem", background: "#1890ff", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", fontSize: "0.85rem" }}
                >
                  💬 Chat
                </button>
                <button
                  onClick={() => transitionMutation.mutate("remove")}
                  style={{ padding: "0.5rem 0.8rem", background: "#f5f5f5", color: "#666", border: "1px solid #d9d9d9", borderRadius: "4px", cursor: "pointer", fontSize: "0.8rem" }}
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Public Safe Derived Astrology Placements */}
      {astro && (
        <div>
          <h3>Public Astrological Placements</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
            <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "4px", backgroundColor: "#fff" }}>
              <div style={{ color: "#888", fontSize: "0.8rem" }}>Sun Sign</div>
              <div style={{ fontSize: "1.3rem", fontWeight: "bold" }}>☀️ {astro.sun_sign}</div>
            </div>

            <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "4px", backgroundColor: "#fff" }}>
              <div style={{ color: "#888", fontSize: "0.8rem" }}>Moon Sign</div>
              <div style={{ fontSize: "1.3rem", fontWeight: "bold" }}>🌙 {astro.moon_sign}</div>
            </div>

            <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "4px", backgroundColor: "#fff" }}>
              <div style={{ color: "#888", fontSize: "0.8rem" }}>Ascendant Sign</div>
              <div style={{ fontSize: "1.3rem", fontWeight: "bold" }}>
                🌅 {astro.ascendant_sign || <span style={{ color: "#999", fontSize: "0.9rem" }}>Unknown</span>}
              </div>
            </div>

            <div style={{ padding: "1rem", border: "1px solid #d9d9d9", borderRadius: "4px", backgroundColor: "#fff" }}>
              <div style={{ color: "#888", fontSize: "0.8rem" }}>Dominant Element & Modality</div>
              <div style={{ fontSize: "1.1rem", fontWeight: "bold" }}>🔥 {astro.element_primary} / ⚡ {astro.modality_primary}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
