import unittest

from satellite_data import SatelliteDataError
from satellite_loader import load_valid_satellites


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
