"""Validate a GitHub issue aligns with our standards."""

import os
from argparse import ArgumentParser

from github import Auth, Github

from validator.checks import (
    MissingHeadingsCheck,
    UnexpectedHeadingsCheck,
    Validator,
    WordCountCheck,
)
from validator.constants import LABEL_PREFIX, REPO_NAME, REPO_OWNER


def _validate_issue(*, github: Github, issue_id: int) -> None:
    issue = github.get_repo(f"{REPO_OWNER}/{REPO_NAME}").get_issue(issue_id)

    # Only act on open issues
    if issue.state != "open":
        print("⚠️  Issue is closed -- skipping")
        return

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

    current_error_labels = {
        label.name for label in issue.labels if label.name.startswith(LABEL_PREFIX)
    }

    # Remove obsolete error labels
    for label in current_error_labels - report.error_labels:
        print(f"ℹ️ Removing label {label} from {issue.html_url}")
        issue.remove_from_labels(label)

    # Add new error labels
    for label in report.error_labels - current_error_labels:
        print(f"ℹ️ Adding label {label} to {issue.html_url}")
        issue.add_to_labels(label)

    # TODO: Post a comment in the issue


def cli() -> None:
    argparser = ArgumentParser()
    argparser.add_argument(
        "issue",
        help=f"Issue to validate (issue id on {REPO_OWNER}/{REPO_NAME})",
    )
    args = argparser.parse_args()

    if not args.issue.isdigit():
        raise ValueError(f"Expected digits, received '{args.issue}'.")

    github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

    _validate_issue(github=github, issue_id=int(args.issue))
