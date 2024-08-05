#!/usr/bin/env python3

"""
Command line tool for sending simple requests to CMR and printing the
results to stdout. This command knows how to find all the collections
for a given provider (and it will optionally limit them to only those with
OPeNDAP URLs).

TODO: This needs a way to work with CMR in UAT. Currently requests for
 collections/granules in UAT do not work even though the internal logic
 exists in the cmr.py package.
"""

import time
import cmr
import errLog


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    parser.add_argument("-P", "--pretty", help="Request pretty responses from CMR.", action="store_true")
    parser.add_argument("-t", "--time", help="Time responses from CMR.", action="store_true")

    group = parser.add_mutually_exclusive_group() # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="Given a provider id, by itself, print all the providers collections.")
    group.add_argument("-c", "--collection", help="Given a collection id, by itself, print some info.")
    group.add_argument("-r", "--resty-path", help="Get the data URL for an OPeNDAP EDC REST URL")
    group.add_argument("-R", "--collection-and-title",
                       help="Get the data URL for a CMR collection concept id and granule title."
                       " The format for this is 'CCID:title,' for example:"
                       " C2205105895-POCLOUD:20220902120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1")

    parser.add_argument("-o", "--opendap", help="For a provider, show only collections with OPeNDAP URLS.",
                        action="store_true")
    parser.add_argument("-B", "--opendap-brutishly", help="For a provider, show only collections with OPeNDAP URLS."
                        " Uses a brute-force search of the first URL for all collection.", action="store_true")
    parser.add_argument("-g", "--granules", help="for a collection, get info about all the granules",
                        action="store_true")
    parser.add_argument("-C", "--count", help="For a collection, get the granule count.", action="store_true")
    parser.add_argument("-d", "--descending", help="For a list of granules, get the newest first (the 'last' granule)."
                        " By default, the granules are listed in ascending order (oldest first)", action="store_true")
    parser.add_argument("-D", "--date-range",
                        help="For a granule request, limit the responses to a range of date/times."
                        " The format is ISO-8601,ISO-8601 (e.g., 2000-01-01T10:00:00Z,2010-03-10T12:00:00Z)")

    parser.add_argument("-j", "--umm-g-json", help="Get the UMM-G JSON info for a collection:granule",
                        action="store_true")
    parser.add_argument("-f", "--first-last", help="Get the first and last granule of a collection.",
                        action="store_true")

    args = parser.parse_args()

    cmr.verbose = True if args.verbose else False
    pretty = True if args.pretty else False
    opendap = True if args.opendap else False
    granules = True if args.granules else False
    first_last = True if args.first_last else False

    try:
        start = time.time()
        if args.collection and granules:
            if args.date_range:
                entries = cmr.get_collection_granules_temporal(args.collection, args.date_range, pretty=pretty,
                                                               descending=args.descending)
            else:
                entries = cmr.get_collection_granules(args.collection, pretty=pretty, descending=args.descending)
        elif args.collection and first_last:
            entries = cmr.get_collection_granules_umm_first_last(args.collection, pretty=pretty)
        elif args.collection:
            entries = cmr.get_collection_entry(args.collection, pretty=pretty, count=args.count)
        elif args.resty_path:
            entries = cmr.decompose_resty_url(args.resty_path, pretty=pretty)
        elif args.collection_and_title:
            collection, title = args.collection_and_title.split(':')
            entries = cmr.get_related_urls(collection, title, pretty=pretty)
        elif args.provider and args.opendap_brutishly:
            entries = cmr.get_provider_opendap_collections_brutishly(args.provider)
        else:
            entries = cmr.get_provider_collections(args.provider, opendap, pretty=pretty)
        duration = time.time() - start

        for key, value in entries.items():
            print(f'{key}: {value}')

        print(f'Total entries: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

    except cmr.CMRException as e:
        err = "/////////////////////////////////////////////////////\n"
        err += "CMRException : ask_cmr.py::main() - " + e.message + "\n"
        errLog.output_errlog(err)
        print(e)


if __name__ == "__main__":
    main()
