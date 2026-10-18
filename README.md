# HAMTRACK-AI

An educational amateur-radio and satellite-tracking application built with Python and Streamlit.

## Features
- Ground-station dashboard
- Satellite tracking and orbital pass predictions
- Sky-view visualisation
- Doppler shift and received-frequency estimation
- Simulated signal generation with adjustable SNR
- Waveform and FFT spectrum analysis

## Technology
- Python
- Streamlit
- NumPy
- Plotly
- Skyfield

## Installation
Clone the development branch:

```bash
git clone -b day5-dashboard https://github.com/annapoorna147/HAMTRACK-AI.git
cd HAMTRACK-AI
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the app
```bash
streamlit run app.py
```

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Limitations
- Doppler calculations use a first-order approximation.
- Signal Laboratory simulates signals; it does not receive live radio transmissions.
- Satellite tracking requires current orbital data, normally downloaded over the internet.

## Project status
HAMTRACK-AI is an educational prototype under active development.
