#!/usr/bin/env python3

"""
Given a URL to a file (nominally in S3 and managed by the EDC, get the paired DMR++ document
"""

import requests
import time


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    parser.add_argument("url", help="The URL to a file that has a paired DMR++ document")

    args = parser.parse_args()

    try:
        start = time.time()
        r = requests.get(f'{args.url}.dmrpp')
        duration = time.time() - start

        if r.status_code == 200:
            print(r.text)
        else:
            print(f'Error: {r.text}')

        print(f'Request time: {duration:.1f}s') if args.time else ''

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
