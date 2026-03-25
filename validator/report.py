from dataclasses import dataclass, field
from datetime import datetime, timezone

from validator.constants import LABEL_PREFIX


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    heading: str | None = None

    @property
    def label(self) -> str:
        return f"{LABEL_PREFIX}{self.code}"

    @property
    def rich_message(self) -> str:
        return f"❌ {self.message}"


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    @property
    def is_failure(self) -> bool:
        return len(self.issues) > 0

    @property
    def error_labels(self) -> set[str]:
        return {issue.label for issue in self.issues}

    @property
    def _summary_message(self) -> str:
        if self.is_failure:
            return f"😭 Validation failed with {len(self.issues)} issues."
        else:
            return "😁 Validation successful!"

    @property
    def _errors_message(self) -> str:
        if not self.is_failure:
            return ""

        return "\n".join([f"- {issue.rich_message}" for issue in self.issues])

    @property
    def github_issue_message(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        lines: list[str] = []

        lines.append(f"**{self._summary_message}** ({timestamp})")
        if self.is_failure:
            lines.append("<details>")
            lines.append("<summary>Errors</summary>")
            lines.append("")
            lines.append(self._errors_message)
            lines.append("")
            lines.append("</details>")

        return "\n".join(lines)

    def __str__(self) -> str:
        lines: list[str] = []

        lines.append(self._summary_message)
        if self.is_failure:
            lines.append("")
            lines.append(self._errors_message)

        return "\n".join(lines)
