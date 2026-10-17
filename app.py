
import streamlit as st
import numpy as np
import plotly.graph_objects as go

from datetime import timedelta
from skyfield.api import load, wgs84

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="HAMTRACK AI",
    page_icon="📡",
    layout="wide"
)

st.title("📡 HAMTRACK AI")
st.subheader("Amateur Radio Signal Laboratory")

st.write(
    "Explore satellite tracking, orbital predictions, "
    "sky-view direction, Doppler shift, and signal analysis."
)

# ============================================================
# SATELLITE ORBITAL DATA
# ============================================================

TLE_URL = (
    "https://celestrak.org/NORAD/elements/"
    "gp.php?GROUP=amateur&FORMAT=tle"
)


@st.cache_resource(ttl=3600)
def get_satellites():
    return load.tle_file(TLE_URL, reload=True)


# ============================================================
# GROUND STATION SETTINGS
# ============================================================

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
    "Enter your ground-station coordinates. "
    "The initial values are approximate for Tumakuru."
)

# ============================================================
# APPLICATION TABS
# ============================================================

tab_tracking, tab_signals = st.tabs(
    [
        "🛰️ Satellite Tracking",
        "📻 Signal Laboratory"
    ]
)

# ============================================================
# TAB 1: SATELLITE TRACKING
# ============================================================

with tab_tracking:

    st.header("Real Satellite Tracking")

    st.write(
        "Calculate satellite direction, distance, visibility, "
        "upcoming passes, sky position, and predicted Doppler shift."
    )

    try:

        with st.spinner(
            "Loading satellite orbital data from CelesTrak..."
        ):
            satellites = get_satellites()

        if not satellites:
            st.error("No satellites were returned by CelesTrak.")
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

        # ----------------------------------------------------
        # CURRENT SATELLITE POSITION
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # DAY 3: SKY-VIEW COMPASS
        # ----------------------------------------------------

        st.divider()
        st.header("🧭 Sky-View Compass")

        st.write(
            "The compass shows the satellite's direction "
            "relative to your ground station."
        )

        st.markdown(
            """
            - **North** is at the top.
            - **East** is on the right.
            - **South** is at the bottom.
            - **West** is on the left.
            - The centre represents directly overhead.
            - The outer circle represents the horizon.
            """
        )

        current_azimuth = float(azimuth.degrees)
        current_elevation = float(elevation.degrees)

        fig_compass = go.Figure()

        compass_angles = np.linspace(0, 360, 361)

        fig_compass.add_trace(
            go.Scatterpolar(
                r=[90.0] * len(compass_angles),
                theta=compass_angles,
                mode="lines",
                name="Horizon",
                line=dict(color="gray", width=2),
                hoverinfo="skip"
            )
        )

        if current_elevation >= 0:

            compass_radius = 90.0 - current_elevation

            fig_compass.add_trace(
                go.Scatterpolar(
                    r=[compass_radius],
                    theta=[current_azimuth],
                    mode="markers+text",
                    name="Satellite",
                    text=["Satellite"],
                    textposition="top center",
                    marker=dict(
                        size=15,
                        color="#22D3EE",
                        line=dict(color="white", width=1)
                    ),
                    hovertemplate=(
                        "Azimuth: %{theta:.1f}°<br>"
                        "Angular distance from overhead: "
                        "%{r:.1f}°<extra></extra>"
                    )
                )
            )

            st.success(
                "The satellite is above the horizon. "
                "Its direction is marked on the compass."
            )

        else:

            st.info(
                "The satellite is below the horizon. "
                "Its position is not shown inside the visible-sky compass."
            )

        fig_compass.update_layout(
            title="Current Satellite Direction",
            template="plotly_dark",
            height=600,
            showlegend=False,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(
                    range=[0, 90],
                    tickmode="array",
                    tickvals=[0, 30, 60, 90],
                    ticktext=[
                        "Overhead",
                        "60° elevation",
                        "30° elevation",
                        "Horizon"
                    ],
                    gridcolor="gray",
                    linecolor="gray"
                ),
                angularaxis=dict(
                    direction="clockwise",
                    rotation=90,
                    tickmode="array",
                    tickvals=[
                        0, 45, 90, 135,
                        180, 225, 270, 315
                    ],
                    ticktext=[
                        "N", "NE", "E", "SE",
                        "S", "SW", "W", "NW"
                    ],
                    gridcolor="gray",
                    linecolor="gray"
                )
            )
        )

        st.plotly_chart(
            fig_compass,
            use_container_width=True
        )

        direction_labels = [
            "North",
            "Northeast",
            "East",
            "Southeast",
            "South",
            "Southwest",
            "West",
            "Northwest"
        ]

        direction_index = (
            int((current_azimuth + 22.5) // 45) % 8
        )

        info1, info2, info3 = st.columns(3)

        info1.metric(
            "Compass direction",
            direction_labels[direction_index]
        )

        info2.metric(
            "Azimuth bearing",
            f"{current_azimuth:.1f}°"
        )

        info3.metric(
            "Elevation above horizon",
            f"{current_elevation:.1f}°"
        )

        st.caption(
            "The compass uses orbital calculations. "
            "It does not control a physical antenna."
        )

        # ----------------------------------------------------
        # DAY 4: SATELLITE DOPPLER PREDICTION
        # ----------------------------------------------------

        st.divider()
        st.header("📻 Satellite Doppler Prediction")

        st.write(
            "Estimate radio-frequency shifts from the satellite's "
            "changing distance to your ground station."
        )

        doppler_frequency_mhz = st.selectbox(
            "Radio carrier frequency (MHz)",
            [145.0, 435.0, 146.0, 437.0, 14.2],
            index=0,
            key="doppler_carrier_frequency"
        )

        doppler_duration_hours = st.selectbox(
            "Prediction window",
            [1, 3, 6, 12, 24],
            index=2,
            format_func=lambda h: f"Next {h} hour(s)",
            key="doppler_prediction_window"
        )

        if st.button(
            "Calculate satellite Doppler shift",
            key="calculate_satellite_doppler"
        ):

            with st.spinner(
                "Calculating satellite range rate and Doppler shift..."
            ):

                # Sample positions once per minute.
                sample_minutes = np.arange(
                    0,
                    doppler_duration_hours * 60 + 1,
                    1
                )

                doppler_times = timescale.tt_jd(
                    now.tt + sample_minutes / (24 * 60)
                )

                topocentric_positions = (
                    satellite - observer
                ).at(doppler_times)

                # Distance in metres.
                ranges_m = (
                    topocentric_positions.distance().km * 1000.0
                )

                # Range rate in metres/second.
                # Positive = moving away.
                # Negative = approaching.
                range_rate_m_s = np.gradient(
                    ranges_m,
                    60.0
                )

                speed_of_light = 299_792_458.0
                carrier_hz = doppler_frequency_mhz * 1e6

                # First-order Doppler approximation.
                doppler_hz = (
                    -carrier_hz
                    * range_rate_m_s
                    / speed_of_light
                )

                received_frequency_hz = (
                    carrier_hz + doppler_hz
                )

                # Metrics at the beginning of the prediction.
                current_shift = float(doppler_hz[0])
                current_range_rate = float(range_rate_m_s[0])
                current_received_hz = float(
                    received_frequency_hz[0]
                )

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric(
                    "Predicted Doppler shift",
                    f"{current_shift:+.1f} Hz"
                )

                metric2.metric(
                    "Range rate",
                    f"{current_range_rate:+.1f} m/s"
                )

                metric3.metric(
                    "Predicted received frequency",
                    f"{current_received_hz / 1e6:.6f} MHz"
                )

                if current_range_rate < 0:
                    st.info(
                        "The satellite is approaching the station. "
                        "The predicted Doppler shift is positive."
                    )
                elif current_range_rate > 0:
                    st.info(
                        "The satellite is moving away from the station. "
                        "The predicted Doppler shift is negative."
                    )
                else:
                    st.info(
                        "The range rate is approximately zero."
                    )

                elapsed_hours = sample_minutes / 60.0

                # --------------------------------------------
                # DOPPLER SHIFT GRAPH
                # --------------------------------------------

                st.subheader("1. Predicted Doppler Shift")

                fig_doppler = go.Figure()

                fig_doppler.add_trace(
                    go.Scatter(
                        x=elapsed_hours,
                        y=doppler_hz,
                        mode="lines",
                        name="Doppler shift",
                        line=dict(width=2),
                        hovertemplate=(
                            "Elapsed time: %{x:.2f} hours<br>"
                            "Doppler shift: %{y:.2f} Hz"
                            "<extra></extra>"
                        )
                    )
                )

                fig_doppler.add_hline(
                    y=0,
                    line_dash="dash",
                    annotation_text="Zero Doppler"
                )

                fig_doppler.update_layout(
                    title="Doppler Shift Over Time",
                    xaxis_title="Hours from now",
                    yaxis_title="Doppler shift (Hz)",
                    template="plotly_dark",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_doppler,
                    use_container_width=True
                )

                # --------------------------------------------
                # RANGE RATE GRAPH
                # --------------------------------------------

                st.subheader("2. Satellite Range Rate")

                fig_range = go.Figure()

                fig_range.add_trace(
                    go.Scatter(
                        x=elapsed_hours,
                        y=range_rate_m_s,
                        mode="lines",
                        name="Range rate",
                        line=dict(width=2),
                        hovertemplate=(
                            "Elapsed time: %{x:.2f} hours<br>"
                            "Range rate: %{y:.1f} m/s"
                            "<extra></extra>"
                        )
                    )
                )

                fig_range.add_hline(
                    y=0,
                    line_dash="dash",
                    annotation_text="Zero range rate"
                )

                fig_range.update_layout(
                    title="Satellite Range Rate Over Time",
                    xaxis_title="Hours from now",
                    yaxis_title="Range rate (m/s)",
                    template="plotly_dark",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_range,
                    use_container_width=True
                )

                # --------------------------------------------
                # RECEIVED FREQUENCY GRAPH
                # --------------------------------------------

                st.subheader("3. Predicted Received Frequency")

                fig_received = go.Figure()

                fig_received.add_trace(
                    go.Scatter(
                        x=elapsed_hours,
                        y=received_frequency_hz / 1e6,
                        mode="lines",
                        name="Received frequency",
                        line=dict(width=2)
                    )
                )

                fig_received.update_layout(
                    title="Predicted Received Frequency Over Time",
                    xaxis_title="Hours from now",
                    yaxis_title="Frequency (MHz)",
                    template="plotly_dark",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_received,
                    use_container_width=True
                )

                st.caption(
                    "Doppler is estimated from changes in orbital range. "
                    "The model uses sampled positions and a first-order "
                    "approximation. It does not measure a transmitted "
                    "radio signal or include transmitter/receiver "
                    "frequency errors."
                )

        # ----------------------------------------------------
        # UPCOMING SATELLITE PASSES
        # ----------------------------------------------------

        st.divider()
        st.header("Upcoming Satellite Passes")

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
                    event_times,
                    event_types
                ):

                    if event_type == 0:
                        current_pass = {"rise": event_time}

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

        # ----------------------------------------------------
        # 24-HOUR ELEVATION AND AZIMUTH GRAPHS
        # ----------------------------------------------------

        st.divider()
        st.header("Satellite Elevation Over the Next 24 Hours")

        st.write(
            "Positive elevation means the satellite is "
            "above the geometric horizon."
        )

        if st.button(
            "Plot satellite path",
            key="plot_satellite_path"
        ):

            with st.spinner("Calculating satellite positions..."):

                offsets = np.arange(0, 24 * 60 + 1, 2)

                future_times = timescale.tt_jd(
                    now.tt + offsets / (24 * 60)
                )

                future_positions = (
                    satellite - observer
                ).at(future_times)

                future_elevation, future_azimuth, _ = (
                    future_positions.altaz()
                )

                elevation_values = future_elevation.degrees
                azimuth_values = future_azimuth.degrees

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
                        line=dict(width=2)
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

                st.subheader("Predicted Satellite Azimuth")

                fig_azimuth = go.Figure()

                fig_azimuth.add_trace(
                    go.Scatter(
                        x=plot_times,
                        y=azimuth_values,
                        mode="lines",
                        name="Azimuth",
                        line=dict(width=2)
                    )
                )

                fig_azimuth.update_layout(
                    title="Satellite Compass Direction Over Time",
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
                    "These graphs show predicted orbital positions, "
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

        st.caption(f"Technical details: {error}")

# ============================================================
# TAB 2: SIGNAL LABORATORY
# ============================================================

with tab_signals:

    st.header("Signal Laboratory")

    st.write(
        "Explore simulated radio signals, noise, Doppler shift, "
        "and FFT frequency spectra."
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

    # Original simulator's first-order Doppler calculation.
    speed_of_light = 299_792_458

    doppler_shift = (
        -frequency_mhz * 1e6 * velocity
        / speed_of_light
    )

    sample_rate = 20_000
    duration = 0.05
    samples = int(sample_rate * duration)

    time = np.arange(samples) / sample_rate

    tone_frequency = 1000.0

    # Apply Doppler shift to the baseband tone.
    # This remains a simplified educational simulation.
    baseband_shift = (
        -tone_frequency * velocity / speed_of_light
    )

    received_frequency = tone_frequency + baseband_shift

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

    col1.metric("Carrier", f"{frequency_mhz} MHz")

    col2.metric(
        "Carrier Doppler estimate",
        f"{doppler_shift:+.2f} Hz"
    )

    col3.metric(
        "Baseband tone",
        f"{received_frequency:.2f} Hz"
    )

    # Time-domain signal
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

    # FFT spectrum
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
        "The Signal Laboratory uses simulated baseband data. "
        "The carrier Doppler estimate and baseband demonstration "
        "are separate calculations. Neither represents a measured "
        "radio transmission."
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "HAMTRACK AI | Day 4 | Satellite Tracking, Sky-View Compass, "
    "Doppler Prediction & Signal Analysis"
)
