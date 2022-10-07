
# PyDMR
PyDMR is a set of utilities to test the idea of a DMR++ invariant and ways that 
might be used in a DMR++ caching scheme.

## What's here
This repository holds a set of functions that ask CMR various questions that
enable reading DMR++ documents for granules using either the 'resty' OPeNDAP
URL or a collection concept id (CCID) and granule title.

Also contained here are some commands that use that library. Those commands are:
* `ask_cmr.py` Ask the CMR for all the collections a provider has, all the 
    granules in a collection, collection info, all the related URLs for a
    granule that are 'GET DATA' or 'USE SERVICE API' URLs.
* `get_dmrpp.py` Will read the DMR++ given the URL to a data file that has a paired
    DMR++. The presumption is that the file is in EDC S3, but there's no 
    requirement that's true, only that _something_ will be returned when `.dmrpp`
    is appended to the URL.
* `mk_invariant_dmrpp.py` Build the invariant form of a DMR++ document. This 
    command can also extract the version information from a DMR++, so it can
    be used to test the idea of cache invalidation based on version numbers.

## Testing out the commands
It can be tedious to figure out all the various providers IDs, Collection IDs,
so here are some to start with.

Providers: PODAAC, GES_DISC, POCLOUD

Using ask_cmr:
* `./ask_cmr.py -p POCLOUD`: Get all the collections
* `./ask_cmr.py -p POCLOUD -o`: Get all the collections with OPeNDAP enabled
* `./ask_cmr.py -c C2036882064-POCLOUD -g -t`: All the granules in the collection, with timing info (-t)
* `./ask_cmr.py -t -r https://opendap.earthdata.nasa.gov/collections/C2205105895-POCLOUD/granules/19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1` 
    Get the Related URLs for this pseudo 'resty URL'
* `./ask_cmr.py -t -R C2205105895-POCLOUD:19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1`: 
    Get the Related URLs for the resty URL that would have the CCID and title that are listed here separated
    by a colon (:)

Getting the paired DMR++:
* `./get_dmrpp.py -t https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/MW_OI-REMSS-L4-GLOB-v5.1/20220902120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc`: 
    Get the DMR++ paired with this granule

Building the invariant:
* `mk_invariant_dmrpp 19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc.dmrpp`: Print the DMR++ 
    invariant
* `mk_invariant_dmrpp -v 19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc.dmrpp`: Print the 
    builder version
* `mk_invariant_dmrpp -l 19980101120000-REMSS-L4_GHRSST-SSTfnd-MW_OI-GLOB-v02.0-fv05.1.nc.dmrpp`: Print the 
    builder version, but in a form that is easier to parse

NB: THis: ./ask_cmr.py -t -R "G2100400959-POCLOUD:cyg.ddmi.s20210228-003000-e20210228-233000.l3.grid-wind-cdr.a10.d10" 
should return a URL to data but does not.

