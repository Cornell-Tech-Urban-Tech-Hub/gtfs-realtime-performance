#!/bin/bash

# First feed
python runner.py \
    --start-date 2024-12-01 \
    --end-date 2024-12-11 \
    --feed-id mdb-513-202409090026 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202409090026/mdb-513-202409090026.zip" \
    --routes M102,M50

# Wait a bit between runs
sleep 60

# Second feed
python runner.py \
    --start-date 2024-12-12 \
    --end-date 2025-01-04 \
    --feed-id mdb-513-202412120015 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202412120015/mdb-513-202412120015.zip" \
    --routes M102,M50

sleep 60

# Third feed
python runner.py \
    --start-date 2025-01-24 \
    --end-date 2025-02-08 \
    --feed-id mdb-513-202501230024 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202501230024/mdb-513-202501230024.zip" \
    --routes M102,M50

sleep 60

# Fourth feed
python runner.py \
    --start-date 2025-02-09 \
    --end-date 2025-03-29 \
    --feed-id mdb-513-202502170105 \
    --gtfs-url "https://files.mobilitydatabase.org/mdb-513/mdb-513-202502170105/mdb-513-202502170105.zip" \
    --routes M102,M50 


    