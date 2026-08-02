import streamlit as st

from monitoring.analytics import (
    get_total_requests,
)


def render_monitoring():

    st.title("📊 Monitoring")

    total_requests = get_total_requests()

    st.metric(
        label="Total Requests",
        value=total_requests,
    )