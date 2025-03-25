# runner.py
import argparse
from datetime import datetime, timedelta
from src.speed_calculator import SpeedCalculator
from src.logger import setup_logger
from src.gtfs_segments import GTFS_shape_processor
from src.api import parse_zipped_gtfs
import warnings
from shapely.errors import ShapelyDeprecationWarning

# Suppress specific Shapely warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='shapely.linear')

def generate_date_list(start_date: str, end_date: str) -> list:
    """Generate list of dates between start and end dates"""
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
    parser = argparse.ArgumentParser(description='Calculate bus speeds')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--feed-id', required=True, help='Feed ID')
    parser.add_argument('--gtfs-url', required=True, help='GTFS URL')
    parser.add_argument('--routes', required=True, help='Comma-separated list of route IDs')
    args = parser.parse_args()

    print(f"Starting main with feed_id: {args.feed_id}")  # Debug print
    
    # Set up logger
    logger = setup_logger(args.feed_id)
    
    print("Logger setup complete")  # Debug print

    try:
        # Configuration
        bucket = "dataclinic-gtfs-rt"
        prefix = "norm/bus-mta-vp/vehicles/"
        route_list = args.routes.split(',')

        # Initialize GTFS data once
        logger.info("Loading feed GTFS data...")
        segment_df = GTFS_shape_processor(args.gtfs_url, 4326, 2263).process_shapes()
        gtfs_dict = parse_zipped_gtfs(args.gtfs_url)
        logger.info("Feed GTFS data loaded successfully")

        # Initialize calculator
        logger.info("Initializing SpeedCalculator")
        calculator = SpeedCalculator(
            bucket=bucket,
            prefix=prefix,
            feed_id=args.feed_id,
            gtfs_dict=gtfs_dict,
            segment_df=segment_df
        )

        # Process dates
        date_list = generate_date_list(args.start_date, args.end_date)
        logger.info(f"Processing dates: {date_list} for routes: {route_list}")
        
        for date in date_list:
            calculator.process_date(date, route_list)

    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()