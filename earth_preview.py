import streamlit as st
from earth_globe import create_earth_globe

st.set_page_config(
    page_title="HAMTRACK-AI | Earth Explorer",
    page_icon="🌍",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 HAMTRACK-AI | Earth Explorer")
st.caption("NASA Blue Marble • Interactive 3D Earth")

fig = create_earth_globe()
fig.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=35, b=0),
    scene=dict(
        camera=dict(
            eye=dict(x=1.45, y=1.45, z=1.0),
            projection=dict(type="perspective"),
        ),
    ),
)

st.plotly_chart(
    fig,
    width="stretch",
    config={
        "scrollZoom": True,
        "displayModeBar": True,
        "responsive": True,
    },
)

st.caption("Drag to rotate • Scroll to zoom • Double-click to reset")
