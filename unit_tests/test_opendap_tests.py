import unittest

import requests
from xml.dom.minidom import parseString

import opendap_tests


class MyTestCase(unittest.TestCase):

    def test_dmr_tester_pass(self):
        opendap_tests.quiet = True
        result = opendap_tests.dmr_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        self.assertEqual(result["dmr_test"].result, "pass")
        self.assertEqual(result["dmr_test"].status, 200)

    def test_dmr_tester_fail(self):
        opendap_tests.quiet = True
        result = opendap_tests.dmr_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h")
        self.assertEqual(result["dmr_test"].result, "fail")
        self.assertEqual(result["dmr_test"].status, 404)

    def test_dap_tester_pass(self):
        opendap_tests.quiet = True
        result = opendap_tests.dap_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        self.assertEqual(result["dap_test"].result, "pass")
        self.assertEqual(result["dap_test"].status, 200)

    def test_dap_tester_fail(self):
        opendap_tests.quiet = True
        result = opendap_tests.dap_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h", False)
        self.assertEqual(result["dap_test"].result, "fail")
        self.assertEqual(result["dap_test"].status, 404)

    def test_var_tester_pass(self):
        opendap_tests.quiet = True
        results = {}
        result = opendap_tests.var_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5", results, True)
        key = next(iter(result))
        self.assertEqual(result[str(key)].result, "pass")
        self.assertEqual(result[str(key)].status, 200)

    def test_var_tester_fail(self):
        opendap_tests.quiet = True
        results = {}
        result = opendap_tests.var_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h", results)
        key = next(iter(result))
        self.assertEqual(result[str(key)].result, "fail")
        self.assertEqual(result[str(key)].status, 404)

    def test_build_leaf_path_group(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/data/hdf5/grid_1_2d.h5.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_doc = parseString(dmr_xml)
                f32s = dmr_doc.getElementsByTagName("Float32")
                var = opendap_tests.build_leaf_path(f32s[0])
                self.assertEqual(var, "HDFEOS/GRIDS/GeoGrid/Data_Fields/temperature")
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")

    def test_build_leaf_path_structure(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_doc = parseString(dmr_xml)
                f32s = dmr_doc.getElementsByTagName("Float32")
                var = opendap_tests.build_leaf_path(f32s[0])
                self.assertEqual(var, "obs.relhum")
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")

    def test_build_leaf_path_sequence(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/data/ff/avhrr.dat.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_doc = parseString(dmr_xml)
                i32s = dmr_doc.getElementsByTagName("Int32")
                var = opendap_tests.build_leaf_path(i32s[0])
                self.assertEqual(var, "URI_Avhrr.year")
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")

    def test_build_leaf_path_default(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_doc = parseString(dmr_xml)
                f32s = dmr_doc.getElementsByTagName("Float32")
                var = opendap_tests.build_leaf_path(f32s[0])
                self.assertEqual(var, "d_16_chunks")
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")


if __name__ == '__main__':
    unittest.main()
