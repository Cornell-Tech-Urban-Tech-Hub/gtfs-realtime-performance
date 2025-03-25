#!/bin/bash

echo "Starting test processing at $(date)"

# Test with one command
python runner.py \
    --start-date 2024-11-01 \
    --end-date 2024-12-11 \
    --feed-id mdb-513-202409090026 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202409090026/mdb-513-202409090026.zip" \
    --routes M50,M102

echo "Test processing completed at $(date)" 