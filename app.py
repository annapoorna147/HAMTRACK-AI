
import streamlit as st
import numpy as np
import plotly.graph_objects as go

from datetime import datetime, timezone, timedelta
from skyfield.api import load, wgs84

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="HAMTRACK AI",
    page_icon="📡",
    layout="wide"
)

st.title("📡 HAMTRACK AI")
st.subheader("Amateur Radio Signal Laboratory")

st.write(
    "Explore satellite tracking, orbital predictions, "
    "Doppler shift, and radio signal analysis."
)

# ==================================================
# SATELLITE DATA
# ==================================================

TLE_URL = (
    "https://celestrak.org/NORAD/elements/"
    "gp.php?GROUP=amateur&FORMAT=tle"
)


@st.cache_resource(ttl=3600)
def get_satellites():
    return load.tle_file(TLE_URL, reload=True)


# ==================================================
# SIDEBAR: GROUND STATION
# ==================================================

st.sidebar.header("Ground Station")

latitude = st.sidebar.number_input(
    "Latitude (degrees)",
    min_value=-90.0,
    max_value=90.0,
    value=13.34,
    step=0.01
)

longitude = st.sidebar.number_input(
    "Longitude (degrees)",
    min_value=-180.0,
    max_value=180.0,
    value=77.10,
    step=0.01
)

altitude = st.sidebar.number_input(
    "Station altitude (metres)",
    min_value=0.0,
    max_value=9000.0,
    value=800.0,
    step=10.0
)

st.sidebar.caption(
    "Coordinates are editable. Replace them with "
    "your actual ground-station coordinates."
)

# ==================================================
# TABS
# ==================================================

tab_tracking, tab_signals = st.tabs(
    ["🛰️ Satellite Tracking", "📻 Signal Laboratory"]
)

# ==================================================
# TAB 1: SATELLITE TRACKING
# ==================================================

with tab_tracking:

    st.header("Real Satellite Tracking")

    st.write(
        "Calculate satellite direction, distance, "
        "visibility, and upcoming passes."
    )

    try:
        with st.spinner("Loading orbital data from CelesTrak..."):
            satellites = get_satellites()

        if not satellites:
            st.error("No satellites were returned.")
            st.stop()

        satellite_names = sorted(
            {sat.name for sat in satellites}
        )

        selected_name = st.selectbox(
            "Choose an amateur-radio satellite",
            satellite_names
        )

        satellite = next(
            sat for sat in satellites
            if sat.name == selected_name
        )

        timescale = load.timescale()
        observer = wgs84.latlon(
            latitude,
            longitude,
            elevation_m=altitude
        )

        now = timescale.now()

        # Current satellite position
        difference = satellite - observer
        position = difference.at(now)

        elevation, azimuth, distance = position.altaz()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Azimuth",
            f"{azimuth.degrees:.1f}°"
        )

        col2.metric(
            "Elevation",
            f"{elevation.degrees:.1f}°"
        )

        col3.metric(
            "Distance",
            f"{distance.km:,.1f} km"
        )

        if elevation.degrees > 0:
            st.success(
                "Satellite is geometrically above your horizon."
            )
        else:
            st.info(
                "Satellite is currently below your horizon."
            )

        st.caption(
            "Predictions depend on orbital data quality, "
            "data age, and ground-station coordinates."
        )

        # ------------------------------------------
        # UPCOMING SATELLITE PASSES
        # ------------------------------------------

        st.divider()
        st.subheader("Upcoming Satellite Passes")

        st.write(
            "Find complete passes above a 10° elevation "
            "threshold during the next 24 hours."
        )

        if st.button(
            "Calculate next 24 hours of passes",
            key="calculate_passes"
        ):

            with st.spinner("Calculating satellite passes..."):

                end_time = timescale.tt_jd(
                    now.tt + 1.0
                )

                event_times, event_types = (
                    satellite.find_events(
                        observer,
                        now,
                        end_time,
                        altitude_degrees=10.0
                    )
                )

                passes = []
                current_pass = {}

                for event_time, event_type in zip(
                    event_times, event_types
                ):

                    if event_type == 0:
                        current_pass = {
                            "rise": event_time
                        }

                    elif (
                        event_type == 1
                        and "rise" in current_pass
                    ):
                        current_pass["maximum"] = event_time

                    elif (
                        event_type == 2
                        and "rise" in current_pass
                    ):
                        current_pass["set"] = event_time

                        if "maximum" in current_pass:
                            passes.append(current_pass)

                        current_pass = {}

            if not passes:

                st.info(
                    "No complete passes above 10° were found "
                    "in this 24-hour period."
                )

            else:

                rows = []

                for sat_pass in passes:

                    rise = sat_pass["rise"]
                    maximum = sat_pass["maximum"]
                    setting = sat_pass["set"]

                    max_position = (
                        satellite - observer
                    ).at(maximum)

                    max_elevation, _, _ = (
                        max_position.altaz()
                    )

                    def format_utc_time(t):
                        return (
                            t.utc_datetime()
                            .strftime("%d %b %Y, %H:%M:%S UTC")
                        )

                    rows.append({
                        "Rise (UTC)": format_utc_time(rise),
                        "Maximum elevation": (
                            f"{max_elevation.degrees:.1f}°"
                        ),
                        "Set (UTC)": format_utc_time(setting)
                    })

                st.dataframe(
                    rows,
                    use_container_width=True,
                    hide_index=True
                )

        # ------------------------------------------
        # 24-HOUR ELEVATION GRAPH
        # ------------------------------------------

        st.divider()

        st.subheader(
            "Satellite Elevation Over the Next 24 Hours"
        )

        st.write(
            "Positive elevation means the satellite is "
            "above the geometric horizon."
        )

        if st.button(
            "Plot satellite path",
            key="plot_satellite_path"
        ):

            with st.spinner(
                "Calculating satellite positions..."
            ):

                # Sample every two minutes
                offsets = np.arange(
                    0,
                    24 * 60 + 1,
                    2
                )

                future_times = timescale.tt_jd(
                    now.tt + offsets / (24 * 60)
                )

                future_positions = (
                    satellite - observer
                ).at(future_times)

                future_elevation, future_azimuth, _ = (
                    future_positions.altaz()
                )

                elevation_values = (
                    future_elevation.degrees
                )

                azimuth_values = (
                    future_azimuth.degrees
                )

                plot_times = [
                    now.utc_datetime()
                    + timedelta(minutes=int(minutes))
                    for minutes in offsets
                ]

                fig_path = go.Figure()

                fig_path.add_trace(
                    go.Scatter(
                        x=plot_times,
                        y=elevation_values,
                        mode="lines",
                        name="Elevation",
                        line=dict(width=2),
                        hovertemplate=(
                            "Time: %{x}<br>"
                            "Elevation: %{y:.2f}°"
                            "<extra></extra>"
                        )
                    )
                )

                fig_path.add_hline(
                    y=0,
                    line_dash="dash",
                    annotation_text="Horizon"
                )

                fig_path.add_hline(
                    y=10,
                    line_dash="dot",
                    annotation_text="10° pass threshold"
                )

                fig_path.update_layout(
                    title="Predicted Satellite Elevation",
                    xaxis_title="Time (UTC)",
                    yaxis_title="Elevation (degrees)",
                    yaxis_range=[-90, 90],
                    template="plotly_dark",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_path,
                    use_container_width=True
                )

                # ----------------------------------
                # AZIMUTH GRAPH
                # ----------------------------------

                st.subheader(
                    "Satellite Compass Direction"
                )

                fig_azimuth = go.Figure()

                fig_azimuth.add_trace(
                    go.Scatter(
                        x=plot_times,
                        y=azimuth_values,
                        mode="lines",
                        name="Azimuth",
                        line=dict(width=2),
                        hovertemplate=(
                            "Time: %{x}<br>"
                            "Azimuth: %{y:.1f}°"
                            "<extra></extra>"
                        )
                    )
                )

                fig_azimuth.update_layout(
                    title="Predicted Satellite Azimuth",
                    xaxis_title="Time (UTC)",
                    yaxis_title="Azimuth (degrees)",
                    yaxis_range=[0, 360],
                    template="plotly_dark",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_azimuth,
                    use_container_width=True
                )

                st.caption(
                    "Graphs show calculated orbital positions, "
                    "not actual radio reception. Positions are "
                    "sampled every two minutes."
                )

    except Exception as error:

        st.error(
            "Unable to load or calculate satellite data."
        )

        st.write(
            "Check your internet connection and try again."
        )

        st.caption(
            f"Technical details: {error}"
        )

# ==================================================
# TAB 2: ORIGINAL SIGNAL LABORATORY
# ==================================================

with tab_signals:

    st.header("Signal Laboratory")

    st.write(
        "Explore simulated radio signals, noise, "
        "Doppler shift, and FFT frequency spectra."
    )

    st.sidebar.header("Signal Settings")

    frequency_mhz = st.sidebar.selectbox(
        "Carrier frequency (MHz)",
        [145.0, 435.0, 14.2]
    )

    velocity = st.sidebar.slider(
        "Relative radial velocity (m/s)",
        -7500,
        7500,
        1000,
        step=100
    )

    snr_db = st.sidebar.slider(
        "Signal-to-noise ratio (dB)",
        -5,
        30,
        10
    )

    # First-order Doppler shift
    speed_of_light = 299_792_458

    doppler_shift = (
        -frequency_mhz * 1e6 * velocity
        / speed_of_light
    )

    # Simulated baseband signal
    sample_rate = 20_000
    duration = 0.05
    samples = int(sample_rate * duration)

    time = np.arange(samples) / sample_rate

    tone_frequency = 1000.0

    received_frequency = (
        tone_frequency + doppler_shift
    )

    rng = np.random.default_rng(42)

    clean_signal = np.sin(
        2 * np.pi * received_frequency * time
    )

    signal_power = np.mean(clean_signal ** 2)

    noise_power = (
        signal_power / (10 ** (snr_db / 10))
    )

    noise = rng.normal(
        0,
        np.sqrt(noise_power),
        samples
    )

    received_signal = clean_signal + noise

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Carrier",
        f"{frequency_mhz} MHz"
    )

    col2.metric(
        "Doppler shift",
        f"{doppler_shift:.2f} Hz"
    )

    col3.metric(
        "Baseband tone",
        f"{received_frequency:.2f} Hz"
    )

    # Time-domain plot
    st.subheader("1. Received Signal")

    fig_time = go.Figure()

    fig_time.add_trace(
        go.Scatter(
            x=time[:500],
            y=received_signal[:500],
            mode="lines",
            name="Received signal"
        )
    )

    fig_time.update_layout(
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_time,
        use_container_width=True
    )

    # Frequency-domain plot
    st.subheader("2. FFT Frequency Spectrum")

    windowed_signal = (
        received_signal * np.hanning(samples)
    )

    spectrum = np.fft.rfft(windowed_signal)

    frequencies = np.fft.rfftfreq(
        samples,
        d=1 / sample_rate
    )

    magnitude_db = 20 * np.log10(
        np.abs(spectrum) + 1e-10
    )

    fig_fft = go.Figure()

    fig_fft.add_trace(
        go.Scatter(
            x=frequencies,
            y=magnitude_db,
            mode="lines",
            name="FFT spectrum"
        )
    )

    fig_fft.update_layout(
        xaxis_title="Baseband frequency (Hz)",
        yaxis_title="Magnitude (dB)",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig_fft,
        use_container_width=True
    )

    st.info(
        "This is simulated baseband data, not a real radio "
        "recording. Doppler shift is calculated using a "
        "first-order approximation."
    )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "HAMTRACK AI | Day 2 | Satellite Tracking & Signal Analysis"
)
