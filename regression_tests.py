#!/usr/bin/env python3

"""
Simple test driver for all Collections held by a NASA DAAC that have OPeNDAP
URLS in the CMR catalog system. The test driver runs a suite of tests on the
oldest and newest granules in each collection.

The output of this test driver is an XML document that can be used as a document
in its own right or rendered as an HTML web page.
"""

import xml.dom.minidom as minidom
import time
import os

import cmr
import opendap_tests


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")
    parser.add_argument("-q", "--quiet", help="quiet the tests. By default print a dot for each test run",
                        action="store_true", default=False)
    parser.add_argument("-s", "--save", help="directory to hold the test responses. Make the directory if needed.",
                        default='')

    parser.add_argument("-d", "--dmr", help="Test getting the DMR response", action="store_true", default=True)
    parser.add_argument("-D", "--dap", help="Test getting the DAP response", action="store_true")
    parser.add_argument("-n", "--netcdf4", help="Test getting the NetCDF4 file response", action="store_true")

    parser.add_argument("-V", "--version", help="increase output verbosity", action="store_true", default="1")

    group = parser.add_mutually_exclusive_group(required=True)   # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False

    opendap_tests.quiet = args.quiet
    opendap_tests.save = args.save
    if args.save != '' and not os.path.exists(opendap_tests.save):
        os.mkdir(opendap_tests.save)

    try:
        start = time.time()

        # make the response document
        root = minidom.Document()
        provider = root.createElement('Provider')
        provider.setAttribute('name', args.provider)
        provider.setAttribute('date', time.asctime())
        root.appendChild(provider)

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)
        # TODO Write an <Error ...> element if there are no entries.
        #  Same for the Collection and Test elements. jhrg 11/22/22

        # For each collection...
        for ccid, title in entries.items():
            print(f'{ccid}: {title}') if args.verbose else ''

            # XML element for the collection
            collection = root.createElement('Collection')
            collection.setAttribute('ccid', ccid)
            collection.setAttribute('long_name', title)
            provider.appendChild(collection)

            first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=args.pretty)
            for gid, granule_tuple in first_last_dict.items():
                # The granule_tuple is the granule title and opendap url
                test_results = opendap_tests.url_test_runner(granule_tuple[1], True, False, False)
                print(f'{gid}: {test_results}') if args.verbose else ''

                # Add XML for all the tests we ran
                for name, result in test_results.items():
                    if result != "NA":
                        test = root.createElement('Test')
                        test.setAttribute('name', name)
                        test.setAttribute('url', granule_tuple[1])
                        test.setAttribute('result', result)
                        collection.appendChild(test)

        duration = time.time() - start

        print(f'Total collections tested: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

        # Save the XML
        xml_str = root.toprettyxml(indent="\t")
        time.strftime("%d.%m.%Y")
        save_path_file = args.provider + time.strftime("-%m.%d.%Y-") + args.version + ".xml"
        with open(save_path_file, "w") as f:
            f.write(xml_str)

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
