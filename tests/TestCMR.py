
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


    def test_collection_granules_dict(self):
        self.assertEqual(cmr.collection_granules_dict(self.d1), {'C1234-Provider': 'A title with spaces'})
        self.assertEqual(cmr.collection_granules_dict(self.d12), {'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'})
        self.assertEqual(cmr.collection_granules_dict(self.d2), {'C1234-Provider': ('A title with spaces', 'G1234')})
        self.assertEqual(cmr.collection_granules_dict(self.d22), {'C1234-Provider': ('A title with spaces', 'G1234'), 'C5678-Provider': 'Another title'})
        self.assertEqual(cmr.collection_granules_dict(self.d3), {})
        self.assertEqual(cmr.collection_granules_dict(self.d4), {})
        self.assertEqual(cmr.collection_granules_dict(self.d5), {})

    def test_provider_collections_dict(self):
        self.assertEqual(cmr.provider_collections_dict(self.d1), {'C1234-Provider': 'A title with spaces'})
        self.assertEqual(cmr.provider_collections_dict(self.d12), {'C1234-Provider': 'A title with spaces', 'C5678-Provider': 'Another title'})
        self.assertEqual(cmr.provider_collections_dict(self.d2), {'C1234-Provider': (10, 'A title with spaces')})
        self.assertEqual(cmr.provider_collections_dict(self.d22), {'C1234-Provider': 'A title with spaces', 'C5678-Provider': (10, 'Another title')})
        self.assertEqual(cmr.provider_collections_dict(self.d3), {})
        self.assertEqual(cmr.provider_collections_dict(self.d4), {})
        self.assertEqual(cmr.provider_collections_dict(self.d5), {})


if __name__ == '__main__':
    unittest.main()
