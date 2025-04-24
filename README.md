# NYC Congestion Zone Bus Speed Tracker

This project is built upon [gtfs-realtime-performance](https://github.com/CanyonFoot/gtfs-realtime-performance) and the GTFS-realtime archiving tool [gtfs-realtime-capsule](https://github.com/tsdataclinic/gtfs-realtime-capsule) for realtime bus speed comparison before and after congestion pricing in NYC using archived GTFS-realtime data.

## Project Design

This project aims to compare bus speeds before and after [Congestion Relief Zone Tolling](https://congestionreliefzone.mta.info/tolling) implementation, using MTA GTFS-realtime bus travel data archived daily in a public S3 data lake (as of today, *s3://dataclinic-gtfs-rt*). This provides a granular view of how congestion pricing impacts bus performance at the route segment level.

### Geographic Scope and Time Scope
The study focuses on the congestion pricing zone in NYC and its immediate surroundings.

We selected dates that provide one month of data before and after the January 5th implementation date:
- Before congestion pricing: December 3, 2024 - January 4, 2025
- After congestion pricing: January 5, 2025 - February 6, 2025

### Route Selection
We selected bus routes that are located within or on a direct path to the Congestion Zone, with a focus on those crossing the East or Hudson Rivers into Manhattan. We use the same routes as NYC DOT reports:

- Williamsburg Bridge: B39 (mdb-512)
- Lincoln Tunnel: SIM24 (mdb-514)
- Hugh Carey Tunnel: SIM4X (mdb-514)
- CBD North/South: M102 (mdb-513)
- CBD East/West: M50 (mdb-513)

### Data Sources
The GTFS static data feeds are obtained from [Mobility Database](https://mobilitydatabase.org/):
- Manhattan Bus: [mdb-513](https://mobilitydatabase.org/feeds/gtfs/mdb-513)
- Brooklyn Bus: [mdb-512](https://mobilitydatabase.org/feeds/gtfs/mdb-512)
- Staten Island Bus: [mdb-514](https://mobilitydatabase.org/feeds/gtfs/mdb-514)

The archived GTFS realtime data are retrieved from the Data Clinic AWS S3 bucket:
- s3://dataclinic-gtfs-rt/norm/bus-mta-vp/vehicles/


### Data Workflow 
1. Data Collection: First step is to fetch daily bus vehicle data from S3 bucket, using the speed calculator to transform it into daily bus speed data.
    - Exploration: **[`speed_tracker_data.ipynb`](notebooks/speed_tracker_data.ipynb)**
    - Implementation: **[`runner.py`](runner.py)**
2. Data Aggregation: Second step is to aggregate and transform raw speed data based on the requirements of visualization.
    - Exploration: **[`speed_tracker_aggregation.ipynb`](notebooks/speed_tracker_aggregation.ipynb)**
    - Implementation: **[`speed_tracker_aggregation.ipynb`](notebooks/speed_tracker_aggregation.ipynb)**
3. Data Visualization: Third step is to show aggregated data in an intuitive way for comparison.
    - Exploration: **[`speed_tracker_visualization.ipynb`](notebooks/speed_tracker_visualization.ipynb)**
    - Implementation: A Streamlit app is built for interactive data visualization. Check out **`application/`** for detailed implementation.

### Data Processing via Docker
The recommended way to run the project is with Docker Compose for isolation. The workflow is as follows:

1. User runs: `docker-compose up`
2. Docker builds image using **[`Dockerfile`](Dockerfile)**
3. Container starts with **[`docker-compose.yml`](docker-compose.yml)** configuration
4. Inside container, the process automatically runs **[`run_feeds.sh`](run_feeds.sh)**
5. `run_feeds.sh` calls **[`runner.py`](runner.py)** multiple times with different parameters
6. For each call, `runner.py`:
   - Sets up logging (using **[`src/logger.py`](src/logger.py)**)
   - Downloads GTFS data (using **[`src/api.py`](src/api.py)**)
   - Processes shapes (using **[`src/gtfs_segments.py`](src/gtfs_segments.py)**)
   - Calculates speeds (using **[`src/speed_calculator.py`](src/speed_calculator.py)**)
   - Stores results in the data directory

The Docker setup includes resource limits and volume mounts for logs and data persistence.


## Project Structure

- **`src/`**: Contains the source code for bus speed calculation.
  - **[`api.py`](src/api.py)**: Contains functions for interacting with external APIs and parsing GTFS data.
    - [`parse_zipped_gtfs`](src/api.py) function parses GTFS static data from a zipped file.
  - **[`gtfs_segments.py`](src/gtfs_segments.py)**: Contains the [`GTFS_shape_processor`](src/gtfs_segments.py) class for processing GTFS shapes and creating segments.
  - **[`process_batch.py`](src/process_batch.py)**: Contains batch processing functions.
  - **[`s3.py`](src/s3.py)**: Contains functions for interacting with AWS S3.
  - **[`speeds.py`](src/speeds.py)**: Contains the [`BusSpeedCalculator`](src/speeds.py) class for calculating bus speeds along segments.
  - **[`utils.py`](src/utils.py)**: Contains utility functions used throughout the project.
  - **[`speed_calculator.py`](src/speed_calculator.py)**: Contains [`SpeedCalculator`](src/speed_calculator.py) class for calculating and storing bus speeds for specific routes and dates, handling data loading from S3, speed calculations, and timezone conversions.

- **`notebooks/`**: Contains Jupyter notebooks used for data fetching, processing, aggregation and visualization.
  - **Core notebooks**: 
    - **[`speed_tracker_data.ipynb`](notebooks/speed_tracker_data.ipynb)**: Handles data collection and processing for bus speed tracking, including S3 integration and GTFS data processing.
    - **[`speed_tracker_aggregation.ipynb`](notebooks/speed_tracker_aggregation.ipynb)**: Aggregates and processes bus speed data for analysis and visualization.
    - **[`speed_tracker_visualization.ipynb`](notebooks/speed_tracker_visualization.ipynb)**: Creates visualizations and charts for bus speed analysis.
  - **Helper notebooks**:
    - **[`process_from_s3.ipynb`](notebooks/process_from_s3.ipynb)**: Processes bus data directly from S3 storage, including data loading and transformation.
    - **[`feed_match.ipynb`](notebooks/feed_match.ipynb)**: Matches and processes GTFS feed data with real-time bus information.

- **`application/`**: Contains the source code for the Streamlit application for interactive visualization.
  - Check out [`application/APP_README.md`](application/APP_README.md) for detailed information on how to develop and run the application.

- **`data/`**: Contains the raw data and the processed data used as source for the visualization app.
  - **Raw data**:
    - **`raw-speeds/`**: Contains daily bus speed data organized by feed ID (mdb-512, mdb-513, mdb-514) and date, storing the raw speed calculated for each route.
  - **Processed data**:
    - **`chart-speeds/`**: Contains aggregated speed data in parquet format (`control_speeds.parquet` and `treatment_speeds.parquet`) used for generating the speed comparison line chart.
    - **`map-segments/`**: Contains GeoJSON files for bus route segments, including both individual route segments (e.g., B39, M50, M102, SIM24, SIM4X) and merged segments for each feed ID(mdb-512, mdb-513, mdb-514).
    - **`map-speeds/`**: Contains parquet files with speed difference data for each route, used for generating the speed difference map.
    - **`congestion_zone_boundary.geojson`**: Defines the boundary of the congestion pricing zone in NYC.

- **`.env`**: Environment variables file that should contain:
  - `REFRESH_TOKEN`: Your Mobility Database refresh token
  - `AWS_ACCESS_KEY_ID`: Your AWS access key
  - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
  - `AWS_DEFAULT_REGION`: Your AWS region (e.g., us-east-1)

- **Docker files**: Configuration files located in the root directory:
  - **[`Dockerfile`](Dockerfile)**: Defines the Python 3.10 Docker image with geospatial dependencies and application setup.
  - **[`docker-compose.yml`](docker-compose.yml)**: Configures container deployment with volume mounts, memory limits, and environment variables.
  - **[`run_feeds.sh`](run_feeds.sh)**: Bash script that sequentially executes multiple GTFS feed processing jobs with pauses between runs.
  - **[`runner.py`](runner.py)**: Main script that processes GTFS feeds with command-line arguments for dates, feeds, and routes.


## Installation

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

## Future Development

### Data Lake Migration
Migrate daily archived data from *s3://busobservatory-lake* to *s3://dataclinic-gtfs-rt*, following the same data format.

### Spark Optimization
Implement batch parallel processing by setting up Spark jobs for selected dates and routes.

### Realtime Ingestion
For this project, static aggregated data is used, specifically:
- Before congestion pricing: December 3, 2024 - January 4, 2025
- After congestion pricing: January 5, 2025 - February 6, 2025

For future development, set up weekly ETL jobs for processing new daily data coming into the data lake, and update **After congestion pricing** metrics on a weekly basis (since we are using a weekly aggregation).