import unittest

from satellite_data import SatelliteDataError
from satellite_loader import (
    load_valid_satellites,
    load_satellites_with_fallback,
)


class SatelliteLoaderTests(unittest.TestCase):
    def test_valid_data_is_returned(self):
        satellite = type(
            "Satellite",
            (),
            {"name": "Satellite A", "at": lambda self, time: None},
        )()

        result = load_valid_satellites(lambda: [satellite])

        self.assertEqual(result, [satellite])

    def test_network_failure_has_clear_message(self):
        def failed_loader():
            raise OSError("connection refused")

        with self.assertRaisesRegex(
            RuntimeError, "Unable to download satellite orbital data"
        ) as context:
            load_valid_satellites(failed_loader)

        self.assertIsInstance(context.exception.__cause__, OSError)

    def test_empty_data_is_rejected(self):
        with self.assertRaises(SatelliteDataError):
            load_valid_satellites(lambda: [])

    def test_none_data_is_rejected(self):
        with self.assertRaises(SatelliteDataError):
            load_valid_satellites(lambda: None)


    def test_live_data_success_skips_fallback(self):
        satellite = type(
            "Satellite",
            (),
            {"name": "Live Satellite", "at": lambda self, time: None},
        )()

        def fallback_loader():
            self.fail("Fallback should not run when live data succeeds.")

        result, source, error = load_satellites_with_fallback(
            lambda: [satellite], fallback_loader
        )

        self.assertEqual(result, [satellite])
        self.assertEqual(source, "CelesTrak (live data)")
        self.assertIsNone(error)

    def test_live_failure_uses_local_fallback(self):
        satellite = type(
            "Satellite",
            (),
            {"name": "Local Satellite", "at": lambda self, time: None},
        )()

        def failed_live_loader():
            raise OSError("connection refused")

        result, source, error = load_satellites_with_fallback(
            failed_live_loader, lambda: [satellite]
        )

        self.assertEqual(result, [satellite])
        self.assertEqual(source, "Local TLE fallback")
        self.assertIsInstance(error, RuntimeError)
        self.assertIsInstance(error.__cause__, OSError)

    def test_both_sources_failing_raises_clear_error(self):
        def failed_loader():
            raise OSError("connection refused")

        with self.assertRaisesRegex(
            RuntimeError, "Unable to download satellite orbital data"
        ):
            load_satellites_with_fallback(
                failed_loader, failed_loader
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
