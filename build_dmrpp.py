#!/usr/bin/env python3

"""
Build DMR++ documents for granules from a collection
"""

import sys
import time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import requests

import cmr


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
        print(result)  # Replace with your desired result handling


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

    try:
        # since build_save_dmrpp() takes two constant args, curry the function binding values to the constant
        # value parameters so the result can be used with concurrent ThreadPool map(). jhrg 4/19/24
        curried_build_save_dmrpp = partial(build_save_dmrpp, directory=args.ccid, headers=headers, verbose=args.very_verbose)
        parallel_processing(curried_build_save_dmrpp, urls, granule_names)
    except Exception as e:
        print(f'DMR++ Build failure: {e}')

    duration = time.time() - start

    print(f'Processing {len(urls)} granules, response time: {duration:.1f}s') if args.time else ''


if __name__ == "__main__":
    main()

