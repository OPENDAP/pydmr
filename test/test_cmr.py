
"""
Test functions in the pydmr cmr module.
"""
import unittest
import cmr


class TestCMR(unittest.TestCase):
    d1 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces'}]}}
    d12 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces'},
                              {'id': 'C5678-Provider', 'title': 'Another title'}]}}

    # These include producer_granule_id and granule_count info
    d2 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces', 'producer_granule_id': 'G1234', 'granule_count': 10}]}}
    d22 = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces', 'producer_granule_id': 'G1234'},
                              {'id': 'C5678-Provider', 'title': 'Another title', 'granule_count': 10}]}}

    d3 = {'feed': {'entry': []}}
    d4 = {'feed': {'missing': ['x']}}
    d5 = {'foo': {'missing': ['x']}}

    # valid 'items' from a granule query are a dictionary where the value is an array.
    # That array holds dictionaries, where each value of the key 'umm' is and array of...
    # dictionaries. gads.
    g1 = {'items': [{'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                              'Type': 'GET DATA'},
                                             {'URL': 'https://archive/250_2101_ovw.l2.nc',
                                              'Type': 'GET DATA'}]}}]}
    # this has one element of the RelatedUrls array with both Type and URL and one missing Type
    g12 = {'items': [{'umm': {'RelatedUrls': [{'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc',
                                               'Type': 'GET DATA'},
                                              {'URL': 'https://archive/250_2101_ovw.l2.nc'}]}}]}

    # These are all missing things
    g2 = {'items': [{'umm': {'RelatedUrls': {'URL': 's3://podaac/metopb_00588_eps_o_250_2101_ovw.l2.nc'}}}]}
    g21 = {'items': [{'umm': {'RelatedUrls': {'Type': 'GET DATA'}}}]}
    g3 = {'items': [{'umm': {}}]}
    g4 = {'items': []}

    def test_collection_granules_dict(self):
        self.assertEqual({'C1234-Provider': 'A title with spaces'}, cmr.collection_granules_dict(self.d1))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'}, cmr.collection_granules_dict(self.d12))
        self.assertEqual({'C1234-Provider': ('A title with spaces', 'G1234')}, cmr.collection_granules_dict(self.d2))
        self.assertEqual({'C1234-Provider': ('A title with spaces', 'G1234'), 'C5678-Provider': 'Another title'}, cmr.collection_granules_dict(self.d22))
        self.assertEqual({}, cmr.collection_granules_dict(self.d3))
        self.assertEqual({}, cmr.collection_granules_dict(self.d4))
        self.assertEqual({}, cmr.collection_granules_dict(self.d5))

    def test_provider_collections_dict(self):
        self.assertEqual({'C1234-Provider': 'A title with spaces'}, cmr.provider_collections_dict(self.d1))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'}, cmr.provider_collections_dict(self.d12))
        self.assertEqual({'C1234-Provider': (10, 'A title with spaces')}, cmr.provider_collections_dict(self.d2))
        self.assertEqual({'C1234-Provider': 'A title with spaces', 'C5678-Provider': (10, 'Another title')}, cmr.provider_collections_dict(self.d22))
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

    def test_merge(self):
        self.assertEqual({'a': 'b', 'c': 'd'}, cmr.merge({'a': 'b'}, {'c': 'd'}))
        self.assertEqual({'a': 'b'}, cmr.merge({'a': 'b'}, {'a': 'b'}))
        self.assertEqual({'a': 'b'}, cmr.merge({'a': 'b'}, {}))
        self.assertEqual({'c': 'd'}, cmr.merge({}, {'c': 'd'}))
        self.assertEqual({}, cmr.merge({}, {}))
        # In the following, just test a small and unique part of the error message.
        self.assertRaisesRegex(TypeError, ".*cmr.merge.*", cmr.merge, [], {'c': 'd'})
        self.assertRaisesRegex(TypeError, ".*cmr.merge.*", cmr.merge, {'c': 'd'}, [])

    def test_convert(self):
        self.assertEqual({'a': 'b', 'c': 'd'}, cmr.convert(['a', 'b', 'c', 'd']))
        self.assertEqual({'a': 'b'}, cmr.convert(['a', 'b']))
        self.assertEqual({}, cmr.convert([]))

        self.assertRaisesRegex(ValueError, ".*cmr.convert.*", cmr.convert, ['a'])  # only one element
        self.assertRaisesRegex(ValueError, ".*cmr.convert.*", cmr.convert, ['a', 'b', 'c'])  # three elements
        self.assertRaisesRegex(TypeError, ".*cmr.convert.*", cmr.convert, {'a', 'b'})   # not a list


class TestCMRProcessRequest(unittest.TestCase):
    url_that_returns_404 = "http://test.opendap.org/fail"

    def unity(json_resp):
        # TODO Can 'methods' not take self? jhrg 10/27/22
        return json_resp

    def test_process_request(self):
        """ def process_request(cmr_query_url, response_processor, page_size=10, page_num=0):
            Test non 200 response
            200 response w/o feed & w/o items
            200 response w/feed but no entry
            success using simple response_processor
            page_size == 1
            page_num = 1 (something not 0)
        """
        # self.assertIsNotNone(cmr.process_request(self.url_that_will_fail, self.unity))
        self.assertRaisesRegex(cmr.CMRException, ".*404.*", cmr.process_request, self.url_that_returns_404, self.unity)


if __name__ == '__main__':
    unittest.main()
