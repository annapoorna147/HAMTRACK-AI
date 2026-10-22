from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from skyfield.api import load
from skyfield.framelib import itrs

from earth_globe import create_earth_globe


TLE_FILE = Path(__file__).parent / "amateur_satellites.tle"
EARTH_RADIUS_KM = 6371.0


def load_amateur_satellites():
    """Load satellites from the local TLE file."""
    if not TLE_FILE.exists():
        raise FileNotFoundError(f"TLE file not found: {TLE_FILE}")

    return load.tle_file(str(TLE_FILE))


def orbital_period_minutes(satellite):
    """Estimate orbital period from the satellite's mean motion."""
    mean_motion = satellite.model.no_kozai  # radians per minute

    if mean_motion <= 0:
        raise ValueError(
            f"Invalid mean motion for {satellite.name}"
        )

    return 2 * np.pi / mean_motion


def calculate_orbit(satellite, timescale, now, samples=180):
    """Calculate an orbit in Earth-fixed coordinates."""
    period = orbital_period_minutes(satellite)

    offsets = np.linspace(
        -period / 2,
        period / 2,
        samples,
    )

    times = timescale.tt_jd(
        now.tt + offsets / 1440.0
    )

    positions = satellite.at(times).frame_xyz(itrs).km
    positions = np.asarray(positions)

    # Scale to the same Earth-radius coordinate system as the globe.
    x = positions[0] / EARTH_RADIUS_KM
    y = positions[1] / EARTH_RADIUS_KM
    z = positions[2] / EARTH_RADIUS_KM

    return x, y, z, period


def add_satellites_to_globe(
    satellite_names=None,
    orbit_samples=180,
):
    """Create a globe with satellite markers and orbital paths."""
    satellites = load_amateur_satellites()
    timescale = load.timescale(builtin=True)
    now = timescale.now()

    if satellite_names is None:
        satellite_names = [
            "OSCAR 7 (AO-7)",
            "UOSAT 2 (UO-11)",
            "ISS (ZARYA)",
        ]

    satellite_lookup = {
        satellite.name: satellite
        for satellite in satellites
    }

    figure = create_earth_globe()
    plotted = 0

    for name in satellite_names:
        satellite = satellite_lookup.get(name)

        if satellite is None:
            print(f"Satellite not found in TLE file: {name}")
            continue

        x, y, z, period = calculate_orbit(
            satellite,
            timescale,
            now,
            samples=orbit_samples,
        )

        # Orbital trajectory.
        figure.add_trace(
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="lines",
                name=f"{name} orbit",
                line=dict(width=5, color="#00E5FF"),
                hovertemplate=(
                    f"{name}<br>"
                    "Orbital trajectory"
                    "<extra></extra>"
                ),
            )
        )

        # Current position.
        current_position = satellite.at(now).frame_xyz(itrs).km
        current_position = np.asarray(current_position) / EARTH_RADIUS_KM

        figure.add_trace(
            go.Scatter3d(
                x=[current_position[0]],
                y=[current_position[1]],
                z=[current_position[2]],
                mode="markers",
                name=name,
                marker=dict(size=7, color="#FF3B30", line=dict(width=1, color="white")),
                customdata=[[satellite.at(now).subpoint().elevation.km]],
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    "Current satellite position"
                    "<br>Altitude: %{customdata[0]:.1f} km"
                    "<extra></extra>"
                ),
            )
        )

        plotted += 1
        print(
            f"Prepared {name}: "
            f"estimated period {period:.1f} minutes"
        )

    figure.update_layout(
        title="HAMTRACK-AI | Satellite Orbit Explorer",
        height=650,
        showlegend=True,
        margin=dict(l=0, r=0, t=55, b=0),
    )

    print(f"Satellites plotted: {plotted}")
    print("Calculation time (UTC):", now.utc_strftime("%Y-%m-%d %H:%M:%S"))

    return figure
