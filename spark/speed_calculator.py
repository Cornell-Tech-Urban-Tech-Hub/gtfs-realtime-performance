from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, split, from_utc_timestamp, date_format, hour, dayofweek
from src.s3 import list_files_in_bucket

class SparkSpeedCalculator:
    def __init__(self, spark: SparkSession, bucket: str, prefix: str, gtfs_dict: dict):
        self.spark = spark
        self.bucket = bucket
        self.prefix = prefix
        self.gtfs_dict = gtfs_dict

    def process_date(self, date: str, route_list: list) -> DataFrame:
        """Process a single date"""
        print(f"Loading data for date {date}...")
        daily_files = list_files_in_bucket(
            bucket_name=self.bucket, 
            prefix=f"{self.prefix}date={date}/"
        )
        
        # Read and filter vehicle positions
        vehicle_positions = (self.spark.read.parquet(*[f"s3://{self.bucket}/{f}" for f in daily_files])
                           .filter(col("`trip.route_id`").isin(route_list)))
        
        print(f"Processing {vehicle_positions.count()} records...")
        return self._calculate_speeds(vehicle_positions)

    def _calculate_speeds(self, vehicle_positions: DataFrame) -> DataFrame:
        """Calculate speeds and process data"""
        return (vehicle_positions
            .withColumn("route_id", col("`trip.route_id`"))
            .filter(col("speed_mph") < 70)
            .withColumn("datetime_nyc", 
                       from_utc_timestamp(col("interpolated_time"), "America/New_York"))
            .withColumn("date", date_format("datetime_nyc", "yyyy-MM-dd"))
            .withColumn("weekday", dayofweek("datetime_nyc"))
            .withColumn("hour", hour("datetime_nyc")))