import React, { useState } from "react";
import { Card, Button, Badge } from "../../../shared/ui";
import { DeepAnalysisPayload } from "../../../core/api/types";

interface DeepAnalysisSectionProps {
  deepAnalysis?: DeepAnalysisPayload | null;
}

const DIMENSION_TRANSLATIONS: Record<string, string> = {
  harmony: "ჰარმონია & კომფორტი",
  emotional: "ემოციური თანხვედრა",
  attraction: "ქიმია & მიზიდულობა",
  communication: "ინტელექტუალური დიალოგი",
  growth: "პიროვნული ტრანსფორმაცია",
  stability: "სტაბილურობა & ნდობა",
  connection: "კავშირის არსი",
  notice: "განსხვავებები & ყურადღება",
};

export const DeepAnalysisSection: React.FC<DeepAnalysisSectionProps> = ({
  deepAnalysis,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const blocks = deepAnalysis?.blocks || [];

  if (blocks.length === 0) {
    return null;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
      {/* Section Header with Progressive Disclosure Toggle */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "0.5rem",
        }}
      >
        <div>
          <h2
            style={{
              margin: "0 0 0.2rem 0",
              fontSize: "1.15rem",
              fontWeight: 700,
              color: "#0f172a",
            }}
          >
            უფრო ღრმად
          </h2>
          <p style={{ margin: 0, fontSize: "0.88rem", color: "#64748b" }}>
            დეტალური თემატური ანალიზი თქვენი ურთიერთობის შესახებ.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExpanded((prev) => !prev)}
          style={{ fontSize: "0.85rem" }}
        >
          {isExpanded
            ? "ჩაკეცვა ↑"
            : `დეტალური ანალიზი (${blocks.length}) ↓`}
        </Button>
      </div>

      {/* Expanded Narrative Blocks */}
      {isExpanded && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "0.25rem" }}>
          {blocks.map((block, idx) => {
            const dimensionLabel =
              DIMENSION_TRANSLATIONS[block.dimension.toLowerCase()] ||
              "თემატური ანალიზი";

            return (
              <Card
                key={idx}
                padded
                style={{
                  backgroundColor: "#ffffff",
                  border: "1px solid #f1f5f9",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.02)",
                }}
              >
                <div style={{ marginBottom: "0.4rem" }}>
                  <Badge variant="default" size="sm" style={{ color: "#6366f1", backgroundColor: "#eef2ff" }}>
                    {dimensionLabel}
                  </Badge>
                </div>

                <p
                  style={{
                    margin: 0,
                    fontSize: "0.92rem",
                    color: "#334155",
                    lineHeight: 1.6,
                  }}
                >
                  {block.resolved_text}
                </p>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
