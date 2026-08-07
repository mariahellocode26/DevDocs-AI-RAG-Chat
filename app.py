"""
app.py

=========================================================
DevDocs AI RAG Chat

Main entry point of the Streamlit application.
=========================================================
"""

from pathlib import Path
import time

import streamlit as st

from rag import ask_rag
from monitoring.logger import log_request
from components.sidebar import render_sidebar
from components.header import render_header
from components.chat import (
    render_chat_history,
    render_assistant_message,
)
from components.source_panel import render_source_panel
from components.monitoring import render_monitoring
from utils.session import initialize_session

# ==========================================================
# Streamlit Configuration
# ==========================================================

st.set_page_config(
    page_title="DevDocs AI RAG Chat",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Load CSS
# ==========================================================

css_file = Path("styles/styles.css")

if css_file.exists():
    st.markdown(
        f"<style>{css_file.read_text()}</style>",
        unsafe_allow_html=True,
    )

# ==========================================================
# Initialize Session
# ==========================================================

initialize_session()

# ==========================================================
# Global Header (Chat + Monitoring)
# ==========================================================

render_header()

# ==========================================================
# Sidebar
# ==========================================================

example_question = render_sidebar()

# ==========================================================
# Monitoring Page
# ==========================================================

if st.session_state.page == "📊 Monitoring":

    render_monitoring()
    st.stop()

# ==========================================================
# CHAT PAGE
# ==========================================================

# 82% Chat
# 18% Sources

chat_column, source_column = st.columns(
    [8.2, 1.8],
    gap="medium",
)

# ----------------------------------------------------------
# Chat Column
# ----------------------------------------------------------

with chat_column:


    render_chat_history()

# ----------------------------------------------------------
# Sources Column
# ----------------------------------------------------------

with source_column:

    render_source_panel(
        sources=st.session_state.sources,
        selected_index=st.session_state.selected_source,
    )

# ==========================================================
# Bottom Chat Input
# ==========================================================

prompt = st.chat_input(
    "Ask a question about the OpenAI API..."
)

# Example question clicked

if example_question:
    prompt = example_question

# ==========================================================
# User Prompt
# ==========================================================

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    st.rerun()

# ==========================================================
# Generate Assistant Response
# ==========================================================

if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
):

    question = st.session_state.messages[-1]["content"]

    with chat_column:

        with st.chat_message("assistant"):

            with st.spinner("Searching documentation..."):

                start = time.perf_counter()

                result = ask_rag(question)

                latency = time.perf_counter() - start

                request_id = None

                try:

                    request_id = log_request(
                        question=question,
                        result=result,
                        latency=latency,
                    )

                except Exception as e:

                    print(f"Logging failed: {e}")
                

            answer = result["answer"]
            sources = result["sources"]
            model = result["model"]
            top_k = result["top_k"]

            render_assistant_message(
                answer=answer,
                latency=latency,
                model=model,
                top_k=top_k,
                source_count=len(sources),
            )

    # Save chat history

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "latency": latency,
            "model": model,
            "source_count": len(sources),
            "request_id": request_id,
        }
    )

    # Save retrieval metadata

    st.session_state.sources = sources
    st.session_state.latency = latency
    st.session_state.model = model

    st.rerun()