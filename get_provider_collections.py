
""""
Get all the collections for a given provider (e.g., ORNL_CLOUD).
"""

import requests
import urs_session


def cmr_provider_collections_json(provider_id):
    """
    Get all the collections for a given provider.
    :param provider_id The string ID for a given EDC provider (e.g., ORNL_CLOUD)
    :return ?
    """
    service = 'cmr.earthdata.nasa.gov'
    cmr_query_url = f'https://{service}/search/collections.json?provider={provider_id}'

    print(f'CMR Query URL: {cmr_query_url}')
