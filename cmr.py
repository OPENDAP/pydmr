"""
Access information about data in NASA's EarthData Cloud system using the
CMR Web API.
"""

# from typing import Dict, Any, Set

import typing
import requests
import threading

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


"""
These are the response processors used by 'process_response()'. They extract
various things from the JSON and return a dictionary.
"""


def is_entry_feed(json_resp: dict) -> bool:
    """
    Does this JSON object have the 'entry' key within a 'feed' key?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.
    """
    return len(json_resp) > 0 and "feed" in json_resp.keys() and "entry" in json_resp["feed"].keys()


def is_item_feed(json_resp: dict) -> bool:
    """
    Does this JSON object have the 'meta' key within a 'items' key/array?
    This function is used to protect various response processors
    from responses that contain no items or are malformed.
    """
    return len(json_resp) > 0 and "items" in json_resp.keys() and "meta" in json_resp["items"][0]


def is_meta_item(json_resp: dict) -> bool:
    """
    Does this JSON object have the 'meta' key that contains concept-id and native-id keys?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.

    This function processes the return information from a granules.umm_json request.
    """
    return len(json_resp) > 0 and "meta" in json_resp.keys() \
           and "concept-id" in json_resp["meta"].keys() \
           and "native-id" in json_resp["meta"].keys()


def is_granule_item(json_resp: dict) -> bool:
    """
    Does this JSON object have the 'RelatedUrls' key within a 'umm' key?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.

    This function processes the return information from a granules.umm_json request.
    """
    return len(json_resp) > 0 and "umm" in json_resp.keys() and "RelatedUrls" in json_resp["umm"].keys()


def collection_granules_dict(json_resp: dict) -> dict:
    """
    This function processes the return information from a granules.json request.
    Do not use it for a granules.umm_json request.

    :param json_resp: CMR JSON response
    :return: A dictionary with the Granule id indexing the producer granule id and granule title
    :rtype: dict
    """
    if not is_entry_feed(json_resp):
        return {}

    dict_resp = {}
    # Look for the entry id, title, producer_granule_id and OPeNDAP link. Build a
    for entry in json_resp["feed"]["entry"]:
        if "producer_granule_id" in entry:  # some granule records lack "producer_granule_id". jhrg 9/4/22
            dict_resp[entry["id"]] = (entry["title"], entry["producer_granule_id"])
        else:
            dict_resp[entry["id"]] = (entry["title"])

    return dict_resp


def collection_granule_and_url_dict(json_resp: dict) -> dict:
    """
    This function processes the return information from a granules.json request.
    Do not use it for a granules.umm_json request.

    :param json_resp: CMR JSON response
    :return: A dictionary with the Granule id indexing the granule title and OPeNDAP URL
    :rtype: dict
    :deprecated: jhrg 1/23/23
    """
    if not is_entry_feed(json_resp):
        return {}

    dict_resp = {}
    # Look for the entry id, title, and OPeNDAP link.
    for entry in json_resp["feed"]["entry"]:
        if len(entry.keys() & ("id", "title", "links")) == 3:
            # check for the OPeNDAP URL in the 'links' array
            for link in entry["links"]:
                if "title" in link and link["title"].find("OPeNDAP") == 0:
                    dict_resp[entry["id"]] = (entry["title"], link["href"])
                    break

    return dict_resp


def provider_collections_dict(json_resp):
    """
    Extract collection IDs and Titles from CMR JSON. Optionally get the granule count.

    :param json_resp: CMR JSON response
    :return: The provider collection IDs and title in a dictionary
    :rtype: dict
    """
    if not is_entry_feed(json_resp):
        return {}

    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        if "granule_count" in entry:
            dict_resp[entry["id"]] = (entry["granule_count"], entry["title"])
        else:
            dict_resp[entry["id"]] = (entry["title"])

    return dict_resp


def provider_id(json_resp: dict) -> set:
    """
    Extract Provider IDs from CMR JSON.

    The JSON passed to this function is an Array of 'items' each of which holds
    a dictionary with a single key 'meta'. The value of the 'meta' key is itself
    a dictionary that holds lots of info, including the provider-id key-value pair.
    :param json_resp: CMR JSON response
    :returns: The provider ids in a set
    :rtype: set
    """
    if not is_item_feed(json_resp):
        return set()

    resp = set()
    for item in json_resp["items"]:
        if "provider-id" in item["meta"]:
            resp.add(item["meta"]["provider-id"])

    return resp


def granule_ur_dict(json_resp: dict) -> dict:
    """
    Extract Related URLs from CMR JSON UMM.

    This function processes the return information from a granules.umm_json request.
    Do not use it for a granules.json request.

    Modified so that only URLs with the 'Subtype' 'OPENDAP DATA' are returned.
    jhrg 1/23/23

    :param json_resp: CMR JSON UMM response
    :returns: The granule UR related URL info in a dictionary. Only Type 'GET DATA'
        or 'USE SERVICE API' with Subtype 'OPENDAP DATA' type URLs are included.
        Each is indexed using 'URL1', ..., 'URLn.' The dictionaries look like:
        {'URL1': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
         'URL2': 'https://archive/250_2101_ovw.l2.nc'}
    :rtype: dict
    """
    # Check json_resp as above but for items, etc. jhrg 10/11/22
    if "items" not in json_resp.keys():
        return {}

    dict_resp = {}
    i = 1
    for item in json_resp["items"]:
        if not is_granule_item(item):
            continue
        for r_url in item["umm"]["RelatedUrls"]:
            if "Type" not in r_url or "URL" not in r_url:
                continue
            if "Type" in r_url and r_url["Type"] in ('GET DATA'):
                dict_resp[f'URL{i}'] = (r_url["URL"])
                i += 1

    return dict_resp


def granule_ur_dict_2(json_resp: dict) -> dict:
    """
    Extract Related URLs from CMR JSON UMM. This version returns a dictionary with
    an ID, Title and URL like {ID : (Title, URL)}.

    This function processes the return information from a granules.umm_json request.
    Do not use it for a granules.json request.

    Modified so that only URLs with the 'Subtype' 'OPENDAP DATA' are returned.
    The response should use the 'concept-id' for ID, native-id for the Title
    and 'URL' for the URL.
    jhrg 1/23/23

    :param json_resp: CMR JSON UMM response
    :returns: The granule UR related URL info in a dictionary. Only Type 'GET DATA'
        or 'USE SERVICE API' with Subtype 'OPENDAP DATA' type URLs are included.
        Each is indexed using the granule concept ID and looks like:
        {'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                 'https://opendap.../podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc')}
    :rtype: dict
    """
    # Check json_resp as above but for items, etc. jhrg 10/11/22
    if "items" not in json_resp.keys():
        return {}

    dict_resp = {}
    for item in json_resp["items"]:
        if not (is_meta_item(item) and is_granule_item(item)):
            continue
        if "concept-id" not in item["meta"].keys() or "native-id" not in item["meta"].keys():
            continue
        concept_id = item["meta"]["concept-id"]
        native_id = item["meta"]["native-id"]
        for r_url in item["umm"]["RelatedUrls"]:
            if "Type" not in r_url or "URL" not in r_url:
                continue
            if "Type" in r_url and r_url["Type"] in ('GET DATA', 'USE SERVICE API') \
                    and "Subtype" in r_url and r_url["Subtype"] == 'OPENDAP DATA':
                dict_resp[concept_id] = (native_id, r_url["URL"])

    return dict_resp


def merge_dict(dict1: dict, dict2: dict) -> dict:
    """
    Merge dictionaries, preserve key order
    See https://www.geeksforgeeks.org/python-merging-two-dictionaries/

    :param dict1:
    :param dict2:
    :returns: The dict1, modified so the entries in dict2 have been appended
    :rtype: dict
    """
    # silently bail
    if not (type(dict1) is dict and type(dict2) is dict):
        raise TypeError("Both arguments to cmr.merge() must be dictionaries.")

    # If there is nothing in dict1, return dict2.
    if len(dict1) == 0:
        return dict2

    for i in dict2.keys():
        dict1[i] = dict2[i]

    return dict1


def convert(a: list) -> dict:
    """
    Convert and array of 2N things to a dictionary of N entries
    See https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/

    :param a: The List/Array to convert
    :return: The resulting dictionary
    :rtype: dict
    """
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


def build_bescmd(collection_and_title: str) -> dict:
    """
        Given a string containing a CMR Collection_Concept_ID:Granule_Concept_ID
        build a BESCMD XML document for use by besstandalone to generate a DMRPP.

        :param collection_and_title: A string containing the Collection Concept_ID : Granule UR
        :rtype: dict
        """

    query_elements = collection_and_title.split(':')

    if len(query_elements) != 2:
        raise IndexError(f"Expected string Collection:Granule got {collection_and_title}")

    filename = query_elements[1] + '.bescmd'

    with open(filename, mode='w') as bescmd:
        bescmd.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        bescmd.write('<request xmlns:bes="http://xml.opendap.org/ns/bes/1.0#" reqID="[thread:http-nio-8080-exec-4-42][bes_client:/-2]">\n')
        bescmd.write('\t<setContext name="dap_format">dap4</setContext>\n')
        bescmd.write('\t<setContainer name="c" space="builddmrpp">/collections/{}/granules/{}</setContainer>\n'.format(query_elements[0], query_elements[1]))
        bescmd.write('\t<define name="d">\n')
        bescmd.write('\t\t<container name="c" />\n')
        bescmd.write('\t</define>\n')
        bescmd.write('\t<get type="dap" definition="d" returnAs="dmrpp"/>\n')
        bescmd.write('</request>\n')

    if verbose > 0:
        print(f'BESCMD File: {filename}')

    return {}

def process_request(cmr_query_url: str, response_processor: callable(dict), session: object, page_size=10,
                    page_num=0) -> dict:
    """
    The generic part of a CMR request. Make the request, print some stuff
    and return the number of entries. The page_size parameter is there so that paged responses
    can be handled. By default, CMR returns 10 entry items per page.

    :param cmr_query_url: The whole URL, query params and all
    :param response_processor: A function that will process the returned json response
    :param session: A requests package session object
    :param page_size: The number of entries per page from CMR. The default is the CMR default value.
    :param page_num: Return an explicit page of the query response. If not given, gets all the pages
    :returns: A dictionary of entries
    :rtype: dict or set
    """

    page = 1 if page_num == 0 else page_num
    entries_dict = {}
    entries_set = set()
    while True:
        # By default, requests uses cookies, supports OAuth2 and reads username and password
        # from a ~/.netrc file.
        r = session.get(f'{cmr_query_url}&page_num={page}&page_size={page_size}')
        page += 1  # if page_num was explicitly set, this is not needed

        if verbose > 0:
            print(f'CMR Query URL: {cmr_query_url}')
            print(f'Status code: {r.status_code}')
            # print(f'text: {r.text}')

        if r.status_code != 200:
            # JSON returned on error: {'errors': ['Collection-concept-id [ECCO Ocean ...']}
            raise CMRException(r.status_code, r.json()["errors"][0])

        json_resp = r.json()
        #print(json_resp)
        if "feed" in json_resp and "entry" in json_resp["feed"]:  # 'feed' is for the json response
            entries_num = len(json_resp["feed"]["entry"])
        elif "items" in json_resp:  # 'items' is for json_umm
            entries_num = len(json_resp["items"])
        else:
            raise CMRException(200, "cmr.process_request does not know how to decode the response")

        if entries_num > 0:
            entries_page = response_processor(json_resp)  # The response_processor() is passed in
            if type(entries_page) is dict:
                entries_dict = merge_dict(entries_dict, entries_page)  # merge is smart if entries is empty



            elif type(entries_page) is set:
                entries_set.update(entries_page)

        if page_num != 0 or entries_num < page_size:
            break

    if len(entries_dict) > 0:
        return entries_dict
    elif len(entries_set) > 0:
        return entries_set
    else:
        return {}


""" Used to ensure that each thread has its own session for the HTTP Requests package """
thread_local = threading.local()


def get_session() -> object:
    """
    With 'thread_local' above, get a new session object for each thread. Reuse session
    for existing threads. The Requests Session object is not multi-thread safe.
    """
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def get_collection_granules_umm_first_last(ccid: str, json_processor=granule_ur_dict_2, pretty=False,
                                           service='cmr.earthdata.nasa.gov') -> dict:
    """
    This method uses the granules.umm_json_v1_4 response and finds the first and
    last granules for a collection using the 'items' response from CMR.

    :param ccid The Collection Concept ID
    :param json_processor A function to parse the JSON from CMR
    :param pretty Ask CMR to return a 'pretty' JSON response
    :param service Which instance of CMR to query
    :return: Return a dictionary that is the result of merging two dicts structured
    like {ID1 : (Title1, URL1), ID2 : (Title2, URL2)} where ID is the granule ID.
    """
    pretty = '&pretty=true' if pretty else ''

    # by default, CMR returns results with "sort_key = +start_date" returning the oldest granule
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={ccid}{pretty}'
    oldest_dict = process_request(cmr_query_url, json_processor, get_session(), page_size=1, page_num=1)

    # Use "-start-date" to get the newest granule
    sort_key = '&sort_key=-start_date'
    cmr_query_url = f'{cmr_query_url}{sort_key}'
    newest_dict = process_request(cmr_query_url, json_processor, get_session(), page_size=1, page_num=1)

    if len(newest_dict) != 1 and len(oldest_dict) != 1:
        raise CMRException(500, f"Expected at least one response item from CMR, got {len(newest_dict)+len(oldest_dict)}"
                                f" while asking about {ccid}, even though has_opendap_url was true for the collection.")

    # Use host_patterns to see if the URL(s) is/are in the dictionaries. Maybe. jhrg 1/25/23
    return merge_dict(oldest_dict, newest_dict)


def get_provider_collections(provider_id: str, opendap=False, pretty=False, service='cmr.earthdata.nasa.gov') -> dict:
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
    return process_request(cmr_query_url, provider_collections_dict, get_session(), page_size=500)


def get_collection_entry(ccid: str, pretty=False, count=False, service='cmr.earthdata.nasa.gov') -> dict:
    """
    Get the collection entry given a concept id.

    :param ccid: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param count: request the granule count for the collection
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns:The collection JSON object
    """
    pretty = '&pretty=true' if pretty else ''
    collection_count = '&include_granule_counts=true' if count else ''
    cmr_query_url = f'https://{service}/search/collections.json?collection_concept_id={ccid}{collection_count}{pretty}'
    return process_request(cmr_query_url, provider_collections_dict, get_session(), page_num=1)


def get_related_urls(ccid: str, granule_ur: str, pretty=False, service='cmr.earthdata.nasa.gov') -> dict:
    """
    Search for a granules RelatedUrls using the collection concept id and granule ur.
    This provides a way to go from the REST form of a URL that the OPeNDAP server typically
    receives and the URLs that can be used to directly access data (and thus the DMR++
    if the data are in S3 and OPeNDAP-enabled).

    :returns: A dictionary that holds all the RelatedUrls that have Type 'GET DATA' or 'USE SERVICE DATA.'
    """
    pretty = '&pretty=true' if pretty else ''
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={ccid}&granule_ur={granule_ur}{pretty}'
    return process_request(cmr_query_url, granule_ur_dict, get_session(), page_num=1)


def get_collection_granules(ccid: str, pretty=False, service='cmr.earthdata.nasa.gov', descending=False) -> dict:
    """
    Get granules for a collection

    :param ccid: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :param descending: If true, get the granules in newest first order, else oldest granule is first
    :returns: The collection JSON object
    """
    pretty = '&pretty=true' if pretty else ''
    sort_key = '&sort_key=-start_date' if descending else ''
    cmr_query_url = f'https://{service}/search/granules.json?collection_concept_id={ccid}{pretty}{sort_key}'
    return process_request(cmr_query_url, collection_granules_dict, get_session(), page_size=500)


def decompose_resty_url(url: str, pretty=False) -> dict:
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
    print(url_pieces)
    url_dict = convert(url_pieces)  # convert the array to a dictionary
    print(url_dict)
    print(f'URL parts: {url_dict}') if verbose else ''

    items = get_related_urls(url_dict['collections'], url_dict['granules'], pretty=pretty)
    print(f'Data URLs: {items}') if verbose else ''
    return items
