#!/usr/bin/env python3

"""
Simple test driver for all Collections held by a NASA DAAC that have OPeNDAP
URLS in the CMR catalog system. The test driver runs a suite of tests on the
oldest and newest granules in each collection.

Now supports limit concurrency via futures. Several collections can be tested
at once.

The output of this test driver is an XML document that can be used as a document
in its own right or rendered as an HTML web page.
"""

import xml.dom.minidom as minidom
import time
import concurrent.futures
import os

import cmr
import opendap_tests


"""
Global variables. These ease getting values into functions that will be
run using a ThreadExecutor.
"""
verbose: bool = False   # Verbose output here and in cmr.py
pretty: bool = False    # Ask CMR for formatted JSON responses


def test_one_collection(ccid, title):
    """
    For one collection, run all the configured tests
    :param: ccid: The collection concept Id
    :param: title: The collections title
    :param: verbose: Should the verbose mode of the cmr.py module be used?
    :param: pretty: Request CMR return nicely formatted JSON
    :return: A dictionary with ccid as key and the title and collected test
        tuple results as a value. The collected results are also a dictionary
        that holds the GID and yet another python dict of tests and their status.
        E.G: {CCID: (<title>, {G2224035357-POCLOUD: (URL, {'dmr': 'pass', 'dap': 'NA', 'netcdf4': 'NA'}), ... } ) }
    """
    # For each collection...
    print(f'testing {ccid}: {title}') if verbose else ''

    try:
        first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=pretty)
    except cmr.CMRException as e:
        return {ccid: (title, {"error": e.message})}

    collected_results = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_gid = {executor.submit(opendap_tests.url_test_runner, granule_tuple[1], True, False, False): gid
                         for gid, granule_tuple in first_last_dict.items()}
        for future in concurrent.futures.as_completed(future_to_gid):
            gid = future_to_gid[future]
            try:
                test_results = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (gid, exc))
            else:
                print(f'{gid}: {test_results}') if verbose else ''
                # first_last_dict[gid][1] is the URL we tested
                collected_results[gid] = (first_last_dict[gid][1], test_results)

    # for gid, granule_tuple in first_last_dict.items():
    #     # The granule_tuple is the granule title and opendap url
    #     test_results = opendap_tests.url_test_runner(granule_tuple[1], True, False, False)
    #     print(f'{gid}: {test_results}') if verbose else ''
    #     collected_results[gid] = (granule_tuple[1], test_results)

    return {ccid: (title, collected_results)}


def write_xml_document(provider, version, results):
    """
    Write the collected results in an XML document.

    The format of 'results' is:
    {CCID: (<title>,
            {G2224035357-POCLOUD: (URL, {'dmr': 'pass', 'dap': 'NA', 'netcdf4': 'NA'}),
            ... }
           ),
    ... }
    But, it might contain an error, like this:
    {'C1371013470-GES_DISC': ('SRB/GEWEX evapotranspiration (Penman-Monteith) L4 3 hour 0.5 degree x 0.5 degree V1 (WC_PM_ET_050) at GES DISC',
                              {'error': 'Expected one response item from CMR, got 0 while asking about C1371013470-GES_DISC'}
                              )
    }

    :param: provider: The name of the Provider as it appears in CMR.
    :param: version: The version number to use when naming the XML document.
    :param: results: a mess of dicts and tuples.
    """
    # make the response document
    # TODO Write an <Error ...> element if there are no entries.
    #  Same for the Collection and Test elements. jhrg 11/22/22
    root = minidom.Document()
    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for ccid in results.keys():
        title = results[ccid][0];
        # XML element for the collection
        collection = root.createElement('Collection')
        collection.setAttribute('ccid', ccid)
        collection.setAttribute('long_name', title)
        prov.appendChild(collection)

        # Add XML for all the tests we ran
        granule_results = results[ccid][1];
        # {G2224035357-POCLOUD: (URL, {'dmr': 'pass', 'dap': 'NA', 'netcdf4': 'NA'}), ...}
        for gid, tests in granule_results.items():
            if gid == "error":
                test = root.createElement('Error')
                test.setAttribute('message', tests)
                collection.appendChild(test)
            else:
                url = tests[0]
                for name, result in tests[1].items():
                    if result != "NA":
                        test = root.createElement('Test')
                        test.setAttribute('name', name)
                        test.setAttribute('url', url)
                        test.setAttribute('result', result)
                        collection.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    time.strftime("%d.%m.%Y")
    save_path_file = provider + time.strftime("-%m.%d.%Y-") + version + ".xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", help="quiet the tests. By default print a dot for each test run",
                        action="store_true", default=False)
    parser.add_argument("-s", "--save", help="directory to hold the test responses. Make the directory if needed.",
                        default='')
    # parser.add_argument("-l", "--limit", help="limit the number of tests to the first N collections."
    #                    "By default, run all the tests.", action="store_true", default=0)

    parser.add_argument("-d", "--dmr", help="Test getting the DMR response", action="store_true", default=True)
    parser.add_argument("-D", "--dap", help="Test getting the DAP response", action="store_true")
    parser.add_argument("-n", "--netcdf4", help="Test getting the NetCDF4 file response", action="store_true")

    parser.add_argument("-V", "--version", help="increase output verbosity", default="1")
    parser.add_argument("-w", "--workers", help="if concurrent (the default), set the number of workers (default: 5)",
                        default=5, type=int)
    parser.add_argument("-c", "--concurrent", help="run the tests concurrently", default=True,
                        action=argparse.BooleanOptionalAction)

    group = parser.add_mutually_exclusive_group(required=True)   # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")

    args = parser.parse_args()

    # These are here mostly to get the values of verbose and pretty into test_one_collection()
    # which is run below using a ThreadPoolExecutor and map()
    global verbose
    verbose = args.verbose
    global pretty
    pretty = args.pretty

    cmr.verbose = args.verbose

    opendap_tests.quiet = args.quiet
    opendap_tests.save = args.save
    if args.save != '' and not os.path.exists(opendap_tests.save):
        os.mkdir(opendap_tests.save)

    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)

        # For each collection...
        results = dict()
        if args.concurrent:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                #result_list = executor.map(test_one_collection, entries.keys(), entries.values())
                #result_list = map(lambda x: executor.submit(test_one_collection, x), entries.keys(), entries.values())
                result_list = {executor.submit(test_one_collection, key, entries[key]): key for key in entries}
                for result in concurrent.futures.as_completed(result_list):
                    try:
                        print(f'Result from test: {result}') if args.verbose else ''
                        results = cmr.merge_dict(results, result)
                    except Exception as exc:
                        print(f'Exception: {exc}')
        else:
            for ccid, title in entries.items():
                r = test_one_collection(ccid, title)
                results = cmr.merge_dict(results, r)

        duration = time.time() - start

        print(f'Total collections tested: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

        write_xml_document(args.provider, args.version, results)

    except cmr.CMRException as e:
        print(e)


if __name__ == "__main__":
    main()
