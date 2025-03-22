To run: 
Make sure you're in gtfs-realtime-performance directory
cd root
```
python -m spark.run_speed_calculation \
    --start-date 2025-01-07 \
    --end-date 2025-01-10 \
    --feed-id mdb-513-202501020055 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501020055/mdb-513-202501020055.zip"
```

## SpeedCalculator (speed_calculator.py):
Acts as the core processing engine
Handles the data transformation logic

## Runner Script (run_speed_calculation.py):
Handles the execution flow
Manages command line arguments
Controls the processing loop
Handles error cases and file existence checks