"""
source_panel.py

=========================================================
Retrieved Sources Panel

Responsibilities
----------------
• Display retrieved source documents
• Allow selecting a source
• Show similarity score
• Show chunk metadata
• Display chunk preview

This component never performs retrieval.

It only visualizes retrieved chunks.
=========================================================
"""

from __future__ import annotations

import streamlit as st


# ==========================================================
# Source Panel
# ==========================================================

def render_source_panel(
    sources: list[dict],
    selected_index: int = 0,
) -> None:
    """
    Render the right-side Sources panel.
    """

    st.markdown("## 📄 Sources")

    if not sources:
        selected_index = min(
            selected_index,
            len(sources) - 1,
        )

        st.info(
            "Retrieved documents will appear here."
        )
        return

    # ---------------------------------------------
    # Source Selector
    # ---------------------------------------------

    labels = []

    for source in sources:

        filename = source.get(
            "filename",
            source.get("title", "Unknown"),
        )

        score = source.get("score")

        if score is not None:
            labels.append(
                f"{filename} ({score:.2f})"
            )
        else:
            labels.append(filename)

    selected = st.radio(
        "Retrieved Documents",
        options=range(len(labels)),
        index=selected_index,
        format_func=lambda i: labels[i],
        label_visibility="collapsed",
    )

    st.session_state.selected_source = selected

    source = sources[selected]

    st.divider()

    # ---------------------------------------------
    # Metadata
    # ---------------------------------------------

    st.markdown("### Preview")

    filename = source.get(
        "filename",
        "Unknown"
    )

    st.markdown(
        f"**File:** `{filename}`"
    )

    if "chunk_id" in source:

        st.markdown(
            f"**Chunk ID:** `{source['chunk_id']}`"
        )

    if "score" in source:

        st.markdown(
            f"**Similarity:** `{source['score']:.3f}`"
        )

    headers = [
        source.get("header1"),
        source.get("header2"),
        source.get("header3"),
    ]

    headers = [
        h for h in headers if h
    ]

    if headers:

        st.markdown(
            "**Section**"
        )

        st.caption(
            " → ".join(headers)
        )

    st.divider()

    # ---------------------------------------------
    # Chunk Preview
    # ---------------------------------------------

    st.markdown(
        "### Chunk"
    )

    st.code(
        source.get(
            "text",
            "No preview available."
        ),
        language="markdown",
    )