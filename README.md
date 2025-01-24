gtfs-realtime-performance
==============================

This library makes it easy to calculate transit performance statistics (e.g., segment speeds, bus bunching) using archival GTFS-realtime data. It is intended to be used in conjunction with the GTFS-realtime archiving tool being developed in [gtfs-realtime-capsule](https://github.com/tsdataclinic/gtfs-realtime-capsule).

### Project Organization

Currently, the main functionalities enabled by this repository are as follows:

1. Segmenting GTFS static feeds into shape segments defined by pairs of consecutive stops ([`src/gtfs_segments.py`](src/gtfs_segments.py))
2. Calculation of trip-level speeds along these segments using archival GTFS-realtime data ([`src/speeds.py`](src/speeds.py))

We have also included a number of utility functions to simplify the process of working with the GTFS data as well as our outputs. In the future, we will add more performance statistics and the ability to segment routes based on OSM street segments in addition to the static-feed segments currently implemented.

### Project Structure

- **`notebooks/`**: Contains Jupyter notebooks used for data analysis and visualization.
- **`src/`**: Contains the source code for the project.
  - **[`api.py`](src/api.py)**: Contains functions for interacting with external APIs and parsing GTFS data.
    - [`parse_zipped_gtfs`](src/api.py) function parses GTFS static data from a zipped file.
  - **[`gtfs_segments.py`](src/gtfs_segments.py)**: Contains the [`GTFS_shape_processor`](src/gtfs_segments.py) class for processing GTFS shapes and creating segments.
  - **[`process_batch.py`](src/process_batch.py)**: Contains batch processing functions.
  - **[`s3.py`](src/s3.py)**: Contains functions for interacting with AWS S3.
  - **[`speeds.py`](src/speeds.py)**: Contains the [`BusSpeedCalculator`](src/speeds.py) class for calculating bus speeds along segments.
  - **[`utils.py`](src/utils.py)**: Contains utility functions used throughout the project.
- **`.env`**: Put your Mobility Database refresh token here under REFRESH_TOKEN

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/gtfs-realtime-performance.git
    cd gtfs-realtime-performance
    ```

2. Install `uv`:
    ```sh
    pip install uv
    ```

3. Create a new virtual environment with `uv`:
    ```sh
    uv venv .venv
    ```

4. Activate the virtual environment:
    ```sh
    source .venv/bin/activate
    ```

5. Install the required dependencies using `uv sync`:
    ```sh
    uv sync
    ```

### Usage

#### Running Speed Calculations

To calculate bus speeds along segments, follow these steps:

1. Prepare the GTFS data:
    ```python
    from src.gtfs_segments import GTFS_shape_processor
    from src.api import parse_zipped_gtfs
    from src.speeds import BusSpeedCalculator
    import pandas as pd

    # Example GTFS feed URL
    GTFS_feed_url = 'https://example.com/path/to/gtfs_feed.zip'

    # Parse the GTFS feed
    GTFS_dict = parse_zipped_gtfs(GTFS_feed_url)

    # Process the GTFS shapes
    shape_processor = GTFS_shape_processor(GTFS_feed_url)
    GTFS_segments = shape_processor.process_shapes()

    # Load GTFS real-time data
    GTFS_rt_df = pd.read_parquet('path/to/gtfs_realtime_data.parquet')

    # Calculate bus speeds
    speed_calculator = BusSpeedCalculator(GTFS_rt_df, GTFS_dict, GTFS_segments)
    trip_speeds = speed_calculator.create_trip_speeds()

    # Save the results
    trip_speeds.to_parquet('path/to/output_speeds.parquet')
    ```

### Notebooks

This repository contains a number of notebooks that contain figures, tables, and maps created using our speed estimates. Some of these are old and messy - I'd recommend looking at [`notebooks/basic_plots_and_mta.ipynb`](notebooks/basic_plots_and_mta.ipynb) for comparisons of our speeds to speeds published by the MTA,  at [`notebooks/holidays.ipynb`](notebooks/holidays.ipynb) to see bus speed comparisons on holidays, and [`notebooks/process_from_s3.ipynb`](notebooks/processs_from_s3.ipynb) to see how to calculate speeds from realtime data hosted on s3.

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
