# Streamlit
## Structure

In its simplest form, a Streamlit app can be a single Python file (e.g., app.py) that contains:

Frontend code: UI elements created with Streamlit commands
Backend logic: Python functions that process data or run models
Data handling: Code that loads, processes, and displays data

For larger applications, you can split your code into multiple files

The key advantage of Streamlit is that it doesn't require separate frontend/backend architecture like traditional web applications - everything runs in a single Python process

## Deployment

Apps sleep after inactivity. When a user visits your sleeping app, they'll see a loading screen while the app "wakes up" and restarts, which can take anywhere from 30 seconds to a couple of minutes.

For context, when an app is already running (hasn't gone to sleep yet), page loads are quite fast - typically just a few seconds, similar to most web applications.

# TODO

1. figure out SIM24,SIM4X mdb-id, dates for comparison

2. docker

3. (optional) spark for nested loop - skipped - need to learn spark first

B39,M102,M50
mdb-513
```
python runner.py \
    --start-date 2025-01-05 \
    --end-date 2025-01-06 \
    --feed-id mdb-513-202501020055 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501020055/mdb-513-202501020055.zip" \
    --routes B39,M102,M50
```

SIM24,SIM4X are not in mdb-513