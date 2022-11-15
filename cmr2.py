import json

import aiohttp
import asyncio
import funcy
import sys

from pip._internal.utils import encoding


class CMRException(Exception):
    """When CMR returns an error"""

    def __init__(self, status, message="No error message given"):
        self.status = status
        self.message = message

    def __str__(self):
        return f'CMR Exception HTTP status: {self.status} - {self.message}'


def is_entry_feed(json_resp):
    """
    Does this JSON object have the 'entry' key within a 'feed' key?
    This function is used to protect various response processors
    from responses that contain no entries or are malformed.
    """
    return len(json_resp) > 0 and "feed" in json_resp.keys() and "entry" in json_resp["feed"].keys()


def provider_collections_dict(json_resp):
    """
    Extract collection IDs and Titles from CMR JSON. Optionally get the granule count.

    :param json_resp: CMR JSON response
    :return: The provider collection IDs and title in a dictionary
    :rtype: dict
    """

    dict_resp = {}

    converted_json = json.loads(json_resp.decode('utf8'))
    for entry in converted_json["feed"]["entry"]:
        if "granule_count" in entry:
            dict_resp[entry["id"]] = (entry["granule_count"], entry["title"])
        else:
            dict_resp[entry["id"]] = (entry["title"])

    return dict_resp


def collection_granules_dict(json_resp):
    """
    :param json_resp: CMR JSON response
    :return: A dictionary with the Granule id indexing the producer granule id and granule title
    :rtype: dict
    """
    converted_json = json.loads(json_resp.decode('utf8'))

    if not is_entry_feed(converted_json):
        return {}

    dict_resp = {}

    for entry in converted_json["feed"]["entry"]:
        if "producer_granule_id" in entry:  # some granule records lack "producer_granule_id". jhrg 9/4/22
            dict_resp[entry["id"]] = (entry["title"], entry["producer_granule_id"])
        else:
            dict_resp[entry["id"]] = (entry["title"])

    return dict_resp


async def fetch(url, session, max_redirects):
    async with session.request('GET', url, max_redirects=max_redirects) as response:
        return (response.url, response.status, await response.read())


async def send(token, chunk):
    max_redirects = len(chunk) * 8
    headers = { 'Authorization': f'Bearer {token}' }

    #TODO: read the json file similar to 'response_processor' from cmr.py
    async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
        provider_urls = []
        for provider in chunk:
            provider_urls.append(f'https://cmr.earthdata.nasa.gov/search/collections.json?provider={provider}&has_opendap_url=true&pretty=false')
        tasks = [asyncio.ensure_future(fetch(url, session, max_redirects)) for url in provider_urls]
        results = await asyncio.gather(*tasks)
        print(f'{results[0][2]}')
        print('Chunk statuses: ', [status for (url, status, text) in results])
        for (url, status, content) in results:
            if status == 500:
                print('--------------------------------')
                print(f'URL: {url}')
                print('Response content:')
                print(content)

        collections = {}
        collections = collection_granules_dict(results[0][2])
        print(collections)


async def main(token_fn, concurrent, providers):
    with open(token_fn, 'rt') as f:
        token = f.readline().strip()
    with open(providers, 'rt') as f:
        requests = f.readlines()

    print()
    print(f'Sending chunks of {concurrent} concurrent requests')

    for chunk in funcy.chunks(concurrent, requests):
        await send(token, chunk)


if __name__ == '__main__':
    token_fn = sys.argv[1]
    concurrent = int(sys.argv[2])
    providers = sys.argv[3]

    asyncio.run(main(token_fn, concurrent, providers))
