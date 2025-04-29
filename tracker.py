import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import geopandas as gpd
import glob

# Page configuration
st.set_page_config(
    page_title="NYC Bus Speed Tracker",
    page_icon="🚌",
    layout="wide"
)

# Initialize session state for toggle buttons if they don't exist
if 'color_blind_mode' not in st.session_state:
    st.session_state.color_blind_mode = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Set page background and text color based on dark mode
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            .stApp {
                background-color: #121212;
                color: white;
            }
            .stMarkdown, .stSelectbox, h1, h2, h3, .stSubheader, label {
                color: white !important;
            }
            .stSelectbox > div > div {
                background-color: #121212 !important;
                color: white !important;
            }
            div[data-baseweb="select"] > div {
                background-color: #121212 !important;
                color: white !important;
            }
            /* Added this for selectbox labels */
            .stSelectbox > label {
                color: white !important;
            }
            .stMarkdown a {
                color: #8ab4f8 !important;
            }
            /* Make buttons transparent */
            .stButton > button {
                background-color: transparent !important;
                border: 1px solid white !important;
                color: white !important;
            }
            .stButton > button:hover {
                border: 1px solid #4682B4 !important;
                color: #4682B4 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp {
                background-color: white;
                color: #333333;
            }
            /* Make buttons transparent */
            .stButton > button {
                background-color: transparent !important;
                border: 1px solid #333333 !important;
                color: #333333 !important;
            }
            .stButton > button:hover {
                border: 1px solid #4682B4 !important;
                color: #4682B4 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# App title and description
st.title("NYC Bus Speed Tracker")
st.markdown("""
    Curious whether [Central Business District Tolling Program](https://www.mta.info/project/CBDTP) (CBDTP), or **Congestion Pricing**, is having an impact on bus speeds in NYC?  
    Take a look below to compare bus speed data before and after Congestion Pricing began on **January 5th, 2025**, powered by MTA's realtime bus travel data.
""")


route_data = {
    "Route B39: Williamsburg Bridge": {
        "id": "B39",
        "geojson_file": "data/map-segments/mdb-512_B39_unique_segments.geojson",
        "is_affected": True
    },
    "Route SIM24: Lincoln Tunnel": {
        "id": "SIM24",
        "geojson_file": "data/map-segments/mdb-514_SIM24_unique_segments.geojson",
        "is_affected": True
    },
    "Route SIM4X: Hugh Carey Tunnel": {
        "id": "SIM4X",
        "geojson_file": "data/map-segments/mdb-514_SIM4X_unique_segments.geojson",
        "is_affected": True
    },
    "Route M102: CBD North/South": {
        "id": "M102",
        "geojson_file": "data/map-segments/mdb-513_M102_unique_segments.geojson",
        "is_affected": True
    },
    "Route M50: CBD East/West": {
        "id": "M50",
        "geojson_file": "data/map-segments/mdb-513_M50_unique_segments.geojson",
        "is_affected": True
    }
}


route_options = list(route_data.keys())

# Day options
day_options = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"]

# Set default values for route and day
default_route = route_options[0]
default_day = day_options[2]  # Wednesday

# Function to toggle modes
def toggle_color_blind_mode():
    st.session_state.color_blind_mode = not st.session_state.color_blind_mode

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

def get_speed_data(route, day):
    # Convert day string to weekday number (0 = Monday, 6 = Sunday)
    day_to_num = {
        "Mondays": 0,
        "Tuesdays": 1,
        "Wednesdays": 2,
        "Thursdays": 3,
        "Fridays": 4,
        "Saturdays": 5,
        "Sundays": 6
    }
    weekday = day_to_num[day]
    
    # Get route ID from the route data
    route_id = route_data[route]["id"]
    
    # Read both control and treatment speeds data
    before_data = pd.read_parquet("data/chart-speeds/control_speeds.parquet")
    after_data = pd.read_parquet("data/chart-speeds/treatment_speeds.parquet")
    
    # Filter data for specific route and weekday
    before_data = before_data[
        (before_data["route_id"] == route_id) & 
        (before_data["weekday"] == weekday)
    ].sort_values("hour")
    
    after_data = after_data[
        (after_data["route_id"] == route_id) & 
        (after_data["weekday"] == weekday)
    ].sort_values("hour")
    
    return before_data, after_data

def get_segment_speed_diff(route_id, weekday, rush_hour):
    """Get speed differences for route segments"""
    try:
        # 1. Read Speed Diff Data
        speed_diff_pattern = f"data/map-speeds/*_{route_id}_speed_diff.parquet"
        speed_diff_files = glob.glob(speed_diff_pattern)
        
        if not speed_diff_files:
            st.warning(f"No speed difference data found for route {route_id}")
            return None
            
        speed_diff_data = pd.read_parquet(speed_diff_files[0])
        
        # Filter by weekday and rush hour
        speed_diff_data = speed_diff_data[
            (speed_diff_data["weekday"] == weekday) & 
            (speed_diff_data["rush_hour"] == rush_hour)
        ]
        
        if speed_diff_data.empty:
            st.warning("No data found for selected weekday and rush hour")
            return None
        
        # 2. Read Segment Geometry Data
        segment_geo_pattern = f"data/map-segments/*_{route_id}_unique_segments.geojson"
        segment_geo_files = glob.glob(segment_geo_pattern)
        
        if not segment_geo_files:
            st.warning(f"No segment geometry data found for route {route_id}")
            return None
        
        # Read the GeoJSON with explicit CRS
        segments_geo = gpd.read_file(segment_geo_files[0])
        
        # Ensure the CRS is set correctly for the source data
        if segments_geo.crs is None:
            segments_geo.set_crs(epsg=2263, inplace=True)
        
        # Convert to WGS84 (EPSG:4326) for web mapping
        segments_geo = segments_geo.to_crs('EPSG:4326')

        # 3. Merge speed data with geometry
        merged_data = speed_diff_data.merge(
            segments_geo,
            how='inner',
            left_on=['prev_stop_id', 'stop_id'],
            right_on=['prev_stop_id', 'stop_id']
        )

        if merged_data.empty:
            st.warning("No matching segments found after merging")
            return None
            
        # Convert to GeoDataFrame to ensure geometry handling is correct
        merged_data = gpd.GeoDataFrame(merged_data, geometry='geometry', crs='EPSG:4326')
            
        return merged_data
        
    except Exception as e:
        st.error(f"Error loading segment data: {str(e)}")
        return None

def create_color_gradient_legend(max_abs_diff, decrease_color, increase_color):
    # Create color gradient for legend
    n_steps = 11  # Same number of steps as in map
    gradient_colors = []
    
    # Convert hex colors to RGB
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    
    decrease_rgb = hex_to_rgb(decrease_color)
    increase_rgb = hex_to_rgb(increase_color)
    
    # Add decrease color gradient (orange)
    for i in range(n_steps // 2):
        intensity = 2 * i / (n_steps - 1)
        alpha = 0.3 + 0.7 * intensity
        r, g, b = decrease_rgb
        gradient_colors.append(f"rgba({r}, {g}, {b}, {alpha})")
    
    # Add white for zero
    gradient_colors.append("rgb(255, 255, 255)")
    
    # Add increase color gradient (blue)
    for i in range(n_steps // 2 + 1, n_steps):
        intensity = 2 * (i - n_steps // 2) / (n_steps - 1)
        alpha = 0.3 + 0.7 * intensity
        r, g, b = increase_rgb
        gradient_colors.append(f"rgba({r}, {g}, {b}, {alpha})")
    
    # Create CSS gradient string
    gradient_str = ", ".join([f"{color} {i * 100 / (len(gradient_colors)-1)}%" for i, color in enumerate(gradient_colors)])
    
    return f"""
    <div style="display: flex; align-items: center; justify-content: center; margin: 10px 0;">
        <div style="display: flex; align-items: center;">
            <div style="text-align: right; min-width: 60px;">
                <span style="font-size: 12px;">{-max_abs_diff:.1f} mph</span>
            </div>
            <div style="width: 200px; height: 15px; margin: 0 8px;
                background: linear-gradient(to right, {gradient_str});
                border: 1px solid #ccc;">
            </div>
            <div style="text-align: left; min-width: 60px;">
                <span style="font-size: 12px;">+{max_abs_diff:.1f} mph</span>
            </div>
        </div>
    </div>
    """

def create_map(route_name, rush_hour, weekday):
    """Create map visualization for route segments"""
    # Get route ID
    route_id = route_data[route_name]["id"]
    
    # Get segment speed differences with geometry
    segments_data = get_segment_speed_diff(route_id, weekday, rush_hour)
    
    # Create the base map
    fig = go.Figure()
    
    if segments_data is not None and not segments_data.empty:
        # Calculate bounds and speed ranges
        all_lons = []
        all_lats = []
        max_abs_diff = max(abs(segments_data['avg_speed_diff'].max()), 
                          abs(segments_data['avg_speed_diff'].min()))
        # Round up to nearest whole number for cleaner scale
        max_abs_diff = np.ceil(max_abs_diff)
        
        # Set colors based on color blind mode
        if st.session_state.color_blind_mode:
            decrease_color = '#D55E00'  # Orange-red for color blind
            increase_color = '#0072B2'  # Blue for color blind
        else:
            decrease_color = '#FF6347'  # Tomato red
            increase_color = '#4169E1'  # Royal blue
        
        # Add each segment as a separate line
        for _, segment in segments_data.iterrows():
            speed_diff = segment["avg_speed_diff"]
            # TODO: might change later
            speed_diff = -speed_diff
            
            # Extract coordinates
            coords = list(segment['geometry'].coords)
            lons, lats = zip(*coords)
            all_lons.extend(lons)
            all_lats.extend(lats)
            
            # Set color based on speed difference
            # Normalize the color intensity based on absolute value
            color_intensity = min(1.0, abs(speed_diff) / max_abs_diff)
            
            if speed_diff > 0:
                # Increase color with intensity
                rgb_color = increase_color
                alpha = 0.3 + 0.7 * color_intensity
                color = f'rgba{tuple(list(int(rgb_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [float(alpha)])}'

            else:
                # Decrease color with intensity
                rgb_color = decrease_color
                alpha = 0.3 + 0.7 * color_intensity
                color = f'rgba{tuple(list(int(rgb_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [float(alpha)])}'
            
            # Add segment to map
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=lons,
                lat=lats,
                line=dict(width=3, color=color),
                name=f"Stop {segment['prev_stop_id']} to {segment['stop_id']}: {speed_diff:+.1f} mph",
                showlegend=False,
                hoverinfo="text",
                hovertext=f"From Stop: {segment['prev_stop_name']}<br>To Stop: {segment['stop_name']}<br>Speed change: {speed_diff:+.1f} mph"
            ))
        
        # Calculate center and zoom
        center_lat = (max(all_lats) + min(all_lats)) / 2
        center_lon = (max(all_lons) + min(all_lons)) / 2
        
        lat_range = max(all_lats) - min(all_lats)
        lon_range = max(all_lons) - min(all_lons)
        
        # Use smaller multipliers to zoom in more and show all segments clearly
        lat_range *= 1.02  # Reduced from 1.05 to zoom in more
        lon_range *= 1.02  # Reduced from 1.05 to zoom in more
        
        # Calculate zoom level with a larger increase to zoom in more
        zoom = min(
            np.log2(360 / lon_range),
            np.log2(180 / lat_range)
        ) + 1.0  # Increased from 0.5 to 1.0 to zoom in more
        
        # Create more detailed colorscale with smooth transitions
        n_steps = 11  # Number of color steps
        colorscale = []
        
        # Convert hex colors to RGB
        decrease_rgb = tuple(int(decrease_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        increase_rgb = tuple(int(increase_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        
        # Add decrease color gradient
        for i in range(n_steps // 2):
            pos = i / (n_steps - 1)
            intensity = 2 * i / (n_steps - 1)
            r = int(decrease_rgb[0] * (0.6 + 0.4 * intensity))
            g = int(decrease_rgb[1] * (1-intensity))
            b = int(decrease_rgb[2] * (1-intensity))
            colorscale.append([pos, f'rgb({r}, {g}, {b})'])
        
        # Add white for zero
        colorscale.append([0.5, 'rgb(255, 255, 255)'])
        
        # Add increase color gradient
        for i in range(n_steps // 2 + 1, n_steps):
            pos = i / (n_steps - 1)
            intensity = 2 * (i - n_steps // 2) / (n_steps - 1)
            r = int(increase_rgb[0] * (1-intensity))
            g = int(increase_rgb[1] * (0.6 + 0.4 * intensity))
            b = int(increase_rgb[2] * (1-intensity))
            colorscale.append([pos, f'rgb({r}, {g}, {b})'])
        
        # Add a continuous color scale
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[],
            lat=[],
            marker=dict(
                size=10,
                colorscale=colorscale,
                colorbar=dict(
                    title=dict(
                        text="Speed Difference (mph)",
                        font=dict(size=12)
                    ),
                    thickness=15,
                    len=0.75,
                    x=0.9,
                    xpad=10,
                    tickmode='array',
                    tickvals=np.linspace(-max_abs_diff, max_abs_diff, 9),
                    ticktext=[f"{x:+.1f}" for x in np.linspace(-max_abs_diff, max_abs_diff, 9)],
                    tickfont=dict(size=10),
                    outlinewidth=0,
                    ticklabelposition="outside"
                ),
                cmin=-max_abs_diff,
                cmax=max_abs_diff,
                showscale=True
            ),
            showlegend=False
        ))
        
        # Set map layout
        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter" if st.session_state.dark_mode else "carto-positron",
                zoom=zoom - 1.0,  # Zoom out more to show all segments
                center=dict(lat=center_lat, lon=center_lon),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=375,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)" if st.session_state.dark_mode else "rgba(255,255,255,0)",
                font=dict(color=text_color)
            )
        )

        # Replace the current legend section with:
        if segments_data is not None and not segments_data.empty:
            max_abs_diff = max(abs(segments_data['avg_speed_diff'].max()), 
                              abs(segments_data['avg_speed_diff'].min()))
            max_abs_diff = np.ceil(max_abs_diff)  # Round up to nearest whole number
            st.markdown(
                create_color_gradient_legend(max_abs_diff, decrease_color, increase_color),
                unsafe_allow_html=True
            )
    else:
        # Default view for NYC if no segments
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=12,
                center=dict(lat=40.75, lon=-73.98),  # NYC center
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=440,
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(0,0,0,0)" if st.session_state.dark_mode else "rgba(255,255,255,0)",
                font=dict(color=text_color)
            )
        )
        print("No segment data available for the selected time period")
    
    return fig



# Add Accessibility options here
access_col1, access_col2, access_col3 = st.columns([1, 1, 2])
with access_col1:
    st.toggle("Color Blind Mode", 
              value=st.session_state.color_blind_mode,
              on_change=toggle_color_blind_mode)
with access_col2:
    st.toggle("Dark Mode", 
              value=st.session_state.dark_mode,
              on_change=toggle_dark_mode)
with access_col3:
    # Empty column for spacing
    pass

# Display the chart and map side by side with 2:1 ratio
col1, col2 = st.columns([2, 1])

with col1:   
    # Add the subheader to the chart column
    st.subheader("Hourly Bus Speed for")
    
    # Create two columns for the route and day selection
    filter_col1, filter_col2 = st.columns([4, 2])
    
    with filter_col1:
        selected_route = st.selectbox("", route_options, index=4, label_visibility="collapsed")
    with filter_col2:
        selected_day = st.selectbox("on", day_options, index=2, label_visibility="collapsed")
    
    # Get data based on selection
    before_data, after_data = get_speed_data(selected_route, selected_day)

    # Check if data is available
    if before_data.empty and after_data.empty:
        st.warning(f"No data found for {selected_route} on {selected_day}")
    
    # Create the plot using Plotly
    fig = go.Figure()
    
    # Create a complete set of hours (0-23)
    all_hours = pd.Series(range(24))
    
    # Reindex and interpolate both datasets to ensure they have values at all hours
    before_interp = before_data.set_index('hour')['average_speed_mph'].reindex(all_hours).interpolate(method='linear')
    after_interp = after_data.set_index('hour')['average_speed_mph'].reindex(all_hours).interpolate(method='linear')

    # Choose colors based on color blind mode
    if st.session_state.color_blind_mode:
        before_color = "#D55E00"   # Orange-red that works well for color blind users
        after_color = "#0072B2"    # Blue that works well for color blind users
        before_fill = "rgba(213, 94, 0, 0.2)"    # Light orange fill
        after_fill = "rgba(0, 114, 178, 0.2)"    # Light blue fill
    else:
        before_color = "#FF6347"   # Tomato red
        after_color = "#4169E1"    # Royal blue
        before_fill = "rgba(255, 99, 71, 0.2)"   # Light tomato red fill
        after_fill = "rgba(65, 105, 225, 0.2)"   # Light blue fill


    # Choose background based on dark mode
    bg_color = "#121212" if st.session_state.dark_mode else "#FFFFFF"
    text_color = "#FFFFFF" if st.session_state.dark_mode else "#333333"
    grid_color = "rgba(255,255,255,0.1)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)"
    
    # Add filled area for before line
    fig.add_trace(go.Scatter(
        x=all_hours,
        y=before_interp,
        mode='lines',
        line=dict(width=0),
        fill='tozeroy',
        fillcolor=before_fill,
        name='',
        showlegend=False,
        hoverinfo='skip'  # Skip hover info for filled areas
    ))
    
    # Add filled area for after line
    fig.add_trace(go.Scatter(
        x=all_hours,
        y=after_interp,
        mode='lines',
        line=dict(width=0),
        fill='tozeroy',
        fillcolor=after_fill,
        name='',
        showlegend=False,
        hoverinfo='skip'  # Skip hover info for filled areas
    ))
    
    # Add the lines
    fig.add_trace(go.Scatter(
        x=all_hours,
        y=before_interp,
        mode='lines',
        line=dict(
            color=before_color, 
            width=2, 
            dash='dash',
            shape='spline',# This creates a smoothed curve
            smoothing=0.3 # Adjust smoothing factor (0.5-1.5 range works well)
        ),   
        name='Before Jan 5th',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=all_hours,
        y=after_interp,
        mode='lines',
        line=dict(
            color=after_color, 
            width=2,
            shape='spline',# This creates a smoothed curve
            smoothing=0.3 # Adjust smoothing factor (0.5-1.5 range works well)
        ),
        name='Jan 5th and After',
        showlegend=True
    ))
    
    # Update layout
    fig.update_layout(
        title="",
        xaxis=dict(
            title='Time of Day',
            tickmode='array',
            tickvals=list(range(24)),
            ticktext=['12 am', '1 am', '2 am', '3 am', '4 am', '5 am', 
                     '6 am', '7 am', '8 am', '9 am', '10 am', '11 am',
                     '12 pm', '1 pm', '2 pm', '3 pm', '4 pm', '5 pm', 
                     '6 pm', '7 pm', '8 pm', '9 pm', '10 pm', '11 pm'],
            gridcolor=grid_color,
            color=text_color,
            title_font_color=text_color,
            tickfont_color=text_color,
        ),
        yaxis=dict(
            title_text='Average Bus Speed (mph)',
            title_standoff=10,
            gridcolor=grid_color,
            color=text_color,
            title_font_color=text_color,
            tickfont_color=text_color,
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)" if st.session_state.dark_mode else "rgba(255,255,255,0)",
            font=dict(color=text_color)
        ),
        margin=dict(l=50, r=20, t=50, b=50),  # Increased top margin to accommodate legend
        height=500,
        autosize=True,
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Speed Difference Map")
    # Rush hour selection - use exact strings that match the parquet data
    rush_hours = {
        "Morning Rush": "morning_rush",
        "Evening Rush": "evening_rush"
    }
    selected_rush_hour = st.radio("Select rush hour period:", 
                                list(rush_hours.keys()), 
                                index=0,
                                horizontal=True)
    
    # Get weekday number for the selected day
    day_to_num = {
        "Mondays": 0, "Tuesdays": 1, "Wednesdays": 2, "Thursdays": 3,
        "Fridays": 4, "Saturdays": 5, "Sundays": 6
    }
    selected_weekday = day_to_num[selected_day]
    
    # Pass the exact rush hour string value to create_map
    map_fig = create_map(selected_route, rush_hours[selected_rush_hour], selected_weekday)
    st.plotly_chart(map_fig, use_container_width=True)

# Explanatory text
st.markdown("""
The chart above shows bus speeds for a chosen route and day of week. The red and blue lines calculate average hourly bus speeds before and after Congestion Pricing, respectively.                   

The map displays the selected route with color indicating the speed difference between January 2025 (after Congestion Pricing) 
and December 2024 (before Congestion Pricing) by segment. Blue indicates faster speeds after Congestion Pricing, while red indicates slower speeds.

Routes selected are located within or on a direct path to the [Congestion Relief Zone](https://congestionreliefzone.mta.info/), with a focus on those cross the East or Hudson Rivers into Manhattan.

Dates selected provide a month of data before and after the January 5th implementation date for comparison. Specifically:
- Before congestion pricing: December 3, 2024 - January 4, 2025
- After congestion pricing: January 5, 2025 - February 6, 2025

""")

# Add a footer
st.markdown("---")
st.markdown("© 2025 NYC Bus Speed Tracker | [Urban Tech Hub](https://urban.tech.cornell.edu/)")
st.markdown("""
This project is run by **[Huaiying Luo](https://www.linkedin.com/in/huaiying-luo/)**, under the supervision of **Dr. Anthony Townsend**
@ Urban Tech Hub, Cornell Tech.

Questions or comments can be directed to hl2446@cornell.edu or amt353@cornell.edu.

Special thanks to **Canyon Foot** and **Kaushik Mohan** for their foundational work on the data archive system of GTFS-realtime data.
""")
