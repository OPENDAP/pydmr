
"""
Test functions in the pydmr cmr module.
"""
import unittest
import cmr


class TestCMR(unittest.TestCase):
    def test_collection_granules_dict(self):
        d = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces'}]}}
        self.assertEqual(cmr.collection_granules_dict(d), {'C1234-Provider': 'A title with spaces'})
        d = {'feed': {'entry': [{'id': 'C1234-Provider', 'title': 'A title with spaces', 'producer_granule_id': 'G1234'}]}}
        self.assertEqual(cmr.collection_granules_dict(d), {'C1234-Provider': ('A title with spaces', 'G1234')})
        d = {'feed': {'entry': []}}
        self.assertEqual(cmr.collection_granules_dict(d), {})
        d = {'feed': {'missing': ['x']}}
        self.assertEqual(cmr.collection_granules_dict(d), {})
        d = {'foo': {'missing': ['x']}}
        self.assertEqual(cmr.collection_granules_dict(d), {})


if __name__ == '__main__':
    unittest.main()
