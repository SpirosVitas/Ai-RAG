"""
context_builder.py
"""


def build_context(
    retrieved_chunks: list[dict],
) -> str:

    context_parts = []

    for idx, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):

        metadata = chunk["metadata"]

        article = metadata.get(
            "article_reference",
            "Unknown",
        )

        title = metadata.get(
            "regulation_title",
            "Unknown",
        )

        context_parts.append(
            f"""
[Source {idx}]
Document: {title}
Article: {article}

{chunk["content"]}
"""
        )

    return "\n\n".join(context_parts)