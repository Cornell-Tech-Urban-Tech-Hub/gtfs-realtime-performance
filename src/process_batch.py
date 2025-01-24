import os 
from src.utils import *
import pandas as pd
import numpy as np
import geopandas as gpd
import numpy as np
pd.options.mode.chained_assignment = None
from src.api import parse_zipped_gtfs
from src.gtfs_segments import GTFS_shape_processor
from src.speeds import BusSpeedCalculator
from datetime import datetime, timedelta

URLs = [
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_023554e8-0a59-413b-a50c-92ff131fa72e',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_09d7b38b-4bab-468d-9d65-2b85853ac75e',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_0b056bcf-6193-41ae-861f-ae884a012e29',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_186201db-2faf-4f38-bffa-92716440d546',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_1c91fac9-079e-4fa3-8182-569df0503ce8',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_20ab74f6-df02-4d2e-b4fe-ebf92fa1ac74',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_230c8436-6a66-4b17-8c0f-121a2eea4844',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_2c9c560f-9d88-4472-9e2c-b4603b2b65d9',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_2eef6e64-dee3-4361-b5a9-9c6c12718809',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_325c4a2c-4c3f-411f-9c50-2e59a85aaf60',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_327a1f49-cc3b-492f-95d9-49d95c6a7232',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_3725fb82-509f-44ce-b944-0cba4a1dab7c',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_4a2f90b7-b974-4ce8-80f0-b857ac7d1aba',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_4bbc8f8c-fe4a-498a-ada9-5b87421153ed',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_4e46b857-fe1d-46ca-abf3-943b39a59399',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_4f01a7e2-100d-4e13-af4b-a82f6a9afcd7',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_64549a48-d240-4d98-965b-e88fc26ccefd',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_65d6c353-bed0-42da-b24e-abfa2bbe93ee',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_79902113-f67d-4d0d-9269-acad795d221a',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_85268431-323c-4085-bcd7-39760d467668',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_8e958b4d-081c-457f-959f-23e7650ced00',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_940417f2-d8b1-4689-81ea-f90692f940a9',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_9a33afba-6c95-48a0-b308-6e9b9b7b49a6',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_a314a451-2435-41e0-bc54-ec8f8e84f8fc',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_df78e2fc-18fa-4f5b-8961-5f07d8427056',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_e2c17c66-e26f-41c9-ade2-fd0902dedaca',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_eab26b88-6970-4f74-a04a-c26c098efe05',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_eaef8733-ca24-4f41-bdc2-7c32f1dcd975',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_fbae25b7-2afe-4ba3-8975-233a5fca1493',
    'https://urbantech-public.s3.amazonaws.com/pickup/dump_NYC_GTFSRT/20240108_183520_00129_ygreg_ffbd96b2-8380-4c00-adbc-536f2fcb8079'
]

start = '2023-09-17'
stop = '2023-12-26'

start_date = datetime.strptime(start, '%Y-%m-%d')
stop_date = datetime.strptime(stop, '%Y-%m-%d')

days = []
current_date = start_date
while current_date <= stop_date:
    days.append(current_date.strftime('%Y%m%d'))
    current_date += timedelta(days=1)


dfs = []
for url in URLs:
    df = pd.read_parquet(url)
    print(df["vehicle.timestamp"].min())
    df = df[(df['vehicle.timestamp'] > start) & (df['vehicle.timestamp'] < stop)]
    dfs.append(df)

filtered_df = pd.concat(dfs)


output_dir = "/home/data/bus-weather/daily_files"
feeds = ["https://transitfeeds.com/p/mta/80/20230918/download", "https://transitfeeds.com/p/mta/81/20230918/download", "https://transitfeeds.com/p/mta/83/20230918/download", "https://transitfeeds.com/p/mta/82/20230919/download", "https://transitfeeds.com/p/mta/84/20230919/download", "https://transitfeeds.com/p/mta/85/20230918/download"]

for day in days:
    daily_data = []
    print(day)
    if not os.path.exists(f"{output_dir}/bus_speeds_nyc_{day}.parquet"):
        for feed in feeds:
            segment_df = GTFS_shape_processor(feed, 4326, 2263).process_shapes()
            GTFS_dict = parse_zipped_gtfs(feed)
            speeds = BusSpeedCalculator(filtered_df.query("`vehicle.trip.start_date` == @day"), GTFS_dict, segment_df).create_trip_speeds()
            daily_data.append(speeds)

        pd.concat(daily_data).to_parquet(f"/home/data/bus-weather/daily_files/bus_speeds_nyc_{day}.parquet")
        print(f"wrote daily data for {day}")