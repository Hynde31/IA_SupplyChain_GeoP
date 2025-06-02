import plotly.graph_objects as go
import streamlit as st

def risk_gauge(score, label="Risk Score", minval=0, maxval=2, thresholds=None):
    thresholds = thresholds or [(0.5, "green"), (1, "orange"), (2, "red")]
    color = "green"
    for t, c in thresholds:
        if score > t:
            color = c
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": label},
        gauge={
            "axis": {"range": [minval, maxval]},
            "bar": {"color": color},
            "steps": [
                {"range": [minval, thresholds[0][0]], "color": "lightgreen"},
                {"range": [thresholds[0][0], thresholds[1][0]], "color": "yellow"},
                {"range": [thresholds[1][0], maxval], "color": "#FF7070"},
            ],
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

def kpi_card(label, value, color="default", helptext=None):
    st.markdown(f"""
    <div style="padding:8px 8px 8px 8px;background:{color};border-radius:8px;width:100%;text-align:center;">
    <span style="font-size:1.3em;color:white;"><b>{value}</b></span><br>
    <span style="font-size:1em;">{label}</span>
    </div>
    """, unsafe_allow_html=True)
    if helptext:
        st.caption(helptext)
