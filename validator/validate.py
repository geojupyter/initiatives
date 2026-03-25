"""Validate a GitHub issue aligns with our standards."""

from argparse import ArgumentParser
import os
import nltk
from typing import Iterable
from mistletoe import Document
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.block_token import Heading
from mistletoe.token import Token
from github import Github, Auth
from typing import NotRequired, TypedDict

REPO_OWNER = "geojupyter"
REPO_NAME = "initiatives"


class HeadingRequirement(TypedDict):
    heading: str
    min_words: NotRequired[int]
    max_words: NotRequired[int]


REQUIRED_HEADINGS: dict[int, HeadingRequirement] = {
    1: [  # Header level 1
        {
            "heading": "Problem statement",
            "min_words": 10,
        },
        {
            "heading": "Who is impacted by this problem?",
            "min_words": 1,
        },
        {
            "heading": "Proposed solution",
            "min_words": 10,
            "max_words": 500,
        },
        {
            "heading": "Proposed implementation",
            "min_words": 10,
            "max_words": 500,
        },
        {
            "heading": "How will this fit in the ecosystem?",
            "min_words": 10,
        },
        {
            "heading": "How do we identify the right time to do this? (Is it now?)",
            "min_words": 10,
        },
        {
            "heading": "Who is doing / will do the work?",
        },
        {
            "heading": "Endorsements",
        },
    ]
}


def _validate_segment(*, heading: str, level: int, content: str) -> None | str:
    """Validate that the segment is permitted and has the expected number of words."""

    if heading == "Other Information":
        return

    # Find segment config
    heading_config = None
    for h in REQUIRED_HEADINGS[level]:
        if h["heading"] == heading:
            heading_config = h
            break

    if heading_config is None:
        print(f"❌ Heading '{heading}' not expected at level {level}")
        return "error:extra-heading"

    # Check word count
    words = nltk.word_tokenize(content.lower())
    word_count = len(words)

    min_words = heading_config.get("min_words", 0)
    if word_count < min_words:
        print(
            f"❌ Heading '{heading}' requires at least {min_words} words, found {word_count} words only"
        )
        return "error:incomplete-info"

    if "max_words" in heading_config:
        max_words = heading_config["max_words"]
        if word_count > max_words:
            print(
                f"❌ Heading '{heading}' requires at most {max_words} words, found {word_count} words"
            )
            return "error:too-much-info"


def _render_tokens_md(*, renderer: MarkdownRenderer, tokens: Iterable[Token]) -> str:
    """Render tokens passed in as markdown.

    Convenience function to convert AST to markdown.
    """
    return "".join([renderer.render(c) for c in tokens])


def _parse_segments(markdown: str) -> dict[str, list[Token]]:
    """Parse given markdown into 'segments' separated by 2nd level headings.

    Returns:

        A dictionary where the keys are the 2nd level headings and values are the
        contents of those headings.
    """
    with MarkdownRenderer() as renderer:
        doc = Document(markdown)
        if not doc.children:
            return {}

        document_segments = {}

        current_segment_header = None
        current_segment_content = []
        for c in doc.children:
            if isinstance(c, Heading) and c.level == 3:
                if current_segment_header is not None:
                    document_segments[current_segment_header] = current_segment_content
                current_segment_header = _render_tokens_md(
                    renderer=renderer,
                    tokens=c.children,
                ).strip()
                current_segment_content = []
            else:
                current_segment_content.append(c)

        # Add the last segment
        document_segments[current_segment_header] = current_segment_content

        return document_segments


def _validate(markdown: str) -> None | str:
    """Validate that a passed in markdown is a valid level 1 header.

    Returns:

        True if validation passes.
        An error label (prefix "error") otherwise.
    """

    segments = _parse_segments(markdown)

    # Make sure that all the level headings are present
    missing_headers = set(h["heading"] for h in REQUIRED_HEADINGS["Level 1"]) - set(
        segments.keys()
    )
    if missing_headers:
        print(f"❌ Missing headers: {missing_headers}")
        return "error:missing-heading"

    # Make sure that none of the content is practically empty
    with MarkdownRenderer() as renderer:
        for header, content in segments.items():
            md_content = _render_tokens_md(renderer=renderer, tokens=content).strip()
            resp = _validate_segment(heading=header, level=1, content=md_content)
            if resp is not True:
                return resp


def _validate_issue(*, github: Github, issue_id: int) -> None:
    issue = github.get_repo(f"{REPO_OWNER}/{REPO_NAME}").get_issue(issue_id)

    # Only act on open issues
    if issue.state != "open":
        print("⚠️  Issue is closed -- skipping")
        return

    error_label = _validate(issue.body)

    error_labels = [
        label.name for label in issue.labels if label.name.startswith("error:")
    ]

    if error_label is None:
        # Remove all error labels
        for label in error_labels:
            print(f"ℹ️  Removing label {label} from {issue.html_url}")
            issue.remove_from_labels(label)
    else:
        # Remove all *other* error: labels
        for label in error_labels:
            if label != error_label:
                print(f"ℹ️  Removing label {label} from {issue.html_url}")
                issue.remove_from_labels(label)
        issue.add_to_labels(error_label)
        print(f"ℹ️  Adding label {label} to {issue.html_url}")


def cli():
    # Download Natural Language Toolkit data for tokenization if needed
    nltk.download("punkt_tab", quiet=True)

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
