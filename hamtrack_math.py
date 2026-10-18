"""Reusable numerical calculations for HAMTRACK-AI."""

import numpy as np

SPEED_OF_LIGHT_M_S = 299_792_458.0


def calculate_doppler_shift(
    carrier_hz,
    range_rate_m_s,
):
    """Calculate first-order Doppler shift in Hz.

    Positive range rate means the satellite is moving away.
    Negative range rate means the satellite is approaching.
    """
    return (
        -np.asarray(carrier_hz)
        * np.asarray(range_rate_m_s)
        / SPEED_OF_LIGHT_M_S
    )


def calculate_received_frequency(carrier_hz, doppler_hz):
    """Calculate received frequency in Hz."""
    return np.asarray(carrier_hz) + np.asarray(doppler_hz)


def calculate_baseband_frequency(tone_hz, velocity_m_s):
    """Calculate the simplified Doppler-shifted baseband tone."""
    shift_hz = (
        -np.asarray(tone_hz)
        * np.asarray(velocity_m_s)
        / SPEED_OF_LIGHT_M_S
    )
    return np.asarray(tone_hz) + shift_hz


def generate_noisy_signal(
    frequency_hz,
    sample_rate=20_000,
    duration=0.05,
    snr_db=10,
    seed=42,
):
    """Generate a sine wave with reproducible Gaussian noise."""
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive.")
    if duration <= 0:
        raise ValueError("Duration must be positive.")

    sample_count = int(sample_rate * duration)
    if sample_count < 1:
        raise ValueError("Duration must produce at least one sample.")

    time = np.arange(sample_count) / sample_rate
    clean_signal = np.sin(2 * np.pi * frequency_hz * time)

    signal_power = np.mean(clean_signal ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))

    rng = np.random.default_rng(seed)
    noise = rng.normal(0, np.sqrt(noise_power), sample_count)

    return time, clean_signal + noise
