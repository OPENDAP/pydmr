
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


def url_tester_ext(url_address, ext='.dmr'):
    """
    Take an url and test whether the server can return its DMR response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """
    dmr_check = False
    try:
        print(".", end="", flush=True) if not quiet else False
        r = requests.get(url_address + ext)
        if r.status_code == 200:
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
        print(".", end="", flush=True) if not quiet else False
        r = requests.get(url_address + '.dmr')
        if r.status_code == 200:
            check = True
            # Save the response?
            if save_all:
                base_name = url_address.split('/')[-1]
                if save:
                    base_name = save + '/' + base_name
                with open(base_name + '.dmr', 'w') as file:
                    file.write(r.text)

            dmr_doc = parseString(r.text)
            # get elements by types ( Byte, Int8[16,32,64], UInt8[16,32,64], Float32[64], String ) to find nodes
            variables = dmr_doc.getElementsByTagName("Int32")
            # variables = dmr_doc.getElementsByTagName("Float32")
            # variables = dmr_doc.getElementsByTagName("Float64")
            variables += dmr_doc.getElementsByTagName("String")
            for v in variables:
                t = build_leaf_path(v)
                dap_url = url_address + '.dap?dap4.ce=/' + t
                print(dap_url)
                dap_r = requests.get(dap_url)
                if dap_r.status_code == 200:
                    print("success [*fireworks*]")
                    check = True
                    # Save the response?
                    if save_all:
                        base_name = url_address.split('/')[-1]
                        if save:
                            base_name = save + '/' + base_name
                        with open(base_name + '.dap', 'w') as file:
                            file.write(r.text)
                else:
                    print("failure [sad noises]")
                    print("F", end="", flush=True) if not quiet else False
                    base_name = url_address.split('/')[-1]
                    if save:
                        base_name = save + '/' + base_name
                    with open(base_name + '.dmr' + '.fail.txt', 'w') as file:
                        file.write(f'Status: {r.status_code}: {r.text}')
        else:
            print("F", end="", flush=True) if not quiet else False
            base_name = url_address.split('/')[-1]
            if save:
                base_name = save + '/' + base_name
            with open(base_name + '.dmr' + '.fail.txt', 'w') as file:
                file.write(f'Status: {r.status_code}: {r.text}')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    if check:
        return "pass"
    else:
        return "fail"


def build_leaf_path (var):
    path = var.getAttribute("name")
    print(path)
    if var.parentNode.nodeName != "Dataset":
        if var.parentNode.nodeName == "Group":
            path = build_leaf_path(var.parentNode) + '/' + path
        elif var.parentNode.nodeName == "Structure":
            path = build_leaf_path(var.parentNode) + '.' + path
        elif var.parentNode.nodeName == "Sequence":
            path = build_leaf_path(var.parentNode) + '.' + path
        print(path)
    return path


def url_test_runner(url, dmr=True, dap=False, nc4=False):
    """
    Common access point for all the tests.
    """
    test_results = {"dmr": url_tester_ext(url) if dmr else "NA",
                    "dap": url_tester_ext(url, '.dap') if dap else "NA",
                    "netcdf4": url_tester_ext(url, '.dap.nc4') if nc4 else "NA"}
    var_results = {"vars": var_tester(url)}
    return test_results


def main():
    import argparse

    try:

        # var_tester("http://test.opendap.org/opendap/data/dmrpp/chunked_fourD.h5")
        # var_tester("http://test.opendap.org/opendap/nc4_test_files/ref_tst_compounds.nc")  # structure test
        # var_tester("http://test.opendap.org:8080/opendap/NSIDC/ATL03_20181027044307_04360108_002_01.h5")  # group test
        var_tester("http://test.opendap.org/opendap/data/ff/avhrr.dat")  # sequence test

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()