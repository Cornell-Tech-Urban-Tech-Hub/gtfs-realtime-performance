#!/bin/bash

echo "Starting processing at $(date)"

echo "Processing Manhattan routes (M102,M50)..."
# Manhattan (mdb-513)
python runner.py \
    --start-date 2024-11-01 \
    --end-date 2024-12-11 \
    --feed-id mdb-513-202409090026 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202409090026/mdb-513-202409090026.zip" \
    --routes M50,M102

echo "Waiting 60 seconds..."
sleep 60

echo "Processing Staten Island routes (SIM24,SIM4X)..."
# Staten Island (mdb-514)
python runner.py \
    --start-date 2024-11-01 \
    --end-date 2025-01-04 \
    --feed-id mdb-514-202412120006 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202412120006/mdb-514-202412120006.zip" \
    --routes SIM24,SIM4X

echo "Waiting 60 seconds..."
sleep 60

python runner.py \
    --start-date 2025-01-05 \
    --end-date 2025-02-09 \
    --feed-id mdb-514-202501020130 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202501020130/mdb-514-202501020130.zip" \
    --routes SIM24,SIM4X

echo "Waiting 60 seconds..."
sleep 60

python runner.py \
    --start-date 2025-02-10 \
    --end-date 2025-03-29 \
    --feed-id mdb-514-202502170029 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202502170029/mdb-514-202502170029.zip" \
    --routes SIM24,SIM4X

echo "Waiting 60 seconds..."
sleep 60

echo "Processing Brooklyn route (B39)..."
# Brooklyn (mdb-512)
python runner.py \
    --start-date 2024-11-01 \
    --end-date 2024-12-11 \
    --feed-id mdb-512-202408290005 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202408290005/mdb-512-202408290005.zip" \
    --routes B39

echo "Waiting 60 seconds..."
sleep 60

python runner.py \
    --start-date 2024-12-12 \
    --end-date 2025-01-03 \
    --feed-id mdb-512-202412120015 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202412120015/mdb-512-202412120015.zip" \
    --routes B39

echo "Waiting 60 seconds..."
sleep 60

python runner.py \
    --start-date 2025-01-04 \
    --end-date 2025-02-08 \
    --feed-id mdb-512-202501020103 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202501020103/mdb-512-202501020103.zip" \
    --routes B39

echo "Waiting 60 seconds..."
sleep 60

python runner.py \
    --start-date 2025-02-09 \
    --end-date 2025-03-29 \
    --feed-id mdb-512-202502170011 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-512/mdb-512-202502170011/mdb-512-202502170011.zip" \
    --routes B39

echo "All feeds processed at $(date)" 