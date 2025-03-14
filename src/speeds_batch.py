import os  # Used for path operations and directory changes
from datetime import datetime, timedelta  # Used for date handling
import pandas as pd  # Used extensively for data manipulation
from concurrent.futures import ThreadPoolExecutor, as_completed  # Used in load_all_parquet_from_s3
from src.gtfs_segments import GTFS_shape_processor  # Used in calculate_speeds_for_route
from src.speeds import BusSpeedCalculator  # Used in calculate_speeds_for_route
from src.api import parse_zipped_gtfs, query_feed_data, get_access_token  # Used for API interactions
from src.s3 import list_files_in_bucket, read_parquet_from_s3  # Used for S3 operations
from src.logger import setup_logger
import logging

class SpeedsBatch:

    def __init__(self, mdb_id:str, route_id:str, start_date:str, end_date:str, prefix:str, bucket:str, output_dir:str):
        self.ACCESS_TOKEN = get_access_token()
        self.mdb_id = mdb_id
        self.route_id = route_id
        self.start_date = start_date
        self.end_date = end_date
        self.prefix = prefix
        self.bucket = bucket
        self.output_dir = output_dir
        self.logger = logging.LoggerAdapter(
            setup_logger(),
            {'route_id': self.route_id}
        )

    # main function to run the batch
    def run(self):
        self.logger.info(f"Starting batch processing from {self.start_date} to {self.end_date}")
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        current_date = start_date
        
        while current_date <= end_date:
            date = current_date.strftime('%Y%m%d')
            try:
                speeds = self.calculate_speeds_for_route(date)
                output_path = os.path.join(self.output_dir, f"bus_speeds_{self.route_id}_{date}.parquet")
                speeds.to_parquet(output_path)
            except Exception as e:
                self.logger.error(f"Failed to process date {date}: {str(e)}", exc_info=True)
            current_date += timedelta(days=1)

    def fetch_all_static_feeds(self) -> pd.DataFrame:
        self.logger.info("Starting static feeds fetch")
        try:
            response = query_feed_data(self.mdb_id, self.ACCESS_TOKEN)
            if response is None:
                self.logger.error(f"No response received for MDB ID: {self.mdb_id}")
                raise ValueError("No response for mdb_id: ", self.mdb_id)
            
            feed_updates = pd.DataFrame(response)
            if "service_date_range_start" in feed_updates.columns:
                extracted_dates = feed_updates["downloaded_at"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0]
                feed_updates["service_date_range_start"] = feed_updates["service_date_range_start"].fillna(extracted_dates)
            return feed_updates
        except Exception as e:
            self.logger.error(f"Error fetching static feeds: {str(e)}", exc_info=True)
            raise

    def get_static_url_for_date(self, feed_updates: pd.DataFrame, date: str) -> tuple[str, str]:
        candidates = feed_updates[feed_updates["service_date_range_start"] <= date]
        if candidates.empty:
            self.logger.error(f"No static feed found for date {date}")
            return None
        return candidates.iloc[-1]["hosted_url"]

    # def load_all_parquet_from_s3(self, file_list, max_workers=100) -> pd.DataFrame:
    #     self.logger.info(f"Starting to load {len(file_list)} files from S3")
    #     bucket = self.bucket
    #     dfs = []
        
    #     with ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         futures = [executor.submit(read_parquet_from_s3, bucket, key) for key in file_list]
    #         for future in as_completed(futures):
    #             try:
    #                 dfs.append(future.result())
    #             except Exception as e:
    #                 self.logger.error(f"Error reading file from S3: {str(e)}")
        
    #     if not dfs:
    #         self.logger.error("No data loaded from S3")
    #         raise Exception("No data loaded from S3")
        
    #     return pd.concat(dfs, ignore_index=True)


    def load_all_parquet_from_s3(self, file_list, max_workers=100) -> pd.DataFrame:
        self.logger.info(f"Starting to load {len(file_list)} files from S3")
        self.logger.info(f"First few files to process: {file_list[:3]}")  # 显示前几个文件
        bucket = self.bucket
        dfs = []
        failed_files = []  # 记录失败的文件
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            self.logger.info(f"Initialized ThreadPoolExecutor with {max_workers} workers")
            futures = []
            
            # 创建任务并记录
            for key in file_list:
                future = executor.submit(read_parquet_from_s3, bucket, key)
                futures.append((key, future))  # 保存文件名和对应的future
            
            self.logger.info(f"Submitted {len(futures)} tasks to executor")
            
            # 处理结果
            for key, future in futures:
                try:
                    df = future.result()
                    dfs.append(df)
                    if len(dfs) % 10 == 0:  # 每处理10个文件记录一次
                        self.logger.info(f"Successfully processed {len(dfs)}/{len(file_list)} files")
                    
                except Exception as e:
                    failed_files.append(key)
                    self.logger.error(f"Error reading file {key} from S3: {str(e)}")
        
        # 总结处理结果
        self.logger.info(f"Processing complete:")
        self.logger.info(f"- Total files: {len(file_list)}")
        self.logger.info(f"- Successfully loaded: {len(dfs)}")
        self.logger.info(f"- Failed files: {len(failed_files)}")
        
        if failed_files:
            self.logger.warning(f"Failed files list: {failed_files}")
        
        if not dfs:
            self.logger.error("No data loaded from S3")
            raise Exception("No data loaded from S3")
        
        # 合并数据并报告大小
        result_df = pd.concat(dfs, ignore_index=True)
        self.logger.info(f"Final DataFrame size: {len(result_df)} rows")
        self.logger.info(f"Memory usage: {result_df.memory_usage().sum() / 1024 / 1024:.2f} MB")
        
        return result_df

    def calculate_speeds_for_route(self, date):
        self.logger.info(f"Starting speed calculation for date {date}")
        try:
            # Get static feeds
            feed_updates = self.fetch_all_static_feeds()
            correct_url = self.get_static_url_for_date(feed_updates, date)
            
            # Process shapes
            segment_df = GTFS_shape_processor(correct_url, 4326, 2263).process_shapes()
            
            # Load realtime data
            daily_files = list_files_in_bucket(bucket_name=self.bucket, 
                                             prefix=f"{self.prefix}date={date}/")
            print(f"Daily files: {daily_files}")
            vehicle_positions = self.load_all_parquet_from_s3(file_list=daily_files)
            self.logger.info(f"Loaded {len(vehicle_positions)} vehicle positions")
            
            # Parse GTFS and calculate speeds
            GTFS_dict = parse_zipped_gtfs(correct_url)
            speed_calculator = BusSpeedCalculator(vehicle_positions, GTFS_dict, segment_df)
            speeds = speed_calculator.create_trip_speeds()
            speeds = speed_calculator.match_trip_with_route(speeds)
            
            # Filter and process
            speeds = speeds[speeds["route_id"] == self.route_id]
            speeds = speeds[speeds["speed_mph"] < 70]
            speeds["date"] = speeds["interpolated_time"].dt.date
            speeds["weekday"] = speeds["interpolated_time"].dt.weekday
            
            return speeds
            
        except Exception as e:
            self.logger.error(f"Error calculating speeds: {str(e)}", exc_info=True)
            raise
        
