#!/usr/bin/env python3

"""
Get the URL to a granule from an OPeNDAP 'resty' URL

An example:
https://opendap.earthdata.nasa.gov/providers/POCLOUD/collections/ECCO%20Ocean%20Temperature%20and%20Salinity%20-%20Daily%20Mean%200.5%20Degree%20(Version%204%20Release%204)/granules/OCEAN_TEMPERATURE_SALINITY_day_mean_2017-12-31_ECCO_V4r4_latlon_0p50deg.dap.nc4
"""

import requests

global verbose


class CMRException(Exception):
    """When CMR returns an error"""
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f'CMR Exception HTTP status: {self.status}'


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    decompose_resty_url(args.url)


def convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def decompose_resty_url(url):
    # Remove the first 3 parts, the result is a dictionary
    url_pieces = url.split('/')[3:]
    print(f'URL parts: {convert(url_pieces)}')


if __name__ == "__main__":
    main()
