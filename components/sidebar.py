"""
sidebar.py

=========================================================
Sidebar Component

Responsibilities
----------------
• Render the application sidebar
• Display retrieval settings
• Display example questions
• Clear the conversation
• Return the selected example question

The sidebar should NOT call the RAG backend.
It simply returns the user's choices.
=========================================================
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------
# Example Questions
# ---------------------------------------------------------

EXAMPLE_QUESTIONS = [
    "How do I authenticate with the OpenAI API?",
    "What is the Responses API?",
    "How do embeddings work?",
    "Explain function calling.",
    "How do I stream responses?",
]


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

def render_sidebar() -> str | None:
    """
    Render the left sidebar.

    Returns
    -------
    str | None
        The selected example question if one was clicked.
        Otherwise None.
    """

    selected_question = None

    with st.sidebar:

        # -------------------------------------------------
        # Logo / Title
        # -------------------------------------------------

        st.markdown("# 📘 DevDocs AI")
        st.caption("RAG Chat")

        st.divider()

        # -------------------------------------------------
        # Retrieval Settings
        # -------------------------------------------------

        st.markdown("### ⚙️ Retrieval")

        model = st.selectbox(
            "Model",
            options=[
                "gpt-5.4-mini",
            ],
            index=0,
            disabled=True,
            help="Model currently used by the RAG pipeline.",
        )

        top_k = st.slider(
            "Top K",
            min_value=1,
            max_value=10,
            value=st.session_state.get("top_k", 5),
            help="Number of retrieved document chunks.",
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            disabled=True,
            help="Currently fixed by the backend.",
        )

        # Save values in session state
        st.session_state.model = model
        st.session_state.top_k = top_k

        st.divider()

        # -------------------------------------------------
        # Conversation
        # -------------------------------------------------

        st.markdown("### 💬 Conversation")

        if st.button(
            "🧹 Clear Chat",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.session_state.sources = []
            st.session_state.selected_source = 0
            st.session_state.latency = 0.0

            st.rerun()

        st.divider()

        # -------------------------------------------------
        # Example Questions
        # -------------------------------------------------

        st.markdown("### 💡 Example Questions")

        for question in EXAMPLE_QUESTIONS:

            if st.button(
                question,
                use_container_width=True,
                key=f"example_{question}",
            ):
                selected_question = question

        st.divider()

        # -------------------------------------------------
        # Application Info
        # -------------------------------------------------

        with st.expander("ℹ️ About"):

            st.markdown(
                """
**DevDocs AI RAG Chat**

A Retrieval-Augmented Generation (RAG)
assistant built for the
LLM Zoomcamp final project.

The assistant answers questions
about the OpenAI API using a curated
documentation corpus.

**Current Knowledge Base**

- authentication.md
- responses-api.md
- embeddings.md
- function-calling.md
- streaming.md
- models.md
"""
            )

    return selected_question