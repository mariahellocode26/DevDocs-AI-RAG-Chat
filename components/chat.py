"""
chat.py

=========================================================
Chat Component

Responsibilities
----------------
• Display the conversation history
• Render user messages
• Render assistant messages
• Display response metrics
• Prepare for future streaming responses

This component does NOT call the backend.

It only renders the UI.
=========================================================
"""

from __future__ import annotations

import streamlit as st
from monitoring.logger import save_feedback


# ==========================================================
# Chat History
# ==========================================================

def render_chat_history() -> None:
    """
    Render every message currently stored
    in Streamlit Session State.
    """

    if not st.session_state.messages:

        st.info(
            "👋 Welcome! Ask a question about the OpenAI API to get started."
        )
        return

    for message in st.session_state.messages:

        role = message["role"]

        with st.chat_message(role):

            st.markdown(message["content"])

            # Assistant metadata
            if role == "assistant":

                render_metrics(
                    latency=message.get("latency"),
                    model=message.get("model"),
                    source_count=message.get("source_count"),
                )

                request_id = message.get("request_id")

                if request_id:

                    feedback_col1, feedback_col2, _ = st.columns(
                        [2, 2, 10]
                    )

                    with feedback_col1:

                        if st.button(
                            "👍 Helpful",
                            key=f"up_{request_id}",
                        ):

                            save_feedback(
                                request_id,
                                1,
                            )

                            st.toast(
                                "Thanks for your feedback!"
                            )

                    with feedback_col2:

                        if st.button(
                            "👎 Not helpful",
                            key=f"down_{request_id}",
                        ):

                            save_feedback(
                                request_id,
                                -1,
                            )

                            st.toast(
                                "Thanks for your feedback!"
                            )


# ==========================================================
# Assistant Message
# ==========================================================

def render_assistant_message(
    *,
    answer: str,
    latency: float,
    model: str,
    top_k: int,
    source_count: int,
) -> None:
    """
    Render the newest assistant response.

    Parameters
    ----------
    answer:
        Assistant response.

    latency:
        Time taken to answer.

    model:
        OpenAI model name.

    top_k:
        Number of retrieved chunks.

    source_count:
        Number of retrieved chunks.
    """

    st.markdown(answer)

    render_metrics(
        latency=latency,
        model=model,
        source_count=source_count,
    )


# ==========================================================
# Metrics
# ==========================================================

def render_metrics(
    *,
    latency: float | None,
    model: str | None,
    source_count: int | None,
) -> None:
    """
    Small metrics line displayed underneath
    assistant responses.
    """

    latency_text = (
        f"{latency:.2f}s"
        if latency is not None
        else "--"
    )

    model_text = model or "--"

    chunks = (
        str(source_count)
        if source_count is not None
        else "--"
    )

    st.markdown(
    f"""
        <div style="
                display:flex;
                gap:12px;
                margin-top:12px;
                padding-bottom:10px;
                flex-wrap:wrap;
            ">

        <span class="status">
        ⏱ {latency_text}
        </span>

        <span class="status">
        📄 {chunks} Chunks
        </span>

        <span class="status">
        🧠 {model_text}
        </span>

        </div>
        """,
            unsafe_allow_html=True,
    )