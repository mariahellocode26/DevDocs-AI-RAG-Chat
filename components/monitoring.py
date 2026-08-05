import streamlit as st
import pandas as pd

from monitoring.analytics import (
    get_total_requests,
    get_average_latency,
    get_total_cost,
    get_total_tokens,
    get_average_retrieved_chunks,
    get_requests_over_time,
    get_latency_over_time,
    get_tokens_over_time,
    get_cost_over_time,
    get_top_documents,
)


def render_monitoring():

    st.title("📊 Monitoring Dashboard")

    # ==========================================================
    # Metrics
    # ==========================================================
    with st.container(border=True):

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Requests",
                get_total_requests(),
            )

        with col2:
            st.metric(
                "Avg Latency",
                f"{get_average_latency():.2f} s",
            )

        with col3:
            st.metric(
                "Tokens",
                f"{get_total_tokens():,}",
            )

        with col4:
            st.metric(
                "Cost",
                f"${get_total_cost():.6f}",
            )

        with col5:
            st.metric(
                "Avg Chunks",
                get_average_retrieved_chunks(),
            )

        st.divider()

        # ==========================================================
        # Evaluation metrics
        # ==========================================================

        st.subheader(" Retrieval Evaluation")

        eval_col1, eval_col2, eval_col3, eval_col4 = st.columns(4)

        with eval_col1:
            st.metric("Hit@1", "0.600")

        with eval_col2:
            st.metric("Hit@3", "0.833")

        with eval_col3:
            st.metric("Hit@5", "0.967")

        with eval_col4:
            st.metric("MRR", "0.730")

        st.divider()
        st.markdown("<div style='height: 24px'></div>",
            unsafe_allow_html=True)

        # ==========================================================
        # Row 1
        # ==========================================================

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:

            st.subheader("Requests over time")

            requests_df = pd.DataFrame(
                get_requests_over_time(),
                columns=["day", "requests"],
            )

            if not requests_df.empty:
                st.line_chart(
                    requests_df.set_index("day")
                )

        with chart_col2:

            st.subheader("Latency over time")

            latency_df = pd.DataFrame(
                get_latency_over_time(),
                columns=["day", "latency"],
            )

            if not latency_df.empty:
                st.line_chart(
                    latency_df.set_index("day")
                )


        st.markdown("<div style='height: 24px'></div>",
            unsafe_allow_html=True)

        # ==========================================================
        # Row 2
        # ==========================================================

        chart_col3, chart_col4 = st.columns(2)

        with chart_col3:

            st.subheader("Token usage over time")

            tokens_df = pd.DataFrame(
                get_tokens_over_time(),
                columns=["day", "tokens"],
            )

            if not tokens_df.empty:
                st.line_chart(
                    tokens_df.set_index("day")
                )

        with chart_col4:

            st.subheader("Cost over time")

            cost_df = pd.DataFrame(
                get_cost_over_time(),
                columns=["day", "cost"],
            )

            if not cost_df.empty:
                st.line_chart(
                    cost_df.set_index("day")
                )

        st.divider()

        # ==========================================================
        # Top retrieved documents
        # ==========================================================

        st.subheader("Most retrieved documents")

        docs_df = pd.DataFrame(
            get_top_documents(),
            columns=["document", "retrievals"],
        )

        if not docs_df.empty:

            st.bar_chart(
                docs_df.set_index("document")
            )

        st.markdown("<div style='height: 50px'></div>",
            unsafe_allow_html=True)

        

