import unittest
import numpy as np

from hamtrack_math import (
    SPEED_OF_LIGHT_M_S,
    calculate_doppler_shift,
    calculate_received_frequency,
    calculate_baseband_frequency,
    generate_noisy_signal,
)


class DopplerTests(unittest.TestCase):
    def test_approaching_satellite_has_positive_shift(self):
        shift = calculate_doppler_shift(145e6, -1000)
        self.assertGreater(float(shift), 0)

    def test_receding_satellite_has_negative_shift(self):
        shift = calculate_doppler_shift(145e6, 1000)
        self.assertLess(float(shift), 0)

    def test_zero_range_rate_has_zero_shift(self):
        shift = calculate_doppler_shift(145e6, 0)
        self.assertAlmostEqual(float(shift), 0.0)

    def test_doppler_magnitude_matches_formula(self):
        shift = calculate_doppler_shift(145e6, -1000)
        expected = 145e6 * 1000 / SPEED_OF_LIGHT_M_S
        self.assertAlmostEqual(float(shift), expected, places=9)

    def test_received_frequency_is_carrier_plus_shift(self):
        carrier = 145e6
        shift = calculate_doppler_shift(carrier, -1000)
        received = calculate_received_frequency(carrier, shift)
        self.assertAlmostEqual(float(received), carrier + float(shift))

    def test_array_inputs_preserve_shape(self):
        shifts = calculate_doppler_shift(145e6, np.array([-1000, 0, 1000]))
        self.assertEqual(shifts.shape, (3,))
        self.assertGreater(shifts[0], 0)
        self.assertAlmostEqual(shifts[1], 0)
        self.assertLess(shifts[2], 0)


class SignalTests(unittest.TestCase):
    def test_baseband_frequency_shifts_with_velocity(self):
        approaching = calculate_baseband_frequency(1000, -1000)
        receding = calculate_baseband_frequency(1000, 1000)
        self.assertGreater(float(approaching), 1000)
        self.assertLess(float(receding), 1000)

    def test_signal_has_expected_sample_count(self):
        time, signal = generate_noisy_signal(1000)
        self.assertEqual(len(time), 1000)
        self.assertEqual(len(signal), 1000)

    def test_signal_samples_are_finite(self):
        _, signal = generate_noisy_signal(1000)
        self.assertTrue(np.isfinite(signal).all())

    def test_signal_generation_is_reproducible(self):
        _, first = generate_noisy_signal(1000, seed=42)
        _, second = generate_noisy_signal(1000, seed=42)
        np.testing.assert_array_equal(first, second)

    def test_invalid_sample_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_noisy_signal(1000, sample_rate=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
