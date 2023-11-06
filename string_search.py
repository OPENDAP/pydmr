
import requests
import regex as re
import time
import concurrent.futures

import cmr

search_string = ""
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

    try:
        first_last_dict = cmr.get_collection_granules_umm_first_last(ccid, pretty=True)

    except cmr.CMRException as e:
        return {ccid: (title, {"error": e.message})}

    for gid, granule_tuple in first_last_dict.items():
        url_address = granule_tuple[1]

        ext = '.dmr'
        try:
            # print(".", end="", flush=True)

            r = requests.get(url_address + ext)
            if re.search(search_string, r.text):
                found = True

        # Ignore exception, the url_tester will return 'fail'
        except requests.exceptions.InvalidSchema:
            pass
        except requests.exceptions.ConnectionError:
            print("DmrE", end="", flush=True)

    return {ccid: (title, found)}


def run_search(providers, search_str, concurrency, workers):
    global search_string
    search_string = search_str
    with open('Exports/' + time.strftime("%m.%d.%y") + '_' + search_str + '_search.txt', 'w') as file:
        pros = len(providers)
        pro_done = 1
        for provider in providers:
            if provider == "LAADS": # <-- remove me, im only here for testing!!!
                print("[ " + str(pro_done) + " / " + str(pros) + " ] searching " + provider + " files for \'"
                      + search_string + "\'")
                file.write(f'Provider: {provider}\n')
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
                    # print(str(result[1]) + " - " + ccid + ": " + result[0])
                    print(str(result[1]) + " - " + ccid)
                    if result[1] is True:
                        file.write(f'\t {ccid}: {result[0]}\n')
            pro_done += 1


def update_progress():
    global done, todo
    done += 1
    print_progress(done, todo)


def print_progress(amount, total):
    percent = amount * 100 / total
    msg = "\t" + str(round(percent, 2)) + "% [ " + str(amount) + " / " + str(total) + " ]                    "
    print(msg, end="\r", flush=True)