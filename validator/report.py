from dataclasses import dataclass, field

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

    def __str__(self) -> str:
        lines: list[str] = []
        if self.is_failure:
            lines.append(f"❌ Validation failed with {len(self.issues)} issues.")
            lines.append("")
            lines.extend([f"- {issue.rich_message}" for issue in self.issues])
        else:
            lines.append("✔️  Validation successful!")

        return "\n".join(lines)
