"""
session.py

Initialize and manage Streamlit Session State.

Keeping all session variables in one place makes the
application easier to maintain as it grows.
"""

from __future__ import annotations

import streamlit as st


DEFAULT_SESSION = {
    "messages": [],
    "sources": [],
    "selected_source": 0,
    "latency": 0.0,
    "model": "gpt-5.4-mini",
    "top_k": 5,
    "page": "💬 Chat",
}


def initialize_session() -> None:
    """
    Initialize Streamlit session variables only once.
    """

    for key, value in DEFAULT_SESSION.items():
        if key not in st.session_state:
            st.session_state[key] = value