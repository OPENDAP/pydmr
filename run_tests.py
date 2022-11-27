#!/usr/bin/env python3

"""
Run a series of tests on a group of providers.
"""

import subprocess
import time

import cmr


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run a series of tests on a group of providers.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")
    # argparse.BooleanOptionalAction makes --xml/--no-xml work. The default is to make xml.
    parser.add_argument("-x", "--xml", help="time responses from CMR", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("-V", "--version", help="version number for test results XML file", action="store_true", default="1")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False

        start = time.time()

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



if __name__ == "__main__":
    main()
