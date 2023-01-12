
"""
A collection of tests for OPeNDAP URLs packaged as functions.
"""

import requests
from xml.dom.minidom import parse, parseString

"""
set 'quiet' in main(), etc., and it affects various functions

set 'save' to save the results of the access operations. If the value is
not null then the results are saved and the value of 'save' is the name of
a subdir where the outputs are stored
"""
quiet: bool = False
save_all: bool = False
save: str = ''

dmr_xml: str = ''


def url_tester_ext(url_address, ext='.dmr'):
    """
    Take an url and test whether the server can return its DMR response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """
    check = False
    global dmr_xml
    try:
        print(".", end="", flush=True) if not quiet else False
        r = requests.get(url_address + ext)
        if r.status_code == 200:
            dmr_xml = r.text
            # save the url for dap tests here
            check = True
            # Save the response?
            if save_all:
                base_name = url_address.split('/')[-1]
                if save:
                    base_name = save + '/' + base_name
                with open(base_name + ext, 'w') as file:
                    file.write(r.text)
        else:
            print("F", end="", flush=True) if not quiet else False
            check = False
            base_name = url_address.split('/')[-1]
            if save:
                base_name = save + '/' + base_name
            with open(base_name + ext + '.fail.txt', 'w') as file:
                file.write(f'Status: {r.status_code}\n')
                for header, values in r.headers.items():
                    file.write(f'{header}: {values}\n')
                file.write('\n')
                file.write(f'Response: {r.text}\n')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    if check:
        return "pass"
    else:
        return "fail"


def var_tester(url_address):
    """
    Take an url and test whether the server can return its DAP response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """
    check = False
    try:
        print("|", end="", flush=True) if not quiet else False
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

        results = {url_address: "data file"}
        for v in variables:
            print(".", end="", flush=True) if not quiet else False
            t = build_leaf_path(v)
            dap_url = url_address + '.dap?dap4.ce=/' + t
            #  print(dap_url)
            dap_r = requests.get(dap_url)
            if dap_r.status_code == 200:
                results[dap_url] = "pass"
                # Save the response?
                if save_all:
                    base_name = url_address.split('/')[-1]
                    if save:
                        base_name = save + '/' + base_name
                    with open(base_name + '.dap', 'w') as file:
                        file.write(dap_r.text)
            else:
                print("F", end="", flush=True) if not quiet else False
                results[dap_url] = "fail"
                base_name = url_address.split('/')[-1]
                if save:
                    base_name = save + '/' + base_name
                with open(base_name + '.dap' + '.fail.txt', 'w') as file:
                    file.write(f'Status: {dap_r.status_code}: {dap_r.text}')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    return results


def build_leaf_path (var):
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


def url_test_runner(url, dmr=True, dap=True, nc4=False):
    """
    Common access point for all the tests.
    """
    if dmr:
        dmr_results = url_tester_ext(url)
        if dap and dmr_results == "pass":
            dap_results = var_tester(url)
        else:
            dap = False

    test_results = {"dmr": dmr_results if dmr else "NA",
                    "dap": dap_results if dap else "NA",
                    "netcdf4": url_tester_ext(url, '.dap.nc4') if nc4 else "NA"}

    return test_results


def print_results(results):
    print()
    print("----- Results -----")
    dmr_results = results["dmr"]
    print(dmr_results + " | dmr test")

    if dmr_results == "pass":
        dap_results = results["dap"]
        keys = dap_results.keys()
        for k in keys:
            print(dap_results[k] + " | " + k)
    print("/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/")


def main():
    import argparse

    try:

        results = url_test_runner("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        print_results(results)

        results = url_test_runner("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc")  # structure test
        print_results(results)

        results = url_test_runner("http://test.opendap.org/opendap/data/hdf5/grid_1_2d.h5")  # group test, few variables
        # var_tester("http://test.opendap.org:8080/opendap/NSIDC/ATL03_20181027044307_04360108_002_01.h5")  # group test
        print_results(results)

        results = url_test_runner("http://test.opendap.org/opendap/data/ff/avhrr.dat")  # sequence test
        print_results(results)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()