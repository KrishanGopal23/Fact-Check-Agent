from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.models.schemas import (
    ExtractionResponse,
    FactCheckResponse,
    UploadResponse,
    VerificationRequest,
    VerificationResponse,
)
from app.services.pipeline import FactCheckPipeline
from app.utils.helpers import PipelineError, compact_snippet

router = APIRouter(tags=["Fact Checking"])


class HealthResponse(BaseModel):
    status: str
    ready: bool
    gemini_configured: bool
    tavily_configured: bool
    configuration_issues: list[str]


@lru_cache
def get_pipeline() -> FactCheckPipeline:
    return FactCheckPipeline(get_settings())


async def provide_settings() -> Settings:
    return get_settings()


async def provide_pipeline() -> FactCheckPipeline:
    return get_pipeline()


async def read_uploaded_pdf(file: UploadFile, settings: Settings) -> tuple[bytes, str]:
    filename = Path(file.filename or "document.pdf").name
    if not filename.lower().endswith(".pdf"):
        raise PipelineError("Only PDF uploads are accepted.", code="unsupported_file_type")
    if file.content_type and file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise PipelineError("Only PDF uploads are accepted.", code="unsupported_file_type")

    content = await file.read(settings.maximum_upload_bytes + 1)
    await file.close()
    if not content:
        raise PipelineError("The uploaded PDF is empty.", code="empty_upload")
    if len(content) > settings.maximum_upload_bytes:
        raise PipelineError(
            f"PDF uploads are limited to {settings.max_upload_mb} MB.",
            status_code=413,
            code="file_too_large",
        )
    return content, filename


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(provide_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        ready=settings.gemini_is_configured and settings.tavily_is_configured,
        gemini_configured=settings.gemini_is_configured,
        tavily_configured=settings.tavily_is_configured,
        configuration_issues=settings.configuration_issues,
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    settings: Settings = Depends(provide_settings),
    pipeline: FactCheckPipeline = Depends(provide_pipeline),
) -> UploadResponse:
    content, filename = await read_uploaded_pdf(file, settings)
    document, text = pipeline.read_pdf(content, filename)
    return UploadResponse(document=document, text_preview=compact_snippet(text, limit=900))


@router.post("/extract", response_model=ExtractionResponse)
async def extract_claims(
    file: UploadFile = File(...),
    settings: Settings = Depends(provide_settings),
    pipeline: FactCheckPipeline = Depends(provide_pipeline),
) -> ExtractionResponse:
    content, filename = await read_uploaded_pdf(file, settings)
    document, text = pipeline.read_pdf(content, filename)
    claims = await pipeline.extract_claims(text)
    return ExtractionResponse(document=document, claims=claims)


@router.post("/verify", response_model=VerificationResponse)
async def verify_claims(
    payload: VerificationRequest,
    pipeline: FactCheckPipeline = Depends(provide_pipeline),
) -> VerificationResponse:
    for index, claim in enumerate(payload.claims, start=1):
        claim.id = claim.id or f"claim-{index:02d}"
        claim.search_query = claim.search_query or claim.claim
    results, summary = await pipeline.verify_claims(payload.claims)
    return VerificationResponse(results=results, summary=summary)


@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(
    file: UploadFile = File(...),
    settings: Settings = Depends(provide_settings),
    pipeline: FactCheckPipeline = Depends(provide_pipeline),
) -> FactCheckResponse:
    content, filename = await read_uploaded_pdf(file, settings)
    return await pipeline.run(content, filename)
