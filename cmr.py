"""
Access information about data in NASA's EarthData Cloud system using the
CMR Web API.
"""

import requests
import json

"""
set 'verbose'' in main(), etc., and it affects various functions
"""
verbose: bool = False


class CMRException(Exception):
    """When CMR returns an error"""

    def __init__(self, status, message="No error message given"):
        self.status = status
        self.message = message

    def __str__(self):
        return f'CMR Exception HTTP status: {self.status} - {self.message}'


def print_collection_granules(json_resp):
    """
    Print the granule ID, the producer id and the title for each granule
    Deprecated; Not used
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["producer_granule_id"]} - {entry["title"]}')


def print_provider_collections(json_resp):
    """
    Print the provider collection IDs based in the json response
    Deprecated
    """
    for entry in json_resp["feed"]["entry"]:
        print(f'ID: {entry["id"]} - {entry["title"]}')


def collection_granules_dict(json_resp):
    """
    :param json_resp: CMR JSON response
    :return: A dictionary with the Granule id indexing the producer granule id and granule title
    :rtype: dict
    """
    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        if "producer_granule_id" in dict_resp:  # some granule records lack "producer_granule_id". jhrg 9/4/22
            dict_resp[entry["id"]] = (entry["title"], entry["producer_granule_id"])
        else:
            dict_resp[entry["id"]] = entry["title"]
    return dict_resp


def collection_granules_first_last(json_resp):
    dict_resp = {}

    if "producer_granule_id" in dict_resp:  # some granule records lack "producer_granule_id". jhrg 9/4/22
        dict_resp[json_resp["id"]] = (json_resp["title"], json_resp["producer_granule_id"])
    else:
        dict_resp[json_resp["id"]] = json_resp["title"]

    with open(json_resp) as f:
        j = json.loads(f.readlines()[-1])

    if "producer_granule_id" in dict_resp:  # some granule records lack "producer_granule_id". jhrg 9/4/22
        dict_resp[j["id"]] = (j["title"], j["producer_granule_id"])
    else:
        dict_resp[j["id"]] = j["title"]
    return dict_resp


def provider_collections_dict(json_resp):
    """
    Extract collection IDs and Titles from CMR JSON

    :param json_resp: CMR JSON response
    :return: The provider collection IDs and title in a dictionary
    :rtype: dict
    """
    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        dict_resp[entry["id"]] = entry["title"]
    return dict_resp


def granule_ur_dict(json_resp):
    """
    Extract Related URLs from CMR JSON UMM

    :param json_resp: CMR JSON UMM response
    :return: The granule UR related URL info in a dictionary. Only 'GET DATA' and 'USE SERVICE API'
        type URLs are included. Each is indexed using 'URL1', ..., 'URLn.'
    :rtype: dict
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
    Merge dictionaries, preserve key order
    See https://www.geeksforgeeks.org/python-merging-two-dictionaries/

    :param dict1:
    :param dict2:
    :returns: The dict1, modified so the entries in dict2 have been appended
    :rtype: dict
    """
    for i in dict2.keys():
        dict1[i] = dict2[i]
    return dict1


def convert(a):
    """
    Convert and array of 2N things to a dictionary of N entries
    See https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/

    :param: a: The Array to convert
    :return: The resulting dictionary
    :rtype: dict
    """
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def process_request(cmr_query_url, response_processor, page_size=10, page_num=0):
    """
    The generic part of a CMR request. Make the request, print some stuff
    and return the number of entries. The page_size parameter is there so that paged responses
    can be handled. By default, CMR returns 10 entry items per page.

    :param cmr_query_url: The whole URL, query params and all
    :param response_processor: A function that will process the returned json response
    :param page_size: The number of entries per page from CMR. The default is the CMR
        default value.
    :param page_num: Return an explicit page of the query response. If not given, gets all
        the pages
    :returns: A dictionary of entries
    """
    page = 1 if page_num == 0 else page_num
    entries_dict = {}
    while True:
        # By default, requests uses cookies, supports OAuth2 and reads username and password
        # from a ~/.netrc file.
        r = requests.get(f'{cmr_query_url}&page_num={page}&page_size={page_size}')
        page += 1  # if page_num was explicitly set, this is not needed

        if verbose > 0:
            print(f'CMR Query URL: {cmr_query_url}')
            print(f'Status code: {r.status_code}')
            print(f'text: {r.text}')

        if r.status_code != 200:
            # JSON returned on error: {'errors': ['Collection-concept-id [ECCO Ocean ...']}
            raise CMRException(r.status_code, r.json()["errors"][0])

        json_resp = r.json()
        if "feed" in json_resp and "entry" in json_resp["feed"]:  # 'feed' is for the json response
            entries = len(json_resp["feed"]["entry"])
        elif "items" in json_resp:  # 'items' is for json_umm
            entries = len(json_resp["items"])
        else:
            raise CMRException(200, "cmr.process_request does not know how to decode the response")

        if entries > 0:
            entries = response_processor(json_resp)  # The response_processor() is passed in
            entries_dict = merge(entries_dict, entries)
        if page_num != 0 or len(entries) < page_size:
            break
    return entries_dict


def process_request_first_last(cmr_query_url, response_processor, page_size=10, page_num=0):
    """
    Only return the first and last granule of a collection

    :param cmr_query_url: The whole URL, query params and all
    :param response_processor: A function that will process the returned json response
    :param page_size: The number of entries per page from CMR. The default is the CMR
        default value.
    :param page_num: Return an explicit page of the query response. If not given, gets all
        the pages
    :returns: A dictionary of entries
    """
    page = 1 if page_num == 0 else page_num
    entries_dict = {}
    granule_dict = {}

    # By default, requests uses cookies, supports OAuth2 and reads username and password
    # from a ~/.netrc file.
    r = requests.get(f'{cmr_query_url}&page_num={page}&page_size={page_size}')
    page += 1  # if page_num was explicitly set, this is not needed

    if verbose > 0:
        print(f'CMR Query URL: {cmr_query_url}')
        print(f'Status code: {r.status_code}')
        print(f'text: {r.text}')

    if r.status_code != 200:
        # JSON returned on error: {'errors': ['Collection-concept-id [ECCO Ocean ...']}
        raise CMRException(r.status_code, r.json()["errors"][0])

    json_resp = r.json()

    entries = response_processor(json_resp)  # The response_processor() is passed in
    entries_dict = merge(entries_dict, entries)

    granule_dict[0] = list(entries_dict.items())[0]
    granule_dict[1] = list(entries_dict.items())[-1]
    return granule_dict


def get_provider_collections(provider_id, opendap=False, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get all the collections for a given provider.

    :param provider_id: The string ID for a given EDC provider (e.g., ORNL_CLOUD)
    :param opendap: If true, return only the collections with OPeNDAP URLS
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns: The total number of entries
    """

    pretty = '&pretty=true' if pretty else ''
    opendap = '&has_opendap_url=true' if opendap else ''
    cmr_query_url = f'https://{service}/search/collections.json?provider={provider_id}{opendap}{pretty}'
    return process_request(cmr_query_url, provider_collections_dict, page_size=500)


def get_collection_entry(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get the collection entry given a concept id.

    :param concept_id: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns:The collection JSON object
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

    :returns: A dictionary that holds all the RelatedUrls that have Type 'GET DATA' or
        'USE SERVICE DATA.'
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={concept_id}&granule_ur={granule_ur}{pretty}'
    return process_request(cmr_query_url, granule_ur_dict, page_num=1)


def get_collection_granules(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get granules for a collection

    :param concept_id: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns: The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.json?concept_id={concept_id}{pretty}'
    return process_request(cmr_query_url, collection_granules_dict, page_size=500)


def get_collection_granules_first_last(concept_id, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Get granules for a collection

    :param concept_id: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns: The collection JSON object
    """
    pretty = '&pretty=true' if pretty > 0 else ''
    cmr_query_url = f'https://{service}/search/granules.json?concept_id={concept_id}{pretty}'
    return process_request_first_last(cmr_query_url, collection_granules_dict, page_size=500)


def decompose_resty_url(url, pretty=False):
    """
    Extract the collection concept id and granule ur. Use this information to
    get the actual URLs that lead to the data. If a 'provider - collection name'
    URL is used, this will result in an error stating that the collection
    concept id does not exist.

    :param url: The URL to parse
    :param pretty: Ask CMR to return a JSON UMM document for humans
    :returns: A dictionary of the URLs, indexed as 'URL1', ..., 'URLn.'
    """
    url_pieces = url.split('/')[3:]
    url_dict = convert(url_pieces)  # convert the array to a dictionary
    print(f'URL parts: {url_dict}') if verbose else ''

    items = get_related_urls(url_dict['collections'], url_dict['granules'], pretty=pretty)
    print(f'Data URLs: {items}') if verbose else ''
    return items
