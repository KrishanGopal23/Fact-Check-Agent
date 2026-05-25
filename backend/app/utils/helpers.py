import re
from urllib.parse import urlparse


class PipelineError(Exception):
    """An expected, user-facing processing error."""

    def __init__(self, message: str, status_code: int = 422, code: str = "processing_error"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


def clean_text(text: str) -> str:
    """Normalize PDF extraction noise while retaining paragraph boundaries."""

    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compact_snippet(text: str | None, limit: int = 520) -> str:
    cleaned = clean_text(text or "")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rsplit(" ", 1)[0] + "..."


def safe_web_url(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url


def source_domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def authority_label(domain: str) -> str:
    official_markers = (
        ".gov",
        ".gov.",
        ".edu",
        ".int",
        "sec.gov",
        "who.int",
        "worldbank.org",
        "imf.org",
        "un.org",
        "europa.eu",
    )
    reputable_markers = (
        "reuters.com",
        "apnews.com",
        "ft.com",
        "bloomberg.com",
        "nature.com",
        "science.org",
    )
    if any(marker in domain for marker in official_markers):
        return "primary"
    if any(marker in domain for marker in reputable_markers):
        return "reputable"
    return "web"
