import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Bus Speed Tracker",
    page_icon="🚌",
    layout="wide"
)

# App title and description
st.title("Bus Speed Tracker")
st.markdown(
    "Curious whether Congestion Pricing is having an impact on bus speeds in NYC? "
    "Take a look below to compare bus speed data before and after Congestion Pricing began on January 5th, 2025."
)

# Accessibility options - adjust to be side by side
col1, col2, col3 = st.columns([1, 1, 2])  # Create a third column to maintain layout
with col1:
    color_blind_mode = st.button("Enable Color Blind Mode")
with col2:
    dark_mode = st.button("Enable Dark Mode")
with col3:
    # Empty column for spacing
    pass

# Create fake route options with route data
route_data = {
    "Route 7: Holland Tunnel (Affected)": {
        "polyline": [
            # Holland Tunnel to Midtown path
            [40.7273, -74.0094], # Holland Tunnel entrance
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
    "Route 9: Lincoln Tunnel (Affected)": {
        "polyline": [
            # Lincoln Tunnel to Midtown path
            [40.7588, -74.0106], # Lincoln Tunnel entrance
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
    "Route 14: Queens Midtown Tunnel": {
        "polyline": [
            # Queens Midtown Tunnel to Midtown path
            [40.7431, -73.9414], # Queens Midtown Tunnel entrance
            [40.7477, -73.9452],
            [40.7503, -73.9477],
            [40.7529, -73.9503],
            [40.7555, -73.9529],
            [40.7582, -73.9560],
            [40.7609, -73.9591],
            [40.7635, -73.9622], # Midtown point
        ],
        "is_affected": False
    },
    "Route 42: Broadway Corridor": {
        "polyline": [
            # Broadway corridor from downtown to uptown
            [40.7048, -74.0123], # Downtown
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

# Generate fake data based on selection
def generate_fake_data(route, day):
    # Hours of the day
    hours = list(range(24))
    
    # Base patterns that represent typical traffic patterns
    morning_peak = [7, 8, 9]  # Morning rush hours
    evening_peak = [16, 17, 18, 19]  # Evening rush hours
    
    # Different routes have different base speeds
    if route_data[route]["is_affected"]:
        base_speed_before = 18
        # After congestion pricing, affected routes show improvement
        base_speed_after = 22
    else:
        base_speed_before = 20
        # Non-affected routes show minimal change
        base_speed_after = 21
    
    # Generate speeds for each hour
    before_speeds = []
    after_speeds = []
    this_week_speeds = []
    speed_differences = []
    
    for hour in hours:
        # Add time-of-day variations
        if hour in morning_peak:
            factor_before = 0.7  # 30% slower during morning rush
            factor_after = 0.85  # Less impact after congestion pricing
        elif hour in evening_peak:
            factor_before = 0.65  # 35% slower during evening rush
            factor_after = 0.8   # Less impact after congestion pricing
        elif 0 <= hour < 6:
            factor_before = 1.2  # Faster at night
            factor_after = 1.2   # Still faster at night
        else:
            factor_before = 1.0
            factor_after = 1.0
        
        # Add some randomness
        noise_before = np.random.normal(0, 1)
        noise_after = np.random.normal(0, 1)
        noise_this_week = np.random.normal(0, 1.5)
        
        # Calculate speeds
        speed_before = max(5, base_speed_before * factor_before + noise_before)
        speed_after = max(5, base_speed_after * factor_after + noise_after)
        
        # Calculate speed difference
        speed_diff = speed_after - speed_before
        
        # This week's data is based on after data but with more variation
        if route_data[route]["is_affected"]:
            # Continue improving for affected routes
            this_week_speed = max(5, base_speed_after * factor_after * 1.05 + noise_this_week)
        else:
            # Slight random variation for non-affected routes
            this_week_speed = max(5, base_speed_after * factor_after + noise_this_week)
        
        before_speeds.append(round(speed_before, 1))
        after_speeds.append(round(speed_after, 1))
        this_week_speeds.append(round(this_week_speed, 1))
        speed_differences.append(round(speed_diff, 1))
    
    # Create dataframes
    before_data = pd.DataFrame({'hour': hours, 'speed': before_speeds})
    after_data = pd.DataFrame({'hour': hours, 'speed': after_speeds})
    this_week_data = pd.DataFrame({'hour': hours, 'speed': this_week_speeds})
    diff_data = pd.DataFrame({'hour': hours, 'diff': speed_differences})
    
    return before_data, after_data, this_week_data, diff_data

# Create mapbox figure
def create_map(route_name, hour, speed_diff):
    # Get route coordinates
    route_coords = route_data[route_name]["polyline"]
    
    # Create the base map centered on Manhattan
    fig = go.Figure()
    
    # Set color based on speed difference
    if speed_diff > 0:
        # Positive difference (blue) - faster after congestion pricing
        color_intensity = min(1, speed_diff / 5)  # Normalize to a max of 5 mph difference
        color = f'rgb({int(135 * (1-color_intensity))}, {int(206 * (1-color_intensity))}, 255)'
    else:
        # Negative difference (red) - slower after congestion pricing
        color_intensity = min(1, abs(speed_diff) / 5)
        color = f'rgb(255, {int(99 * (1-color_intensity))}, {int(71 * (1-color_intensity))})'
    
    # Add the route as a polyline
    lats = [coord[0] for coord in route_coords]
    lons = [coord[1] for coord in route_coords]
    
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=lons,
        lat=lats,
        line=dict(width=6, color=color),
        name=f"{route_name} ({speed_diff:+.1f} mph)"
    ))
    
    # Set map layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=12,
            center=dict(lat=40.75, lon=-73.98),  # Center on Manhattan
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,  # Match the height of the chart
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5,
        )
    )
    
    return fig

# Display the chart and map side by side with 2:1 ratio
col1, col2 = st.columns([2, 1])

with col1:
    # Add the subheader to the chart column
    st.subheader("Bus Speed Times for")
    
    # Create two columns for the route and day selection
    filter_col1, filter_col2, filter_col3 = st.columns([4, 2, 0.5])
    
    with filter_col1:
        selected_route = st.selectbox("", route_options, index=0, label_visibility="collapsed")
    with filter_col2:
        selected_day = st.selectbox("on", day_options, index=2, label_visibility="collapsed")
    with filter_col3:
        refresh = st.button("🔄", help="Refresh data")
    
    # Get data based on selection
    before_data, after_data, this_week_data, diff_data = generate_fake_data(selected_route, selected_day)
    
    # Choose colors based on color blind mode
    if color_blind_mode:
        before_color = "#0072B2"  # Blue that works well for color blind users
        after_color = "#D55E00"   # Orange-red that works well for color blind users
        this_week_color = "#CC79A7"  # Pink that works well for color blind users
    else:
        before_color = "#4169E1"  # Royal Blue
        after_color = "#FF6347"   # Tomato Red
        this_week_color = "#9370DB"  # Medium Purple

    # Choose background based on dark mode
    bg_color = "#121212" if dark_mode else "#FFFFFF"
    text_color = "#FFFFFF" if dark_mode else "#333333"
    grid_color = "rgba(255,255,255,0.1)" if dark_mode else "rgba(0,0,0,0.1)"

    # Create the plot
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=before_data['hour'],
        y=before_data['speed'],
        mode='lines',
        name='Before Jan 5th',
        line=dict(color=before_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(before_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
    ))
    
    fig.add_trace(go.Scatter(
        x=after_data['hour'],
        y=after_data['speed'],
        mode='lines',
        name='Jan 5th and After',
        line=dict(color=after_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(after_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}',
    ))
    
    fig.add_trace(go.Scatter(
        x=this_week_data['hour'],
        y=this_week_data['speed'],
        mode='lines',
        name='This Week',
        line=dict(color=this_week_color, width=3),
    ))
    
    # Update layout
    fig.update_layout(
        title=None,
        xaxis=dict(
            title='Time of Day',
            tickmode='array',
            tickvals=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22],
            ticktext=['12 am', '2 am', '4 am', '6 am', '8 am', '10 am', 
                     '12 pm', '2 pm', '4 pm', '6 pm', '8 pm', '10 pm'],
            gridcolor=grid_color,
            color=text_color,
        ),
        yaxis=dict(
            title='Average Bus Speed (mph)',
            gridcolor=grid_color,
            color=text_color,
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
            bgcolor="rgba(0,0,0,0)" if dark_mode else "rgba(255,255,255,0)"
        ),
        margin=dict(l=50, r=20, t=30, b=50),  # Increased left margin for y-axis label
        height=500,  # Set a minimum height
        autosize=True,  # Still keep autosize for width responsiveness
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Speed Difference Map")
    # Hour selection for map
    selected_hour = st.selectbox("Select hour to view on map:", list(range(24)), index=8)  # Default to 8 AM
    hour_text = f"{selected_hour if selected_hour != 0 else 12}:00 {'AM' if selected_hour < 12 else 'PM'}"
    if selected_hour > 12:
        hour_text = f"{selected_hour - 12}:00 PM"
    st.write(f"Showing speed difference at {hour_text}")

    # Get speed difference for the selected hour
    speed_diff = diff_data[diff_data['hour'] == selected_hour]['diff'].values[0]

    # Create and display the map
    map_fig = create_map(selected_route, selected_hour, speed_diff)
    map_fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=0, b=0),
        height=400  # Changed map height to 400px
    )
    st.plotly_chart(map_fig, use_container_width=True)

# Legend explanation
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
and after Jan 5th 2025, respectively. The purple line shows real-time data from the current week for the chosen route.

The map displays the selected route with color indicating the speed difference between January 2025 (after congestion pricing) 
and December 2024 (before congestion pricing). Blue indicates faster speeds after congestion pricing, while red indicates slower speeds.

Routes 1-13, excluding 8, are located within or on a direct path to the Congestion Zone. Routes 8, 14, 15, 17 and 19 are routes within
New York City, but outside of the congestion zone.

**Note: This is demonstration data only.** When the application is connected to real data, the patterns will reflect actual bus speeds.
""")

# Add a footer
st.markdown("---")
st.markdown("© 2025 Bus Speed Tracker | Demo Version")