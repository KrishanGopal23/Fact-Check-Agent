from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


ClaimCategory = Literal[
    "statistic",
    "date",
    "financial",
    "technical",
    "scientific",
    "market",
    "other",
]
Verdict = Literal[
    "VERIFIED",
    "INACCURATE",
    "FALSE",
    "MISLEADING",
    "OUTDATED",
    "INSUFFICIENT_EVIDENCE",
]


class DocumentInfo(BaseModel):
    filename: str
    pages: int
    characters: int
    truncated_for_analysis: bool = False


class UploadResponse(BaseModel):
    document: DocumentInfo
    text_preview: str


class ExtractedClaim(BaseModel):
    id: str = ""
    claim: str = Field(description="A precise, externally verifiable factual claim.")
    category: ClaimCategory = Field(description="The kind of fact expressed by the claim.")
    page_number: int | None = Field(
        default=None,
        description="The PDF page on which this claim appears, when identified.",
    )
    context: str = Field(
        default="",
        description="A short excerpt that helps disambiguate the claim.",
    )
    search_query: str = Field(
        default="",
        description="A focused web-search query for independently verifying this claim.",
    )


class ExtractedClaimSet(BaseModel):
    claims: list[ExtractedClaim]


class ExtractionResponse(BaseModel):
    document: DocumentInfo
    claims: list[ExtractedClaim]


class EvidenceSource(BaseModel):
    id: int
    title: str
    url: HttpUrl
    domain: str
    snippet: str
    relevance_score: float | None = None
    authority: Literal["primary", "reputable", "web"] = "web"


class VerificationDecision(BaseModel):
    verdict: Verdict = Field(description="The best-supported verdict from the supplied evidence.")
    confidence: int = Field(ge=0, le=100, description="Confidence justified by the evidence only.")
    explanation: str = Field(description="Brief evidence-based reasoning for the verdict.")
    corrected_fact: str | None = Field(
        default=None,
        description="A supported correction or current value when the original claim is not verified.",
    )
    supported_source_ids: list[int] = Field(
        default_factory=list,
        description="IDs of supplied evidence sources supporting this decision.",
    )


class IndexedVerificationDecision(VerificationDecision):
    claim_id: str = Field(description="The ID of the original claim being assessed.")


class VerificationDecisionSet(BaseModel):
    decisions: list[IndexedVerificationDecision]


class ClaimResult(BaseModel):
    claim: ExtractedClaim
    verdict: Verdict
    confidence: int
    explanation: str
    corrected_fact: str | None = None
    sources: list[EvidenceSource] = Field(default_factory=list)


class VerificationRequest(BaseModel):
    claims: list[ExtractedClaim] = Field(min_length=1, max_length=50)


class ReportSummary(BaseModel):
    total_claims: int
    verified: int
    inaccurate: int
    false: int
    misleading: int
    outdated: int
    insufficient_evidence: int
    average_confidence: int
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "UNDETERMINED"]
    narrative: str


class VerificationResponse(BaseModel):
    results: list[ClaimResult]
    summary: ReportSummary


class FactCheckResponse(VerificationResponse):
    document: DocumentInfo
    claims: list[ExtractedClaim]
