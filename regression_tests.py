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

import xml.dom.minidom as minidom
import time
import concurrent.futures
import os
import itertools

import cmr
import opendap_tests

"""
Global variables. These ease getting values into functions that will be
run using a ThreadExecutor.
"""
verbose: bool = False  # Verbose output here and in cmr.py
pretty: bool = False  # Ask CMR for formatted JSON responses
dmr: bool = True  # Three types of tests follow
dap: bool = False
netcdf4: bool = False
umm_json: bool = True  # Use the newer (correct) technique to get granule information
cloud_only: bool = True  # By default, only unit_tests URLs for the cloud. If False, unit_tests all the OPeNDAP URLs


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

    try:
        if umm_json:
            first_last_dict = cmr.get_collection_granules_umm_first_last(ccid, pretty=pretty)
        else:
            first_last_dict = cmr.get_collection_granules_first_last(ccid, pretty=pretty)

    # unit_tests for cloud URLs here - throw but make it a warning? jhrg 1/25/23
    except cmr.CMRException as e:
        return {ccid: (title, {"error": e.message})}

    # Test for cloud URLs and return an 'info' response if they are not present.
    # What if there is one on-premises and one cloud URL?  For now, all the URLs
    # must be cloud URLs if 'cloud_only' is true. jhrg 1/25/23
    if cloud_only and not has_only_cloud_opendap_urls(first_last_dict):
        return {ccid: (title, {"info": f'Testing only data in the cloud but found one or more URLs '
                                       f'to data not in the cloud: {formatted_urls(first_last_dict)}'})}

    collected_results = dict()
    # future_to_gid = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # future_to_gid is a dictionary where the key is a future that will return
        # the results of running tests on a granule and the value is the granule's concept ID
        future_to_gid = {executor.submit(opendap_tests.url_test_runner, granule_tuple[1], dmr, dap, netcdf4): gid
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

    if collected_results.items() is None:
        return {}
    else:
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
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='/NGAP-PROD-tests/details.xsl'")
    root.appendChild(xsl_element)

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
            elif gid == "info":
                test = root.createElement('Info')
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

    parser.add_argument("-d", "--dmr", help="Test getting the DMR response", action="store_true", default=True)
    parser.add_argument("-D", "--dap", help="Test getting the DAP response", action="store_true")
    parser.add_argument("-n", "--netcdf4", help="Test getting the NetCDF4 file response", action="store_true")

    parser.add_argument("-V", "--version", help="increase output verbosity", default="1")
    parser.add_argument("-w", "--workers", help="if concurrent (the default), set the number of workers (default: 5)",
                        default=5, type=int)
    # Use --no-concurrency to run the tests serially.
    parser.add_argument('-c', '--concurrency', help="run the tests concurrently", default=True, action='store_true')
    parser.add_argument('--no-concurrency', dest='concurrency', action='store_false')
    # Requires Python 3.10.x which has its own set of issues
    # parser.add_argument("-c", "--concurrency", help="run the tests concurrently", default=True,
    #                     action=argparse.BooleanOptionalAction)

    group = parser.add_mutually_exclusive_group(required=True)  # only one option in 'group' is allowed at a time
    group.add_argument("-p", "--provider", help="a provider id, by itself, print all the providers collections")

    args = parser.parse_args()

    # These are here mostly to get the values of verbose and pretty into test_one_collection()
    # which is run below using a ThreadPoolExecutor and map()
    global verbose
    verbose = args.verbose
    global pretty
    pretty = args.pretty
    global dmr
    dmr = args.dmr
    global dap
    dap = args.dap
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

    try:
        start = time.time()

        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(args.provider, opendap=True, pretty=args.pretty)

        # Truncate the entries if --limit is used
        # NB: itertools.islice(sequence, start, stop, step) or itertools.islice(sequence, stop)
        if args.limit > 0:
            entries = dict(itertools.islice(entries.items(), args.limit))

        # For each collection...
        results = dict()
        if args.concurrency:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                result_list = executor.map(test_one_collection, entries.keys(), entries.values())
                for result in result_list:
                    try:
                        print(f'Result from unit_tests: {result}') if args.verbose else ''
                        results = cmr.merge_dict(results, result)
                    except Exception as exc:
                        print(f'Exception: {exc}')
        else:
            for ccid, title in entries.items():
                r = test_one_collection(ccid, title)
                results = cmr.merge_dict(results, r)

        duration = time.time() - start

        print(f'\nTotal collections tested: {len(entries)}') if len(entries) > 1 else ''
        print(f'Request time: {duration:.1f}s') if args.time else ''

        write_xml_document(args.provider, args.version, results)

    except cmr.CMRException as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
