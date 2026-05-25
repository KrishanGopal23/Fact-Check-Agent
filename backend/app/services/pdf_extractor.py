import pymupdf as fitz

from app.models.schemas import DocumentInfo
from app.utils.helpers import PipelineError, clean_text


class PDFExtractor:
    """Validate PDFs and extract page-aware text with PyMuPDF."""

    def extract(self, content: bytes, filename: str, max_characters: int) -> tuple[DocumentInfo, str]:
        if not content.startswith(b"%PDF"):
            raise PipelineError("The uploaded file is not a valid PDF.", code="invalid_pdf")

        try:
            document = fitz.open(stream=content, filetype="pdf")
        except (fitz.FileDataError, RuntimeError, ValueError) as exc:
            raise PipelineError(
                "The PDF could not be opened. It may be damaged or encrypted.",
                code="unreadable_pdf",
            ) from exc

        with document:
            if document.needs_pass:
                raise PipelineError(
                    "Password-protected PDFs are not supported.",
                    code="protected_pdf",
                )
            if document.page_count == 0:
                raise PipelineError("The PDF has no pages.", code="empty_pdf")

            pages: list[str] = []
            for page_number, page in enumerate(document, start=1):
                extracted = clean_text(page.get_text("text"))
                if extracted:
                    pages.append(f"[Page {page_number}]\n{extracted}")

            full_text = "\n\n".join(pages).strip()
            if not full_text:
                raise PipelineError(
                    "No selectable text was found. Upload a text-based PDF rather than a scanned image.",
                    code="no_text",
                )

            truncated = len(full_text) > max_characters
            analysis_text = full_text[:max_characters]
            info = DocumentInfo(
                filename=filename,
                pages=document.page_count,
                characters=len(full_text),
                truncated_for_analysis=truncated,
            )
            return info, analysis_text
