
import xml.dom.minidom as minidom
import time
import os

verbose: bool = False  # Verbose output here and in cmr.py


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
        # {G2224035357-POCLOUD: (URL, {'dmr': 'pass',
        #                               'dap': 'NA',
        #                               'netcdf4': 'NA'}), ...}
        # ..G2599786095-POCLOUD: {'dmr':
        #                               {'dmr_test': <opendap_tests.TestResult object at 0x7f06591abc88>},
        #                         'dap': 'NA',
        #                         'netcdf4': 'NA'}

        # for gid, tests in granule_results.items():
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
                    print(result) if verbose else ''
                    if result != "NA":
                        if name == "dmr":
                            test_result = result.get("dmr_test")
                            test = create_attribute(root, name, url, test_result)
                            collection.appendChild(test)
                        elif name == "dap":
                            test_result = result.get("dap_test")
                            test = create_attribute(root, name, url, test_result)
                            collection.appendChild(test)
                        elif name == "dap_vars":
                            for key, tr in result.items():
                                test = create_attribute(root, name, key, tr)
                                collection.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)


def create_attribute(root, name, url, result):
    """
    Sub-function for write_xml_document(...)
    Creates a Xml attribute for xml document

    :param root:    Root of the xml document
    :param name:    test result type ('dmr', 'dap', 'dap_vars', 'message')
    :param url:     url of the file that was tested
    :param result:  result of the test
    :return:
    """
    test = root.createElement('Test')
    test.setAttribute('name', name)
    test.setAttribute('url', url)
    test.setAttribute('result', result.result)
    test.setAttribute('status', str(result.status))
    return test

