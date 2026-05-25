from datetime import date

from app.core.config import Settings
from app.models.schemas import ExtractedClaim, ExtractedClaimSet
from app.services.gemini_client import GeminiStructuredClient


class ClaimExtractor:
    """Extract audit-worthy claims from source text using Gemini."""

    def __init__(self, settings: Settings, gemini: GeminiStructuredClient):
        self._settings = settings
        self._gemini = gemini

    async def extract(self, document_text: str) -> list[ExtractedClaim]:
        prompt = f"""
You are the extraction stage of an evidence-first fact-checking system.
Today's date is {date.today().isoformat()}.

Read the PDF text below and return at most {self._settings.max_claims} distinct claims that can
be checked against independent, public web sources. Prioritize claims likely to matter in an
audit: numerical statistics, percentages, money or market sizes, dates, product capabilities,
scientific measurements, company results, rankings, and current-world claims.

Rules:
- Copy each claim faithfully; do not correct it or assume it is true.
- Ignore opinions, slogans, predictions without measurable assertions, and duplicate restatements.
- Include the page number derived from the [Page N] marker where possible.
- Include enough context to identify the entity and time period.
- Write a focused search query that seeks an authoritative confirmation or contradiction.
- A claim can be false or outdated; still extract it exactly for verification.

PDF TEXT:
{document_text}
"""
        response = await self._gemini.generate_json(prompt, ExtractedClaimSet)

        deduplicated: list[ExtractedClaim] = []
        seen: set[str] = set()
        for claim in response.claims[: self._settings.max_claims]:
            normalized = " ".join(claim.claim.lower().split())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            claim.id = f"claim-{len(deduplicated) + 1:02d}"
            claim.claim = claim.claim.strip()
            claim.context = claim.context.strip()
            claim.search_query = claim.search_query.strip() or claim.claim
            deduplicated.append(claim)
        return deduplicated
