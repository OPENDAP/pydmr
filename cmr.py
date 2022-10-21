"""
Access information about data in NASA's EarthData Cloud system using the
CMR Web API.
"""

import requests

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


def is_entry_feed(json_resp):
    """
    Does this JSON object have the 'entry' key within a 'feed' key?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.
    """
    return len(json_resp) > 0 and "feed" in json_resp.keys() and "entry" in json_resp["feed"].keys()


def is_granule_item(json_resp):
    """
    Does this JSON object have the 'RelatedUrls' key within a 'umm' key?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.
    """
    return len(json_resp) > 0 and "umm" in json_resp.keys() and "RelatedUrls" in json_resp["umm"].keys()


def collection_granules_dict(json_resp):
    """
    :param json_resp: CMR JSON response
    :return: A dictionary with the Granule id indexing the producer granule id and granule title
    :rtype: dict
    """
    if not is_entry_feed(json_resp):
        return {}

    dict_resp = {}
    for entry in json_resp["feed"]["entry"]:
        if "producer_granule_id" in entry:  # some granule records lack "producer_granule_id". jhrg 9/4/22
            dict_resp[entry["id"]] = (entry["title"], entry["producer_granule_id"])
        else:
            dict_resp[entry["id"]] = (entry["title"])

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


def granule_ur_dict(json_resp):
    """
    Extract Related URLs from CMR JSON UMM
    :param json_resp: CMR JSON UMM response
    :return: The granule UR related URL info in a dictionary. Only 'GET DATA' and 'USE SERVICE API'
        type URLs are included. Each is indexed using 'URL1', ..., 'URLn.'
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
            if "Type" in r_url and r_url["Type"] in ('GET DATA', 'USE SERVICE API'):
                dict_resp[f'URL{i}'] = (r_url["URL"])
                i += 1

    return dict_resp


def merge(dict1: dict, dict2: dict) -> dict:
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

    :param: a: The List/Array to convert
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
            # print(f'text: {r.text}')

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

        entries_pg = {}
        if entries > 0:
            entries_pg = response_processor(json_resp)  # The response_processor() is passed in
            entries_dict = merge(entries_dict, entries_pg)  # merge is smart if entries_dict is empty

        if page_num != 0 or len(entries_pg) < page_size:
            break

    return entries_dict


def url_tester_dmr(url_address):
    """
    Take in a url and test whether or not it has a dmr for testing purposes
    :param url_address: The url to be checked
    :return: A pass/fail of whether or not the url passes
    """
    dmr_check = False
    try:
        # TODO Maybe add a 'quiet' option... jhrg 10/21/22
        print(".", end="", flush=True)
        r = requests.get(url_address + '.dmr')
        if r.status_code == 200:
            dmr_check = True
            # Save the response to the local directory
            base_name = url_address.split('/')[-1]
            with open(base_name + '.dmr', 'w') as file:
                file.write(r.text)
        else:
            print("F", end="", flush=True)
            base_name = url_address.split('/')[-1]
            with open(base_name + '.dmr.fail', 'w') as file:
                file.write(f'Status: {r.status_code}: {r.text}')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    if dmr_check:
        return "pass"
    else:
        return "fail"


def url_tester_nc4(url_address):
    """
    Take in a url and test whether or not it has a dmr for testing purposes
    :param url_address: The url to be checked
    :return: A pass/fail of whether or not the url passes
    """
    nc4_check = False
    try:
        # TODO Maybe add a 'quiet' option... jhrg 10/21/22
        print(".", end="", flush=True)
        # TODO Why does using '.dap.nc4' hang for requests that fail? jhrg 10/21/22
        r = requests.get(url_address + '.nc4')
        if r.status_code == 200:
            nc4_check = True
            # Save the response to the local directory
            base_name = url_address.split('/')[-1]
            with open(base_name + '.nc4', 'wb') as file:
                file.write(r.content)
        else:
            print("F", end="", flush=True)
            base_name = url_address.split('/')[-1]
            with open(base_name + '.nc4.fail', 'w') as file:
                file.write(f'Status: {r.status_code}: {r.text}')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    if nc4_check:
        return "pass"
    else:
        return "fail"


def url_test_array(concept_id, granule_ur, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Gather a list of urls and put them in an array/list to be tested

    :return: A list of urls
    """
    url_list = []
    url_dmr_test = {}

    # Get the urls
    pretty = '&pretty=true' if pretty else ''
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={concept_id}&granule_ur={granule_ur}{pretty}'
    url_collection = process_request(cmr_query_url, granule_ur_dict, page_num=1)

    # Store just the url value in the list
    for urls in url_collection:
        url_list.append(url_collection[urls])

    # Run test but only on opendap.earthdata.nasa.gov urls
    for url in url_list:
        if url.find("opendap.earthdata.nasa.gov") > 0:
            dmr_result = url_tester_dmr(url)
            nc4_result = url_tester_nc4(url)
            url_dmr_test[url] = (dmr_result, nc4_result)

    return url_dmr_test


# TODO Change the name jhrg 10/21/22
# TODO Add print(".'. end="") here where appropriate. jhrg 10/21/22
def get_test_format(provider_id, opendap=True, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Take the collections for a provider and get the first and last granule for each one.

    :param provider_id: The string ID for a given EDC provider (e.g., ORNL_CLOUD)
    :return: A dictionary of entries formatted as 'Provider, Collection, Granule'
    """
    test_dict = {}

    # Get the list of collections
    pretty = '&pretty=true' if pretty else ''
    opendap = '&has_opendap_url=true' if opendap else ''
    cmr_query_url = f'https://{service}/search/collections.json?provider={provider_id}{opendap}{pretty}'
    collect_dict = process_request(cmr_query_url, provider_collections_dict, page_size=500)

    # Loop through the collections and get the first and last granule of each
    i = 0
    for collection in collect_dict.keys():
        # by default, CMR returns results with "sort_key = +start_date"
        cmr_query_url = f'https://{service}/search/granules.json?concept_id={collection}{pretty}'
        oldest_dict = process_request(cmr_query_url, collection_granules_dict, page_size=1, page_num=1)
        if len(oldest_dict) == 1:
            test_dict[i] = (oldest_dict, collection, provider_id)
            if verbose:
                print(f'{list(test_dict.items())[i]}')
            i += 1

        sort_key = '&sort_key=-start_date'
        cmr_query_url = f'https://{service}/search/granules.json?concept_id={collection}{sort_key}{pretty}'
        newest_dict = process_request(cmr_query_url, collection_granules_dict, page_size=1, page_num=1)
        if len(newest_dict) == 1:
            test_dict[i] = (newest_dict, collection, provider_id)
            if verbose:
                print(f'{list(test_dict.items())[i]}')
            i += 1

    return test_dict


def full_url_test(provider_id, opendap=False, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Given a provider, gather the collections and the first and last granule of each collection.
    Then run through them and test each url.
    :param provider_id:
    :param opendap:
    :param pretty:
    :param service:
    :return:
    """

    url_results = {}

    print(".", end="", flush=True)
    collection_info = get_test_format(provider_id, opendap=opendap, pretty=pretty, service=service)

    for granules in collection_info:
        collection_id = collection_info[granules][1]
        value = list(collection_info[granules][0].values())[0]
        url_results[granules] = url_test_array(collection_id, value)

    # TODO Maybe add a 'quiet' option... jhrg 10/21/22
    print("", end="\n", flush=True)

    return url_results


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


def get_collection_entry(concept_id, pretty=False, count=False, service='cmr.earthdata.nasa.gov'):
    """
    Get the collection entry given a concept id.

    :param concept_id: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param count: request the granule count for the collection
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :returns:The collection JSON object
    """
    pretty = '&pretty=true' if pretty else ''
    collection_count = '&include_granule_counts=true' if count else ''
    cmr_query_url = f'https://{service}/search/collections.json?concept_id={concept_id}{collection_count}{pretty}'
    return process_request(cmr_query_url, provider_collections_dict, page_num=1)


def get_related_urls(concept_id, granule_ur, pretty=False, service='cmr.earthdata.nasa.gov'):
    """
    Search for a granules RelatedUrls using the collection concept id and granule ur.
    This provides a way to go from the REST form of a URL that the OPeNDAP server typically
    receives and the URLs that can be used to directly access data (and thus the DMR++
    if the data are in S3 and OPeNDAP-enabled).

    :returns: A dictionary that holds all the RelatedUrls that have Type 'GET DATA' or
        'USE SERVICE DATA.'
    """
    pretty = '&pretty=true' if pretty else ''
    cmr_query_url = f'https://{service}/search/granules.umm_json_v1_4?collection_concept_id={concept_id}&granule_ur={granule_ur}{pretty}'
    return process_request(cmr_query_url, granule_ur_dict, page_num=1)


def get_collection_granules(concept_id, pretty=False, service='cmr.earthdata.nasa.gov', descending=False):
    """
    Get granules for a collection

    :param concept_id: The string Collection (Concept) Id
    :param pretty: request a 'pretty' version of the response from the service. default False
    :param service: The URL of the service to query (default cmr.earthdata.nasa.gov)
    :param descending: If true, get the granules in newest first order, else oldest granule is first
    :returns: The collection JSON object
    """
    pretty = '&pretty=true' if pretty else ''
    sort_key = '&sort_key=-start_date' if descending else ''
    cmr_query_url = f'https://{service}/search/granules.json?concept_id={concept_id}{pretty}{sort_key}'
    return process_request(cmr_query_url, collection_granules_dict, page_size=500)


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
