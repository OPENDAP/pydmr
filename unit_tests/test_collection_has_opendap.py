import unittest
from unittest.mock import patch  # For mocking external dependencies

import cmr


# Assuming process_request and get_session are defined elsewhere
def mock_process_request(url, data_processor, session, page_size, page_num):
    # Simulate successful retrieval of granule data
    if url == 'https://cmr.earthdata.nasa.gov/search/granules.umm_json_v1_4?collection_concept_id=TEST_CCID':
        return {'granule1': ('metadata', 'https://opendap.earthdata.nasa.gov/data/example.opendap')}
    elif url == 'https://cmr.earthdata.nasa.gov/search/granules.umm_json_v1_4?collection_concept_id=NO_OPENDAP_CCID':
        return {'granule1': ('metadata', 'https://not_opendap.com/data')}
    else:
        raise Exception('Unexpected URL')


def mock_get_session():
    # Simulate a session object
    return 'mock_session'


def mock_granule_ur_dict_2(data):
    # Simulate granule URL extraction (replace with your actual implementation if needed)
    return data[1]  # Assuming the URL is the second element in the granule data


@patch('cmr.process_request', side_effect=mock_process_request)
@patch('cmr.get_session', return_value=mock_get_session)
class TestCollectionHasOpendap(unittest.TestCase):

    def test_collection_has_opendap_success(self, mock_get_session, mock_process_request):
        """
        Test case where the first granule has an OPeNDAP URL in the cloud.
        """
        ccid = 'TEST_CCID'
        cloud_prefix = 'https://opendap.earthdata.nasa.gov/'

        result = cmr.collection_has_opendap(ccid, cloud_prefix, json_processor=mock_granule_ur_dict_2)

        self.assertEqual(result, (ccid, True, cloud_prefix + 'data/example.opendap'))

    def test_collection_has_opendap_no_opendap(self, mock_get_session, mock_process_request):
        """
        Test case where the first granule does not have an OPeNDAP URL.
        """
        ccid = 'NO_OPENDAP_CCID'
        cloud_prefix = 'https://opendap.earthdata.nasa.gov/'

        result = cmr.collection_has_opendap(ccid, cloud_prefix, json_processor=mock_granule_ur_dict_2)

        self.assertEqual(result, (ccid, False, 'https://not_opendap.com/data'))

    def test_collection_has_opendap_empty_response(self, mock_get_session, mock_process_request):
        """
        Test case where process_request returns an empty response.
        """
        ccid = 'INVALID_CCID'
        cloud_prefix = 'https://opendap.earthdata.nasa.gov/'

        with self.assertRaises(Exception):
            cmr.collection_has_opendap(ccid, cloud_prefix, json_processor=mock_granule_ur_dict_2)

        # The exception will be raised by the mock_process_request


if __name__ == '__main__':
    unittest.main()
