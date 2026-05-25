import asyncio
from typing import TypeVar

from google import genai
from google.genai.errors import ClientError, ServerError
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.utils.helpers import PipelineError

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


class GeminiStructuredClient:
    """Small adapter for schema-validated Gemini JSON responses."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if not self._settings.gemini_is_configured:
            issue = next(
                (
                    message
                    for message in self._settings.configuration_issues
                    if "GEMINI" in message
                ),
                "Gemini is not configured on the server.",
            )
            raise PipelineError(
                issue,
                status_code=503,
                code="invalid_gemini_configuration",
            )
        if self._client is None:
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    async def generate_json(
        self,
        prompt: str,
        response_model: type[ResponseModel],
    ) -> ResponseModel:
        client = self._get_client()

        def request() -> str:
            response = client.models.generate_content(
                model=self._settings.gemini_model,
                contents=prompt,
                config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json",
                    "response_json_schema": response_model.model_json_schema(),
                },
            )
            return response.text or ""

        try:
            raw_response = await asyncio.wait_for(
                asyncio.to_thread(request),
                timeout=self._settings.ai_timeout_seconds,
            )
            return response_model.model_validate_json(raw_response)
        except TimeoutError as exc:
            raise PipelineError(
                "Gemini timed out while analyzing the document.",
                status_code=504,
                code="gemini_timeout",
            ) from exc
        except ValidationError as exc:
            raise PipelineError(
                "Gemini returned a response that could not be validated.",
                status_code=502,
                code="invalid_ai_response",
            ) from exc
        except ClientError as exc:
            error_code = getattr(exc, "code", None)
            error_status = getattr(exc, "status", None)
            if error_code == 429 or error_status == "RESOURCE_EXHAUSTED":
                raise PipelineError(
                    "Gemini quota has been reached for this API key. Wait for quota reset "
                    "or use a project with available Gemini quota.",
                    status_code=429,
                    code="gemini_quota_exceeded",
                ) from exc
            if error_code in {401, 403} or error_status in {"UNAUTHENTICATED", "PERMISSION_DENIED"}:
                raise PipelineError(
                    "Gemini rejected the configured API key or it lacks model access.",
                    status_code=503,
                    code="gemini_auth_error",
                ) from exc
            raise PipelineError(
                f"Gemini rejected the analysis request (HTTP {error_code or 'unknown'}).",
                status_code=502,
                code="gemini_request_error",
            ) from exc
        except ServerError as exc:
            raise PipelineError(
                "Gemini is temporarily unavailable. Please retry shortly.",
                status_code=503,
                code="gemini_service_error",
            ) from exc
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(
                "Gemini analysis is currently unavailable.",
                status_code=502,
                code="gemini_error",
            ) from exc
