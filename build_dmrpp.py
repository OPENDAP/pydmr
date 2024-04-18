#!/usr/bin/env python3

"""
Build DMR++ documents for granules from a collection
"""

import requests
import time
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
    return [f"https://{hic}/build_dmrpp/collections/{ccid}/granules{granule}" for granule in granules.values()]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC "
                                                 "authentication using an EDL token is needed.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")
    parser.add_argument("-D", "--date-range",
                        help="for a granule request, limit the responses to a range of date/times."
                             "The format is ISO-8601,ISO-8601 (e.g., 2000-01-01T10:00:00Z,2010-03-10T12:00:00Z)")

    parser.add_argument("ccid", help="Build DMR++ documents for granules in this collection")

    args = parser.parse_args()

    try:
        start = time.time()

        entries = cmr.get_collection_granules_temporal(args.ccid, args.date_range)
        urls = build_rest_urls(args.ccid, granules=entries)

        duration = time.time() - start

        print(f'Requesting {urls[0]}:')

        r = requests.get(urls[0])
        if r.status_code == 200:
            print(r.text)
        else:
            print(f'Error: {r.text}')

        print(f'Request time: {duration:.1f}s') if args.time else ''

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
