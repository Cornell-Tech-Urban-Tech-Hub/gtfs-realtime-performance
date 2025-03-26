#!/bin/bash

echo "Starting processing at $(date)"

# Staten Island (mdb-514)
python runner.py \
    --start-date 2024-12-01 \
    --end-date 2025-01-04 \
    --feed-id mdb-514-202412120006 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-514/mdb-514-202412120006/mdb-514-202412120006.zip" \
    --routes SIM24,SIM4X

echo "All feeds processed at $(date)" 