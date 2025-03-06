1.figure out whether all streamlit code should be written in one single file
2.figure out how to design the database schema

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

# DB?
1. bus speed table(one large table?)
2. geojson data
3. GTFS static data: date -> GTFS dict -> segment df

# Realtime data ingestion and processing
Similar to how they set up the scraper, we need sth like that for bus speed data ETL to the db.


# toso
- visualization: rush hour
- batch processing: 1. parquet format? 2. set up docker for backend running?


