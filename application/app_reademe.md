# Bus Speed Tracker Application

This application visualizes bus speed data before and after congestion pricing implementation in NYC.

## How to Run the Demo

1. Make sure you have all the required dependencies installed:
   ```
   pip install streamlit pandas numpy plotly geopandas
   ```

2. Navigate to the application directory:
   ```
   cd application
   ```

3. Run the Streamlit application:
   ```
   streamlit run demo.py
   ```

4. The application will open in your default web browser at http://localhost:8501

## Features

- Interactive visualization of bus speeds before and after congestion pricing
- Route selection for different bus lines
- Day of week filtering
- Morning and evening rush hour analysis
- Accessibility options (Color Blind Mode and Dark Mode)
- Interactive map showing speed differences along routes

## Data Notes

The demo uses simulated data. When connected to real data sources, the application will display actual bus speed patterns.


## TODO:
code
- use r trees to speed up merging of speed and segment?
- create dict for segment, speed for faster look up
- rearrange aggregation notebook
- Fix the reversed diff of the map

UI
- toggle for rush hour
- color match of the chart and the map
- Line smoothing
- color the gap between lines (Seaborn, Altair)
- dark mode for the map




