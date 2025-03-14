import os
from src.speeds_batch import SpeedsBatch

def main():
    os.makedirs('data/speeds', exist_ok=True)
    
    config = {
        "mdb_id": "mdb-513",
        "route_id": "M50",
        "start_date": "2025-01-06",
        "end_date": "2025-01-08",
        "prefix": "norm/bus-mta-vp/vehicles/",
        "bucket": "dataclinic-gtfs-rt",
        "output_dir": "data/speeds"
    }
    
    try:
        batch_processor = SpeedsBatch(**config)
        batch_processor.run()
        print("Processing completed successfully")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()