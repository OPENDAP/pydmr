
"""
A collection of tests for OPeNDAP URLs packaged as functions.
"""

import requests

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
    Take a url and test whether the server can return its DMR response

    :param: url_address: The url to be checked
    :return: A pass/fail of whether the url passes
    """
    dmr_check = False
    try:
        print(".", end="", flush=True) if not quiet else False
        r = requests.get(url_address + ext)
        if r.status_code == 200:
            dmr_check = True
            # Save the response?
            if save_all:
                base_name = url_address.split('/')[-1]
                if save:
                    base_name = save + '/' + base_name
                with open(base_name + ext, 'w') as file:
                    file.write(r.text)
        else:
            print("F", end="", flush=True) if not quiet else False
            base_name = url_address.split('/')[-1]
            if save:
                base_name = save + '/' + base_name
            with open(base_name + ext + '.fail', 'w') as file:
                file.write(f'Status: {r.status_code}: {r.text}')

    # Ignore exception, the url_tester will return 'fail'
    except requests.exceptions.InvalidSchema:
        pass

    if dmr_check:
        return "pass"
    else:
        return "fail"


def url_test_runner(url, dmr=True, dap=False, nc4=False):
    """
    Common access point for all the tests.
    """
    test_results = {"dmr": url_tester_ext(url) if dmr else "NA",
                    "dap": url_tester_ext(url, '.dap') if dap else "NA",
                    "netcdf4": url_tester_ext(url, '.dap.nc4') if nc4 else "NA"}
    return test_results

