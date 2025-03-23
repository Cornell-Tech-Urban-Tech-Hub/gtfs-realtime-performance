import pandas as pd
import pytz
import os
from typing import List, Dict
from .s3 import list_files_in_bucket, load_all_parquet_files
from .speeds import BusSpeedCalculator
from .logger import setup_logger

class SpeedCalculator:
    def __init__(
        self,
        bucket: str,
        prefix: str,
        feed_id: str,
        gtfs_dict: Dict,
        segment_df: pd.DataFrame
    ):
        self.bucket = bucket
        self.prefix = prefix
        self.feed_id = feed_id
        self.gtfs_dict = gtfs_dict
        self.segment_df = segment_df
        self.logger = setup_logger()

    def process_date(self, date: str, route_list: List[str]) -> pd.DataFrame:
        """Process vehicle positions for a single date"""
        self.logger.info(f"Processing Date: {date}")

        # First check if data already exists
        output_path = f"data/raw-speeds/{self.feed_id}/bus_speeds_{date}.parquet"
        if os.path.exists(output_path):
            self.logger.info(f"Data already exists for {date}, skipping to next date")
            return None

        # Load relevant realtime data from s3 bucket
        daily_files = list_files_in_bucket(bucket_name=self.bucket, 
                                         prefix=f"{self.prefix}date={date}/")
        try:
            vehicle_positions = load_all_parquet_files(file_list=daily_files, 
                                                     bucket=self.bucket)
        except Exception as e:
            self.logger.error(f"Error loading parquets from s3 for {date}: {e}")
            return None

        # Filter vps by routes in route_list
        vehicle_positions = vehicle_positions[
            vehicle_positions['trip.route_id'].isin(route_list)
        ]

        # Check if vehicle_positions is empty
        if vehicle_positions.empty:
            self.logger.error(f"No vehicle positions found for {date}. Check if the feed id and date match. Skipping to next date")
            return None
        
        # Check if vehicle_positions has all the routes in route_list and log the missing routes
        missing_routes = set(route_list) - set(vehicle_positions['trip.route_id'].unique())
        if missing_routes:
            self.logger.warning(f"Missing routes in vehicle positions for {date}: {missing_routes}")

        # Calculate speeds
        speed_calculator = BusSpeedCalculator(vehicle_positions, 
                                            self.gtfs_dict, 
                                            self.segment_df)
        try:
            speeds = speed_calculator.create_trip_speeds()
        except Exception as e:
            self.logger.error(f"Error calculating speeds for {date}: {e}")
            return None

        # Check if speeds is empty
        if speeds.empty:
            self.logger.error(f"No speeds found for {date}. Check if the feed id and date match. Skipping to next date")
            return None

        # Process the speeds DataFrame
        speeds = self._process_speeds_df(speeds)
        
        # Save results
        speeds.to_parquet(output_path)
        self.logger.info(f"Wrote daily data for {date}")
        return speeds

    def _process_speeds_df(self, speeds: pd.DataFrame) -> pd.DataFrame:
        """Process the speeds DataFrame - exactly matching notebook logic"""

        # Drop cols that are not needed
        speeds.drop(columns=[
            "stop_sequence", "stop_name", "prev_stop_name",
            "projected_position", "prev_projected_position", "unique_trip_id"
        ], inplace=True)

        # Remove outlier
        speeds = speeds[speeds["speed_mph"] < 70]

        # Timezone conversion
        eastern_tz = pytz.timezone('America/New_York')
        speeds['interpolated_time'] = pd.to_datetime(speeds['interpolated_time'])
        speeds['datetime_nyc'] = speeds['interpolated_time'].dt.tz_localize('UTC').dt.tz_convert(eastern_tz)

        # Add time-related columns
        speeds["date"] = speeds["datetime_nyc"].dt.date
        speeds["weekday"] = speeds["datetime_nyc"].dt.weekday
        speeds["hour"] = speeds["datetime_nyc"].dt.hour

        # Drop interpolated_time
        speeds.drop(columns=["interpolated_time"], inplace=True)

        return speeds