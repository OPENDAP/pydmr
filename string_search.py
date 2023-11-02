
import requests
import regex as re
import time

import cmr

search_string = ""


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

        return found


def run_search(providers, search_str):
    global search_string
    search_string = search_str
    with open('Exports/' + time.strftime("%m.%d.%y") + '_' + search_str + '_search.txt', 'w') as file:
        for provider in providers:
            print("searching " + provider + " files for \'" + search_string + "\'")
            file.write(f'Provider: {provider}\n')
            collections = get_provider_collections(provider)
            todo = len(collections.items())
            done = 0
            for ccid, title in collections.items():
                found = search(ccid, title)
                done += 1
                print_progress(done, todo)
                if found:
                    # print("! ", end="", flush=True)
                    file.write(f'\t {ccid}: {title}\n')
            print('\n')


def print_progress(done, todo):
    percent = done * 100 / todo
    msg = "\t" + str(round(percent, 2)) + "% [ " + str(done) + " / " + str(todo) + " ]                    "
    print(msg, end="\r", flush=True)