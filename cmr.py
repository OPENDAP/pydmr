
"""
Access information about data in NASA's EarthData Cloud system using the
CMR Web API.
"""

import requests
import time

"""
set 'verbose'' in main(), etc., and it affects various functions
"""
global verbose
verbose = False


class CMRException(Exception):
    """When CMR returns an error"""
    def __init__(self, status):
        self.status = status
        self.message = "No error message given"

    def __init__(self, status, message):
        self.status = status
        self.message = message

    def __str__(self):
        return f'CMR Exception HTTP status: {self.status} - {self.message}'


def print_collection_granules(json_resp):
    """
    Print the granule ID, the producer id and the title for each granule
    :deprecated Not used
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["producer_granule_id"]} - {entry["title"]}')


def collection_granules_dict(json_resp):
    """
    :return A dictionary with the Granule id indexing the producer granule id and granule title
    """
    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        if "producer_granule_id" in dict_resp:  # some granule records lack "producer_granule_id". jhrg 9/4/22
            dict_resp[entry["id"]] = (entry["title"], entry["producer_granule_id"])
        else:
            dict_resp[entry["id"]] = entry["title"]
    return dict_resp


def print_provider_collections(json_resp):
    """
    Print the provider collection IDs based in the json response
    :deprecated Not used
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["title"]}')


def provider_collections_dict(json_resp):
    """
    :return The provider collection IDs and title in a dictionary
    """
    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        dict_resp[entry["id"]] = entry["title"]
    return dict_resp


def granule_ur_dict(json_resp):
    """
    :return The granule UR related URL info in a dictionary
    """
    dict_resp = {}
    i = 1
    for item in json_resp["items"]:
        for r_url in item["umm"]["RelatedUrls"]:
            if "Type" in r_url and r_url["Type"] in ('GET DATA', 'USE SERVICE API'):
                dict_resp[f'URL{i}'] = r_url["URL"]
                i += 1
    return dict_resp


def merge(dict1, dict2):
    """
    merge dictionaries, preserve key order
    :param dict1
    :param dict2
    :return The dict1, modified so the entries in dict2 have been appended
    :see https://www.geeksforgeeks.org/python-merging-two-dictionaries/
    """
    for i in dict2.keys():
        dict1[i] = dict2[i]
    return dict1


def convert(a):
    """
    Convert and array of 2N things to a dictionary of N entries
    :see https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/
    :param a The Array to convert
    :return The resulting dictionary
    """
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def process_request(cmr_query_url, response_processor, page_size=10, page_num=0):
    """
    The generic part of a CMR request. Make the request, print some stuff
    and return the number of entries. The page_size parameter is there so that paged responses
    can be handled. By default, CMR returns 10 entry items per page.
    :param cmr_query_url The whole URL, query params and all
    :param response_processor A function that will process the returned json response
    :param page_size The number of entries per page from CMR. The default is the CMR
    default value.
    :param page_num Return an explicit page of the query response. If not given, gets all
    the pages
    :return A dictionary of entries
    """
    page = 1 if page_num == 0 else page_num
    entries_dict = {}
    while True:
        # By default, requests uses cookies, supports OAuth2 and reads username and password
        # from a ~/.netrc file.
        r = requests.get(f'{cmr_query_url}&page_num={page}&page_size={page_size}')
        page += 1   # if page_num was explicitly set, this is not needed

        global verbose
        if verbose > 0:
            print(f'CMR Query URL: {cmr_query_url}')
            print(f'Status code: {r.status_code}')
            print(f'text: {r.text}')

        if r.status_code != 200:
            # JSON returned on error: {'errors': ['Collection-concept-id [ECCO Ocean ...']}
            raise CMRException(r.status_code, r.json()["errors"][0])

        json_resp = r.json()
        if "feed" in json_resp and "entry" in json_resp["feed"]:    # 'feed' is for the json response
            entries = len(json_resp["feed"]["entry"])
        elif "items" in json_resp:                                  # 'items' is for json_umm
            entries = len(json_resp["items"])
        else:
            raise CMRException(200, "cmr.process_request does not know how to decode the response")

        if entries > 0:
            entries = response_processor(json_resp)   # The response_processor() is passed in
            entries_dict = merge(entries_dict, entries)
        if page_num != 0 or len(entries) < page_size:
            break
    return entries_dict


def get_provider_collections(provider_id, opendap=False, pretty=False, service='cmr.earthdata.nasa.gov'):
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
    return process_request(cmr_query_url, provider_collections_dict, page_size=500)


def get_collection_entry(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get the collection entry given a concept id.
    :param concept_id The string Collection (Concept) Id
    :param pretty request a 'pretty' version of the response from the service. default False
    :param service The URL of the service to query (default cmr.earthdata.nasa.gov)
    :return The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/collections.json?concept_id={concept_id}{pretty}'
    return process_request(cmr_query_url, provider_collections_dict, page_num=1)
    # return cmr_process_request(cmr_query_url)


def get_related_urls(concept_id, granule_ur, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Search for a granules RelatedUrls using the collection concept id and granule ur.
    This provides a way to go from the REST form of a URL that the OPeNDAP server typically
    receives and the URLs that can be used to directly access data (and thus the DMR++
    if the data are in S3 and OPeNDAP-enabled).
    :return A dictionary that holds all the RelatedUrls that have Type 'GET DATA' or
    'USE SERVICE DATA.'
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={concept_id}&granule_ur={granule_ur}{pretty}'
    return process_request(cmr_query_url, granule_ur_dict, page_num=1)


def get_collection_granules(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get granules for a collection
    :param concept_id The string Collection (Concept) Id
    :param pretty request a 'pretty' version of the response from the service. default False
    :param service The URL of the service to query (default cmr.earthdata.nasa.gov)
    :return The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.json?concept_id={concept_id}{pretty}'
    return process_request(cmr_query_url, collection_granules_dict, page_size=500)


def decompose_resty_url(url, pretty=False):
    """
    Extract the collection concept id and granule ur. Use this information to
    get the actual URLs that lead to the data. If a 'provider - collection name'
    URL is used, this will result in an error stating that the collection
    concept id does not exist.
    :param url The URL to parse
    :pretty Ask CMR to return a JSON UMM document for humans
    """
    url_pieces = url.split('/')[3:]
    url_dict = convert(url_pieces)          # convert the array to a dictionary
    print(f'URL parts: {url_dict}') if verbose else ''

    items = get_related_urls(url_dict['collections'], url_dict['granules'], pretty=pretty)
    print(f'Data URLs: {items}') if verbose else ''
    return items
