"""
Interpretation Contract & Content Layer Data Models for Jester (Architecture V2).
Defines structured contracts, multi-asset content lifecycle entities,
voice taxonomies, and user-facing resolved responses.
"""
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

SignalContext = Literal[
    "relationship",
    "friendship",
    "business",
    "daily_energy",
    "deep_analysis",
    "discovery",
    "profile",
    "onboarding",
    "self",
    "natal",
]


ContentStatus = Literal[
    "draft",
    "ai_draft",
    "review",
    "approved",
    "experimental",
    "winner",
    "archived",
    "not_reviewed",  # Legacy status alias
]


class InterpretationSignal(BaseModel):
    category: str
    type: str
    strength: float = Field(ge=0.0, le=1.0)


class InterpretationMeaning(BaseModel):
    type: str
    intensity: str = "high"
    human_meaning: list[str] = Field(default_factory=list)


class InterpretationVoice(BaseModel):
    tone: str = "witty"
    sarcasm: str = "light"
    warmth: str = "high"
    directness: str = "high"
    no_astrology_jargon: bool = True


class InterpretationOutput(BaseModel):
    format: str = "short_insight"
    max_sentences: int = 2
    language: str = "ka"


class InterpretationConstraints(BaseModel):
    must_not: list[str] = Field(
        default_factory=lambda: [
            "predict the future",
            "claim certainty about another person's feelings",
            "use astrology jargon",
            "sound generic or horoscope-like",
            "humiliate or degrade user",
        ]
    )


class InterpretationContract(BaseModel):
    """
    Stable structured contract decoupling astronomical signals from human wording.
    Defines meaning and constraints without hardcoding copy.
    """
    interpretation_id: str
    context: str = "relationship"
    signal: InterpretationSignal
    meaning: InterpretationMeaning
    voice: InterpretationVoice = Field(default_factory=InterpretationVoice)
    output: InterpretationOutput = Field(default_factory=InterpretationOutput)
    constraints: InterpretationConstraints = Field(default_factory=InterpretationConstraints)


class ContentAsset(BaseModel):
    """
    First-class Content Asset representing an individual wording variant.
    One interpretation can have dozens or hundreds of content assets across
    locales, tones, contexts, and variants.
    """
    model_config = ConfigDict(from_attributes=True)

    asset_id: str
    interpretation_id: str
    locale: str = "ka"
    context: str = "relationship"
    tone: str = "witty"
    persona: str = "jester"
    text: str
    status: ContentStatus = "ai_draft"
    version: int = 1
    priority: int = 50
    source: str = "ai"  # "ai" | "copywriter" | "system"
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    archived: bool = False
    experiment_id: str | None = None
    variant_key: str | None = None
    weight: float = 1.0
    internal_notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContentSlot(BaseModel):
    """Legacy slot kept for backward compatibility."""
    text: str | None = None
    status: ContentStatus = "not_reviewed"
    author: str | None = None
    updated_at: datetime | None = None


class ContentRecord(BaseModel):
    """
    Legacy content record tracking AI Draft vs Copywriter Final approval status.
    Kept for backward compatibility with existing V1 consumers.
    """
    interpretation_id: str
    meaning: dict[str, Any]
    draft: ContentSlot
    final: ContentSlot = Field(default_factory=ContentSlot)


class ResolvedInterpretation(BaseModel):
    """
    User-facing resolved interpretation delivered to client applications.
    Preserves id and language for backward compatibility while surfacing
    rich content asset metadata.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    content_status: ContentStatus = "ai_draft"
    language: str = "ka"
    content_asset_id: str | None = None
    context: str = "relationship"
    locale: str = "ka"
    tone: str = "witty"
    persona: str = "jester"
    variant_key: str | None = None


class ContentUpdatePayload(BaseModel):
    """Legacy update payload kept for backward compatibility."""
    text: str
    status: ContentStatus = "approved"
    author: str | None = "copywriter"


class ContentAssetCreatePayload(BaseModel):
    """Payload for creating a new content asset."""
    text: str
    locale: str = "ka"
    context: str = "relationship"
    tone: str = "witty"
    persona: str = "jester"
    status: ContentStatus = "approved"
    priority: int = 50
    variant_key: str | None = None
    author: str | None = "copywriter"
    tags: list[str] = Field(default_factory=list)
    internal_notes: str | None = None
    experiment_id: str | None = None
    weight: float = 1.0


class ContentAssetUpdatePayload(BaseModel):
    """Payload for patching an existing content asset."""
    text: str | None = None
    status: ContentStatus | None = None
    locale: str | None = None
    context: str | None = None
    tone: str | None = None
    persona: str | None = None
    priority: int | None = None
    variant_key: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    archived: bool | None = None
    internal_notes: str | None = None
    experiment_id: str | None = None
    weight: float | None = None


class ContentInventoryItem(BaseModel):
    """Machine-readable inventory record for copywriter / CMS status."""
    interpretation_id: str
    context: str
    meaning_type: str
    available_locales: list[str]
    available_tones: list[str]
    total_assets: int
    approved_assets: int
    ai_draft_assets: int
    archived_assets: int
    source_signal: str
    status: str


class JesterMessageRequest(BaseModel):
    context: str
    target_user_id: str | None = None
    user_prompt: str | None = None


class JesterMessageResponse(BaseModel):
    message: str
    tone: str = "smart_warm_ironic"


class DeepAnalysisBlock(BaseModel):
    interpretation_id: str
    dimension: str
    resolved_text: str
    evidence_aspects: list[str] = Field(default_factory=list)
    content_status: ContentStatus = "ai_draft"
    content_asset_id: str | None = None
    tone: str = "witty"


class DeepAnalysisPayload(BaseModel):
    primary_interpretation: ResolvedInterpretation
    blocks: list[DeepAnalysisBlock] = Field(default_factory=list)
    overall_score: float
    data_confidence: float = 1.0


