#!/usr/bin/env python3

"""
Simple unit_tests driver for all Collections held by a NASA DAAC that have OPeNDAP
URLS in the CMR catalog system. The unit_tests driver runs a suite of tests on the
oldest and newest granules in each collection.

Now supports limit concurrency via futures. Several collections can be tested
at once.

The output of this unit_tests driver is an XML document that can be used as a document
in its own right or rendered as an HTML web page.
"""
import math
import xml.dom.minidom as minidom
import time
import concurrent.futures
import os
import itertools

import requests.exceptions

import cmr
import errLog
import opendap_tests
import testing_results as tr
import xml_utils as xu

"""
Global variables. These ease getting values into functions that will be
run using a ThreadExecutor.
"""
verbose: bool = False  # Verbose output here and in cmr.py
pretty: bool = False  # Ask CMR for formatted JSON responses
dmr: bool = True  # Three types of tests follow
dap: bool = False
dap_var: bool = False
netcdf4: bool = False
umm_json: bool = True  # Use the newer (correct) technique to get granule information
cloud_only: bool = True  # By default, only unit_tests URLs for the cloud. If False, unit_tests all the OPeNDAP URLs

request_timeout: int = 60


def is_opendap_cloud_url(url) -> bool:
    """
    :returns: True if the URL references the OPeNDAP NASA cloud server
    """
    return "opendap.earthdata.nasa.gov" in url


def has_only_cloud_opendap_urls(first_last_dict) -> bool:
    """
    :param first_last_dict: Dictionary of the form {ID1 : (Title1, URL1), ID2 : (Title2, URL2)}
    :returns: True if all the URLs in the dictionary satisfy is_opendap_cloud_url()
    """
    # for value in first_last_dict.values():
    #     if not is_opendap_cloud_url(value[1]):
    #         return False
    # return True
    return all(is_opendap_cloud_url(value[1]) for value in first_last_dict.values())


def formatted_urls(first_last_dict) -> str:
    """
    Extract the URLs from the first_last_dict and return them as a single
    string of CSVs.
    :param first_last_dict: Dictionary of the form {ID1 : (Title1, URL1), ID2 : (Title2, URL2)}
    :returns: A formatted string
    """
    # urls = []
    # for value in first_last_dict.values():
    #     urls.append(value[1])
    # return ", ".join(urls)
    return ", ".join(value[1] for value in first_last_dict.values())


def test_one_collection(ccid, title):
    """
    For one collection, run all the configured tests. If no URLs are found, then an
    error response is returned (not an exception, but a dictionary with an 'error'
    message. If the global 'cloud_only' is true (indicating the caller only want to
    unit_tests URLs for data in the cloud) but one or more non-cloud URLs are returned,
    an 'info' message is returned that includes the URLs.

    :param: ccid: The collection concept ID
    :param: title: The collections title
    :param: verbose: Should the verbose mode of the cmr.py module be used?
    :param: pretty: Request CMR return nicely formatted JSON
    :return: A dictionary with ccid as key and the title and collected unit_tests
        tuple results as a value. The collected results are also a dictionary
        that holds the GID and yet another python dict of tests and their status.
        E.G: {CCID: (<title>, {G2224035357-POCLOUD: (URL, {'dmr': 'pass', 'dap': 'NA', 'netcdf4': 'NA'}), ... } ) }
    """
    # For each collection...
    print(f'{ccid}: {title}') if verbose else ''
    collected_results = []

    try:
        if umm_json:
            first_last_dict = cmr.get_collection_granules_umm_first_last(ccid, pretty=pretty)
        else:
            first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=pretty)

    # unit_tests for cloud URLs here - throw but make it a warning? jhrg 1/25/23
    except cmr.CMRException as e:
        err_tr = tr.Result("Error", "error", 500)
        err_tr.addcollection(ccid, title)
        err_tr.payload = e.message
        collected_results.append(err_tr)
        return collected_results

    # Test for cloud URLs and return an 'info' response if they are not present.
    # What if there is one on-premises and one cloud URL?  For now, all the URLs
    # must be cloud URLs if 'cloud_only' is true. jhrg 1/25/23
    if cloud_only and not has_only_cloud_opendap_urls(first_last_dict):
        err_tr = tr.Result("Info", "info", 500)
        err_tr.addcollection(ccid, title)
        err_tr.payload = (f'Testing only data in the cloud but found one or more URLs to data not in the cloud: '
                          f'{formatted_urls(first_last_dict)}')
        collected_results.append(err_tr)
        return collected_results

    # future_to_gid = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        try:
            # future_to_gid is a dictionary where the key is a future that will return
            # the results of running tests on a granule and the value is the granule's concept ID
            future_to_gid = {executor.submit(opendap_tests.url_test_runner, granule_tuple[1], dmr, dap, dap_var, netcdf4): gid
                             for gid, granule_tuple in first_last_dict.items()}

            for future in concurrent.futures.as_completed(future_to_gid, timeout=request_timeout):
                    gid = future_to_gid[future]
                    try:
                        test_results = future.result()
                    except Exception as exc:
                        print('\n%r generated an exception: %s\n' % (gid, exc))
                    else:
                        print(f'{gid}: {test_results}\n') if verbose else ''
                        # first_last_dict[gid][1] is the URL we tested
                        for r in test_results:
                            r.gid = gid
                            r.addcollection(ccid, title)
                            collected_results.append(r)

        except concurrent.futures.TimeoutError as exc:
            # print(f"\nOpendap_tests took to long... {exc}")  # It suspends infinitely.
            err_tr = tr.Result("Error", "timeout", 408)
            err_tr.addcollection(ccid, title)
            err_tr.payload = f"Request timed out after {request_timeout} seconds."
            collected_results.append(err_tr)

    if not collected_results:
        err_tr = tr.Result("Error", "empty", 500)
        err_tr.addcollection(ccid, title)
        err_tr.payload = "No results collected"
        collected_results.append(err_tr)
        return collected_results
    else:
        return collected_results


def run_provider_tests(args):
    """
    Retrieves all collections for given provider
        then runs test_one_collection on each collection in list
        once all results are in, writes all results to a xml document

    :param args: all args used when calling 'main'
    :return:
    """
    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)
        total = len(entries)

        # Truncate the entries if --limit is used
        # NB: itertools.islice(sequence, start, stop, step) or itertools.islice(sequence, stop)
        if args.limit > 0:
            entries = dict(itertools.islice(entries.items(), args.limit))

        # For each collection...
        #  results = dict()
        results = tr.TestResults(args.provider)
        done = 0
        # timeout = len(entries) * request_timeout
        # min = math.trunc(timeout / 60)
        # sec = timeout % 60
        # print(f"\tProvider timeout: {min}m {sec}s @ {request_timeout} seconds per")
        if args.concurrency:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                try:
                    result_list = executor.map(test_one_collection, entries.keys(), entries.values(), timeout=600)
                    for result in result_list:
                        try:
                            print(f'Result from unit_tests: {result}') if args.verbose else ''
                            done += 1
                            print_progress(done, total)
                            results.sort(result)
                        except Exception as exc:
                            print(f'Exception: {exc}\n')
                except concurrent.futures.TimeoutError as exc:
                    print(f"\ntest_one_collection took to long... {exc}")  # It suspends infinitely.

        else:
            for ccid, title in entries.items():
                r = test_one_collection(ccid, title)
                done += 1
                print_progress(done, total)
                results.sort(r)
                #  results = cmr.merge_dict(results, r)

        duration = time.time() - start

        print(f'\n\tTotal collections tested: {done}') if done > 1 else ''
        print(f'\tRequest time: {duration:.1f}s') if args.time else ''

        results.set_runs(done, len(entries), str(round(duration, 1)))

        xu.write_xml_documents(args.path, args.version, results)

    except cmr.CMRException as e:
        print(e)
    except requests.exceptions.ConnectionError:
        err = "/////////////////////////////////////////////////////\n"
        err += "ConnectionError : regression_tests.py::run_provider_tests()\n"
        errLog.output_errlog(err)
    except Exception as e:
        print(e)


def print_progress(amount, total):
    """
    outputs the progress bar to the terminal
    :param amount:
    :param total:
    :return:
    """
    percent = amount * 100 / total
    msg = "\t" + str(round(percent, 2)) + "% [ " + str(amount) + " / " + str(total) + " ] "
    print(msg, end="\r", flush=True)


def run_collection_test(args):
    """
    Takes the ccid of a collection and runs the test on it

    :param args:
    :return:
    """
    try:
        start = time.time()

        ccid = args.ccid
        results = tr.TestResults(args.providers)
        r = test_one_collection(ccid, "Single Collection Test")
        results.sort(r)
        try:
            print(f'Result from unit_tests: {results}') if args.verbose else ''
        except Exception as exc:
            print(f'Exception: {exc}')

        duration = time.time() - start

        print(f'Request time: {duration:.1f}s') if args.time else ''

        index = ccid.index("-") + 1
        provider = ccid[index:]
        print(f'Provider: {provider}') if args.verbose else ''
        xu.write_xml_documents(provider, args.version, results)

    except cmr.CMRException as e:
        print(e)
    except Exception as e:
        print(e)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", help="quiet the tests. By default print a dot for each unit_tests run",
                        action="store_true", default=False)
    parser.add_argument("-a", "--all", help="save the output from all the tests, including the ones that pass",
                        action="store_true", default=False)
    parser.add_argument("-s", "--save", help="directory to hold the unit_tests responses. Make the directory if needed.",
                        default='')
    parser.add_argument("-u", "--umm", help="Use the granules.umm_json query instead of the granules.json."
                                            "By default, this is true since it's the correct way to query CMR"
                                            "for information about OPeNDAP URLs to collections. The code"
                                            "used the non-umm json previously, which is less reliable. Use the"
                                            "option -no-umm to get the old behavior.",
                        action="store_true", default=True)
    parser.add_argument('--no-umm', dest='umm', action='store_false')
    parser.add_argument('-C', '--cloud', help="Only unit_tests URLs for data in the cloud. See --all-urls"
                                              "for a way to unit_tests all the URLs for a given provider. For some"
                                              "providers, this can take a long time since it will unit_tests all"
                                              "their on-premises collections",
                        default=True, action='store_true')
    parser.add_argument('--all-urls', dest='cloud', action='store_false')

    parser.add_argument("-l", "--limit", help="limit the number of tests to the first N collections."
                                              "By default, run all the tests.",
                        type=int, default=0)

    parser.add_argument("-d", "--dap", help="Test getting the DAP response", action="store_true", default=False)
    parser.add_argument("-D", "--dap_var", help="Test getting the DAP_var response", action="store_true", default=False)
    parser.add_argument("--no-dap", dest="dap", help="Test getting the DAP response", action="store_false")
    parser.add_argument("-n", "--netcdf4", help="Test getting the NetCDF4 file response", action="store_true")

    parser.add_argument("-V", "--version", help="increase output verbosity", default="1")
    parser.add_argument("-w", "--workers", help="if concurrent (the default), set the number of workers (default: 5)",
                        default=5, type=int)
    # Use --no-concurrency to run the tests serially.
    parser.add_argument('-c', '--concurrency', help="run the tests concurrently", default=True, action='store_true')
    parser.add_argument('--no-concurrency', dest='concurrency', action='store_false')
    parser.add_argument("-x", "--path", help="path to the summary page")

    group = parser.add_mutually_exclusive_group(required=True)  # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")
    group.add_argument("-i", "--ccid", help="a collection id (ccid), by itself, print the single collection")

    args = parser.parse_args()

    # These are here mostly to get the values of verbose and pretty into test_one_collection()
    # which is run below using a ThreadPoolExecutor and map()
    global verbose
    verbose = args.verbose
    global pretty
    pretty = args.pretty
    global dap
    dap = args.dap
    global dap_var
    dap_var = args.dap_var
    global netcdf4
    netcdf4 = args.netcdf4
    global umm_json
    umm_json = args.umm
    global cloud_only
    cloud_only = args.cloud

    cmr.verbose = args.verbose

    opendap_tests.quiet = args.quiet
    opendap_tests.save_all = args.all
    opendap_tests.save = args.save
    if args.save != '' and not os.path.exists(opendap_tests.save):
        os.mkdir(opendap_tests.save)

    if args.provider is not None:
        run_provider_tests(args)
    elif args.ccid is not None:
        run_collection_test(args)


if __name__ == "__main__":
    main()
