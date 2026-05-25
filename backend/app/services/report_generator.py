from collections import Counter

from app.models.schemas import ClaimResult, ReportSummary


class ReportGenerator:
    """Build a deterministic top-level summary from per-claim verdicts."""

    def summarize(self, results: list[ClaimResult]) -> ReportSummary:
        counts = Counter(result.verdict for result in results)
        total = len(results)
        average_confidence = (
            round(sum(result.confidence for result in results) / total) if total else 0
        )
        challenged = (
            counts["INACCURATE"]
            + counts["FALSE"]
            + counts["MISLEADING"]
            + counts["OUTDATED"]
        )

        if not total or counts["INSUFFICIENT_EVIDENCE"] == total:
            risk_level = "UNDETERMINED"
            narrative = "There was not enough sourced evidence to assess the document reliably."
        elif counts["FALSE"] or challenged / total >= 0.4:
            risk_level = "HIGH"
            narrative = "Material claims require correction before this document is published or reused."
        elif challenged:
            risk_level = "MEDIUM"
            narrative = "Some claims require updates or additional context before publication."
        else:
            risk_level = "LOW"
            narrative = "The checked claims are supported by the retrieved evidence."

        return ReportSummary(
            total_claims=total,
            verified=counts["VERIFIED"],
            inaccurate=counts["INACCURATE"],
            false=counts["FALSE"],
            misleading=counts["MISLEADING"],
            outdated=counts["OUTDATED"],
            insufficient_evidence=counts["INSUFFICIENT_EVIDENCE"],
            average_confidence=average_confidence,
            risk_level=risk_level,
            narrative=narrative,
        )
