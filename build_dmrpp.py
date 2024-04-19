#!/usr/bin/env python3

"""
Build DMR++ documents for granules from a collection
"""

import os
import sys
import time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import requests
import boto3

import cmr


def make_s3_client(key_id: str, secret_access_key: str, region_name='us-west-2'):
    """
    Make an S3 client
    Args:
        key_id:
        secret_access_key:
        region_name: us-west-2 by default

    Returns:
        An S3 client object
    """
    print(f"Using {region_name} region")
    print(f"Using {key_id} key")
    print(f"Using {secret_access_key} secret")
    return boto3.client('s3',
                         aws_access_key_id=key_id,
                         aws_secret_access_key=secret_access_key,
                         region_name=region_name)


def upload_to_s3(s3_client: object, bucket_name: str, object_key: str, data_string: str, verbose=False) -> bool:
    """
    Upload a file to an S3 bucket
    Args:
        s3_client: An S3 client object
        bucket_name:
        object_key:
        data_string: For this code, a DMR++ document.
        verbose: True prints more info, including on success

    Returns:
        True on success, False otherwise
    """
    try:
        data_bytes = data_string.encode('utf-8')
        # Body=data_bytes, Bucket=bucket_name, Key=object_key
        s3_client.put_object(Body=data_bytes, Bucket=bucket_name, Key=object_key)
        if verbose:
            print(f"Data uploaded successfully to s3://{bucket_name}/{object_key}")
        return True
    except Exception as e:
        print(f"Error uploading data: {e}")
        return False


def build_rest_urls(ccid: str, granules: dict, hic='opendap.earthdata.nasa.gov') -> list:
    """
    Extract each granule from the granules dictionary and build
    a list of OPeNDAP RESTified URLs that will get a DMR++ from the
    DMR++ BaaS.

    Args:
        ccid: The Collection Concept ID. All the granules are part
        of this collection
        granules: The dictionary of GIDs and granule names
        hic: Hyrax in the cloud. Change for SIT and UAT environments

    Returns:
        Alist of URLs that will each return one DMR++ document
    """
    return [f"https://{hic}/build_dmrpp/collections/{ccid}/granules/{granule}" for granule in granules.values()]


def build_save_dmrpp(url: str, filename: str, directory: str, headers: dict[str,str], verbose=False) -> tuple[int,str]:
    """
    Build a DMR++ document. Save it to a local file
    Args:
        url: RESTified URL to DMR++ Builder
        filename: Save to this file
        directory: Save into this directory
        headers: Used these headers when running the DMR++ Builder
        verbose: Chatty output?

    Returns:
        A tuple of HTTP status code and URL.
    """
    if verbose:
        print(f'Requesting {url}')
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        with open(f'./{directory}/{filename}.dmrpp', "wt") as file:
            file.writelines(r.text)
        if verbose:
            print(f'Saved to {filename}')
        else:
            print(".", end="")
            sys.stdout.flush()
    else:
        with open(f'./{directory}/{filename}.error', "wt") as file:
            file.writelines(r.text)
        if verbose:
            print(f'Error: {r.text} ({url})')

    return r.status_code, url


def build_save_to_s3_dmrpp(url: str, object_key: str, bucket: str, s3_client: object, ccid: str, headers: dict[str,str], verbose=False) -> tuple[int,str]:
    """
    Build a DMR++ document. Save it to an S3 Bucket
    Args:
        url: RESTified URL to DMR++ Builder
        object_key: Save to this key. The actual key is the ccid/granule name
        bucket: S3 Bucket name
        s3_client: Use this S3 client to upload the file
        ccid: Collection Concept ID. Combined with the granule name to make the object key
        headers: Used these headers when running the DMR++ Builder
        verbose: Chatty output?

    Returns:
        A tuple of HTTP status code and URL.
    """
    if verbose:
        print(f'Requesting {url}')
    r = requests.get(url, headers=headers)
    dmrpp_key = f"{ccid}/{object_key}.dmrpp"
    if r.status_code == 200:
        status = upload_to_s3(s3_client, bucket, dmrpp_key, r.text, verbose=verbose)
        if not status:
            msg = f"Error uploading DMR++ document to S3: {url}"
            if verbose:
                print(msg)
            return -1, msg

        if verbose:
            print(f'Saved to {object_key}')
        else:
            print(".", end="")
            sys.stdout.flush()
    else:
        error_key = f"{ccid}/{object_key}.error"
        upload_to_s3(s3_client, bucket, error_key, r.text, verbose=verbose)
        if verbose:
            print(f'Error: {r.text} ({url})')

    return r.status_code, url


def parallel_processing(dmrpp_builder: Callable[[str,str],tuple[int,str]], urls: list[str], names: list[str]):
    # Ensure lists have the same size
    if len(urls) != len(names):
        raise ValueError("URL and name lists must have the same size")

    # Use ThreadPoolExecutor with 10 worker threads
    with ThreadPoolExecutor(max_workers=16) as executor:
        # Submit tasks (URL/name pairs) to the executor
        results = executor.map(dmrpp_builder, urls, names)

    # Process or display the results
    for result in results:
        if result[0] != 200:
            print(f'Error: {result[0]}: {result[1]}')


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC "
                                                 "authentication using an EDL token is needed.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-V", "--very-verbose", help="really increase output verbosity", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")
    parser.add_argument("-D", "--date-range",
                        help="for a granule request, limit the responses to a range of date/times."
                             "The format is ISO-8601,ISO-8601 (e.g., 2000-01-01T10:00:00Z,2010-03-10T12:00:00Z)")
    parser.add_argument("-S", "--s3-bucket", help="Upload built DMR++ documents to this S3 bucket")
    parser.add_argument("-T", "--token", help="EDL authentication token")

    parser.add_argument("ccid", help="Build DMR++ documents for granules in this collection")

    args = parser.parse_args()

    start = time.time()

    try:
        path = Path(args.ccid)
        if not path.is_dir():
            path.mkdir(parents=True)

        entries = cmr.get_collection_granules_temporal(args.ccid, args.date_range)
        urls = build_rest_urls(args.ccid, granules=entries, hic='opendap.sit.earthdata.nasa.gov')
        granule_names = [granule for granule in entries.values()]

        if args.verbose:
            print(f'Processing {len(urls)} granules')

        with open(args.token, "rt") as file:
            token = file.readline().strip()
        headers = {'Authorization': f'Bearer {token}', 'Accepts': 'deflate', 'User-Agent': 'James-pydmr'}

    except Exception as e:
        print(f'Initialization failure: {e}')
        exit(1)

    try:
        if args.s3_bucket:
            # Get the value of an environment variable
            key_id = os.environ.get('AWS_ACCESS_KEY_ID')
            secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            region = os.environ.get('AWS_DEFAULT_REGION')
            if not region:
                region = 'us-west-2'

            s3 = make_s3_client(key_id, secret_access_key, region_name=region)

            dmrpp_builder_function = partial(build_save_to_s3_dmrpp, bucket=args.s3_bucket, s3_client=s3,
                                             ccid=args.ccid, headers=headers, verbose=args.very_verbose)

        else:
            # since build_save_dmrpp() takes two constant args, curry the function binding values to the constant
            # value parameters so the result can be used with concurrent ThreadPool map(). jhrg 4/19/24
            dmrpp_builder_function = partial(build_save_dmrpp, directory=args.ccid, headers=headers,
                                             verbose=args.very_verbose)

        parallel_processing(dmrpp_builder_function, urls, granule_names)

    except Exception as e:
        print(f'DMR++ Build failure: {e}')

    duration = time.time() - start

    print(f'Processing {len(urls)} granules, response time: {duration:.1f}s') if args.time else ''


if __name__ == "__main__":
    main()

