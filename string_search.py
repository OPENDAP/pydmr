import os.path

import requests
import regex as re
import time
import concurrent.futures

import cmr

verbose = False
vVerbose = False
search_string = ""
divider = "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="
todo = 0
done = 0


def get_provider_collections(provider):
    try:
        # Get the collections for a given provider - this provides the CCID and title
        entries = cmr.get_provider_collections(provider, opendap=True, pretty=True)

    except cmr.CMRException as e:
        print(e)
    except Exception as e:
        print(e)

    return entries


def search(ccid, title):
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
                    print("DmrE", end="", flush=True)

    return {ccid: results}


def write_to_file(url):
    if not os.path.exists("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt"):
        with open("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt", 'w') as create:
            create.write(url+"\n")
            create.close()
    else:
        with open("Exports/" + time.strftime("%m.%d.%y") + "_dmrpp_urls.txt", 'a') as file:
            file.write(url+"\n")
            file.close()


def run_search(providers, search_str, concurrency, workers, ver, very):
    global verbose, vVerbose
    verbose = ver
    vVerbose = very
    global search_string
    search_string = search_str
    with open('Exports/' + time.strftime("%m.%d.%y") + '_' + search_str + '_search.txt', 'w') as file:
        pros = len(providers)
        pro_done = 1
        for provider in providers:
            if provider == "ORNL_CLOUD":  # <-- remove me, im only here for testing!!!
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
                        result_list = executor.map(search, collections.keys(), collections.values())
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
            pro_done += 1


def update_progress():
    global done, todo
    done += 1
    print_progress(done, todo)


def print_progress(amount, total):
    percent = amount * 100 / total
    msg = "\t" + str(round(percent, 2)) + "% [ " + str(amount) + " / " + str(total) + " ]                    "
    print(msg, end="\r", flush=True)