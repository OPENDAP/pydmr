#!/usr/bin/env python3

"""
Simple test driver for all Collections held by a NASA DAAC that have OPeNDAP
URLS in the CMR catalog system. The test driver runs a suite of tests on the
oldest and newest granules in each collection.

The output of this test driver is an XML document that can be used as a document
in its own right or rendered as an HTML web page.
"""

import xml.dom.minidom
import xml.dom
import time
import cmr


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    parser.add_argument("-d", "--dmr", help="Test getting the DMR response", action="store_true", default=True)
    parser.add_argument("-D", "--dap", help="Test getting the DAP response", action="store_true")
    parser.add_argument("-n", "--netcdf4", help="Test getting the NetCDF4 file response", action="store_true")

    group = parser.add_mutually_exclusive_group(required=True)   # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False

    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)

        # For each collection...
        for ccid, title in entries.items():
            print(f'{ccid}: {title}') if args.verbose else ''
            first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=args.pretty)
            for gid, granule_tuple in first_last_dict.items():
                print(f'{gid}: {granule_tuple}') if args.verbose else ''
                # The granule_tuple is the granule title and opendap url
                test_results = cmr.url_test_runner(granule_tuple[1])
                print(f'{gid}: {test_results}')

        duration = time.time() - start

        print(f'Total collections tested: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
