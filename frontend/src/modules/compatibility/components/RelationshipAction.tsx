import React from "react";
import { Card, Button, Badge } from "../../../shared/ui";

interface RelationshipActionProps {
  targetName: string;
  relState: "none" | "pending_out" | "pending_in" | "accepted" | "blocked";
  onConnect: () => void;
  onAccept: () => void;
  onDecline: () => void;
  onOpenChat: () => void;
  isConnecting?: boolean;
  isTransitioning?: boolean;
}

export const RelationshipAction: React.FC<RelationshipActionProps> = ({
  targetName,
  relState,
  onConnect,
  onAccept,
  onDecline,
  onOpenChat,
  isConnecting = false,
  isTransitioning = false,
}) => {
  if (relState === "blocked") {
    return null;
  }

  return (
    <Card
      padded
      style={{
        backgroundColor: "#ffffff",
        border: "1px solid #e2e8f0",
        borderRadius: "16px",
        padding: "1.5rem",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        boxShadow: "0 2px 8px rgba(15, 23, 42, 0.04)",
      }}
    >
      {/* State: none (Unconnected) */}
      {relState === "none" && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
              დაკავშირება {targetName}-თან
            </div>
            <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
              ინსაითი გაძლევთ საუბრის დასაწყისს — გაუგზავნეთ მოწვევა.
            </p>
          </div>

          <Button
            variant="brand"
            size="md"
            isLoading={isConnecting}
            onClick={onConnect}
            icon={<span>🤝</span>}
          >
            დაკავშირება
          </Button>
        </div>
      )}

      {/* State: pending_out (Request Sent) */}
      {relState === "pending_out" && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
              მოწვევა გაგზავნილია
            </div>
            <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
              თქვენი მოთხოვნა {targetName}-ის პასუხის მოლოდინშია.
            </p>
          </div>

          <Badge variant="warning" size="md">
            ⏳ მოლოდინში
          </Badge>
        </div>
      )}

      {/* State: pending_in (Incoming Request) */}
      {relState === "pending_in" && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
              {targetName} გიწვევთ დასაკავშირებლად
            </div>
            <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
              დათანხმდით მოწვევას პირდაპირი საუბრის დასაწყებად.
            </p>
          </div>

          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              variant="outline"
              size="md"
              isLoading={isTransitioning}
              onClick={onDecline}
            >
              უარყოფა
            </Button>
            <Button
              variant="brand"
              size="md"
              isLoading={isTransitioning}
              onClick={onAccept}
            >
              მოწვევის მიღება
            </Button>
          </div>
        </div>
      )}

      {/* State: accepted (Connected) */}
      {relState === "accepted" && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <div style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
              თქვენ დაკავშირებული ხართ
            </div>
            <p style={{ margin: "0.2rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
              გადადით პირდაპირ ჩატში და გაუზიარეთ თქვენი აზრი.
            </p>
          </div>

          <Button
            variant="brand"
            size="md"
            onClick={onOpenChat}
            icon={<span>💬</span>}
          >
            ჩატის გახსნა
          </Button>
        </div>
      )}
    </Card>
  );
};
