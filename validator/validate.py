"""Validate a GitHub issue aligns with our standards."""

import os
import sys
from argparse import ArgumentParser

from github import Auth, Github

from validator.checks import (
    MissingHeadingsCheck,
    UnexpectedHeadingsCheck,
    Validator,
    WordCountCheck,
)
from validator.constants import LABEL, REPO_NAME, REPO_OWNER
from validator.github import _post_or_update_github_comment
from validator.report import ValidationReport


def _validate_issue(
    *,
    github: Github,
    issue_id: int,
    post_comment: bool = False,
) -> ValidationReport:
    issue = github.get_repo(f"{REPO_OWNER}/{REPO_NAME}").get_issue(issue_id)

    # Only act on open issues
    if issue.state != "open":
        print("⚠️  Issue is closed -- skipping")

        # Should this be considered a failure? ¯\_(ツ)_/¯
        return ValidationReport()

    validator = Validator(
        checks=[
            MissingHeadingsCheck(),
            UnexpectedHeadingsCheck(),
            WordCountCheck(),
        ]
    )

    report = validator.validate(issue.body)

    print()
    print(report)
    print()

    has_error_label = any(label.name == LABEL for label in issue.labels)

    if report.is_failure and not has_error_label:
        issue.add_to_labels(LABEL)
        print(f"ℹ️ Added label {LABEL} to {issue.html_url}")

    if not report.is_failure and has_error_label:
        issue.remove_from_labels(LABEL)
        print(f"ℹ️ Removed label {LABEL} from {issue.html_url}")

    if post_comment:
        _post_or_update_github_comment(issue=issue, report=report)

    return report


def cli() -> None:
    argparser = ArgumentParser()
    argparser.add_argument(
        "issue",
        help=f"Issue to validate (issue id on {REPO_OWNER}/{REPO_NAME})",
    )
    argparser.add_argument(
        "--post-report-as-comment",
        action="store_true",
        help="On validation failure, post validation report as a comment in the issue.",
    )
    args = argparser.parse_args()

    if not args.issue.isdigit():
        raise ValueError(f"Expected digits, received '{args.issue}'.")

    github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

    report = _validate_issue(
        github=github,
        issue_id=int(args.issue),
        post_comment=args.post_report_as_comment,
    )

    if report.is_failure:
        sys.exit(1)
