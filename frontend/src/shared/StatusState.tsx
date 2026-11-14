import React from "react";
import { Button } from "./ui/Button";

export const LoadingState: React.FC<{ message?: string }> = ({
  message = "იტვირთება / Loading...",
}) => (
  <div
    style={{
      padding: "3rem 1.5rem",
      textAlign: "center",
      color: "var(--jester-color-status-loading-text, #64748b)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: "0.75rem",
    }}
  >
    <div style={{ fontSize: "1.75rem", animation: "pulse 1.5s infinite" }}>⏳</div>
    <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--jester-color-status-loading-title, #475569)" }}>
      {message}
    </div>
  </div>
);

export const ErrorState: React.FC<{
  error?: string | Error | null;
  onRetry?: () => void;
}> = ({ error, onRetry }) => {
  const msg =
    typeof error === "string"
      ? error
      : error?.message || "დაფიქსირდა მოულოდნელი შეცდომა.";

  return (
    <div
      style={{
        padding: "1.5rem",
        margin: "1rem 0",
        border: "1px solid var(--jester-color-status-danger-border, #fecaca)",
        backgroundColor: "var(--jester-color-status-danger-bg, #fef2f2)",
        borderRadius: "12px",
        color: "var(--jester-color-status-danger-text, #b91c1c)",
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
      }}
    >
      <div style={{ fontWeight: 700, fontSize: "0.95rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <span>⚠️</span> შეცდომა (Error)
      </div>
      <div style={{ fontSize: "0.9rem", color: "var(--jester-color-status-danger-detail, #991b1b)" }}>{msg}</div>
      {onRetry && (
        <div style={{ marginTop: "0.5rem" }}>
          <Button variant="danger" size="sm" onClick={onRetry}>
            🔄 განმეორება / Retry
          </Button>
        </div>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: string;
}> = ({ title, description, actionLabel, onAction, icon = "📭" }) => (
  <div
    style={{
      padding: "3rem 1.5rem",
      textAlign: "center",
      border: "1px dashed var(--jester-color-status-empty-border, #cbd5e1)",
      borderRadius: "12px",
      margin: "1.5rem 0",
      backgroundColor: "var(--jester-color-status-empty-bg, #f8fafc)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "0.5rem",
    }}
  >
    <div style={{ fontSize: "2.5rem", marginBottom: "0.25rem" }}>{icon}</div>
    <div style={{ fontWeight: 700, fontSize: "1.1rem", color: "var(--jester-color-status-empty-title, #1e293b)" }}>
      {title}
    </div>
    {description && (
      <div style={{ color: "var(--jester-color-status-empty-text, #64748b)", fontSize: "0.9rem", maxWidth: "400px", lineHeight: 1.5 }}>
        {description}
      </div>
    )}
    {actionLabel && onAction && (
      <div style={{ marginTop: "1rem" }}>
        <Button variant="brand" size="md" onClick={onAction}>
          {actionLabel}
        </Button>
      </div>
    )}
  </div>
);

export const PrivacySafeNotFoundState: React.FC<{
  message?: string;
}> = ({
  message = "მოთხოვნილი გვერდი ან პროფილი მიუწვდომელია / Resource not found or unavailable.",
}) => (
  <div
    style={{
      padding: "3.5rem 1.5rem",
      textAlign: "center",
      border: "1px solid var(--jester-primitive-slate-200, #e2e8f0)",
      borderRadius: "12px",
      backgroundColor: "var(--jester-color-surface, #ffffff)",
      margin: "1.5rem 0",
    }}
  >
    <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🔒</div>
    <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--jester-primitive-slate-800, #1e293b)" }}>რესურსი მიუწვდომელია</h3>
    <p style={{ color: "var(--jester-primitive-slate-500, #64748b)", fontSize: "0.9rem", margin: 0 }}>
      {message}
    </p>
  </div>
);
