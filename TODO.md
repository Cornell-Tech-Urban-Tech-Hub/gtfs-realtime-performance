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


# TODO
- visualization: rush hour
- batch processing steps:


# Discussion
1. local: parquet format? - yes
- schema metadata: has column names, data types, ... Stored at the file level and shared across all row groups
- Apache Spark can read parquet and write to postgres SQL
- AWS Glue ETL can read parquet from s3 and load directly to RDS

2. what cols should be in parquet file - done 
precomputing the weekday col during etl for faster query: weekday (0-6)
precomputing the hour col during etl for faster query: hour (0-23)

3. batch processing with pyspark? - in progress
- todo: to ood
- todo: test on sample data set

________________________________________






4. db schema design
url -> date range -> 
- GTFS dict -> json
- segment -> geojson
- daily speeds -> parquet? a table?

query senario: filter by weekday and route





5. pipeline design
- s3 -> daily parquet -> load into db
- s3 -> processing -> into db



6. set up docker for isolation and logging

# routes * # hours * # segments 
# 50mb
# streamlit application -> table -> parquet is fine
# don't have to a continous project

# all the aggregation before loading into 


drop all the routes 

only use the url we need 






table 
row -> speeds -> 