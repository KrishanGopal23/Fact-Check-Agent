from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routes.factcheck import router as factcheck_router
from app.utils.helpers import PipelineError

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Evidence-first PDF claim verification with Gemini and Tavily.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def privacy_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(PipelineError)
async def pipeline_exception_handler(_: Request, exc: PipelineError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ready",
        "documentation": "/docs",
    }


app.include_router(factcheck_router)
