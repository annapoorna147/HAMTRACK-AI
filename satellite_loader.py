"""Reliable satellite-data loading helpers for HAMTRACK-AI."""

from satellite_data import validate_satellites


def load_valid_satellites(loader):
    """Load satellite records and validate them.

    The loader is injected so failures can be tested without
    requiring a live network connection.
    """
    try:
        satellites = loader()
    except Exception as error:
        raise RuntimeError(
            "Unable to download satellite orbital data. "
            "Check your internet connection and try again."
        ) from error

    return validate_satellites(satellites)
