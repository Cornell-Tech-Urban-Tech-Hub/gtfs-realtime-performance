import requests
import zipfile
import io
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def get_access_token(refresh_token = REFRESH_TOKEN):
    url = "https://api.mobilitydatabase.org/v1/tokens"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        # Access the response JSON content
        return response.json()['access_token']
    else:
        print(f"Request failed with status code {response.status_code}")

def query_feed_data(feed_id, access_token):
    url_metadata = f"https://api.mobilitydatabase.org/v1/gtfs_feeds/{feed_id}/datasets"
    headers_metadata = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response_metadata = requests.get(url_metadata, headers=headers_metadata)

    if response_metadata.status_code == 200:
        return response_metadata.json()
    else:
        print(f"Request failed with status code {response_metadata.status_code}")


def parse_zipped_gtfs(url):
    response = requests.get(url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    file_names = zip_file.namelist()

    dataframes = {}
    for file_name in file_names:
        if file_name.endswith('.txt'):
            with zip_file.open(file_name) as csv_file:
                df = pd.read_csv(csv_file)
                dataframes[file_name] = df
    print("Parsed GTFS static feed data successfully")

    return dataframes