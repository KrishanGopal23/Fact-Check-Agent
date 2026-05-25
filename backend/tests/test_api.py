import asyncio

import httpx
import pymupdf
import pytest
from google.genai.errors import ClientError

from app.core.config import Settings
from app.main import app
from app.models.schemas import (
    EvidenceSource,
    ExtractedClaim,
    IndexedVerificationDecision,
    VerificationDecisionSet,
)
from app.services.gemini_client import GeminiStructuredClient
from app.services.pdf_extractor import PDFExtractor
from app.services.report_generator import ReportGenerator
from app.services.verifier import ClaimVerifier
from app.utils.helpers import PipelineError


def make_pdf(text: str) -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


async def request(method: str, url: str, **kwargs) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, url, **kwargs)


def test_health_is_available_without_api_keys() -> None:
    response = asyncio.run(request("GET", "/health"))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_settings_reports_api_key_entered_as_model_name() -> None:
    settings = Settings(
        _env_file=None,
        gemini_api_key="your_gemini_api_key",
        gemini_model="AIza-not-a-model-name",
        tavily_api_key="configured-tavily-value",
    )

    assert settings.gemini_is_configured is False
    assert len(settings.configuration_issues) == 2


def test_upload_extracts_pdf_text_without_external_services() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/upload",
            files={"file": ("sample.pdf", make_pdf("Revenue rose 40% in 2024."), "application/pdf")},
        )
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document"]["pages"] == 1
    assert "Revenue rose 40%" in payload["text_preview"]


def test_upload_rejects_non_pdf_content() -> None:
    response = asyncio.run(
        request(
            "POST",
            "/upload",
            files={"file": ("sample.pdf", b"not really a pdf", "application/pdf")},
        )
    )

    assert response.status_code == 422
    assert response.json()["code"] == "invalid_pdf"


def test_pdf_extractor_rejects_blank_text_document() -> None:
    document = pymupdf.open()
    document.new_page()
    content = document.tobytes()
    document.close()

    try:
        PDFExtractor().extract(content, "blank.pdf", max_characters=5_000)
    except Exception as exc:
        assert getattr(exc, "code") == "no_text"
    else:
        raise AssertionError("Expected blank document extraction to fail.")


def test_report_summary_flags_material_corrections() -> None:
    from app.models.schemas import ClaimResult

    claim = ExtractedClaim(id="claim-01", claim="The value is 10.", category="statistic")
    result = ClaimResult(
        claim=claim,
        verdict="FALSE",
        confidence=95,
        explanation="An official source reports a different value.",
    )

    summary = ReportGenerator().summarize([result])

    assert summary.false == 1
    assert summary.risk_level == "HIGH"


def test_verifier_batches_multiple_claims_into_one_gemini_call() -> None:
    class FakeSearch:
        async def search(self, claim: ExtractedClaim) -> list[EvidenceSource]:
            return [
                EvidenceSource(
                    id=1,
                    title="Official evidence",
                    url="https://example.gov/report",
                    domain="example.gov",
                    snippet=f"Evidence about {claim.id}.",
                    authority="primary",
                )
            ]

    class FakeGemini:
        calls = 0

        async def generate_json(self, prompt: str, response_model):
            self.calls += 1
            assert "claim-01" in prompt and "claim-02" in prompt
            assert response_model is VerificationDecisionSet
            return VerificationDecisionSet(
                decisions=[
                    IndexedVerificationDecision(
                        claim_id="claim-01",
                        verdict="VERIFIED",
                        confidence=91,
                        explanation="Supported.",
                        supported_source_ids=[1],
                    ),
                    IndexedVerificationDecision(
                        claim_id="claim-02",
                        verdict="OUTDATED",
                        confidence=88,
                        explanation="Superseded.",
                        corrected_fact="The current figure is 12.",
                        supported_source_ids=[1],
                    ),
                ]
            )

    claims = [
        ExtractedClaim(id="claim-01", claim="The figure is 10.", category="statistic"),
        ExtractedClaim(id="claim-02", claim="The figure is 11.", category="statistic"),
    ]
    gemini = FakeGemini()
    settings = Settings(_env_file=None)
    verifier = ClaimVerifier(settings, gemini, FakeSearch())

    results = asyncio.run(verifier.verify_all(claims))

    assert gemini.calls == 1
    assert [result.verdict for result in results] == ["VERIFIED", "OUTDATED"]


def test_gemini_quota_error_is_actionable(monkeypatch) -> None:
    class FailedModels:
        def generate_content(self, **_):
            raise ClientError(
                429,
                {
                    "error": {
                        "code": 429,
                        "status": "RESOURCE_EXHAUSTED",
                        "message": "Quota exceeded",
                    }
                },
            )

    class FailedClient:
        models = FailedModels()

    settings = Settings(
        _env_file=None,
        gemini_api_key="configured-key",
        gemini_model="gemini-2.5-flash",
    )
    gemini = GeminiStructuredClient(settings)
    gemini._client = FailedClient()

    async def run_inline(function):
        return function()

    monkeypatch.setattr(asyncio, "to_thread", run_inline)
    with pytest.raises(PipelineError) as error:
        asyncio.run(gemini.generate_json("Analyze this.", VerificationDecisionSet))

    assert error.value.status_code == 429
    assert error.value.code == "gemini_quota_exceeded"
