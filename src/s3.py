
import re
from typing import List, Optional
import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
def get_s3_client():
    """
    Returns a boto3 S3 client using standard AWS credentials configuration.
    (i.e., environment variables or ~/.aws/credentials)
    """
    return boto3.client('s3')


def get_s3_resource():
    """
    Returns a boto3 S3 resource using standard AWS credentials configuration.
    Some operations can be more convenient with the resource interface.
    """
    return boto3.resource('s3')


def list_files_in_bucket(bucket_name: str, prefix: str = "") -> List[str]:
    """
    List all files (object keys) in an S3 bucket (optionally with a prefix).

    :param bucket_name: Name of the S3 bucket.
    :param prefix: (Optional) Filter to keys beginning with this prefix.
    :return: A list of object keys.
    """
    s3_client = get_s3_client()

    files = []
    continuation_token = None

    while True:
        if continuation_token:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name, Prefix=prefix, ContinuationToken=continuation_token
            )
        else:
            response = s3_client.list_objects_v2(
                Bucket=bucket_name, Prefix=prefix
            )

        contents = response.get('Contents', [])
        for obj in contents:
            files.append(obj['Key'])

        # Check if there's more data to retrieve
        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    return files


def filter_files_by_pattern(
    bucket_name: str,
    pattern: str,
    prefix: str = "",
    ignore_case: bool = False
) -> List[str]:
    """
    List and filter files in an S3 bucket using a regex pattern.

    :param bucket_name: Name of the S3 bucket.
    :param pattern: Regex pattern to match in the file key.
    :param prefix: (Optional) Filter to keys beginning with this prefix.
    :param ignore_case: If True, case-insensitive matching.
    :return: A list of object keys that match the pattern.
    """
    all_files = list_files_in_bucket(bucket_name, prefix=prefix)

    flags = re.IGNORECASE if ignore_case else 0
    regex = re.compile(pattern, flags=flags)

    filtered = [key for key in all_files if regex.search(key)]
    return filtered


def read_parquet_from_s3(bucket_name: str, key: str) -> pd.DataFrame:
    """
    Read a Parquet file from S3 directly into a Pandas DataFrame.
    Requires 'pyarrow' or 'fastparquet' and 's3fs'.

    :param bucket_name: S3 bucket name.
    :param key: Key (path) to the Parquet file in the bucket.
    :return: Pandas DataFrame.
    """
    # Construct the S3 URL in the form s3://bucket-name/key
    s3_path = f"s3://{bucket_name}/{key}"
    # pandas can read directly from S3 if s3fs is installed
    df = pd.read_parquet(s3_path)
    return df


def upload_file_to_s3(local_file_path: str, bucket_name: str, s3_key: str) -> None:
    """
    Upload a local file to an S3 bucket.

    :param local_file_path: Path to the local file you want to upload.
    :param bucket_name: Name of the S3 bucket.
    :param s3_key: Object key (file name/path) in the bucket.
    """
    s3_client = get_s3_client()
    s3_client.upload_file(local_file_path, bucket_name, s3_key)


def download_file_from_s3(bucket_name: str, s3_key: str, local_file_path: str) -> None:
    """
    Download a file from an S3 bucket to a local path.

    :param bucket_name: Name of the S3 bucket.
    :param s3_key: Object key (file name/path) in the bucket.
    :param local_file_path: Path to save the downloaded file locally.
    """
    s3_client = get_s3_client()
    s3_client.download_file(bucket_name, s3_key, local_file_path)


def delete_file_in_s3(bucket_name: str, s3_key: str) -> None:
    """
    Delete a file in an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param s3_key: Object key (file name/path) to delete.
    """
    s3_client = get_s3_client()
    s3_client.delete_object(Bucket=bucket_name, Key=s3_key)


def load_all_parquet_files(file_list: List[str], bucket: str, max_workers: int = 100) -> pd.DataFrame:
    """
    Load all parquet files from a list of file paths in an S3 bucket.

    :param file_list: List of file paths in the S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param max_workers: Maximum number of worker threads to use.
    """
    dfs = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(read_parquet_from_s3, bucket, key) for key in file_list]
        for future in as_completed(futures):
            try:
                dfs.append(future.result())
            except Exception as e:
                print(f"Error reading a file: {e}")
    print(f"Read {len(dfs)} parquet files from s3")
    return pd.concat(dfs, ignore_index=True)