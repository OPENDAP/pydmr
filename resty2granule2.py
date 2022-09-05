#!/usr/bin/env python3

"""
Get the URL to a granule from an OPeNDAP 'resty' URL

An example:
https://opendap.earthdata.nasa.gov/collections/C2205105895-POCLOUD/granules/19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1

That url will result in a dictionary that has the s3 and https cloud URLs for the
real granule from which we can find the URL to the DMR++. That URL is:
https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MW_OI-REMSS-L4-GLOB-v5.1/19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc.dmrpp

The resulting URL can be downloaded using burl or with the requests package
"""

import cmr


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true")
    args = parser.parse_args()

    cmr.verbose = args.verbose

    try:
        items = cmr.decompose_resty_url(args.url, pretty=args.pretty)
        for key, value in items.items():
            print(f'{key}: {value}')
    except cmr.CMRException as e:
        print(f'Error: {e}')


if __name__ == "__main__":
    main()
