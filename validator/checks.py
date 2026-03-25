from abc import ABC, abstractmethod

import nltk

from validator.headings import ALLOWED_HEADINGS, HEADING_REQUIREMENTS
from validator.markdown import _parse_segments, _render_tokens_as_md
from validator.report import ValidationIssue, ValidationReport
from validator.types import SegmentsMap


class Validator:
    def __init__(self, *, checks: list[ValidationCheck]):
        self.checks = checks

    def validate(self, markdown: str) -> ValidationReport:
        report = ValidationReport()
        segments = _parse_segments(markdown)

        for check in self.checks:
            check.check(segments, report)

        return report


class ValidationCheck(ABC):
    def __init__(self) -> None:
        self.heading_requirements = HEADING_REQUIREMENTS

    @abstractmethod
    def check(self, segments: SegmentsMap, report: ValidationReport) -> None:
        pass


class MissingHeadingsCheck(ValidationCheck):
    def check(self, segments: SegmentsMap, report: ValidationReport) -> None:
        missing_headings = [
            req["heading"]
            for req in self.heading_requirements
            if req["heading"] not in segments.keys()
        ]

        for heading in missing_headings:
            report.add_issue(
                ValidationIssue(
                    code="missing-heading",
                    message=f"Missing required heading: '{heading}'",
                    heading=heading,
                )
            )


class UnexpectedHeadingsCheck(ValidationCheck):
    def check(self, segments: SegmentsMap, report: ValidationReport) -> None:
        unexpected_headings = [
            heading for heading in segments.keys() if heading not in ALLOWED_HEADINGS
        ]

        for heading in unexpected_headings:
            report.add_issue(
                ValidationIssue(
                    code="unexpected-heading",
                    message=f"Unexpected heading: '{heading}'",
                    heading=heading,
                )
            )


class WordCountCheck(ValidationCheck):
    def check(self, segments: SegmentsMap, report: ValidationReport) -> None:
        # Download Natural Language Toolkit data for tokenization if needed
        nltk.download("punkt_tab", quiet=True)

        for heading, tokens in segments.items():
            content = _render_tokens_as_md(tokens).strip()

            heading_requirement = next(
                (
                    entry
                    for entry in self.heading_requirements
                    if entry["heading"] == heading
                ),
                None,
            )

            if heading_requirement is None:
                continue

            words = nltk.word_tokenize(content.lower())
            word_count = len(words)

            min_words = heading_requirement.get("min_words", 0)
            if word_count < min_words:
                report.add_issue(
                    ValidationIssue(
                        code="incomplete-info",
                        message=f"Heading '{heading}' requires at least {min_words} words, found {word_count} words",
                        heading=heading,
                    )
                )

            max_words = heading_requirement.get("max_words", None)
            if max_words is not None and word_count > max_words:
                report.add_issue(
                    ValidationIssue(
                        code="too-much-info",
                        message=f"Heading '{heading}' requires at most {max_words} words, found {word_count} words",
                        heading=heading,
                    )
                )
