
"""
A collection of tests for OPeNDAP URLs packaged as functions.
"""

import requests
from xml.dom.minidom import parseString

import errLog
import testing_results as tr

"""
set 'quiet' in main(), etc., and it affects various functions

set 'save' to save the results of the access operations. If the value is
not null then the results are saved and the value of 'save' is the name of
a subdir where the outputs are stored
"""
quiet: bool = False
save_all: bool = False
save: str = ''
s = requests.session()


def dmr_tester(url_address):
    """
    Take an url and unit_tests whether the server can return its DMR response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """

    ext = '.dmr'
    dmr_tr = tr.Result("dmr", "fail", 500)
    dmr_tr.url = url_address + ext
    dmr_tr.murl = url_address + ext
    try:
        #  print(".", end="", flush=True) if not quiet else False

        r = requests.get(url_address + ext)
        if r.status_code == 200:

            dmr_tr.status = "pass"
            dmr_tr.code = r.status_code

            # Save the response?
            if save_all:
                save_response(url_address, ext, r)
        else:
            #  print("F", end="", flush=True) if not quiet else False

            dmr_tr.code = r.status_code

            if save:
                write_error_file(url_address, ext, r)

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass
    except requests.exceptions.ConnectionError:
        err = "/////////////////////////////////////////////////////\n"
        err += "ConnectionError : opendap_tests.py::dmr_tester() - " + url_address + ext + "\n"
        errLog.output_errlog(err)
    finally:
        return dmr_tr


def dap_tester(url_address):
    """
    Take an url and unit_tests whether the server can return its DMR response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """
    ext = '.dap'
    #  print("|", end="", flush=True) if not quiet else False
    dap_tr = tr.Result("dap", "fail", 500)
    dap_tr.url = url_address + ".dmr"
    try:
        # makes the dmr request so we can parse out the first variable
        r = requests.get(url_address + ".dmr")
        if r.status_code == 200:
            dmr_xml = r.text
            variables = parse_variables(dmr_xml)
            var = variables[0]
            postfix = build_subset_postfix(var)
            url = url_address + postfix
            dap_tr.murl = url

            # making the dap request with the first variable to cut down on response time
            r = requests.get(url)
            if r.status_code == 200:

                dap_tr.status = "pass"
                dap_tr.code = r.status_code

                # Save the response?
                if save_all:
                    save_response(url_address, ext, r)
            else:
                #  print("F", end="", flush=True) if not quiet else False

                dap_tr.code = r.status_code

                if save:
                    write_error_file(url_address, ext, r)

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass
    except requests.exceptions.ConnectionError:
        print("DapE", end="", flush=True)
    finally:
        return dap_tr


def var_tester(url_address, save_passes=False):
    """
    Take an url and unit_tests whether the server can return its DAP response
    def dap_tester(url_address, ext='.dap'):
    """
    ext = '.dap'
    results = []
    try:
        r = requests.get(url_address + ".dmr")
        if r.status_code == 200:
            dmr_xml = r.text
            variables = parse_variables(dmr_xml)
            var_tester_helper(url_address, variables, results, ext, r, save_passes)
        else:
            #  print("F", end="", flush=True) if not quiet else False

            dmr_tr = tr.Result("dap_var", "fail", r.status_code)
            dmr_tr.url = url_address
            results.append(dmr_tr)

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass
    except requests.exceptions.ConnectionError:
        print("VarE", end="", flush=True)

    return results


def var_tester_helper(url_address, variables, results, ext, dmr_r, save_passes):
    """
    sub-function for var_tester(...)
    :param url_address:
    :param variables:
    :param results:
    :param ext:
    :param dmr_r:
    :param save_passes:
    :return:
    """
    for v in variables:
        #  print("-", end="", flush=True) if not quiet else False
        t = build_subset_postfix(v)
        dap_url = url_address + t
        #  print(dap_url)
        dap_r = requests.get(dap_url)
        if dap_r.status_code == 200:

            if save_passes:
                var_tr = tr.Result("dap_var", "pass", dap_r.status_code)
                var_tr.url = url_address + ".dmr"
                var_tr.murl = dap_url
                results.append(var_tr)

            # Save the response?
            if save_all:
                save_response(url_address, ext, dap_r)
        else:
            #  print("F", end="", flush=True) if not quiet else False

            var_tr = tr.Result("dap_var", "fail", dap_r.status_code)
            var_tr.url = dap_url
            results.append(var_tr)

            if save:
                write_error_file(url_address, ext, dmr_r)


def pydmr_headers():
    """
    global function for setting request headers
    :return:
    """
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'pydmr/1.0.0', })
    return headers


def save_response(url_address, ext, r):
    """
    Saves request response to a file for debugging
    :param url_address:
    :param ext:
    :param r:
    :return:
    """
    base_name = url_address.split('/')[-1]
    if save:
        base_name = save + '/' + base_name
    with open(base_name + ext, 'w') as file:
        file.write(r.text)
    with open(base_name + ext + ".h", 'w') as header:
        header.write("/!\\ REQUEST HEADERS: /!\\ \n")
        for k, v in r.request.headers.items():
            header.write(k + " : " + v + "\n")
        header.write("\n/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-\n\n")
        header.write("/!\\ RESPONSE HEADERS: /!\\ \n")
        for k, v in r.headers.items():
            header.write(k + " : " + v + "\n")


def write_error_file(url_address, ext, r):
    """
    Writes error files, used for debugging
    :param url_address:
    :param ext:
    :param r:
    :return:
    """
    base_name = url_address.split('/')[-1]
    base_name = save + '/' + base_name
    with open(base_name + ext + '.fail.txt', 'w') as file:
        file.write(f'Status: {r.status_code}\n')
        for header, values in r.headers.items():
            file.write(f'{header}: {values}\n')
        file.write('\n')
        file.write(f'Response: {r.text}\n')


def parse_variables(dmr_xml):
    """
    breaks all dmr vars into a list of variables
    :param dmr_xml:
    :return:
    """
    dmr_doc = parseString(dmr_xml)
    # get elements by types ( Byte, Int8[16,32,64], UInt8[16,32,64], Float32[64], String ) to find nodes
    variables = dmr_doc.getElementsByTagName("Byte")

    variables += dmr_doc.getElementsByTagName("Int8")
    variables += dmr_doc.getElementsByTagName("Int16")
    variables += dmr_doc.getElementsByTagName("Int32")
    variables += dmr_doc.getElementsByTagName("Int64")

    variables += dmr_doc.getElementsByTagName("UInt8")
    variables += dmr_doc.getElementsByTagName("UInt16")
    variables += dmr_doc.getElementsByTagName("UInt32")
    variables += dmr_doc.getElementsByTagName("UInt64")

    variables += dmr_doc.getElementsByTagName("Float32")
    variables += dmr_doc.getElementsByTagName("Float64")

    variables += dmr_doc.getElementsByTagName("String")

    return variables


def build_subset_postfix(var):
    var_path = build_leaf_path(var)
    postfix = '.dap?dap4.ce=/' + var_path
    dims = var.getElementsByTagName("Dim")
    # So, ‘[’ is %5B and ‘]’ is %5D in this scheme. If you take
    for d in dims:
        postfix += "%5B0%5D"

    return postfix


def build_leaf_path(var):
    """
    builds the path from a leaf back to the root
    :param var:
    :return:
    """
    path = var.getAttribute("name")
    # print(path)
    if var.parentNode.nodeName != "Dataset":
        if var.parentNode.nodeName == "Group":
            path = build_leaf_path(var.parentNode) + '/' + path
        elif var.parentNode.nodeName == "Structure":
            path = build_leaf_path(var.parentNode) + '.' + path
        elif var.parentNode.nodeName == "Sequence":
            path = build_leaf_path(var.parentNode) + '.' + path
        # print(path)
    return path


def url_test_runner(url, dmr=True, dap=True, dap_vars=True, nc4=False):
    """
    Common access point for all the tests.
    """

    s.headers = pydmr_headers()
    results = []
    if dmr:
        dmr_results = dmr_tester(url)
        results.append(dmr_results)
        if dap and dmr_results.status == "pass":
            dap_results = dap_tester(url)
            results.append(dap_results)
            if dap_vars and dap_results.status == "fail":
                var_results = var_tester(url)
                for r in var_results:
                    results.append(r)

    return results


def print_results(results):
    """
    Takes results and outputs it to the terminal
    used for debugging
    :param results:
    :return:
    """
    print()
    print("----- Results -----")
    dmr_results = results["dmr"]
    print(dmr_results["dmr_test"].result + " | " + str(dmr_results["dmr_test"].status) + " | dmr_test")

    if results["dap"] != "NA" and dmr_results["dmr_test"].result == "pass":
        dap_results = results["dap"]  # getting the dap inner dictionary from outer dictionary
        print(dap_results["dap_test"].result + " - " + dap_results["dap_test"].payload + " | " +
              str(dap_results["dap_test"].status) + " | dap_test")

        if results["dap_vars"] != "NA":
            var_results = results["vars"]
            keys = var_results.keys()
            for k in keys:
                print(var_results[k].result + " | " + str(var_results[k].status) + " | " + k)
    print("/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/")


def main():
    import argparse

    try:
        # results = url_test_runner("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        # print_results(results)

        # structure unit_tests
        # results = url_test_runner("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc")
        # print_results(results)

        # group unit_tests, few variables
        # results = url_test_runner("http://test.opendap.org/opendap/data/hdf5/grid_1_2d.h5")
        results = url_test_runner("http://test.opendap.org:8080/opendap/NSIDC/ATL03_20181027044307_04360108_002_01.h5")
        print_results(results)

        # results = url_test_runner("http://test.opendap.org/opendap/data/ff/avhrr.dat")  # sequence unit_tests
        # print_results(results)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
