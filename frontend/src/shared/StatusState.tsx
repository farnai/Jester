import React from "react";

export const LoadingState: React.FC<{ message?: string }> = ({
  message = "Loading...",
}) => (
  <div style={{ padding: "2rem", textAlign: "center", color: "#666" }}>
    <div style={{ marginBottom: "0.5rem", fontWeight: "bold" }}>⏳ {message}</div>
  </div>
);

export const ErrorState: React.FC<{
  error?: string | Error | null;
  onRetry?: () => void;
}> = ({ error, onRetry }) => {
  const msg =
    typeof error === "string"
      ? error
      : error?.message || "An unexpected error occurred.";

  return (
    <div
      style={{
        padding: "1.5rem",
        margin: "1rem 0",
        border: "1px solid #ff4d4f",
        backgroundColor: "#fff1f0",
        borderRadius: "4px",
        color: "#cf1322",
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
        ⚠️ Error: {msg}
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            marginTop: "0.5rem",
            padding: "0.4rem 0.8rem",
            cursor: "pointer",
            background: "#cf1322",
            color: "#fff",
            border: "none",
            borderRadius: "3px",
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ title, description, actionLabel, onAction }) => (
  <div
    style={{
      padding: "2.5rem 1rem",
      textAlign: "center",
      border: "1px dashed #ccc",
      borderRadius: "4px",
      margin: "1rem 0",
      backgroundColor: "#fafafa",
    }}
  >
    <div style={{ fontWeight: "bold", fontSize: "1.1rem", marginBottom: "0.4rem" }}>
      {title}
    </div>
    {description && (
      <div style={{ color: "#666", marginBottom: "1rem" }}>{description}</div>
    )}
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        style={{
          padding: "0.5rem 1rem",
          cursor: "pointer",
          background: "#1890ff",
          color: "#fff",
          border: "none",
          borderRadius: "3px",
        }}
      >
        {actionLabel}
      </button>
    )}
  </div>
);

export const PrivacySafeNotFoundState: React.FC = () => (
  <div style={{ padding: "2rem", textAlign: "center" }}>
    <h3>Resource Not Found</h3>
    <p style={{ color: "#666" }}>
      The requested profile or connection is unavailable.
    </p>
  </div>
);
