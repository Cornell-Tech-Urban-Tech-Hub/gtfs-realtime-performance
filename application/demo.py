import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import geopandas as gpd

# Page configuration
st.set_page_config(
    page_title="Bus Speed Tracker",
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
st.title("Bus Speed Tracker")
st.markdown(
    "Curious whether Congestion Pricing is having an impact on bus speeds in NYC? "
    "Take a look below to compare bus speed data before and after Congestion Pricing began on January 5th, 2025."
)

# Create fake route options with route data
route_data = {
    "Route B39: Williamsburg Bridge": {
        "id": "B39",
        "polyline": [
            # Holland Tunnel to Midtown path coordinates
            [40.7273, -74.0094],
            [40.7266, -74.0037],
            [40.7262, -73.9986],
            [40.7282, -73.9945],
            [40.7332, -73.9902],
            [40.7380, -73.9862],
            [40.7427, -73.9818],
            [40.7473, -73.9774],
            [40.7518, -73.9730],
            [40.7565, -73.9687], # Midtown point
        ],
        "is_affected": True
    },
    "Route SIM24: Lincoln Tunnel": {
        "id": "SIM24",
        "polyline": [
            # Lincoln Tunnel to Midtown path coordinates
            [40.7588, -74.0106],
            [40.7593, -74.0053],
            [40.7598, -74.0002],
            [40.7602, -73.9954],
            [40.7606, -73.9906],
            [40.7613, -73.9851],
            [40.7618, -73.9800],
            [40.7624, -73.9749],
            [40.7629, -73.9699], # Midtown point
        ],
        "is_affected": True
    },
    "Route SIM4X: Hugh Carey Tunnel": {
        "id": "SIM4X",
        "polyline": [
            # Queens Midtown Tunnel to Midtown path coordinates
            [40.7431, -73.9414],
            [40.7477, -73.9452],
            [40.7503, -73.9477],
            [40.7529, -73.9503],
            [40.7555, -73.9529],
            [40.7582, -73.9560],
            [40.7609, -73.9591],
            [40.7635, -73.9622], # Midtown point
        ],
        "is_affected": True
    },
    "Route M102: CBD North/South": {
        "id": "M102",
        "polyline": [
            # Broadway corridor coordinates
            [40.7048, -74.0123],
            [40.7119, -74.0095],
            [40.7190, -74.0067],
            [40.7261, -74.0038],
            [40.7333, -74.0008],
            [40.7404, -73.9980],
            [40.7476, -73.9951],
            [40.7547, -73.9923],
            [40.7618, -73.9895],
            [40.7690, -73.9866], # Midtown/Uptown
        ],
        "is_affected": True
    },
    "Route M50: CBD East/West": {
        "id": "M50",
        "polyline": [
            # Using existing coordinates
            [40.7048, -74.0123],
            [40.7119, -74.0095],
            [40.7190, -74.0067],
            [40.7261, -74.0038],
            [40.7333, -74.0008],
            [40.7404, -73.9980],
            [40.7476, -73.9951],
            [40.7547, -73.9923],
            [40.7618, -73.9895],
            [40.7690, -73.9866], # Midtown/Uptown
        ],
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
    before_data = pd.read_parquet("../data/chart-speeds/control_speeds.parquet")
    after_data = pd.read_parquet("../data/chart-speeds/treatment_speeds.parquet")
    
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
        # Read merged speed differences data
        speeds_data = pd.read_parquet("../data/map-speeds/merged_speeds_diff.parquet")
        
        # Filter data for specific route, weekday and rush hour period
        segments_data = speeds_data[
            (speeds_data["route_id"] == route_id) & 
            (speeds_data["weekday"] == weekday) & 
            (speeds_data["rush_hour"] == rush_hour)
        ]
        
        if segments_data.empty:
            return None
            
        # Read segments geometry
        segments_geo = gpd.read_file("../data/map-segments/merged_segments.geojson")
        
        # Merge speed data with geometry
        merged_data = segments_data.merge(
            segments_geo,
            how='left',
            left_on=['prev_stop_id', 'stop_id'],
            right_on=['prev_stop_id', 'stop_id']
        )
        
        return merged_data
        
    except FileNotFoundError:
        st.warning(f"No segment data available for route {route_id}")
        return None

def create_map(route_name, rush_hour, weekday):
    """Create map visualization for route segments"""
    # Get route ID
    route_id = route_data[route_name]["id"]
    
    # Get segment speed differences with geometry
    segments_data = get_segment_speed_diff(route_id, weekday, rush_hour)
    
    # Create the base map
    fig = go.Figure()
    
    if segments_data is not None and not segments_data.empty:
        # Add each segment as a separate line
        for _, segment in segments_data.iterrows():
            speed_diff = segment["avg_speed_diff"]
            
            # Extract coordinates from geometry
            coords = segment['geometry'].coords[:]
            
            # Set color based on speed difference
            if speed_diff > 0:
                color_intensity = min(1, speed_diff / 5)
                color = f'rgb({int(135 * (1-color_intensity))}, {int(206 * (1-color_intensity))}, 255)'
            else:
                color_intensity = min(1, abs(speed_diff) / 5)
                color = f'rgb(255, {int(99 * (1-color_intensity))}, {int(71 * (1-color_intensity))})'
            
            # Add segment to map
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=[coord[0] for coord in coords],
                lat=[coord[1] for coord in coords],
                line=dict(width=6, color=color),
                name=f"Stop {segment['prev_stop_id']} to {segment['stop_id']}: {speed_diff:+.1f} mph",
                showlegend=False,
                hoverinfo="text",
                hovertext=f"From Stop: {segment['prev_stop_id']}<br>To Stop: {segment['stop_id']}<br>Speed change: {speed_diff:+.1f} mph"
            ))
        
        # Add a colorscale legend
        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=[],
            lat=[],
            marker=dict(
                size=10,
                colorscale=[
                    [0, 'rgb(255, 71, 71)'],     # Red for negative
                    [0.5, 'rgb(255, 255, 255)'],  # White for zero
                    [1, 'rgb(135, 206, 255)']     # Blue for positive
                ],
                colorbar=dict(
                    title="Speed Difference (mph)",
                    thickness=15,
                    len=0.5,
                    x=0.9
                ),
                cmin=-5,
                cmax=5
            ),
            showlegend=False
        ))
        
    else:
        st.warning("No segment data available for the selected time period")
    
    # Set map layout
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
        )
    )
    
    return fig

# Display the chart and map side by side with 2:1 ratio
col1, col2 = st.columns([2, 1])

with col1:
    # Add the subheader to the chart column
    st.subheader("Hourly Bus Speed for")
    
    # Add Accessibility options here
    access_col1, access_col2, access_col3 = st.columns([1, 1, 2])
    with access_col1:
        color_blind_mode = st.button(
            "Color Blind Mode: " + ("ON" if st.session_state.color_blind_mode else "OFF"),
            on_click=toggle_color_blind_mode
        )
    with access_col2:
        dark_mode = st.button(
            "Dark Mode: " + ("ON" if st.session_state.dark_mode else "OFF"),
            on_click=toggle_dark_mode
        )
    with access_col3:
        # Empty column for spacing
        pass
    
    # Create two columns for the route and day selection
    filter_col1, filter_col2, filter_col3 = st.columns([4, 2, 0.5])
    
    with filter_col1:
        selected_route = st.selectbox("", route_options, index=0, label_visibility="collapsed")
    with filter_col2:
        selected_day = st.selectbox("on", day_options, index=2, label_visibility="collapsed")
    with filter_col3:
        refresh = st.button("🔄", help="Refresh data")
    
    # Get data based on selection
    before_data, after_data = get_speed_data(selected_route, selected_day)
    
    # Calculate speed difference for the map when needed
    selected_hour = 8  # Assuming morning rush hour
    speed_diff = after_data[after_data['hour'] == selected_hour]['average_speed_mph'].values[0] - \
                before_data[before_data['hour'] == selected_hour]['average_speed_mph'].values[0]

    # Choose colors based on color blind mode
    if st.session_state.color_blind_mode:
        before_color = "#0072B2"  # Blue that works well for color blind users
        after_color = "#D55E00"   # Orange-red that works well for color blind users
    else:
        before_color = "#4169E1"  # Royal Blue
        after_color = "#FF6347"   # Tomato Red

    # Choose background based on dark mode
    bg_color = "#121212" if st.session_state.dark_mode else "#FFFFFF"
    text_color = "#FFFFFF" if st.session_state.dark_mode else "#333333"
    grid_color = "rgba(255,255,255,0.1)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)"

    # Create the plot
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=before_data['hour'],
        y=before_data['average_speed_mph'],
        mode='lines',
        name='Before Jan 5th',
        line=dict(color=before_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(before_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
    ))
    
    fig.add_trace(go.Scatter(
        x=after_data['hour'],
        y=after_data['average_speed_mph'],
        mode='lines',
        name='Jan 5th and After',
        line=dict(color=after_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(after_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
    ))
    
    # Update layout
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Time of Day',
            tickmode='array',
            tickvals=list(range(24)),  # Changed to show all 24 hours
            ticktext=['12 am', '1 am', '2 am', '3 am', '4 am', '5 am', 
                     '6 am', '7 am', '8 am', '9 am', '10 am', '11 am',
                     '12 pm', '1 pm', '2 pm', '3 pm', '4 pm', '5 pm', 
                     '6 pm', '7 pm', '8 pm', '9 pm', '10 pm', '11 pm'],  # Added all hours
            gridcolor=grid_color,
            color=text_color,
            title_font_color=text_color,
            tickfont_color=text_color,
        ),
        yaxis=dict(
            title='Average Bus Speed (mph)',
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
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)" if st.session_state.dark_mode else "rgba(255,255,255,0)",
            font=dict(color=text_color)
        ),
        margin=dict(l=50, r=20, t=30, b=50),
        height=500,
        autosize=True,
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Speed Difference Map")
    # Rush hour selection - use exact strings that match the parquet data
    rush_hours = {
        "Morning Rush": "morning_rush",
        "Evening Rush": "evening_rush"
    }
    selected_rush_hour = st.selectbox("Select rush hour period:", 
                                    list(rush_hours.keys()), 
                                    index=0)
    
    # Get weekday number for the selected day
    day_to_num = {
        "Mondays": 0, "Tuesdays": 1, "Wednesdays": 2, "Thursdays": 3,
        "Fridays": 4, "Saturdays": 5, "Sundays": 6
    }
    selected_weekday = day_to_num[selected_day]
    
    # Pass the exact rush hour string value to create_map
    map_fig = create_map(selected_route, rush_hours[selected_rush_hour], selected_weekday)
    st.plotly_chart(map_fig, use_container_width=True)

    # Legend explanation moved inside col2
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; margin-right: 20px;">
            <div style="width: 20px; height: 20px; background-color: #4682B4; margin-right: 5px;"></div>
            <span>Faster after congestion pricing</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 20px; height: 20px; background-color: #FF6347; margin-right: 5px;"></div>
            <span>Slower after congestion pricing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Explanatory text
st.markdown("""
The chart above shows bus speeds for a chosen route and day of week. The blue and red lines calculate average bus speeds prior to,
and after Jan 5th 2025, respectively.

The map displays the selected route with color indicating the speed difference between January 2025 (after congestion pricing) 
and December 2024 (before congestion pricing). Blue indicates faster speeds after congestion pricing, while red indicates slower speeds.

Routes selected are located within or on a direct path to the Congestion Zone, with a focus on those cross the East or Hudson Rivers into Manhattan.

**Note: This is demonstration data only.** When the application is connected to real data, the patterns will reflect actual bus speeds.
""")

# Add a footer
st.markdown("---")
st.markdown("© 2025 Bus Speed Tracker | Demo Version")