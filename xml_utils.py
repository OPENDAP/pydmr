
import xml.dom.minidom as minidom
import time
import os

verbose: bool = False  # Verbose output here and in cmr.py
detail_xsl = "/NGAP-PROD-tests/details.v2.xsl"


def write_xml_documents(path, version, results):

    if results.misc_results:
        results.misc_path = write_misc_doc(results.provider, version, results.misc_results,
                                           str(results.misc_total), str(results.error_count), str(results.info_count))

    if results.dmr_results:
        results.dmr_path = write_dmr_doc(results.provider, version, results.dmr_results,
                                         str(results.dmr_total), str(results.dmr_pass), str(results.dmr_fail))

    if results.dap_results:
        results.dap_path = write_dap_doc(results.provider, version, results.dap_results,
                                         str(results.dap_total), str(results.dap_pass), str(results.dap_fail))

    if results.dap_var_results:
        results.dap_var_path = write_var_doc(results.provider, version, results.dap_var_results,
                                             str(results.dap_var_total), str(results.dap_var_pass),
                                             str(results.dap_var_fail))

    if results.netcdf_results:
        results.netcdf_path = write_netcdf_doc(results.provider, version, results.netcdf_results,
                                               str(results.netcdf_total), str(results.netcdf_pass),
                                               str(results.netcdf_fail))

    update_summary(path, results.provider, results)


def write_misc_doc(provider, version, misc_list, total, err, info):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    prov.setAttribute('total', total)
    prov.setAttribute('err_count', err)
    prov.setAttribute('info_count', info)
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

    url = provider + time.strftime("-%m.%d.%Y-") + version + ".err.xml"
    save_path_file = directory + url
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return url


def write_dmr_doc(provider, version, dmr_list, total, pas, fail):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    prov.setAttribute('total', total)
    prov.setAttribute('pass_count', pas)
    prov.setAttribute('fail_count', fail)
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

    url = provider + time.strftime("-%m.%d.%Y-") + version + ".dmr.xml"
    save_path_file = directory + url
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return url


def write_dap_doc(provider, version, dap_list, total, pas, fail):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    prov.setAttribute('total', total)
    prov.setAttribute('pass_count', pas)
    prov.setAttribute('fail_count', fail)
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

    url = provider + time.strftime("-%m.%d.%Y-") + version + ".dap.xml"
    save_path_file = directory + url
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return url


def write_var_doc(provider, version, var_list, total, pas, fail):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    prov.setAttribute('total', total)
    prov.setAttribute('pass_count', pas)
    prov.setAttribute('fail_count', fail)
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

    url = provider + time.strftime("-%m.%d.%Y-") + version + ".var.xml"
    save_path_file = directory + url
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return url


def write_netcdf_doc(provider, version, netcdf_list, total, pas, fail):
    # make the response document
    root = minidom.Document()

    xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                   "type='text/xsl' href='" + detail_xsl + "'")
    root.appendChild(xsl_element)

    prov = root.createElement('Provider')
    prov.setAttribute('name', provider)
    prov.setAttribute('date', time.asctime())
    prov.setAttribute('total', total)
    prov.setAttribute('pass_count', pas)
    prov.setAttribute('fail_count', fail)
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

    url = provider + time.strftime("-%m.%d.%Y-") + version + ".net.xml"
    save_path_file = directory + url
    with open(save_path_file, "w") as f:
        f.write(xml_str)

    return url


def update_summary(path, provider, results):
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
        dmr.setAttribute('name', 'DMR Tests')
        dmr.setAttribute('url', results.dmr_path)
        dmr.setAttribute('total', str(results.dmr_total))
        dmr.setAttribute('pass', str(results.dmr_pass))
        dmr.setAttribute('fail', str(results.dmr_fail))
        pro.appendChild(dmr)

    if results.dap_results:
        dap = root.createElement('Test')
        dap.setAttribute('name', 'DAP Tests')
        dap.setAttribute('url', results.dap_path)
        dap.setAttribute('total', str(results.dap_total))
        dap.setAttribute('pass', str(results.dap_pass))
        dap.setAttribute('fail', str(results.dap_fail))
        pro.appendChild(dap)

    if results.dap_var_results:
        dap_var = root.createElement('Test')
        dap_var.setAttribute('name', 'DAP Variable Tests')
        dap_var.setAttribute('url', results.dap_var_path)
        dap_var.setAttribute('total', str(results.dap_var_total))
        dap_var.setAttribute('pass', str(results.dap_var_pass))
        dap_var.setAttribute('fail', str(results.dap_var_fail))
        pro.appendChild(dap_var)

    if results.netcdf_results:
        netcdf = root.createElement('Test')
        netcdf.setAttribute('name', 'NETCDF Tests')
        netcdf.setAttribute('url', results.netcdf_path)
        netcdf.setAttribute('total', str(results.netcdf_total))
        netcdf.setAttribute('pass', str(results.netcdf_pass))
        netcdf.setAttribute('fail', str(results.netcdf_fail))
        pro.appendChild(netcdf)

    xml_str = root.toprettyxml(indent="\t")
    xml_str = '\n'.join([s for s in xml_str.splitlines() if s.strip()])
    with open(path, "w") as f:
        f.write(xml_str)


def create_attribute(root, name, result):

    test = root.createElement(name)
    #  collection level information
    test.setAttribute('ccid', result.ccid)
    test.setAttribute('title', result.title)
    #  granule level information
    test.setAttribute('gid', result.gid)
    test.setAttribute('url', result.url)
    test.setAttribute('murl', result.murl)
    #  test results
    test.setAttribute('type', result.type)
    test.setAttribute('status', result.status)
    test.setAttribute('code', str(result.code))
    test.setAttribute('payload', result.payload)
    return test

