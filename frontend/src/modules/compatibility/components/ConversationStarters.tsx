import React, { useState } from "react";
import { Card, Button, Badge } from "../../../shared/ui";

interface ConversationStartersProps {
  bestTopics?: string[];
  conversationStarters?: string[];
  isConnected?: boolean;
  onSendToChat?: (starterText: string) => void;
}

export const TOPIC_LABELS: Record<string, string> = {
  // Canonical 16 topics (Section 17)
  ideas: "იდეები და ხედვები",
  philosophy: "ცხოვრებისეული ფილოსოფია",
  books: "წიგნები და ლიტერატურა",
  creative_work: "შემოქმედებითი პროექტები",
  travel: "მოგზაურობა და თავგადასავლები",
  adventure: "ახალი გამოცდილებები",
  fitness: "აქტიური ცხოვრება და სპორტი",
  ambition: "მიზნები და ამბიციები",
  art: "ვიზუალური ხელოვნება",
  music: "მუსიკა და ემოციური რიტმი",
  psychology: "ადამიანის ბუნება და ფსიქოლოგია",
  cinema: "კინო და ვიზუალური ისტორიები",
  architecture: "არქიტექტურა და ურბანისტიკა",
  food: "გასტრონომია და გემოები",
  design: "დიზაინი და ესთეტიკა",
  lifestyle: "ცხოვრების სტილი და რიტმი",

  // Legacy aliases to preserve backward compatibility
  creative_projects: "კრეატიული პროექტები",
  daily_habits: "ყოველდღიური რიტმი",
  books_and_ideas: "წიგნები და იდეები",
  career_ambitions: "კარიერა და მიზნები",
  shared_values: "საერთო ღირებულებები",
  art_and_culture: "ხელოვნება და კულტურა",
};

export function getTopicLabel(topic: string): string {
  const normalized = (topic || "").toLowerCase().trim();
  return TOPIC_LABELS[normalized] || TOPIC_LABELS[topic] || topic;
}

export const ConversationStarters: React.FC<ConversationStartersProps> = ({
  bestTopics = [],
  conversationStarters = [],
  isConnected = false,
  onSendToChat,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2500);
  };

  const hasTopics = bestTopics.length > 0;
  const hasStarters = conversationStarters.length > 0;

  if (!hasTopics && !hasStarters) {
    return null;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div>
        <h2
          style={{
            margin: "0 0 0.25rem 0",
            fontSize: "1.15rem",
            fontWeight: 700,
            color: "#0f172a",
          }}
        >
          საუბრის იდეები
        </h2>
        <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b" }}>
          ინსაითი, რომელიც შეგიძლიათ გამოიყენოთ დიალოგის დასაწყებად.
        </p>
      </div>

      {/* Shared Topics Pills */}
      {hasTopics && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
          {bestTopics.map((topic, i) => {
            const label = getTopicLabel(topic);
            return (
              <Badge
                key={i}
                variant="default"
                size="md"
                style={{
                  backgroundColor: "#f8fafc",
                  border: "1px solid #e2e8f0",
                  color: "#334155",
                  fontWeight: 500,
                }}
              >
                💬 {label}
              </Badge>
            );
          })}
        </div>
      )}

      {/* Actionable Conversation Starters */}
      {hasStarters && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {conversationStarters.slice(0, 3).map((starter, i) => (
            <Card
              key={i}
              padded
              style={{
                backgroundColor: "#ffffff",
                border: "1px solid #f1f5f9",
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
              }}
            >
              <div
                style={{
                  fontSize: "0.95rem",
                  color: "#1e293b",
                  lineHeight: 1.55,
                  fontStyle: "italic",
                }}
              >
                „{starter}“
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  alignItems: "center",
                  gap: "0.5rem",
                }}
              >
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(starter, i)}
                  style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}
                >
                  {copiedIndex === i ? "დაკოპირდა! ✓" : "📋 ტექსტის კოპირება"}
                </Button>

                {isConnected && onSendToChat && (
                  <Button
                    variant="brand"
                    size="sm"
                    onClick={() => onSendToChat(starter)}
                    style={{ fontSize: "0.8rem", padding: "0.35rem 0.75rem" }}
                  >
                    💬 ჩატში გადატანა
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
