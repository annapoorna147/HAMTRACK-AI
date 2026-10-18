import unittest
from types import SimpleNamespace

from satellite_data import (
    SatelliteDataError,
    validate_satellites,
)


def make_satellite(name):
    return SimpleNamespace(
        name=name,
        at=lambda time: None,
    )


class SatelliteValidationTests(unittest.TestCase):
    def test_valid_satellites_are_returned(self):
        satellites = [
            make_satellite("Satellite A"),
            make_satellite("Satellite B"),
        ]

        result = validate_satellites(satellites)

        self.assertEqual(result, satellites)

    def test_none_is_rejected(self):
        with self.assertRaises(SatelliteDataError):
            validate_satellites(None)

    def test_empty_list_is_rejected(self):
        with self.assertRaises(SatelliteDataError):
            validate_satellites([])

    def test_missing_name_is_rejected(self):
        invalid = SimpleNamespace(at=lambda time: None)

        with self.assertRaises(SatelliteDataError):
            validate_satellites([invalid])

    def test_missing_position_method_is_rejected(self):
        invalid = SimpleNamespace(name="Satellite A")

        with self.assertRaises(SatelliteDataError):
            validate_satellites([invalid])

    def test_invalid_records_are_filtered(self):
        valid = make_satellite("Satellite A")
        invalid = SimpleNamespace(name="", at=lambda time: None)

        result = validate_satellites([invalid, valid])

        self.assertEqual(result, [valid])


if __name__ == "__main__":
    unittest.main(verbosity=2)
