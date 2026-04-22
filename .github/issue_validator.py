from gh_issue_validator import validate
from gh_issue_validator.checks.headings import (
    CheckDisorderedHeadings,
    CheckMissingHeadings,
    CheckUnexpectedHeadings,
    CheckWordCount,
    HeadingRequirement,
)

HEADING_REQUIREMENTS: list[HeadingRequirement] = [
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
FREEFORM_HEADINGS = [
    "Other information",
    "Open questions",
]

validate(
    checks=[
        CheckMissingHeadings(requirements=HEADING_REQUIREMENTS),
        CheckUnexpectedHeadings(
            requirements=HEADING_REQUIREMENTS,
            freeform_headings=FREEFORM_HEADINGS,
        ),
        CheckDisorderedHeadings(
            requirements=HEADING_REQUIREMENTS,
            freeform_headings=FREEFORM_HEADINGS,
        ),
        CheckWordCount(requirements=HEADING_REQUIREMENTS),
    ]
)
