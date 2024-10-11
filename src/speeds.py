import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.ops import linemerge
import bisect
from tqdm import tqdm
import logging

class BusSpeedCalculator:
    """
    A class to calculate bus speeds along segments of a transit network using GTFS real-time data.
    """

    def __init__(self, GTFS_rt_df, GTFS_dict, GTFS_segments, in_crs=4326, out_crs=2263):
        """
        Initialize the BusSpeedCalculator.

        Parameters:
        GTFS_rt_df (pd.DataFrame): The real-time GTFS data as a pandas DataFrame.
        GTFS_dict (dict): A dictionary containing GTFS data files as DataFrames.
        GTFS_segments (gpd.GeoDataFrame): GeoDataFrame of GTFS segments with geometries.
        in_crs (int): Input Coordinate Reference System (CRS) code. Default is 4326.
        out_crs (int): Output CRS code. Default is 2263.
        """
        self.buses_raw = GTFS_rt_df
        self.GTFS_dict = GTFS_dict
        self.in_crs = in_crs
        self.out_crs = out_crs
        self.GTFS_segments = GTFS_segments

    def prep_buses(self):
        """
        Prepare the buses DataFrame by converting it to a GeoDataFrame,
        transforming coordinate systems, and merging with GTFS trip data.

        Returns:
        gpd.GeoDataFrame: Prepared buses GeoDataFrame.
        """
        buses = self.buses_raw.copy()

        buses = gpd.GeoDataFrame(
            buses,
            geometry=gpd.points_from_xy(
                buses["vehicle.position.longitude"],
                buses["vehicle.position.latitude"]
            ),
            crs=self.in_crs
        ).drop("id", axis = 1)

        buses = buses.to_crs(self.out_crs)

        buses.columns = buses.columns.str.replace("vehicle.", '', regex=False)
        buses.columns = buses.columns.str.replace('trip.', '', regex=False)
        buses.columns = buses.columns.str.replace('position.', '', regex=False)

        required_columns = ['trip_id', 'id', 'start_date']
        for col in required_columns:
            if col not in buses.columns:
                raise KeyError(f"Required column '{col}' is missing in the buses DataFrame.")

        buses["unique_trip_id"] = (
            buses["trip_id"].astype(str) +
            buses["id"].astype(str) +
            buses["start_date"].astype(str)
        )

        # Merge with 'trips.txt' to get 'shape_id'
        buses = buses.merge(
            self.GTFS_dict['trips.txt'][["trip_id", "shape_id"]].drop_duplicates(),
            on='trip_id',
            how='inner'
        )

        return buses

    def prep_full_strings(self):
        """
        Prepare full strings (merged LineStrings) for each shape_id.

        Returns:
        dict: Dictionary mapping shape_id to merged LineString geometry.
        """
        # Group by 'shape_id' and merge LineStrings
        full_strings = self.GTFS_segments.groupby("shape_id")["geometry"].apply(
            lambda x: linemerge(list(x.dropna()))
        )
        return full_strings.to_dict()

    def add_position_on_route(self, buses, full_strings_dict):
        """
        Add 'distance_to_line' and 'position_on_line' to buses GeoDataFrame.

        Parameters:
        buses (gpd.GeoDataFrame): GeoDataFrame of bus positions.
        full_strings_dict (dict): Dictionary mapping shape_id to merged LineString geometry.

        Returns:
        gpd.GeoDataFrame: Updated buses GeoDataFrame with additional columns.
        """
        # Initialize arrays
        distances = np.empty(len(buses))
        positions = np.empty(len(buses))
        distances.fill(np.nan)
        positions.fill(np.nan)

        # Loop over buses
        for i, (point, shape_id) in enumerate(zip(buses['geometry'], buses['shape_id'])):
            if pd.notnull(point) and shape_id in full_strings_dict:
                line = full_strings_dict[shape_id]
                distances[i] = point.distance(line)
                positions[i] = line.project(point)

        # Assign to DataFrame
        buses['distance_to_line'] = distances
        buses['position_on_line'] = positions

        return buses

    def _longest_increasing_subsequence(self, df):
        """
        Finds the longest increasing subsequence in the 'position_on_line' column of a DataFrame.

        Parameters:
        df (pd.DataFrame): DataFrame sorted by 'timestamp' and containing 'position_on_line' column.

        Returns:
        pd.DataFrame: DataFrame containing the longest increasing subsequence.
        """
        positions = df['position_on_line'].values
        n = len(positions)

        # Arrays to hold the end positions and predecessors
        tails = []
        predecessors = [-1] * n
        indices = []

        for i in range(n):
            pos = positions[i]
            # Find the insertion point
            idx = bisect.bisect_left(tails, pos)

            if idx == len(tails):
                tails.append(pos)
                indices.append(i)
            else:
                tails[idx] = pos
                indices[idx] = i

            if idx > 0:
                predecessors[i] = indices[idx - 1]

        # Reconstruct the longest increasing subsequence
        lis_indices = []
        k = indices[-1]
        while k >= 0:
            lis_indices.append(k)
            k = predecessors[k]
        lis_indices.reverse()

        # Return the DataFrame rows corresponding to the longest increasing subsequence
        return df.iloc[lis_indices].reset_index(drop=True)

    def create_trip_speeds(self):
        """
        Create trip speeds by processing bus positions and calculating speeds along segments.

        Returns:
        pd.DataFrame: DataFrame containing speed information for each trip segment.
        """
        full_strings = self.prep_full_strings()
        buses = self.prep_buses()
        buses_with_speeds = self.add_position_on_route(buses, full_strings)

        trip_ids = buses_with_speeds["unique_trip_id"].drop_duplicates()
        buses_with_speeds = buses_with_speeds.set_index("unique_trip_id")
        trip_speeds = {}
        print(f"Processing {len(trip_ids)} trips...")
        for trip_id in tqdm(trip_ids):
            trip_df = buses_with_speeds.loc[trip_id]
            if isinstance(trip_df, pd.Series):
                trip_df = trip_df.to_frame().T

            if trip_df.shape[0] < 10:
                continue
            trip_df = trip_df.sort_values(by="timestamp")
            trip_df = self._longest_increasing_subsequence(trip_df)
            trip_df["epoch_timestamp"] = trip_df["timestamp"].astype(int) // 10**9

            shape_id = trip_df["shape_id"].iloc[0]
            trip_segments = self.GTFS_segments[self.GTFS_segments["shape_id"] == shape_id].copy()
            trip_segments = trip_segments.sort_values("projected_position")

            trip_segments["interpolated_time"] = pd.to_datetime(
                np.round(
                    np.interp(
                        trip_segments["projected_position"],
                        trip_df["position_on_line"],
                        trip_df["epoch_timestamp"]
                    )
                ),
                unit='s'
            )

            trip_segments["time_elapsed"] = trip_segments["interpolated_time"].diff().dt.total_seconds()
            trip_segments["speed_mph"] = (
                (trip_segments["segment_length"] / trip_segments["time_elapsed"]) * 0.681818
            )
            trip_segments["unique_trip_id"] = trip_id
            trip_segments = trip_segments.drop("geometry", axis=1).replace(
                [np.inf, -np.inf], np.nan
            ).dropna()

            trip_speeds[trip_id] = trip_segments

        if trip_speeds:
            return pd.concat(trip_speeds.values(), ignore_index=True)
        else:
            return pd.DataFrame()
