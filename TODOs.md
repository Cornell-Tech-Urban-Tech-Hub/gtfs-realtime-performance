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

M102,M50
mdb-513 Manhattan
```
        python runner.py         --start-date 2025-01-25         --end-date 2025-02-01         --feed-id mdb-513-202501230024         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501230024/mdb-513-202501230024.zip"         --routes M50,M102

        python runner.py         --start-date 2024-11-01         --end-date 2024-12-11         --feed-id mdb-513-202409090026         --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202409090026/mdb-513-202409090026.zip"         --routes M50,M102
```


SIM24,SIM4X
mdb-514 Staten Island
SIM24 - staten island, new jersey, manhattan
SIM4X - staten island, brooklyn, manhattan

```
        python runner.py         --start-date 2024-12-12         --end-date 2025-01-04         --feed-id mdb-514-202412120006         --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202412120006/mdb-514-202412120006.zip"         --routes SIM24,SIM4X
        

        python runner.py         --start-date 2025-01-05         --end-date 2025-02-09         --feed-id mdb-514-202501020130         --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202501020130/mdb-514-202501020130.zip"         --routes SIM24,SIM4X
        

        python runner.py         --start-date 2025-02-10         --end-date 2025-03-29         --feed-id mdb-514-202502170029         --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202502170029/mdb-514-202502170029.zip"         --routes SIM24,SIM4X


```

B39
mdb-512 Brooklyn
```
        python runner.py         --start-date 2024-11-01         --end-date 2024-12-11         --feed-id mdb-512-202408290005         --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202408290005/mdb-512-202408290005.zip"         --routes B39
        

        python runner.py         --start-date 2024-12-12         --end-date 2025-01-03         --feed-id mdb-512-202412120015         --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202412120015/mdb-512-202412120015.zip"         --routes B39
        

        python runner.py         --start-date 2025-01-04         --end-date 2025-02-08         --feed-id mdb-512-202501020103         --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202501020103/mdb-512-202501020103.zip"         --routes B39
        

        python runner.py         --start-date 2025-02-09         --end-date 2025-03-29         --feed-id mdb-512-202502170011         --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202502170011/mdb-512-202502170011.zip"         --routes B39
```



2024-11-02 might be too big to fit in RAM -> trouble shooting
(optional) docker memory allocation and optimization
(optional) spark for nested loop - skipped - need to learn spark first
