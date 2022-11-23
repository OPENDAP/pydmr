#!/usr/bin/env python3

"""
Find all the NASA ESDIS Providers in the CMR catalog that have collections
accessible using OPeNDAP.
"""

import xml.dom.minidom as minidom
import xml.dom
import time
import os

import cmr
import opendap_tests


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Providers with Collections "
                                                 "accessible using OPeNDAP.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False

    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        # cmr_endpoint = "https://cmr.earthdata.nasa.gov/search/collections.umm_json"
        # cmr_base_query = "${cmr_endpoint}?pretty=true&has_opendap_url=true"

        # entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)

        pretty = '&pretty=true' if args.pretty else ''
        opendap = '&has_opendap_url=true'
        service = 'cmr.earthdata.nasa.gov'
        cmr_query_url = f'https://{service}/search/collections.umm_json?{opendap}{pretty}'

        # this uses the new return value as a set feature of process_request
        entries = cmr.process_request(cmr_query_url, cmr.provider_id, page_size=2000)

        duration = time.time() - start

        print(f'Total providers found: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

        for provider in entries:
            print(provider)

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
