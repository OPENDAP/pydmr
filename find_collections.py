#!/usr/bin/env python3

"""
Command line tool for finding all the collections for a provider, or a set
group of providers, that have OPeNDAP URLs, either in the cloud or under
on-premises systems.

This looks for the first granule in the collection and evaluates it for
'OPeNDAP-ishness.' It does not look at any other granules.
"""

import time
import cmr
import errLog


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find all the collections for a given provider that have OPeNDAP"
                                                 "URLs. Use a brute for query (look at the first granule of each"
                                                 "collection). Return information about both Cloud and on-premises"
                                                 "URLs and optionally, print all of each kind.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true")
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    parser.add_argument("-B", "--opendap-brutishly", help="for a provider, show only collections with OPeNDAP URLS, "
                        "Uses a brute-force search of the first URL for all collection.", action="store_true")
    parser.add_argument("-c", "--cloud", help="Print the CCID and first URL for all the collections that have an"
                        "OPeNDP in-the-cloud URL. This will return both the old and current (6/24) REST URLs",
                        action="store_true")
    parser.add_argument("-s", "--site", help="Print the CCID and first URL for all the collections that have an OPeNDAP URL"
                        "that points to an on-premises (on-site) server.", action="store_true")

    parser.add_argument("providers", nargs="*")

    args = parser.parse_args()

    # cmr.verbose = True if args.verbose else False
    pretty = True if args.pretty else False

    try:
        for provider in args.providers:
            start = time.time()

            if args.opendap_brutishly:
                entries = cmr.get_provider_opendap_collections_brutishly(provider)
            else:
                entries = cmr.get_provider_collections(provider, True, pretty=pretty)

            duration = time.time() - start

            if args.verbose:
                for key, value in entries.items():
                    print(f'{key}: {value}')

            print(f'Total entries: {len(entries)}') if len(entries) > 1 else ""
            print(f'Request time: {duration:.1f}s') if args.time else ""

            # count all the True responses - collections with OPeNDAP cloud URLs. The value is a tuple (True, URL)
            true_values = [value[1] for value in entries.values() if value[0] is True]
            print(f"Number of {provider} OPeNDAP-enabled cloud collections found: {len(true_values)}, out of {len(entries.keys())}")

            # count all collections that don't have a cloud URL, but do claim to have OPeNDAP URLs. These
            # are the on-premises servers. The value is the tuple (False, URL)
            false_with_url_values = [value[1] for value in entries.values() if
                                     value[0] is False and len(value[1]) != 0]
            print(f"Number of {provider} OPeNDAP-enabled non-cloud collections found: {len(false_with_url_values)}")

            if args.cloud:
                with open(f"{provider}-cloud.txt", "w") as cloud:
                    cloud.write(f"OPeNDAP Cloud URLs\n")
                    for key, value in entries.items():
                        if value[0]:
                            cloud.write(f"{key}: {value[1]}\n")

            if args.site:
                with open(f"{provider}-site.txt", "w") as site:
                    site.write(f"OPeNDAP on-premises URLs\n")
                    for key, value in entries.items():
                        if value[0] is False and len(value[1]) != 0:
                            site.write(f"{key}: {value[1]}\n")

    except cmr.CMRException as e:
        errLog.output_errlog("/////////////////////////////////////////////////////\n")
        errLog.output_errlog(f"CMRException: find_collections.py::main() - {e.message}\n")
        print(e)


if __name__ == "__main__":
    main()
