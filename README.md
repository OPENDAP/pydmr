
# PyDMR
PyDMR is a set of utilities that implement a regression testing framework for OPeNDAP data 
held in the NASA Earthdata Cloud system. It also can be used to test the idea of a DMR++ 
invariant and ways that might be used in a DMR++ caching scheme.

## What's here
This repository holds code for a testing framework for Hyrax in NGAP and for 
a simple prototype system to determine if the DMR++ documents held in a cache
are stale. The code is mixed together since some parts are shared by both systems.

### The testing framework
WIP

#### Using the commands
```
./regression_tests.py -p POCLOUD -t -v
```
Run tests on all the collections from POCLOUD that have OPeNDAP URLs. Show verbose
output and basic timing stats. The results are written to an XML file. See --help
for more info.
```
./opendap_providers.py
```
Query CMR to find all the providers that have collections with the _has\_opendap\_url_
property

### Building DMR++ Documents
The command line utility ```build_dmrpp``` can be used to build DMR++ documents
for a whole collection or a range of granules in a collection selected using
ISO8601 dates. The DMR++ documents are either saved to local files in a directory
named using collection concept ID or to an S3 bucket using the CCID as an object
name prefix.

The command has help.

Here is an example for one collection:
```
./build_dmrpp.py -v -t -T prod-token.txt \
    -D "2018-08-01T00:00:00Z,2018-08-02T23:59:59Z" C2036877806-POCLOUD
```

### DMR++ Caching
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

#### Testing out the commands
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

NB: This: ./ask_cmr.py -t -R "G2100400959-POCLOUD:cyg.ddmi.s20210228-003000-e20210228-233000.l3.grid-wind-cdr.a10.d10" 
should return a URL to data but does not.

