import os.path

import requests
import regex as re
import time
import concurrent.futures

import cmr
import errLog

verbose = False
vVerbose = False
search_string = ""
divider = "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="
todo = 0
done = 0


def get_provider_collections(provider):
    """
    Retrieves all collections for a specified provider
    :param provider:
    :return: all collections
    """
    try:
        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(provider, opendap=True, pretty=True)

    except cmr.CMRException as e:
        err = "/////////////////////////////////////////////////////\n"
        err += "CMRException : string_search.py::get_provider_collections() - " + e.message + "\n"
        errLog.output_errlog(err)
        print(e)
    except Exception as e:
        print(e)

    return entries


def search(ccid, title):
    """
    Gets the first and last granules for a collection
        checks the granules for any urls that begin with 'http' and adds them to a list
        once url list has been populated, runs a request on each url
            once the request is finished, searches the request response for the search string
    :param ccid: collection id
    :param title:
    :return:
    """
    update_progress()
    found = False
    results = []

    try:
        first_last_dict = cmr.get_collection_granules_umm_first_last(ccid, pretty=True)
        # print("size: " + str(len(first_last_dict)))

    except cmr.CMRException as e:
        return {ccid: (title, "error")}
        # return {ccid: (title, {"error": e.message})}

    for gid, granule_tuple in first_last_dict.items():
        if re.search('https://opendap.earthdata.nasa.gov/collections/', granule_tuple[1]):
            entries = cmr.get_related_urls(ccid, granule_tuple[0], pretty=True)
            url_list = []
            for url in entries:
                print("entries.url: " + entries[url]) if vVerbose else ''
                if re.search('https', entries[url]):
                    url_list.append(entries[url])
                    # write_to_file(entries[url])

            for url_address in url_list:
                print("\turl_address: " + url_address[0:10]) if vVerbose else ''
                if url_address != "":
                    ext = '.dmrpp'
                    try:

                        full_url = url_address + ext
                        # print(full_url)
                        r = requests.get(full_url)

                        if re.search(search_string, r.text):
                            print("\t\tfound: true") if vVerbose else ''
                            a = (full_url, True)
                            results.append(a)

                    # Ignore exception, the url_tester will return 'fail'
                    except requests.exceptions.InvalidSchema:
                        pass
                    except requests.exceptions.ConnectionError:
                        err = "/////////////////////////////////////////////////////\n"
                        err += "ConnectionError : string_search.py::search() - " + url_address + ext + "\n"
                        errLog.output_errlog(err)

    return {ccid: results}


def write_to_file(url):
    """
    Writes a provided text to a file
    :param url: provided text
    :return:
    """
    if not os.path.exists("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt"):
        with open("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt", 'w') as create:
            create.write(url+"\n")
            create.close()
    else:
        with open("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt", 'a') as file:
            file.write(url+"\n")
            file.close()


def run_search(providers, search_str, concurrency, workers, ver, very):
    """
    entry point for the search functionality
    :param providers:       list of providers to run the string search on
    :param search_str:      the string to be searched for
    :param concurrency:     flag to use threads or not
    :param workers:         number of threads to use if concurrency is true
    :param ver:             verbose flag
    :param very:            very verbose flag
    :return:
    """
    global verbose, vVerbose
    verbose = ver
    vVerbose = very
    global search_string
    search_string = search_str
    with open('Exports/' + time.strftime("%m.%d.%y") + '_' + search_str + '_search.txt', 'w') as file:
        pros = len(providers)
        pro_done = 1
        for provider in providers:
            # if provider == "ORNL_CLOUD":  # Add me to test single provider, make sure to TAB all line below
            print("[ " + str(pro_done) + " / " + str(pros) + " ] searching " + provider + " files for \'"
                  + search_string + "\'")
            file.write(f'{divider}\nProvider: {provider}\n\n')
            collections = get_provider_collections(provider)
            global todo, done
            todo = len(collections.items())
            done = 0
            results = dict()
            if concurrency:
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                    try:
                        result_list = executor.map(search, collections.keys(), collections.values(), timeout=300)
                    except concurrent.futures.TimeoutError:
                        print("This took to long...") # It suspends infinitely.
                    except Exception as exc:
                        print(f'Exception: {exc}')
                for result in result_list:
                    try:
                        results = cmr.merge_dict(results, result)
                    except Exception as exc:
                        print(f'Exception: {exc}')
            else:
                for ccid, title in collections.items():
                    found = search(ccid, title)
                    results = cmr.merge_dict(results, found)

            print('\n')
            for ccid, result in results.items():
                # print(ccid + "\nresults: " + str(len(result)))
                for rTuple in result:
                    # print("tuple: " + rTuple[0] + " : " + str(rTuple[1]))
                    if rTuple != "error":
                        print("\t" + rTuple[1] + "\n\t\t" + ccid + "\n\t\t" + rTuple[0]) if verbose else ''
                        if rTuple[1] is True:
                            file.write(f'\t {ccid}: {rTuple[0]}\n\n')
            # end "if provider == ..." /!\ DO NOT TAB SHIFT PASS THIS LINE /!\
            pro_done += 1


def run_url_finder(providers, concurrency, workers, ver, very):
    """
    entry point for the url finder functionality
    :param providers:       list of providers to run the string search on
    :param concurrency:     flag to use threads or not
    :param workers:         number of threads to use if concurrency is true
    :param ver:             verbose flag
    :param very:            very verbose flag
    :return:
    """
    global verbose, vVerbose
    verbose = ver
    vVerbose = very
    pros = len(providers)
    pro_done = 1
    for provider in providers:
        print("[ " + str(pro_done) + " / " + str(pros) + " ] searching " + provider + " for urls")
        collections = get_provider_collections(provider)
        global todo, done
        todo = len(collections.items())
        done = 0
        if concurrency:
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                executor.map(find, collections.keys(), collections.values())
        else:
            for ccid, title in collections.items():
                find(ccid, title)

        print('\n')
        pro_done += 1


def find(ccid, title):
    """
    Retrieves first and last granules and retrieves urls from those granules
        then check if the url matches and if so, save to file
    :param ccid:
    :param title:
    :return:
    """
    update_progress()

    try:
        first_last_dict = cmr.get_collection_granules_umm_first_last(ccid, pretty=True)
        # print("size: " + str(len(first_last_dict)))

    except cmr.CMRException as e:
        # print("CMRException: " + e.message)
        return

    for gid, granule_tuple in first_last_dict.items():
        if re.search('https://opendap.earthdata.nasa.gov/collections/', granule_tuple[1]):
            write_to_file(granule_tuple[1])


def update_progress():
    """
    updates the progress bar on the terminal
    :return:
    """
    global done, todo
    done += 1
    print_progress(done, todo)


def print_progress(amount, total):
    """
    outputs the progress bar to the terminal
    :param amount:
    :param total:
    :return:
    """
    percent = amount * 100 / total
    msg = "\t" + str(round(percent, 2)) + "% [ " + str(amount) + " / " + str(total) + " ]                    "
    print(msg, end="\r", flush=True)