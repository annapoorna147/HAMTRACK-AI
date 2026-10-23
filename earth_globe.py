"""Lightweight NASA-textured 3D Earth globe for HAMTRACK-AI."""

from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from PIL import Image

TEXTURE_PATH = Path(__file__).parent / "assets" / "earth_texture.jpg"


def create_earth_globe():
    """Create a browser-friendly 3D Earth with satellite-image colors."""
    if not TEXTURE_PATH.exists():
        raise FileNotFoundError(
            f"Earth texture not found: {TEXTURE_PATH}"
        )

    # Lower mesh resolution to keep Plotly's serialized payload manageable.
    image = Image.open(TEXTURE_PATH).convert("RGB")
    image.thumbnail((240, 120), Image.Resampling.LANCZOS)
    rgb = np.asarray(image, dtype=np.uint8)

    height, width, _ = rgb.shape

    longitude = np.linspace(-180, 180, width)
    latitude = np.linspace(90, -90, height)
    lon, lat = np.meshgrid(longitude, latitude)

    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)

    x = (np.cos(lat_rad) * np.cos(lon_rad)).ravel()
    y = (np.cos(lat_rad) * np.sin(lon_rad)).ravel()
    z = np.sin(lat_rad).ravel()

    # Store one color per vertex instead of generating thousands of
    # high-resolution triangles from the full source image.
    vertex_colors = [
        f"rgb({r},{g},{b})"
        for r, g, b in rgb.reshape(-1, 3)
    ]

    rows, cols = np.indices((height - 1, width - 1))
    a = (rows * width + cols).ravel()
    b = a + 1
    c = a + width
    d = c + 1

    i = np.concatenate((a, b, a, b))
    j = np.concatenate((c, c, d, d))
    k = np.concatenate((b, d, c, c))

    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=x,
                y=y,
                z=z,
                i=i,
                j=j,
                k=k,
                vertexcolor=vertex_colors,
                flatshading=False,
                hoverinfo="skip",
                lighting=dict(
                    ambient=0.8,
                    diffuse=0.8,
                    specular=0.12,
                    roughness=0.85,
                ),
                lightposition=dict(x=100, y=150, z=200),
                name="NASA Earth",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="🌍 HAMTRACK-AI | Earth Explorer",
            x=0.5,
            font=dict(size=22, color="white"),
        ),
        paper_bgcolor="#050B16",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=65, b=0),
        height=700,
        scene=dict(
            bgcolor="#050B16",
            aspectmode="cube",
            xaxis=dict(visible=False, range=[-1.08, 1.08]),
            yaxis=dict(visible=False, range=[-1.08, 1.08]),
            zaxis=dict(visible=False, range=[-1.08, 1.08]),
            camera=dict(
                eye=dict(x=1.55, y=1.55, z=0.9),
                center=dict(x=0, y=0, z=0),
                projection=dict(type="orthographic"),
            ),
        ),
    )

    return fig
