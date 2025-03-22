# Streamlit
## Structure

In its simplest form, a Streamlit app can be a single Python file (e.g., app.py) that contains:

Frontend code: UI elements created with Streamlit commands
Backend logic: Python functions that process data or run models
Data handling: Code that loads, processes, and displays data

For larger applications, you can split your code into multiple files

The key advantage of Streamlit is that it doesn't require separate frontend/backend architecture like traditional web applications - everything runs in a single Python process

## Database
For database access, you simply add database connection code in your app


## Deployment

Apps sleep after inactivity. When a user visits your sleeping app, they'll see a loading screen while the app "wakes up" and restarts, which can take anywhere from 30 seconds to a couple of minutes.

For context, when an app is already running (hasn't gone to sleep yet), page loads are quite fast - typically just a few seconds, similar to most web applications.

# Data Storage
parquet files

Raw:
- data/raw-speeds

Processed:
- data
    - table-chart
        - before_chart.parquet (speed by time)
        - after_chart.parquet (speed by time)
    - table-map
        - before_map.parquet (speed by segment)
        - after_map.parquet (speed by segment)
        - segments.parquet


# TODO

- routes * # hours * # segments 
- 50mb
- streamlit application -> table -> parquet is fine
- don't have to be a continous project
- all the aggregation before loading into 


1. oop py runner for speed calculation
- with loggers
2. docker


todo: spark for nested loop - skipped 