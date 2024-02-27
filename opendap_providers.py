#!/usr/bin/env python3

"""
Find all the NASA ESDIS Providers in the CMR catalog that have collections
accessible using OPeNDAP.
"""

import xml.dom.minidom as minidom
import time
import requests
import subprocess
import os

import cmr
import errLog
import string_search


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query CMR and get information about Providers with Collections "
                                                 "accessible using OPeNDAP.")

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-y", "--very_verbose", help="increase output verbosity", action="store_true", default=False)
    parser.add_argument("-P", "--pretty", help="request pretty responses from CMR", action="store_true", default=False)
    parser.add_argument("-t", "--time", help="time responses from CMR", action="store_true")

    parser.add_argument('-x', '--xml', default=True, action='store_true')
    parser.add_argument('--no-xml', dest='xml', action='store_false')
    # argparse.BooleanOptionalAction makes --xml/--no-xml work. The default is to make xml. Requires Python 3.10.x
    # parser.add_argument("-x", "--xml", help="time responses from CMR", action=argparse.BooleanOptionalAction,
    #                     default=True)
    parser.add_argument("-V", "--version", help="version number for unit_tests results XML file", action="store_true",
                        default="1")
    parser.add_argument("-T", "--tests", help="run the regression tests on the provider's collections",
                        action="store_true", default=False)
    parser.add_argument("-s", "--search", help="search for the provided string in all "
                                               "collections and write out collection names.")
    parser.add_argument("-f", "--find", help="find urls in all collections and write to file.")
    parser.add_argument("-w", "--workers", help="if concurrent (the default), set the number of workers (default: 5)",
                        default=5, type=int)
    # Use --no-concurrency to run the tests serially.
    parser.add_argument('-c', '--concurrency', help="run the tests concurrently", default=True, action='store_true')
    parser.add_argument('--no-concurrency', dest='concurrency', action='store_false')

    parser.add_argument('-d', '--dap', help="run the dap tests", action='store_true', default=False)
    parser.add_argument('-D', '--dap_var', help="run the dap_var tests", action='store_true', default=False)

    group = parser.add_mutually_exclusive_group(required=True)  # only one option in 'group' is allowed at a time
    group.add_argument("-e", "--environment", help="an environment, a placeholder for now. This only works for PROD.")

    args = parser.parse_args()

    # cmr.verbose = True if args.verbose else False
    cmr.verbose = args.verbose

    try:
        start = time.time()

        # make the response document
        if args.xml:
            root = minidom.Document()
            xsl_element = root.createProcessingInstruction("xml-stylesheet",
                                                           "type='text/xsl' href='/NGAP-PROD-tests/home.v2.xsl'")
            root.appendChild(xsl_element)

            environment = root.createElement('Environment')
            environment.setAttribute('name', args.environment)
            environment.setAttribute('date', time.asctime())
            root.appendChild(environment)

        pretty = '&pretty=true' if args.pretty else ''
        opendap = '&has_opendap_url=true'
        service = 'cmr.earthdata.nasa.gov'
        cmr_query_url = f'https://{service}/search/collections.umm_json?{opendap}{pretty}'

        # this uses the new return value as a set feature of process_request
        entries = cmr.process_request(cmr_query_url, cmr.provider_id, requests.Session(), page_size=2000)

        duration = time.time() - start

        if args.verbose:
            print(f'Total providers found: {len(entries)}') if len(entries) > 1 else ''
            print(f'Request time: {duration:.1f}s') if args.time else ''

        for provider in entries:
            print(provider) if args.verbose else ''
            if args.xml:
                # XML element for the collection
                prov = root.createElement('Provider')
                # TODO The names here, below in the 'if args.xml' block and in regression-tests.py
                #  are coupled in a very fragile way. Fix this so the name is made once and passed
                #  into regression_tests.py, etc. jhrg 12/05/22
                prov.setAttribute('name', provider)
                environment.appendChild(prov)

        if args.search:
            print("\nsearch string: " + args.search)
            string_search.run_search(entries, args.search, args.concurrency, args.workers,
                                     args.verbose, args.very_verbose)
        elif args.find:
            string_search.run_url_finder(entries, args.concurrency, args.workers,
                                     args.verbose, args.very_verbose)
        else:
            save_path_file = ""
            if args.xml:
                # Save the XML
                xml_str = root.toprettyxml(indent="\t")
                directory = "Exports/" + time.strftime("%m.%d.%y") + "/"
                exists = os.path.exists(directory)
                if not exists:
                    os.makedirs(directory)

                save_path_file = directory + args.environment + time.strftime("-%m.%d.%Y-") + args.version + ".xml"
                with open(save_path_file, "w") as f:
                    f.write(xml_str)

            if args.tests:
                # once we have the list of providers, call regression_tests.py for each one
                save_dir_name = "logs"
                cur = 1
                total = len(entries)
                for provider in entries:
                    print(f"[ {cur} / {total} ] Running tests on {provider}'s collections...")

                    cmd = ["./regression_tests.py", f"--provider={provider}", "-t",
                           f"--save={save_dir_name}", f"--path={save_path_file}"]

                    if args.verbose:
                        cmd.append("-v")
                    if args.dap:
                        cmd.append(f"--dap={args.dap}")
                    if args.dap_var:
                        cmd.append(f"--dap_var={args.dap_var}")

                    result = subprocess.run(cmd)
                    cur += 1

                    if result.returncode != 0:
                        print(f"Error running regression_tests.py {result.args}")

    except cmr.CMRException as e:
        err = "/////////////////////////////////////////////////////\n"
        err += "CMRException : opendap_providers.py::main() - " + e.message + "\n"
        errLog.output_errlog(err)
        print(e)


if __name__ == "__main__":
    main()
