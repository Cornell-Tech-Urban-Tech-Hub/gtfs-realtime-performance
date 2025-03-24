#!/bin/bash

# List of feeds to process
FEEDS=(
    "mdb-513"
    "mdb-514"
    # Add more feed IDs as needed
)

# Common parameters
START_DATE="2025-01-07"
END_DATE="2025-01-10"
ROUTES="M50,M15"

# Process each feed
for feed_id in "${FEEDS[@]}"
do
    echo "Processing feed: $feed_id"
    
    # Construct GTFS URL
    GTFS_URL="https://files.mobilitydatabase.org/$feed_id/$feed_id-202501020055/$feed_id-202501020055.zip"
    
    # Run the processing script
    python runner.py \
        --start-date "$START_DATE" \
        --end-date "$END_DATE" \
        --feed-id "$feed_id" \
        --gtfs-url "$GTFS_URL" \
        --routes "$ROUTES"
    
    # Wait between feeds
    sleep 60
done 