import os 
import pandas as pd
import os
os.chdir("/home/canyon/Bus-Weather-Impacts")
import numpy as np
import geopandas as gpd
import numpy as np
from shapely.ops import nearest_points
pd.options.mode.chained_assignment = None
from shapely.geometry import Point, LineString
import src.api as api
from shapely.ops import linemerge
from shapely.ops import substring

class GTFS_shape_processor:
    """
    A class to process GTFS shapes and stop data, compute distances, 
    and create segments between stops along routes.
    """
    
    def __init__(self, GTFS_zip_file, crs=4326, target_crs=2263):
        """
        Initialize the processor with GTFS zip file and coordinate reference systems.
        
        Parameters:
        - GTFS_zip_file: Path to the GTFS zip file.
        - crs: The coordinate reference system of the input data (default EPSG:4326).
        - target_crs: The target CRS for output (default EPSG:2263).
        """
        self.GTFS_dict = api.parse_zipped_gtfs(GTFS_zip_file)
        self.crs = crs
        self.target_crs = target_crs

    def _prep_shapes(self, shapes):
        """
        Prepare shapes by grouping them into LineStrings based on shape_id.
        
        Parameters:
        - shapes: The 'shapes.txt' data from the GTFS file.

        Returns:
        - A GeoDataFrame with LineStrings for each shape_id.
        """
        gdf = shapes.groupby('shape_id').apply(
            lambda x: LineString(zip(x['shape_pt_lon'], x['shape_pt_lat'])), include_groups =False
        ).reset_index()

        gdf = gdf.rename(columns={0: 'geometry'})
        gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
        gdf = gdf.set_crs(epsg=self.crs)

        return gdf

    def _prep_GTFS(self):
        """
        Prepare the merged stop and shape data from the GTFS files.

        Returns:
        - merged_stops: A GeoDataFrame of stops with geometry.
        - shape_lines: A GeoDataFrame of shape lines.
        """
        stop_times = self.GTFS_dict['stop_times.txt']
        shapes = self.GTFS_dict['shapes.txt']
        stops = self.GTFS_dict['stops.txt']
        trips = self.GTFS_dict['trips.txt']

        merged_stops = stop_times.merge(trips).drop_duplicates(["stop_id", "shape_id"]).merge(stops)
        merged_stops['geometry'] = merged_stops.apply(lambda row: Point(row['stop_lon'], row['stop_lat']), axis=1)
        merged_stops = gpd.GeoDataFrame(merged_stops, geometry='geometry').set_crs(self.crs).to_crs(self.target_crs)

        shape_lines = self._prep_shapes(shapes).to_crs(self.target_crs).set_index("shape_id")

        return merged_stops, shape_lines

    def _get_shape_position(self, point_location, shape_id, shape_lines):
        """
        Compute the distance from a stop point to the nearest location on a shape line.

        Parameters:
        - point_location: A shapely Point object representing the stop location.
        - shape_id: The shape_id corresponding to the route.
        - shape_lines: A GeoDataFrame containing LineStrings for each shape_id.

        Returns:
        - A dictionary containing the distance to the line and the projected position along the line.
        """
        out = {}
        try:
            line = shape_lines.loc[shape_id].iloc[0]
            out["distance_to_line"] = point_location.distance(line)
            out["projected_position"] = line.project(point_location)
        except KeyError:
            out["distance_to_line"] = None
            out["projected_position"] = None

        return out
    
    def _create_segment(self, shape_lines, shape_id, distance1, distance2):
        """
        Create a segment from a LineString defined by two distances along the line.

        Parameters:
        - shape_lines: A GeoDataFrame containing LineStrings for each shape_id.
        - shape_id: The shape_id corresponding to the route.
        - distance1: First distance along the LineString.
        - distance2: Second distance along the LineString.

        Returns:
        - A LineString representing the segment between distance1 and distance2, or None if an error occurs.
        """
        try:
            line = shape_lines.loc[shape_id].iloc[0]
            # Ensure distance1 is less than distance2
            start_distance = min(distance1, distance2)
            end_distance = max(distance1, distance2)
            segment = substring(line, start_distance, end_distance)
            return segment
        except Exception as e:
            return None

    def process_shapes(self, out_path=None):
        """
        Process the GTFS shapes and stop data, computing the segment between consecutive stops.

        Parameters:
        - out_path: If specified, saves the output GeoDataFrame to a file. Otherwise, returns the GeoDataFrame.

        Returns:
        - A GeoDataFrame containing segments between consecutive stops, or writes to a file if out_path is specified.
        """
        merged_stops, shape_lines = self._prep_GTFS()
        
        dists = merged_stops.apply(lambda x: self._get_shape_position(x.geometry, x.shape_id, shape_lines), axis=1)
        merged_stops = merged_stops.join(pd.json_normalize(dists))
        merged_stops["prev_projected_position"] = merged_stops.groupby("shape_id")["projected_position"].shift(1)
        merged_stops["prev_stop_id"] = merged_stops.groupby("shape_id")["stop_id"].shift(1)
        merged_stops["prev_stop_name"] = merged_stops.groupby("shape_id")["stop_name"].shift(1)
        merged_stops["segment_length"] = merged_stops["projected_position"] - merged_stops["prev_projected_position"]
        merged_stops = merged_stops.dropna(subset = ["prev_stop_id"])

        merged_stops["segment_linestring"] = merged_stops.apply(
            lambda x: self._create_segment(shape_lines, x.shape_id, x.prev_projected_position, x.projected_position), 
            axis=1
        )
        
        merged_stops = gpd.GeoDataFrame(merged_stops.drop("geometry", axis=1).rename({"segment_linestring" : "geometry"}, axis = 1), geometry="geometry", crs=self.target_crs)

        out_cols = ["trip_id", "shape_id", "stop_sequence", "stop_id", "stop_name", "prev_stop_id", "prev_stop_name", "projected_position", "prev_projected_position", "segment_length", "geometry"]

        merged_stops["trip_id"] = merged_stops["trip_id"].astype(str)
        merged_stops["shape_id"] = merged_stops["shape_id"].astype(str)
        merged_stops["stop_id"] = merged_stops["stop_id"].astype(int)
        merged_stops["stop_name"] = merged_stops["stop_name"].astype(str)
        merged_stops["prev_stop_id"] = merged_stops["prev_stop_id"].astype(int)
        merged_stops["prev_stop_name"] = merged_stops["prev_stop_name"].astype(str)
        merged_stops["projected_position"] = merged_stops["projected_position"].astype(float)
        merged_stops["prev_projected_position"] = merged_stops["prev_projected_position"].astype(float)
                

        if out_path is not None:
            merged_stops[out_cols].to_file(out_path)
            print(f"Wrote segments to {out_path}")
        else:
            return merged_stops[out_cols]