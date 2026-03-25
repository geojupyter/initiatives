from typing import Iterable

from mistletoe.block_token import Document, Heading
from mistletoe.markdown_renderer import MarkdownRenderer
from mistletoe.token import Token


def _parse_segments(markdown: str) -> dict[str, list[Token]]:
    """Parse given markdown into 'segments' separated by 3rd level headings.

    Returns:

        A dictionary where the keys are the 3rd level headings and values are the
        contents of those headings.
    """
    doc = Document(markdown)
    if not doc.children:
        return {}

    document_segments = {}

    current_segment_header = None
    current_segment_content: list[Heading | Token] = []
    for child in doc.children:
        is_l2_header = isinstance(child, Heading) and child.level == 3

        if is_l2_header:
            if current_segment_header is not None:
                # TODO: Confusing! Adding content from previous iteration?
                document_segments[current_segment_header] = current_segment_content

            current_segment_header = _render_tokens_as_md(child.children).strip()
            current_segment_content = []
        else:
            current_segment_content.append(child)

    # Add the last segment
    if current_segment_header is not None:
        # TODO: Can we refactor to remove this typeguard
        document_segments[current_segment_header] = current_segment_content

    print(f"ℹ️ Parsed h3 segments: {list(document_segments.keys())}")
    return document_segments


def _render_tokens_as_md(
    tokens: Iterable[Token] | None,
) -> str:
    """Render tokens passed in as markdown.

    Convenience function to convert AST to markdown.
    """
    if not tokens:
        # TODO: Guarantee tokens will be passed in?
        return ""

    with MarkdownRenderer() as renderer:
        return "".join([renderer.render(c) for c in tokens])
