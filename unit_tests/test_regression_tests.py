"""
Test functions in the pydmr regression_tests module.
"""
import unittest
import regression_tests


class TestRegressionTests(unittest.TestCase):
    def test_is_opendap_cloud_url(self):
        self.assertTrue(regression_tests.is_opendap_cloud_url('http://opendap.earthdata.nasa.gov/hello/world.h5'),
                        "Should pass")
        self.assertTrue(regression_tests.is_opendap_cloud_url('https://opendap.earthdata.nasa.gov/foo/bar.h5'),
                        "Should pass")
        self.assertFalse(regression_tests.is_opendap_cloud_url('http://opendap.uat.earthdata.nasa.gov/k/r.h5'),
                         "Fails because 'opendap.uat...'")
        self.assertFalse(regression_tests.is_opendap_cloud_url('http://podaac.nasa.gov/k/r.h5'),
                         "Fails because 'podaac...'")


    pass1 = {'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://opendap.earthdata.nasa.gov/foo/bar.h5'),
             'G2081589999-POCLOUD': ('ascat_20231029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://opendap.earthdata.nasa.gov/hello/world.h5')}
    fail2 = {'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://opendap.uat.earthdata.nasa.gov/foo/bar.h5'),  # opendap.uat...
             'G2081589999-POCLOUD': ('ascat_20231029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://opendap.earthdata.nasa.gov/hello/world.h5')}
    fail3 = {'G2081588885-POCLOUD': ('ascat_20121029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://opendap.earthdata.nasa.gov/foo/bar.h5'),
             'G2081589999-POCLOUD': ('ascat_20231029_010001_metopb_00588_eps_o_250_2101_ovw.l2',
                                     'https://podaac.machine.domain.tld/hello/world.h5')}   # podaac...

    def test_has_only_opendap_urls(self):
        self.assertTrue(regression_tests.has_only_cloud_opendap_urls(self.pass1), "Should pass")
        self.assertFalse(regression_tests.has_only_cloud_opendap_urls(self.fail2), "Fails because 'opendap.uat...'")
        self.assertFalse(regression_tests.has_only_cloud_opendap_urls(self.fail3), "Fails because 'podaac...'")

    def test_formatted_urls(self):
        self.assertEqual(regression_tests.formatted_urls(self.pass1),
                         "https://opendap.earthdata.nasa.gov/foo/bar.h5, https://opendap.earthdata.nasa.gov/hello/world.h5",
                         "Should pass")
        self.assertEqual(regression_tests.formatted_urls(self.fail3),
                         "https://opendap.earthdata.nasa.gov/foo/bar.h5, https://podaac.machine.domain.tld/hello/world.h5",
                         "Should pass")


if __name__ == '__main__':
    unittest.main()
