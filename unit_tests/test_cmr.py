"""
Test functions in the pydmr cmr module.
"""
import unittest

import requests
import responses

import cmr
from unit_tests import CMR_Responses


class TestCMR(unittest.TestCase):
    d1 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces'}]}}
    d12 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces'},
                              {'id': 'C5678-Provider', 'title': 'Another title'}]}}

    # These include producer_granule_id and granule_count info
    d2 = {'feed': {'entry': [
        {'id': 'C1234-Provider', 'title': 'A title with spaces', 'producer_granule_id': 'G1234', 'granule_count': 10}]}}
    d22 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces', 'producer_granule_id': 'G1234'},
                              {'id': 'C5678-Provider', 'title': 'Another title', 'granule_count': 10}]}}

    d3 = {'feed': {'entry': []}}
    d4 = {'feed': {'missing': ['x']}}
    d5 = {'foo': {'missing': ['x']}}

    # valid 'items' from a granule query are a dictionary where the value is an array.
    # That array holds dictionaries, where each value of the key 'umm' is and array of...
    # dictionaries. gads.
    g1 = {'items': [{'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                              'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA'},
                                             {'URL': 'https://archive/250_2101_ovw.l2.nc',
                                              'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA'}]}}]}
    # this has one element of the RelatedUrls array with both Type and URL and one missing Type
    g12 = {'items': [{'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                               'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA'},
                                              {'URL': 'https://archive/250_2101_ovw.l2.nc'}]}}]}

    # These are all missing things
    g2 = {'items': [{'umm': {'RelatedUrls': {'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}}}]}
    g21 = {'items': [{'umm': {'RelatedUrls': {'Type': 'GET DATA'}}}]}
    g3 = {'items': [{'umm': {}}]}
    g4 = {'items': []}

    # valid 'items' from a granule query are a dictionary where the value is an array.
    # That array holds dictionaries, where each value of the key 'umm' is and array of...
    # dictionaries. gads.
    g6 = {'items': [{'meta': {'concept-type': 'granule',
                              'concept-id': 'G2081588885-POCLOUD',
                              'revision-id': 4,
                              'native-id': 'ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                              'provider-id': 'POCLOUD',
                              'format': 'application/vnd.nasa.cmr.umm+json',
                              'revision-date': '2021-11-13T15:38:38.955Z'},
                     'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                              'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA'},
                                             {'URL': 'https://archive/250_2101_ovw.l2.nc', 'Type': 'GET DATA'}]}}]}
    # this has one element of the RelatedUrls array with both Type and URL and one missing Type
    g62 = {'items': [{'meta': {'concept-type': 'granule',
                               'concept-id': 'G2081588885-POCLOUD',
                               'revision-id': 4,
                               'native-id': 'ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                               'provider-id': 'POCLOUD',
                               'format': 'application/vnd.nasa.cmr.umm+json',
                               'revision-date': '2021-11-13T15:38:38.955Z'},
                      'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                               'Type': 'USE SERVICE API', 'Subtype': 'OPENDAP DATA'},
                                              {'URL': 'https://archive/250_2101_ovw.l2.nc'}]}}]}

    g7 = {'items': [{'meta': {'concept-type': 'granule',
                              'concept-id': 'G2081588885-POCLOUD',
                              'revision-id': 4,
                              # 'native-id': 'ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                              'revision-date': '2021-11-13T15:38:38.955Z'},
                     'umm': {'RelatedUrls': {'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}}}]}
    g72 = {'items': [{'meta': {'concept-type': 'granule',
                               # 'concept-id': 'G2081588885-POCLOUD',
                               'revision-id': 4,
                               # 'native-id': 'ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                               'revision-date': '2021-11-13T15:38:38.955Z'},
                      'umm': {'RelatedUrls': {'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}}}]}
    g73 = {'items': [{'meta': {'concept-type': 'granule',
                               # 'concept-id': 'G2081588885-POCLOUD',
                               'revision-id': 4,
                               'native-id': 'ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                               'revision-date': '2021-11-13T15:38:38.955Z'},
                      'umm': {'RelatedUrls': {'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}}}]}
    g74 = {'items': [{'umm': {'RelatedUrls': {'Type': 'GET DATA', 'Subtype': 'OPENDAP DATA', 'URL': 'stuff'}}}]}
    g75 = {'items': [{'umm': {}}]}
    g76 = {'items': []}

    # Test granule (taken from collection:2075141559-POCLOUD)
    p1 = {'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                  'https://opendap.earthdata.nasa.gov/collections/C2075141559-POCLOUD/granules'
                                  '/ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2')}

    def test_collection_granules_dict(self):
        self.assertEqual({'C1234-Provider': 'A title with spaces'}, cmr.collection_granules_dict(self.d1))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'},
                         cmr.collection_granules_dict(self.d12))
        self.assertEqual({'C1234-Provider': ('A title with spaces', 'G1234')}, cmr.collection_granules_dict(self.d2))
        self.assertEqual({'C1234-Provider': ('A title with spaces', 'G1234'), 'C5678-Provider': 'Another title'},
                         cmr.collection_granules_dict(self.d22))
        self.assertEqual({}, cmr.collection_granules_dict(self.d3))
        self.assertEqual({}, cmr.collection_granules_dict(self.d4))
        self.assertEqual({}, cmr.collection_granules_dict(self.d5))

    def test_provider_collections_dict(self):
        self.assertEqual({'C1234-Provider': 'A title with spaces'}, cmr.provider_collections_dict(self.d1))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'},
                         cmr.provider_collections_dict(self.d12))
        self.assertEqual({'C1234-Provider': (10, 'A title with spaces')}, cmr.provider_collections_dict(self.d2))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': (10, 'Another title')},
                         cmr.provider_collections_dict(self.d22))
        self.assertEqual({}, cmr.provider_collections_dict(self.d3))
        self.assertEqual({}, cmr.provider_collections_dict(self.d4))
        self.assertEqual({}, cmr.provider_collections_dict(self.d5))

    def test_granule_ur_dict(self):
        self.assertEqual({'URL1': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                          'URL2': 'https://archive/250_2101_ovw.l2.nc'},
                         cmr.granule_ur_dict(self.g1))
        self.assertEqual({'URL1': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}, cmr.granule_ur_dict(self.g12))

        self.assertEqual({}, cmr.granule_ur_dict(self.g2))
        self.assertEqual({}, cmr.granule_ur_dict(self.g21))
        self.assertEqual({}, cmr.granule_ur_dict(self.g3))
        self.assertEqual({}, cmr.granule_ur_dict(self.g4))

    def test_granule_ur_dict_2(self):
        # granule_ur_dict_2 should return a dictionary like {ID : (Title, URL)}.
        self.assertEqual({'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                                  's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc')},
                         cmr.granule_ur_dict_2(self.g6))
        self.assertEqual({'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                                  's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc')},
                         cmr.granule_ur_dict_2(self.g62))

        self.assertEqual({}, cmr.granule_ur_dict_2(self.g7))
        self.assertEqual({}, cmr.granule_ur_dict_2(self.g72))
        self.assertEqual({}, cmr.granule_ur_dict_2(self.g73))
        self.assertEqual({}, cmr.granule_ur_dict_2(self.g74))
        self.assertEqual({}, cmr.granule_ur_dict_2(self.g75))
        self.assertEqual({}, cmr.granule_ur_dict_2(self.g76))

    def test_merge(self):
        self.assertEqual({'a': 'b', 'c': 'd'}, cmr.merge_dict({'a': 'b'}, {'c': 'd'}))
        self.assertEqual({'a': 'b'}, cmr.merge_dict({'a': 'b'}, {'a': 'b'}))
        self.assertEqual({'a': 'b'}, cmr.merge_dict({'a': 'b'}, {}))
        self.assertEqual({'c': 'd'}, cmr.merge_dict({}, {'c': 'd'}))
        self.assertEqual({}, cmr.merge_dict({}, {}))
        # In the following, just unit_tests a small and unique part of the error message.
        self.assertRaisesRegex(TypeError, ".*cmr.merge.*", cmr.merge_dict, [], {'c': 'd'})
        self.assertRaisesRegex(TypeError, ".*cmr.merge.*", cmr.merge_dict, {'c': 'd'}, [])

    @responses.activate
    def test_process_request(self):
        # Make a mock url to store the test response data
        responses.add(responses.GET, 'http://testcmr.com/api/1/foobar&page_num=1&page_size=1',
                      json=CMR_Responses.g3, status=200)

        resp = requests.get('http://testcmr.com/api/1/foobar&page_num=1&page_size=1')

        # Make sure the responses are setup correctly
        assert resp.json() == CMR_Responses.g3
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://testcmr.com/api/1/foobar&page_num=1&page_size=1'

        # Use mock url to compare that process request reads the json properly
        self.assertEqual(cmr.process_request('http://testcmr.com/api/1/foobar', cmr.collection_granule_and_url_dict,
                                             cmr.get_session(), 1, 1), self.p1)

    @responses.activate
    def test_get_collection_granules_umm_first_last(self):
        # ccid = "TESTID"
        # granule1 = {'G2081588885-POCLOUD': ['ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
        #                                    'https://opendap.earthdata.nasa.gov/collections/C2075141559-POCLOUD/granules/ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2']}
        # granule2 = {'G2600391229-POCLOUD': ['ascat_20230131_193300_metopb_53818_eps_o_250_3301_ovw.l2',
        #                                    'https://opendap.earthdata.nasa.gov/collections/C2075141559-POCLOUD/granules/ascat_20230131_193300_metopb_53818_eps_o_250_3301_ovw.l2']}

        # Setup two urls because the 'get_collection_granules_first_last' uses the same url but with
        # '&sort_key=-start_date' to get the newest granule
        responses.add(responses.GET,
                      'https://test_service/search/granules.json?collection_concept_id=TESTID&page_num=1&page_size=1',
                      json=CMR_Responses.g3, status=200)
        responses.add(responses.GET,
                      'https://test_service/search/granules.json?collection_concept_id=TESTID&sort_key=-start_date'
                      '&page_num=1&page_size=1',
                      json=CMR_Responses.g3, status=200)

        self.assertEqual(cmr.get_collection_granules_umm_first_last("TESTID", cmr.collection_granule_and_url_dict, False,
                                                                'test_service'), self.p1)


if __name__ == '__main__':
    unittest.main()
