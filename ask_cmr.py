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
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    group = parser.add_mutually_exclusive_group() # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")
    group.add_argument("-c", "--collection", help="a collection id, by itself, print some info")
    group.add_argument("-r", "--resty-path", help="get the data URL for an OPeNDAP EDC REST URL")

    parser.add_argument("-o", "--opendap", help="for a provider, show only collections with opendap URLS", action="store_true")
    parser.add_argument("-g", "--granules", help="for a collection, get info about all the granules", action="store_true")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False
    pretty = True if args.pretty else False
    opendap = True if args.opendap else False
    granules = True if args.granules else False

    try:
        start = time.time()
        if args.collection and granules:
            entries = cmr.get_collection_granules(args.collection, pretty)
        elif args.collection:
            entries = cmr.get_collection_entry(args.collection, pretty)
        elif args.resty_path:
            entries = cmr.decompose_resty_url(args.resty_path, pretty)
        else:
            entries = cmr.get_provider_collections(args.provider, opendap, pretty)
        duration = time.time() - start

        for key, value in entries.items():
            print(f'{key}: {value}')

        print(f'Total entries: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
