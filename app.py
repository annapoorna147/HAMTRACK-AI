
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="HAMTRACK AI",
    page_icon="📡",
    layout="wide"
)

st.title("📡 HAMTRACK AI")
st.subheader("Amateur Radio Signal Laboratory")

st.write(
    "Explore radio signals, Doppler shift, and frequency "
    "spectra using software simulations."
)

st.sidebar.header("Signal Settings")

frequency_mhz = st.sidebar.selectbox(
    "Carrier frequency (MHz)",
    [145.0, 435.0, 14.2]
)

velocity = st.sidebar.slider(
    "Relative radial velocity (m/s)",
    -7500, 7500, 1000, step=100
)

snr_db = st.sidebar.slider(
    "Signal-to-noise ratio (dB)",
    -5, 30, 10
)

# Approximate first-order Doppler shift
speed_of_light = 299_792_458
doppler_shift = -frequency_mhz * 1e6 * velocity / speed_of_light

# Simulated baseband signal
sample_rate = 20_000
duration = 0.05
samples = int(sample_rate * duration)

time = np.arange(samples) / sample_rate
tone_frequency = 1000.0
received_frequency = tone_frequency + doppler_shift

rng = np.random.default_rng(42)

clean_signal = np.sin(
    2 * np.pi * received_frequency * time
)

signal_power = np.mean(clean_signal ** 2)
noise_power = signal_power / (10 ** (snr_db / 10))

noise = rng.normal(
    0, np.sqrt(noise_power), samples
)

received_signal = clean_signal + noise

col1, col2, col3 = st.columns(3)

col1.metric("Carrier", f"{frequency_mhz} MHz")
col2.metric("Doppler shift", f"{doppler_shift:.2f} Hz")
col3.metric("Baseband tone", f"{received_frequency:.2f} Hz")

st.divider()

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

st.plotly_chart(fig_time, use_container_width=True)

# Frequency-domain analysis
st.subheader("2. FFT Frequency Spectrum")

windowed_signal = received_signal * np.hanning(samples)

spectrum = np.fft.rfft(windowed_signal)
frequencies = np.fft.rfftfreq(
    samples, d=1 / sample_rate
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

st.plotly_chart(fig_fft, use_container_width=True)

st.info(
    "This is simulated baseband data, not a real radio recording. "
    "The Doppler calculation is a first-order approximation."
)

st.caption("HAMTRACK AI | Day 1 prototype")
