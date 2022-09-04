
"""
Get all the collections for a given provider (e.g., ORNL_CLOUD).
"""

import requests
import json
import argparse
import getopt
import sys
from datetime import datetime

global verbose


def usage(argv0):
    print(f'{argv0}: [hv c <collection> | p <provider>]')


class CMRException(Exception):
    """When CMR returns an error"""
    def __init__(self, status):
        self.status


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvPgoc:p:",
                                   ["help", "verbose", "Pretty", "granules", "opendap", "collection=", "provider="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage(sys.argv[0])
        sys.exit(2)
    collection = None
    provider = None
    global verbose
    verbose = False
    pretty = False
    granules = False
    opendap = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--collection"):
            collection = a
        elif o in ("-p", "--provider"):
            provider = a
        elif o in ("-g", "--granules"):
            granules = True
        elif o in ("-P", "--Pretty"):
            pretty = True
        elif o in ("-o", "--opendap"):
            opendap = True
        else:
            assert False, "unhandled option"

    if granules:
        json_resp = cmr_get_collection_granules_json(collection, pretty)
        print_collection_granules(json_resp)
    elif collection:
        json_resp = cmr_get_collection_entry_json(collection, pretty)
    else:
        # Providers: ORNL_CLOUD, LPDAAC_ECS, PODAAC, GES_DISC
        entries = cmr_get_provider_collections_json(provider, opendap, pretty)
        print(f'Total entries: {entries}')


def print_collection_granules(json_resp):
    """
    Print the granule ID, the producer id and the title for each granule
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["producer_granule_id"]} - {entry["title"]}')


def print_provider_collections(json_resp):
    """
    Print the provider collection IDs based in the json response
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["title"]}')


def cmr_process_request(cmr_query_url, response_processor, page_size=10):
    """
    The generic part of a CMR request. Make the request, optionally print some stuff
    and return the resulting JSON. The page parameter is there so that paged responses
    can be handled. By default, CMR returns 10 entry items per page.
    :param cmr_query_url The whole URL, query params and all
    :param response_processor A function that will process the returned json response
    :param page_size The number of entries per page from CMR. The default is the CMR
    default value.
    :return The number of entries and the JSON response
    """
    page = 1
    total_entries = 0
    while True:
        # By default, requests uses cookies, supports OAuth2 and reads username and password
        # from a ~/.netrc file.
        r = requests.get(f'{cmr_query_url}&page_num={page}&page_size={page_size}')
        page += 1

        if verbose > 0:
            print(f'CMR Query URL: {cmr_query_url}')
            print(f'Status code: {r.status_code}')
            print(f'text: {r.text}')

        if r.status_code != 200:
            raise CMRException(r.status_code)

        json_resp = r.json()
        entries = len(json_resp["feed"]["entry"])
        if entries > 0:
            response_processor(json_resp)   # The response_processor is passed in
            total_entries += entries
        if entries < page_size:
            break
    return total_entries


def cmr_get_provider_collections_json(provider_id, opendap=False, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get all the collections for a given provider.
    :param provider_id The string ID for a given EDC provider (e.g., ORNL_CLOUD)
    :param opendap If true, return only the collections with OPeNDAP URLS
    :param pretty request a 'pretty' version of the response from the service. default False
    :param service The URL of the service to query (default cmr.earthdata.nasa.gov)
    :return The total number of entries
    """

    pretty = '&pretty=true' if pretty else ''
    opendap = '&has_opendap_url=true' if opendap else ''
    cmr_query_url = f'https://{service}/search/collections.json?provider={provider_id}{opendap}{pretty}'
    return cmr_process_request(cmr_query_url, print_provider_collections, page_size=50)


def cmr_get_collection_entry_json(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get the collection entry given a concept id.
    :param concept_id The string Collection (Concept) Id
    :param pretty request a 'pretty' version of the response from the service. default False
    :param service The URL of the service to query (default cmr.earthdata.nasa.gov)
    :return The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/collections.json?concept_id={concept_id}{pretty}'
    return cmr_process_request(cmr_query_url)


def cmr_get_collection_granules_json(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get granules for a collection
    :param concept_id The string Collection (Concept) Id
    :param pretty request a 'pretty' version of the response from the service. default False
    :param service The URL of the service to query (default cmr.earthdata.nasa.gov)
    :return The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.json?concept_id={concept_id}{pretty}'
    return cmr_process_request(cmr_query_url)


if __name__ == "__main__":
    main()
