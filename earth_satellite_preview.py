import streamlit as st
import streamlit.components.v1 as components

from earth_satellites import add_satellites_to_globe


st.set_page_config(
    page_title="HAMTRACK-AI Orbit Explorer",
    page_icon="🛰️",
    layout="wide",
)

st.title("🛰️ HAMTRACK-AI — Satellite Orbit Explorer")
st.caption(
    "Experimental 3D orbital visualization using Skyfield and local TLE data."
)

satellite_options = [
    "OSCAR 7 (AO-7)",
    "UOSAT 2 (UO-11)",
    "ISS (ZARYA)",
    "PHASE 3B (AO-10)",
    "LUSAT (LO-19)",
]

selected = st.multiselect(
    "Choose satellites",
    options=satellite_options,
    default=[
        "OSCAR 7 (AO-7)",
        "UOSAT 2 (UO-11)",
        "ISS (ZARYA)",
    ],
)

if not selected:
    st.info("Select at least one satellite to display.")
else:
    try:
        with st.spinner("Calculating satellite positions and orbits..."):
            figure = add_satellites_to_globe(selected)

        components.html(
            figure.to_html(
                include_plotlyjs="cdn",
                full_html=False,
                config={
                    "responsive": True,
                    "displaylogo": False,
                },
            ),
            height=820,
            scrolling=False,
        )

        st.success(
            f"Displayed {len(selected)} selected satellite(s)."
        )
        st.caption(
            "Orbit paths are model-based estimates from the local TLE file. "
            "TLE freshness affects positional accuracy."
        )

    except Exception as error:
        st.error(f"Could not build the orbit preview: {error}")
        st.exception(error)
