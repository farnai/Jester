import React, { useState } from "react";
import { supabase } from "../../../core/realtime/supabase";
import { Button } from "../../../shared/ui";

interface ProfilePhotoStepProps {
  userId: string;
  avatarUrl: string | null;
  onNext: (avatarUrl: string | null) => void;
  onSkip: () => void;
  onBack: () => void;
}

export const ProfilePhotoStep: React.FC<ProfilePhotoStepProps> = ({
  userId,
  avatarUrl,
  onNext,
  onSkip,
  onBack,
}) => {
  const [currentAvatar, setCurrentAvatar] = useState<string | null>(avatarUrl);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check size limit: 5MB
    if (file.size > 5 * 1024 * 1024) {
      setError("ფაილის ზომა არ უნდა აღემატებოდეს 5MB-ს.");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const cleanName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
      const filePath = `${userId}/${Date.now()}_${cleanName}`;

      const { data, error: uploadErr } = await supabase.storage
        .from("avatars")
        .upload(filePath, file, {
          cacheControl: "3600",
          upsert: true,
        });

      if (uploadErr) {
        throw uploadErr;
      }

      const { data: publicData } = supabase.storage.from("avatars").getPublicUrl(data.path);
      setCurrentAvatar(publicData.publicUrl);
    } catch (err: any) {
      console.error("Avatar upload error:", err);
      setError(err.message || "ფოტოს ატვირთვა ვერ მოხერხდა. სცადეთ თავიდან ან გამოტოვეთ.");
    } finally {
      setUploading(false);
    }
  };

  const handleContinue = (e: React.FormEvent) => {
    e.preventDefault();
    onNext(currentAvatar);
  };

  return (
    <form onSubmit={handleContinue} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h3 style={{ margin: "0 0 0.4rem 0", fontSize: "1.2rem", fontWeight: 700, color: "#0f172a" }}>
          7. პროფილის ფოტო (Profile Photo)
        </h3>
        <p style={{ margin: "0 0 1.25rem 0", color: "#64748b", fontSize: "0.875rem" }}>
          ატვირთეთ ფოტო, რათა სხვა ადამიანებმა შეძლონ თქვენი ამოცნობა (არასავალდებულო).
        </p>
      </div>

      {error && (
        <div
          style={{
            padding: "0.75rem",
            background: "#fff1f0",
            border: "1px solid #ff4d4f",
            borderRadius: "6px",
            color: "#cf1322",
            fontSize: "0.85rem",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {/* Avatar Preview / Placeholder */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1rem", margin: "1rem 0" }}>
        {currentAvatar ? (
          <img
            src={currentAvatar}
            alt="Profile Avatar"
            style={{
              width: "120px",
              height: "120px",
              borderRadius: "50%",
              objectFit: "cover",
              border: "3px solid #6366f1",
            }}
          />
        ) : (
          <div
            style={{
              width: "120px",
              height: "120px",
              borderRadius: "50%",
              background: "#f1f5f9",
              border: "2px dashed #cbd5e1",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "2rem",
              color: "#94a3b8",
            }}
          >
            👤
          </div>
        )}

        <div>
          <label
            style={{
              display: "inline-block",
              padding: "0.5rem 1rem",
              background: "#f8fafc",
              border: "1px solid #cbd5e1",
              borderRadius: "6px",
              cursor: uploading ? "not-allowed" : "pointer",
              fontSize: "0.875rem",
              fontWeight: 600,
              color: "#334155",
            }}
          >
            {uploading ? "იტვირთება..." : currentAvatar ? "ფოტოს შეცვლა" : "ფოტოს არჩევა"}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              disabled={uploading}
              onChange={handleFileChange}
              style={{ display: "none" }}
            />
          </label>
        </div>
      </div>

      <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
        <Button
          type="button"
          variant="secondary"
          size="lg"
          style={{ flex: 1 }}
          onClick={onBack}
        >
          ⬅️ უკან
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="lg"
          style={{ flex: 1 }}
          onClick={onSkip}
        >
          გამოტოვება (Skip)
        </Button>
        <Button
          type="submit"
          variant="brand"
          size="lg"
          style={{ flex: 1.5 }}
          disabled={uploading}
        >
          შემდეგი ➡️
        </Button>
      </div>
    </form>
  );
};
