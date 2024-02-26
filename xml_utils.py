
import xml.dom.minidom as minidom
import time
import os

verbose: bool = False  # Verbose output here and in cmr.py
detail_xsl = "/NGAP-PROD-tests/details.v2.xsl"
summary_xsl = "/NGAP-PROD-tests/home.v2.xsl"


def write_xml_documents(environment, path, version, results):
    print("write_xml_documents start")

    if results.misc_results:
        path = write_misc_doc(results.provider, version, results.misc_results)
        results.misc_path = path

    if results.dmr_results:
        path = write_dmr_doc(results.provider, version, results.dmr_results)
        results.dmr_path = path

    if results.dap_results:
        path = write_dap_doc(results.provider, version, results.dap_results)
        results.dap_path = path

    if results.dap_var_results:
        path = write_var_doc(results.provider, version, results.dap_var_results)
        results.dap_var_path = path

    if results.netcdf_results:
        path = write_netcdf_doc(results.provider, version, results.netcdf_results)
        results.netcdf_path = path

    update_summary(environment, path, results.provider, version, results)


def write_misc_doc(provider, version, misc_list):
    print("write_misc start")
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for item in misc_list:
        test = create_attribute(root, item.type, item)
        prov.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".err.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return save_path_file


def write_dmr_doc(provider, version, dmr_list):
    print("write_dmr start")
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for item in dmr_list:
        test = create_attribute(root, "Test", item)
        prov.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".dmr.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return save_path_file


def write_dap_doc(provider, version, dap_list):
    print("write_dap start")
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for item in dap_list:
        test = create_attribute(root, "Test", item)
        prov.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".dap.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return save_path_file


def write_var_doc(provider, version, var_list):
    print("write_var start")
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for item in var_list:
        test = create_attribute(root, "Test", item)
        prov.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".var.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return save_path_file


def write_netcdf_doc(provider, version, netcdf_list):
    print("write_netcdf start")
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    root.appendChild(prov)

    for item in netcdf_list:
        test = create_attribute(root, "Test", item)
        prov.appendChild(test)

    # Save the XML
    xml_str = root.toprettyxml(indent="\t")
    directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
    isExist = os.path.exists(directory)
    if not isExist:
        os.makedirs(directory)

    save_path_file = directory + provider + time.strftime("-%m.%d.%Y-") + version + ".net.xml"
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return save_path_file


def update_summary(environment, path, provider, version, results):
    print("update start")
    # make the response document
    root = minidom.parse(path)
    pros = root.getElementsByTagName('Provider')
    pro = None
    for p in pros:
        if p.getAttribute('name') == provider:
            pro = p
            break

    if results.misc_results:
        misc = root.createElement('Error')
        misc.setAttribute('url', results.misc_path)
        misc.setAttribute('total', str(results.misc_total))
        misc.setAttribute('error', str(results.error_count))
        misc.setAttribute('info', str(results.info_count))
        pro.appendChild(misc)

    if results.dmr_results:
        dmr = root.createElement('Test')
        dmr.setAttribute('url', results.dmr_path)
        dmr.setAttribute('total', results.dmr_total)
        dmr.setAttribute('pass', results.dmr_pass)
        dmr.setAttribute('fail', results.dmr_fail)
        pro.appendChild(dmr)

    if results.dap_results:
        dap = root.createElement('Test')
        dap.setAttribute('url', results.dap_path)
        dap.setAttribute('total', results.dap_total)
        dap.setAttribute('pass', results.dap_pass)
        dap.setAttribute('fail', results.dap_fail)
        pro.appendChild(dap)

    if results.dap_var_results:
        dap_var = root.createElement('Test')
        dap_var.setAttribute('url', results.dap_var_path)
        dap_var.setAttribute('total', results.dap_var_total)
        dap_var.setAttribute('pass', results.dap_var_pass)
        dap_var.setAttribute('fail', results.dap_var_fail)
        pro.appendChild(dap_var)

    if results.netcdf_results:
        netcdf = root.createElement('Test')
        netcdf.setAttribute('url', results.netcdf_path)
        netcdf.setAttribute('total', results.netcdf_total)
        netcdf.setAttribute('pass', results.netcdf_pass)
        netcdf.setAttribute('fail', results.netcdf_fail)
        pro.appendChild(netcdf)

    xml_str = root.toprettyxml(indent="\t")
    with open(path, "wb") as f:
        f.write(xml_str)


def create_attribute(root, name, result):
    """
    Sub-function for write_xml_document(...)
    Creates a Xml attribute for xml document

    :param root:    Root of the xml document
    :param name:    test result type ('dmr', 'dap', 'dap_vars', 'message')
    :param url:     url of the file that was tested
    :param result:  result of the test
    :return:
    """
    test = root.createElement(name)
    #  collection level information
    test.setAttribute('ccid', result.ccid)
    test.setAttribute('title', result.title)
    #  granule level information
    test.setAttribute('gid', result.gid)
    test.setAttribute('url', result.url)
    #  test results
    test.setAttribute('type', result.type)
    test.setAttribute('status', result.status)
    test.setAttribute('code', str(result.code))
    test.setAttribute('payload', result.payload)
    return test

