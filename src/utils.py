import requests
import gzip
import pandas as pd
import tempfile
import shutil
import os
import geopandas as gpd
import numpy as np
import tarfile
import traceback

def read_parquet_from_tar_gz(url):
    """
    Downloads a .tar.gz file from the given URL, extracts its contents which are 
    expected to be Parquet files, and reads them into a single Pandas DataFrame.

    Parameters:
    url (str): URL to the .tar.gz file.

    Returns:
    pd.DataFrame: DataFrame containing the data from the Parquet files.
    """

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the .tar.gz file
        response = requests.get(url)
        tar_gz_path = os.path.join(temp_dir, 'data.tar.gz')
        with open(tar_gz_path, 'wb') as f:
            f.write(response.content)

        # Extract the .tar.gz file
        with tarfile.open(tar_gz_path, 'r:gz') as tar:
            tar.extractall(path=temp_dir)

        # Read all Parquet files in the temp directory into DataFrames
        df_list = []
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                try: 
                    file_path = os.path.join(root, file)
                    df_list.append(pd.read_parquet(file_path))
                except:  # Catch the exception
                    continue

        # Concatenate all DataFrames
        df = pd.concat(df_list, ignore_index=True)

    return df