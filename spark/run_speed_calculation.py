import argparse
import os
from datetime import datetime, timedelta
from spark.config import create_spark_session
from spark.speed_calculator import SparkSpeedCalculator
from src.api import parse_zipped_gtfs

def generate_date_list(start_date: str, end_date: str) -> list:
    """Generate list of dates between start and end date."""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    return date_list

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--feed-id', required=True)
    parser.add_argument('--gtfs-url', required=True)
    args = parser.parse_args()

    # Config
    prefix = "norm/bus-mta-vp/vehicles/"
    bucket = "dataclinic-gtfs-rt"
    route_list = ["M50"]

    # Initialize Spark
    spark = create_spark_session()
    
    try:
        print("Loading GTFS data...")
        gtfs_dict = parse_zipped_gtfs(args.gtfs_url)
        
        print("Initializing calculator...")
        calculator = SparkSpeedCalculator(spark, bucket, prefix, gtfs_dict)
        
        # Process dates
        date_list = generate_date_list(args.start_date, args.end_date)
        print(f"Processing dates: {date_list}")
        
        for date in date_list:
            print(f"\nProcessing date: {date}")
            output_path = f"data/raw-speeds/{args.feed_id}/bus_speeds_{date}.parquet"
            
            if os.path.exists(output_path):
                print(f"Data already exists for {date}")
                continue
            
            try:
                speeds = calculator.process_date(date, route_list)
                speeds.write.mode("overwrite").parquet(output_path)
                print(f"Successfully processed {date}")
            except Exception as e:
                print(f"Error processing {date}: {e}")
                continue
    finally:
        print("Stopping Spark session...")
        spark.stop()

if __name__ == "__main__":
    main()