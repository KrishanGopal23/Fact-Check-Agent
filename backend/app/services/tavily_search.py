from tavily import AsyncTavilyClient

from app.core.config import Settings
from app.models.schemas import EvidenceSource, ExtractedClaim
from app.utils.helpers import (
    PipelineError,
    authority_label,
    compact_snippet,
    safe_web_url,
    source_domain,
)


class TavilySearchService:
    """Retrieve live evidence for a claim and normalize citation metadata."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: AsyncTavilyClient | None = None

    def _get_client(self) -> AsyncTavilyClient:
        if not self._settings.tavily_is_configured:
            raise PipelineError(
                "Set a real TAVILY_API_KEY in backend/.env.",
                status_code=503,
                code="invalid_tavily_configuration",
            )
        if self._client is None:
            self._client = AsyncTavilyClient(api_key=self._settings.tavily_api_key)
        return self._client

    async def search(self, claim: ExtractedClaim) -> list[EvidenceSource]:
        try:
            response = await self._get_client().search(
                query=claim.search_query or claim.claim,
                topic="general",
                search_depth="advanced",
                max_results=self._settings.max_search_results,
                include_answer=False,
                include_raw_content=False,
            )
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(
                "Live web search is currently unavailable.",
                status_code=502,
                code="tavily_error",
            ) from exc

        evidence: list[EvidenceSource] = []
        for item in response.get("results", []):
            url = safe_web_url(item.get("url"))
            if not url:
                continue
            domain = source_domain(url)
            evidence.append(
                EvidenceSource(
                    id=len(evidence) + 1,
                    title=(item.get("title") or domain or "Web evidence").strip(),
                    url=url,
                    domain=domain,
                    snippet=compact_snippet(item.get("content")),
                    relevance_score=item.get("score"),
                    authority=authority_label(domain),
                )
            )

        evidence.sort(
            key=lambda source: (
                {"primary": 0, "reputable": 1, "web": 2}[source.authority],
                -(source.relevance_score or 0),
            )
        )
        for index, source in enumerate(evidence, start=1):
            source.id = index
        return evidence
