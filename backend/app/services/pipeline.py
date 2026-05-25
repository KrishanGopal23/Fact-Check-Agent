from app.core.config import Settings
from app.models.schemas import (
    ClaimResult,
    DocumentInfo,
    ExtractedClaim,
    FactCheckResponse,
    ReportSummary,
)
from app.services.claim_extractor import ClaimExtractor
from app.services.gemini_client import GeminiStructuredClient
from app.services.pdf_extractor import PDFExtractor
from app.services.report_generator import ReportGenerator
from app.services.tavily_search import TavilySearchService
from app.services.verifier import ClaimVerifier


class FactCheckPipeline:
    """Application workflow composition root."""

    def __init__(self, settings: Settings):
        gemini = GeminiStructuredClient(settings)
        self.pdf = PDFExtractor()
        self.claims = ClaimExtractor(settings, gemini)
        self.verifier = ClaimVerifier(settings, gemini, TavilySearchService(settings))
        self.reports = ReportGenerator()
        self.settings = settings

    def read_pdf(self, content: bytes, filename: str) -> tuple[DocumentInfo, str]:
        return self.pdf.extract(content, filename, self.settings.max_document_chars)

    async def extract_claims(self, text: str) -> list[ExtractedClaim]:
        return await self.claims.extract(text)

    async def verify_claims(self, claims: list[ExtractedClaim]) -> tuple[list[ClaimResult], ReportSummary]:
        results = await self.verifier.verify_all(claims)
        return results, self.reports.summarize(results)

    async def run(self, content: bytes, filename: str) -> FactCheckResponse:
        document, text = self.read_pdf(content, filename)
        claims = await self.extract_claims(text)
        if not claims:
            return FactCheckResponse(
                document=document,
                claims=[],
                results=[],
                summary=self.reports.summarize([]),
            )
        results, summary = await self.verify_claims(claims)
        return FactCheckResponse(
            document=document,
            claims=claims,
            results=results,
            summary=summary,
        )
