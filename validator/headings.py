from typing import NotRequired, TypedDict


class HeadingRequirement(TypedDict):
    heading: str
    min_words: NotRequired[int]
    max_words: NotRequired[int]


FREEFORM_HEADINGS = [
    "Other information",
]


# TODO: Support multiple levels of headings
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

ALLOWED_HEADINGS = FREEFORM_HEADINGS + [req["heading"] for req in HEADING_REQUIREMENTS]
