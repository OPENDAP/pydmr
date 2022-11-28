#!/usr/bin/env python3

"""
Find all the NASA ESDIS Providers in the CMR catalog that have collections
accessible using OPeNDAP.
"""

import xml.dom.minidom as minidom
import time

import requests

import cmr


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Providers with Collections "
                                                 "accessible using OPeNDAP.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")
    # argparse.BooleanOptionalAction makes --xml/--no-xml work. The default is to make xml.
    parser.add_argument("-x", "--xml", help="time responses from CMR", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-V", "--version", help="version number for test results XML file", action="store_true", default="1")

    group = parser.add_mutually_exclusive_group(required=True)  # only one option in 'group' is allowed at a time
    group.add_argument("-e", "--environment", help="an environment, a placeholder for now. This only works for PROD.")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False

    try:
        start = time.time()

        # make the response document
        if args.xml:
            root = minidom.Document()
            environment = root.createElement('Environment')
            environment.setAttribute('name', args.environment)
            environment.setAttribute('date', time.asctime())
            root.appendChild(environment)

        pretty = '&pretty=true' if args.pretty else ''
        opendap = '&has_opendap_url=true'
        service = 'cmr.earthdata.nasa.gov'
        cmr_query_url = f'https://{service}/search/collections.umm_json?{opendap}{pretty}'

        # this uses the new return value as a set feature of process_request
        entries = cmr.process_request(cmr_query_url, cmr.provider_id, requests.Session(), page_size=2000)

        duration = time.time() - start

        print(f'Total providers found: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

        for provider in entries:
            print(provider)
            if args.xml:
                # XML element for the collection
                prov = root.createElement('Provider')
                prov.setAttribute('name', provider)
                environment.appendChild(prov)

        if args.xml:
            # Save the XML
            xml_str = root.toprettyxml(indent="\t")
            time.strftime("%d.%m.%Y")
            save_path_file = args.environment + time.strftime("-%m.%d.%Y-") + args.version + ".xml"
            with open(save_path_file, "w") as f:
                f.write(xml_str)

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()