"""Satellite-data validation helpers for HAMTRACK-AI."""


class SatelliteDataError(ValueError):
    """Raised when satellite orbital data is empty or invalid."""


def validate_satellites(satellites):
    """Validate a collection of satellite objects and return it."""
    if satellites is None:
        raise SatelliteDataError("Satellite data is unavailable.")

    satellites = list(satellites)

    if not satellites:
        raise SatelliteDataError("No satellites were returned.")

    valid_satellites = []

    for satellite in satellites:
        name = getattr(satellite, "name", None)

        if not isinstance(name, str) or not name.strip():
            continue

        if not callable(getattr(satellite, "at", None)):
            continue

        valid_satellites.append(satellite)

    if not valid_satellites:
        raise SatelliteDataError(
            "Satellite data contains no usable satellite records."
        )

    return valid_satellites
