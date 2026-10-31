# HAMTRACK-AI

An educational amateur-radio and satellite-tracking application built with Python and Streamlit.

HAMTRACK-AI provides an interactive environment to explore satellite tracking, orbital passes, Doppler shift, and simulated radio signals.

## Features

- Ground-station dashboard
- Satellite tracking and orbital pass predictions
- Sky-view visualisation
- Satellite Doppler shift and received-frequency estimation
- Simulated signal generation with adjustable signal-to-noise ratio (SNR)
- Waveform and FFT spectrum analysis
- Interactive 3D Earth and satellite orbit visualisation

## Technology Stack

- Python
- Streamlit
- NumPy
- Plotly
- Skyfield
- Pillow

## Requirements

- Python 3
- Internet connection for downloading current satellite orbital data
- Python packages listed in `requirements.txt`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/annapoorna147/HAMTRACK-AI.git
cd HAMTRACK-AI
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

On macOS or Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the Application

Start the Streamlit application from the project directory:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to use the application.

## Run Tests

Run the automated test suite with:

```bash
python -m unittest discover -s tests -v
```

Alternatively, if `pytest` is installed:

```bash
python -m pytest -q
```

## Project Structure

```text
HAMTRACK-AI/
├── app.py
├── earth_globe.py
├── earth_satellites.py
├── hamtrack_math.py
├── satellite_data.py
├── satellite_loader.py
├── requirements.txt
├── README.md
├── assets/
└── tests/
```

## Limitations

- Doppler calculations use a first-order approximation.
- The Signal Laboratory simulates signals; it does not receive live radio transmissions.
- Satellite tracking requires current orbital data, normally downloaded over the internet.
- Satellite positions and pass predictions depend on the availability and freshness of orbital data.

## Project Status

HAMTRACK-AI is an educational prototype under active development.

## Repository

GitHub: https://github.com/annapoorna147/HAMTRACK-AI

## Satellite Data and Fallback

HAMTRACK-AI attempts to retrieve current amateur-satellite orbital
elements from CelesTrak. If live data cannot be loaded or validated,
the application can fall back to the local `amateur_satellites.tle` file.

The local TLE file is a snapshot and may become outdated. Satellite
positions and pass predictions calculated from stale orbital elements
may be less accurate. For the best results, use current orbital data
whenever an internet connection is available.

The Signal Laboratory uses simulated signals; it does not receive
live radio transmissions.
