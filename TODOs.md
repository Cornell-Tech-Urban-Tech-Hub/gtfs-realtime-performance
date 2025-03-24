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

Build
docker-compose build

Run
docker-compose up

Or with custom parameters
docker-compose run --rm bus-speed-processor \
    --start-date 2025-01-07 \
    --end-date 2025-01-10 \
    --feed-id mdb-513-202501020055 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501020055/mdb-513-202501020055.zip" \
    --routes M50,M15

3. (optional) spark for nested loop - skipped - need to learn spark first

M102,M50
mdb-513
```
python runner.py \
    --start-date 2024-12-12 \
    --end-date 2025-01-04 \
    --feed-id mdb-513-202412120015 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202412120015/mdb-513-202412120015.zip" \
    --routes M102,M50

```



for mdb-513
```
        python runner.py         --start-date 2024-12-12         --end-date 2024-12-11         --feed-id mdb-513-202409090026         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202409090026/mdb-513-202409090026.zip"         --routes M102,M50
                

        python runner.py         --start-date 2024-12-12         --end-date 2025-01-04         --feed-id mdb-513-202412120015         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202412120015/mdb-513-202412120015.zip"         --routes M102,M50
        

        python runner.py         --start-date 2025-01-24         --end-date 2025-02-08         --feed-id mdb-513-202501230024         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501230024/mdb-513-202501230024.zip"         --routes M102,M50
        

        python runner.py         --start-date 2025-02-09         --end-date 2025-03-29         --feed-id mdb-513-202502170105         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202502170105/mdb-513-202502170105.zip"         --routes M102,M50

```


Not urgent:  set up loggers by mdb-id and date
