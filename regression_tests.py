#!/usr/bin/env python3

"""
Command line tool for sending simple requests to CMR and printing the
results to stdout. This command knows how to find all the collections
for a given provider (and it will optionally limit them to only those with
OPeNDAP URLs).

It will also return all the granules for a given collection and
"""

import time
import cmr


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    group = parser.add_mutually_exclusive_group() # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")

    parser.add_argument("-o", "--opendap", help="for a provider, show only collections with OPeNDAP URLS", action="store_true")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False
    pretty = True if args.pretty else False
    opendap = True if args.opendap else False

    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap, pretty=pretty)

        # For each collection...
        for ccid, title in entries.items():
            print(f'{ccid}: {title}')
            first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=pretty)
            print(f'first_last_dict: {first_last_dict}')

        duration = time.time() - start
        print(f'Request time: {duration:.1f}s') if args.time else ''

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
