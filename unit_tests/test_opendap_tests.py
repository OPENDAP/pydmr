import unittest

import requests
from xml.dom.minidom import parseString

import opendap_tests


def var_tester_success_percent(dmr_vars, r, url, var_len):
    results = []
    opendap_tests.var_tester_helper(url, dmr_vars, results, ".dap", r, False)
    fail_len = len(results)
    if var_len == fail_len:
        percent = "0.0%"
    else:
        percent = str(round(fail_len / var_len * 100, 2)) + "%"
    return percent


class MyTestCase(unittest.TestCase):

    def test_dmr_tester_pass(self):
        opendap_tests.quiet = True
        result = opendap_tests.dmr_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.code, 200)

    def test_dmr_tester_fail(self):
        opendap_tests.quiet = True
        result = opendap_tests.dmr_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h")
        self.assertEqual(result.status, "fail")
        self.assertEqual(result.code, 404)

    def test_dap_tester_pass(self):
        opendap_tests.quiet = True
        result = opendap_tests.dap_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.code, 200)

    def test_dap_tester_fail(self):
        opendap_tests.quiet = True
        result = opendap_tests.dap_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h")
        self.assertEqual("fail", result.status)
        self.assertEqual(500, result.code)

    def test_var_tester_pass(self):
        opendap_tests.quiet = True
        result = opendap_tests.var_tester("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc", True)
        key = next(iter(result))
        self.assertEqual("pass", key.status)
        self.assertEqual(200, key.code)
        # no longer returned. jhrg 5/15/24 self.assertEqual("100.0%", result["percent"])

    def test_var_tester_fail(self):
        opendap_tests.quiet = True
        result = opendap_tests.var_tester("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.n")
        key = next(iter(result))
        self.assertEqual("fail", key.status)
        self.assertEqual(404, key.code)
        # self.assertEqual("0.0%", result["percent"])

    def test_var_tester_helper_1(self):
        opendap_tests.quiet = True
        try:
            url = "http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc"
            r = requests.get(url + ".dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_vars = opendap_tests.parse_variables(dmr_xml)
                var_len = len(dmr_vars)

                name = dmr_vars[1].getAttribute("name")
                name += "z"
                dmr_vars[1].setAttribute("name", name)

                percent = var_tester_success_percent(dmr_vars, r, url, var_len)

                self.assertEqual("20.0%", percent)
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_var_tester_helper_1")

    def test_var_tester_helper_2(self):
        opendap_tests.quiet = True
        try:
            url = "http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc"
            r = requests.get(url + ".dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_vars = opendap_tests.parse_variables(dmr_xml)
                var_len = len(dmr_vars)

                name = dmr_vars[1].getAttribute("name")
                name += "z"
                dmr_vars[1].setAttribute("name", name)

                name = dmr_vars[2].getAttribute("name")
                name += "z"
                dmr_vars[2].setAttribute("name", name)

                percent = var_tester_success_percent(dmr_vars, r, url, var_len)

                self.assertEqual("40.0%", percent)
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_var_tester_helper_2")

    def test_var_tester_helper_3(self):
        opendap_tests.quiet = True
        try:
            url = "http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5"
            r = requests.get(url + ".dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_vars = opendap_tests.parse_variables(dmr_xml)
                var_len = len(dmr_vars)

                name = dmr_vars[0].getAttribute("name")
                name += "z"
                dmr_vars[0].setAttribute("name", name)

                percent = var_tester_success_percent(dmr_vars, r, url, var_len)

                self.assertEqual("0.0%", percent)
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_var_tester_helper_3")

    def test_build_leaf_path_group(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/data/hdf5/grid_1_2d.h5.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_doc = parseString(dmr_xml)
                f32s = dmr_doc.getElementsByTagName("Float32")
                var = opendap_tests.build_leaf_path(f32s[2])
                self.assertEqual("HDFEOS/GRIDS/GeoGrid/Data_Fields/temperature", var)
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
                self.assertEqual("obs.relhum", var)
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
                self.assertEqual("URI_Avhrr.year", var)
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
                self.assertEqual("d_16_chunks", var)
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")

    def test_parse_variables_true(self):
        opendap_tests.quiet = True
        try:
            r = requests.get("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc.dmr")
            if r.status_code == 200:
                dmr_xml = r.text
                dmr_vars = opendap_tests.parse_variables(dmr_xml)
                self.assertEqual(5, len(dmr_vars))
            else:
                self.fail("Could not reach unit_tests file")
        except requests.exceptions.RequestException:
            self.fail("exception thrown in unit_tests: test_build_leaf_path_groups")


if __name__ == '__main__':
    unittest.main()
