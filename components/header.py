"""
header.py

=========================================================
Application Header

Responsibilities
----------------
• Display the application title
• Display subtitle
• Display Chat / Monitoring navigation
• Display version badge

This component contains NO business logic.
=========================================================
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

import streamlit as st


def render_header():

    # Two columns:
    # Left = title
    # Right = page switch

    title_col, nav_col = st.columns(
        [7, 3],
        vertical_alignment="center",
    )

    with title_col:

        st.markdown(
            """
            <div class="app-heade">
                <h3>📘 DevDocs AI RAG Chat</h3>
                <p>
                    Developer Documentation Assistant.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_col:

        page = st.segmented_control(
            "",
            [
                "💬 Chat",
                "📊 Monitoring",
            ],
            default=st.session_state.page,
        )

        if page:
            st.session_state.page = page