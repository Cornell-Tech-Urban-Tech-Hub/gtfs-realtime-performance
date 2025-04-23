# Bus Speed Tracker Application

This application visualizes bus speed data before and after congestion pricing implementation in NYC.

## How to Run the App

1. Make sure you have all the required dependencies installed:
   ```
   pip install streamlit pandas numpy plotly geopandas matplotlib
   ```

2. Navigate to the application directory:
   ```
   cd application
   ```

3. Run the Streamlit application:
   ```
   streamlit run tracker.py
   ```

4. The application will open in your default web browser at http://localhost:8501

## Features

1. Interactive visualization of bus speeds before and after congestion pricing
   - Route selection for different bus lines
   - Day of week filtering
2. Interactive map showing speed differences along routes
   - Route and day of week pre-selected as above
   - Morning and evening rush hour selection
3. Accessibility options (Color Blind Mode and Dark Mode)

## Data Sources

1. Route Data:
   Stored in a dictionary `route_data` containing information about 5 specific bus routes:
   - B39 (Williamsburg Bridge)
   - SIM24 (Lincoln Tunnel)
   - SIM4X (Hugh Carey Tunnel)
   - M102 (CBD North/South)
   - M50 (CBD East/West)

2. Speed Data:
   - Two main parquet files:
     - `../data/chart-speeds/control_speeds.parquet` (before congestion pricing)
     - `../data/chart-speeds/treatment_speeds.parquet` (after congestion pricing)
   - These files contain hourly average speed data for each route

3. Map Segment Data:
   - GeoJSON files for route segments stored in:
     - `../data/map-segments/`
   - Files follow the pattern: `{mdb_id}_{route_id}_unique_segments.geojson`
   - Contains geometry data for each route segment

4. Speed Difference Data:
   - Parquet files for speed differences stored in:
     - `../data/map-speeds/`
   - Files follow the pattern: `*_{route_id}_speed_diff.parquet`
   - Contains speed difference data between before and after congestion pricing periods. Negative speed difference shows that speed decreased after congestion pricing implementation.
