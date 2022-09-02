#!/bin/bash


####################################################################
#
# cmr_provider_collections_json()
#  
#
# cmr_provider_collections_json uat ORNL_CLOUD | jq '.feed.entry[] | [.id, .dataset_id, .summary]'
#
function cmr_provider_collections_json(){
    local ngap_env="${1}";
    local provider_id="${2}";

    # echo "ngap_env: ${target_ngap_env}" >&2;
    # echo "provider_id: ${target_provider_id}" >&2;

    if [ -n "${ngap_env}" ]; then  ngap_env="${ngap_env}."; fi
   
    local cmr_query_url="https://cmr.${ngap_env}earthdata.nasa.gov/search/collections.json?provider=${provider_id}"
    echo "# cmr_url: ${cmr_query_url}" >&2
    local provider_json=""
    provider_json=$(burl -s "${cmr_query_url}")
    # echo "collections_doc:" >&2 
    echo "${provider_json}" | jq '.'
}




####################################################################
#
# cmr_get_granule_entry_json()
#
# Return granule json with the (entry) title, aka granule_ur
#
function cmr_get_granule_entry_json() {
    target_ngap_env="${1}";
    target_granule_concept_id="${2}"
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    granule_doc=`curl -s "https://cmr.${target_ngap_env}earthdata.nasa.gov/search/granules.json?concept_id=${target_granule_concept_id}&pretty=true"`
    #echo "granule_doc: "; 
    echo "${granule_doc}";
}

####################################################################
#
# cmr_get_granule_entry_json_umm_v1_4()
#
# Return granule json with the (entry) title, aka granule_ur
#
function cmr_get_granule_entry_json_umm_v1_4() {
    target_ngap_env="${1}";
    target_granule_concept_id="${2}"
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    cmr_query_url="https://cmr.${target_ngap_env}earthdata.nasa.gov/search/granules.umm_json_v1_4?concept_id=${target_granule_concept_id}&pretty=true";
    # echo "        cmr_query_url=\"${cmr_query_url}\"" >&2
    granule_doc=`curl -s "${cmr_query_url}"`
    echo "${granule_doc}"
}
# https://cmr.earthdata.nasa.gov/search/granules.umm_json_v1_4?concept_id=G1652996789-PODAAC&pretty=true



####################################################################
#
# cmr_get_granule_entry_json_umm_v1_4_from_resty_path()
#
# Return granule json with the (entry) title, aka granule_ur
#
# https://opendap.uat.earthdata.nasa.gov/collections/C1238618527-POCUMULUS/granules/JA3_GPSOPR_2PfS219_126_20220122_222016_20220123_000001.dmr.html
#
# C1238621141-POCLOUD 20210110090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1
# 
function cmr_get_granule_entry_json_umm_v1_4_from_resty_path() {
    local target_ngap_env="${1}";
    local target_collection_concept_id="${2}"
    local target_granule_ur="${3}"
    local target_edl_token="${4}"
        
    if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    cmr_query_url="https://cmr.${target_ngap_env}earthdata.nasa.gov/search/granules.umm_json_v1_4?collection_concept_id=${target_collection_concept_id}&granule_ur=${target_granule_ur}&pretty=true";
    echo "        cmr_query_url=\"${cmr_query_url}\"" >&2
    if test -n "${target_edl_token}"; then
        granule_doc=`curl -L -H "${target_edl_token}" -s "${cmr_query_url}"`
    else 
        granule_doc=`curl -L -s "${cmr_query_url}"`
    fi
    echo "${granule_doc}"
}

# cmr_get_granule_entry_json_umm_v1_4_from_resty_path "uat." "C1238618527-POCUMULUS" "JA3_GPSOPR_2PfS219_126_20220122_222016_20220123_000001"

# cmr_get_granule_entry_json_umm_v1_4_from_resty_path "C2184546470-POCLOUD" "20211206154529-NAVO-L2P_GHRSST-SST1m-IMAGER_EWSG1-v02.0-fv01.0"

# cmr_query_url="https://cmr.uat.earthdata.nasa.gov/search/granules.umm_json_v1_4?collection_concept_id=C1238618527-POCUMULUS&granule_ur=JA3_GPSOPR_2PfS219_126_20220122_222016_20220123_000001&pretty=true";
# https://opendap.earthdata.nasa.gov/collections/C2184546470-POCLOUD/granules/20211206154529-NAVO-L2P_GHRSST-SST1m-IMAGER_EWSG1-v02.0-fv01.0.dmr.html
# 
# resty_path=https://opendap.earthdata.nasa.gov/collections/C2036880672-POCLOUD/granules/ssh_grids_v1812_1992100212
# collection="C2036880672-POCLOUD"
# granule_ur="ssh_grids_v1812_1992100212"
# cmr_get_granule_entry_json_umm_v1_4_from_resty_path "" "C2036880672-POCLOUD" "ssh_grids_v1812_1992100212" "Authorization: Bearer EDL-O114598835d4a68e3964ef6df0c2beac340c6073a3e1f5349751f019cebc"
#
# resty_path="=https://opendap.earthdata.nasa.gov/collections/C2146321631-POCLOUD/granules/cyg01.ddmi.s20210101-000000-e20210101-235959.l1.power-brcs.a31.d32"
# collection="C2146321631-POCLOUD"
# granule_ur="cyg01.ddmi.s20210101-000000-e20210101-235959.l1.power-brcs.a31.d32"
# cmr_get_granule_entry_json_umm_v1_4_from_resty_path "" "C2146321631-POCLOUD" "cyg01.ddmi.s20210101-000000-e20210101-235959.l1.power-brcs.a31.d32" "Authorization: Bearer EDL-O2bb63122af29730c9bc8020163c6191d167184d13d603162a8cb8f9e9d9"
#
# resty_path="https://opendap.uat.earthdata.nasa.gov/collections/C1241426872-NSIDC_CUAT/granules/ATL06_20181014190217_005_01.h5"
#
# resty_path="https://opendap.uat.earthdata.nasa.gov/collections/C1234714698-EEDTEST/granules/SC:ATL08.005:230469509"
#
#



export netrc_file="/Users/ndp/.netrc"

####################################################################
#
# get_edl_authorization_header_from_hyrax()
#
# This function reaches out to the hyrax instance at the location 
# provided in $1. The request process requeires the client (this
# script) to login to EDL. Then the client can look at their
# login profile page: 
#
#     ${hyrax_service_endpoint}/login
# 
# and scrape the AWS EDL token from there.
#
function get_edl_authorization_header_from_hyrax() {
    echo "###################################################################" >&2
    echo "#" >&2
    echo "# get_edl_authorization_header_from_hyrax() - " >&2
    local hyrax_service_endpoint="${1}"
    echo "# hyrax_service_endpoint: ${hyrax_service_endpoint}" >&2
    
    local cookies=$(mktemp ./test_cookies.XXXXXX)
    burl="curl -s -L -c ${cookies} -b ${cookies} -n --netrc-file ${netrc_file}"
    
    local fnoc1_dds=$(${burl} ${hyrax_service_endpoint}/hyrax/data/nc/fnoc1.nc.dds)
    echo "#                     fnoc1_dds: "
    echo "${fnoc1_dds}" | awk '{print "#                                "$0;}' >&2
    
    local token_type=$(${burl} ${hyrax_service_endpoint}/login | grep token_type | awk '{print $3}' | sed -e "s/\"//g" -e "s/,//g")
    echo "#                    token_type: '${token_type}'" >&2
    
    local access_token=$(${burl} ${hyrax_service_endpoint}/login | \
        grep access_token | \
        awk '{print $3}' | \
        sed -e "s/\"//g" -e "s/,//g" )    
    echo "#                  access_token: '${access_token}'" >&2
    
    edl_auth_header="Authorization: ${token_type} ${access_token}";
    echo "# EDL Athorization Header: '${edl_auth_header}'" >&2
    
    echo ${edl_auth_header};
}


####################################################################
#
# cmr_granule_from_restified_path_url()
#
# Return CMR granule entry for a granule specified by an NGAP 
# restified path URL
# Works for OPeNDAP access restified path URLs revised
# structure and semantics: 
# 
#  https://opendap.????earthdata.nasa.gov/collections/COLLECTION_NAME/granules/GRANULE_UR
#
# The $2 parameter is optional. If omitted the script will attempt 
# to get the authorization header from the hyrax service.
#
#
function cmr_granule_from_restified_path_url() {
    local restified_path_url="${1}"
    local authorization_header="${2}"
    
    echo "# restified_path_url=\"${restified_path_url}\"" >&2
    echo "# authorization_header=\"${authorization_header}\"" >&2
        
    local ngap_env=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{num=split($3,names,"."); if(num>4){print names[2];}}')
    if [ -n "${ngap_env}" ]; then  ngap_env="${ngap_env}."; else ngap_env="";  fi
    echo "# ngap_env=\"${ngap_env}\"" >&2
    
    local collection=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{print $5;}')
    echo "# collection=\"${collection}\"" >&2

    local granule_ur=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{print $7;}')
    echo "# granule_ur=\"${granule_ur}\"" >&2

    local cmr_query_url="https://cmr.${ngap_env}earthdata.nasa.gov/search/granules.umm_json_v1_4?collection_concept_id=${collection}&granule_ur=${granule_ur}&pretty=true";
    echo "# cmr_query_url=\"${cmr_query_url}\"" >&2

    local granule_doc=""
    if test ! -n "${authorization_header}"; then
        local hyrax_endpoint=""
        hyrax_endpoint=$(echo $restified_path_url | awk '{split($0,a,"/"); print a[1]"//"a[2]a[3];}')
        authorization_header=$(get_edl_authorization_header_from_hyrax "${hyrax_endpoint}")
    fi
    echo "# EDL Authorization Header: '${authorization_header}'" >&2
    granule_doc=$(curl -L -H "${authorization_header}" -s "${cmr_query_url}")

    echo "${granule_doc}"
}

####################################################################
#
# cmr_get_collection_entry_json()
#
# Return collection entry json doc
#
function cmr_get_collection_entry_json() {
    target_ngap_env="${1}";
    target_collection_concept_id="${2}"
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    collection_doc=`curl -s "https://cmr.${target_ngap_env}earthdata.nasa.gov/search/collections.json?concept_id=${target_collection_concept_id}&pretty=true"`
    #echo "collection_doc: "; 
    echo "${collection_doc}";
}

####################################################################
#
# cmr_get_collection_granules_json()
#
# Return collecdtions granles json doc
#
function cmr_get_collection_granules_json() {
    target_ngap_env="${1}";
    target_collection_concept_id="${2}"
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    collection_doc=`curl -s "https://cmr.${target_ngap_env}earthdata.nasa.gov/search/granules.json?concept_id=${target_collection_concept_id}&pretty=true"`
    #echo "collection_doc: "; 
    echo "${collection_doc}";
}





####################################################################
#
# cmr_get_entry_title()
#
# Return collection json with dataset_id, aka entry_title
#
# In the returned collection document the dataset_id and the title 
# are both the same as entry_title, but there are two "title" 
# fields, one at the top level and one inside the "entry" member, 
# which is the one we want.
#{
#  "feed" : {
#    "entry" : [ {
#       "dataset_id" : "ATLAS-ICESat-2 L2A Global Geolocated Photon Data V003",
#       "title"      : "ATLAS-ICESat-2 L2A Global Geolocated Photon Data V003",
#
function cmr_get_entry_title() {
    target_ngap_env="${1}";
    collection_concept_id="${2}"

    collection_doc=`cmr_get_collection_entry_json "${target_ngap_env}" "${collection_concept_id}"`
    # echo "collection_doc: "; echo "${collection_doc}";
    echo ${collection_doc} | jq ".feed.entry[].title" | sed -e "s/\"//g"
}




####################################################################
#
# cmr_get_granule_ur()
#
# Return granule json with the (entry) title, aka granule_ur
#
# In the returned granule document the "title" field inside of "entry" member is the granule_ur
#
function cmr_get_granule_ur() {
    target_ngap_env="${1}";
    granule_concept_id="${2}"
    
    granule_doc=`cmr_get_granule_entry_json "${target_ngap_env}" "${granule_concept_id}" `
    # echo "granule_doc: "; echo "${granule_doc}";
    echo ${granule_doc} | jq ".feed.entry[].title" | sed -e "s/\"//g"
}


####################################################################
#
# get_collections_with_opendap_url()
#
# Queries CMR for all the collections in the target 
# environment (SIT|UAT|PROD) that contain OPeNDAP URLs
#
function get_collections_with_opendap_url(){
    target_ngap_env="${1}";

    if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=; fi
    #set -x
    matching_doc=`curl -s "https://cmr.${ngap_env}earthdata.nasa.gov/search/collections.json?has_opendap_url=true&pretty=true"`;
    #set +x
    #echo "Matching Doc: ${matching_doc}";
    echo $matching_doc |  jq -r ".feed.entry[].id";
    
}


####################################################################
#
# cmr_collections()
#
function cmr_collections(){
    target_ngap_env="${1}";
    provider_id="${2}";

    # echo "ngap_env: ${target_ngap_env}" >&2;
    # echo "provider_id: ${provider_id}" >&2;

    
    provider_doc=`cmr_provider_collections_json "${target_ngap_env}" "${provider_id}" `
    echo "$provider_doc" | jq ".feed.entry[].id" | sed -e "s/\"//g"
    
}



####################################################################
#
# cmr_granules()
#
function cmr_granules(){
    target_ngap_env="${1}";
    collection_id="${2}";
    
    collection_doc=`cmr_get_collection_granules_json "${target_ngap_env}" "${collection_id}"`
    echo "${collection_doc}" | jq ".feed.entry[].id" | sed -e "s/\"//g"
}




####################################################################
#
# build_collection_opendap_urls()
#  
# Constructs both new and okd stype restified path URLs for every
# granule in the collection
#
function build_collection_opendap_urls() {
    target_ngap_env="${1}"
    target_provider="${2}"
    collection_concept_id="${3}"
    
    echo "########################################################################"
    echo "# collection_concept_id: ${collection_concept_id}"
        
    ngap_service_env="${target_ngap_env}";    
    if [ -n "${target_ngap_env}" ]; then  target_ngap_env="${ngap_service_env}."; fi
    ngap_service="http://opendap.${target_ngap_env}earthdata.nasa.gov"


    #echo "Working on collection_concept_id: ${collection_concept_id}"
    entry_title=`cmr_get_entry_title "${ngap_env}" "${collection_concept_id}" `
    echo "# collection entry_title: ${entry_title}"
    echo "#"
   
    for granule_concept_id in `cmr_granules "${ngap_env}" "${collection_concept_id}" `
    do
        echo "# granule_concept_id: ${granule_concept_id}"
    
        granule_ur=`cmr_get_granule_ur "${ngap_env}" "${granule_concept_id}"`
        echo "# granule_ur: ${granule_ur}"
        
        
    
        old_ngap_api_url="${ngap_service}/providers/${target_provider}/collections/${entry_title}/granules/${granule_ur}"
        echo "      old_ngap_api_url: ${old_ngap_api_url}"

        new_ngap_api_url="${ngap_service}/collections/${collection_concept_id}/granules/${granule_ur}"
        echo "      new_ngap_api_url: ${new_ngap_api_url}"
       
    done  
        
}


####################################################################
#
# get_provider_opendap_urls()
#  
# Constructs both new and okd stype restified path URLs for every
# granule held bu the provider
#
function get_provider_opendap_urls() {
    target_ngap_env="${1}"
    provider_id="${2}"
        
    for collection_concept_id in `cmr_collections "${target_ngap_env}" "${provider_id}" `
    do
        build_collection_opendap_urls "${ngap_env}" "${provider_id}" "${collection_concept_id}"

    done
}


function probe_provider() {
    target_ngap_env=${1};
    target_provider=${2};
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    
    export eedtest_collections=`cmr_collections "${ngap_env}" "${target_provider}"`
    echo "eedtest_collections: "
    echo "${eedtest_collections}"
    
    for collection_concept_id in ${eedtest_collections};
    do 
        echo ""
        echo "########################################################################################"
        echo "collection_concept_id=\"${collection_concept_id}\""
        granule_cids=`cmr_granules "${ngap_env}" "${collection_concept_id}"`;
        echo "granule_cids=\"${granule_cids}\""
        for granule_cid in ${granule_cids};
        do
            echo "-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --"
            echo "   granule_concept_id=\"${granule_cid}\""
            granule_ur=`cmr_get_granule_ur "${ngap_env}" "${granule_cid}"`
            echo "           granule_ur=\"${granule_ur}\""
            entry_title=`cmr_get_entry_title "${ngap_env}" "${collection_cid}"`
            
            old_ngap_api_url="${ngap_service}/providers/${target_provider}/collections/${entry_title}/granules/${granule_ur}"
            echo "     old_ngap_api_url=\"${old_ngap_api_url}\""
    
            new_ngap_api_url="${ngap_service}/collections/${collection_concept_id}/granules/${granule_ur}"
            echo "     new_ngap_api_url=\"${new_ngap_api_url}\""
        done
    done
}


####################################################################
#
# cmr_get_granule_opendap_link()
#
# Return the granule's OPeNDAP Data access URL
#
function cmr_get_granule_opendap_link() {
    target_ngap_env="${1}";
    granule_concept_id="${2}"
    
    granule_doc=`cmr_get_granule_entry_json_umm_v1_4 "${target_ngap_env}" "${granule_concept_id}" `
    # echo "granule_doc: ${granule_doc}" >&2
    echo ${granule_doc} | jq -r '.items[].umm.RelatedUrls[] | select( .Subtype != null and .Subtype == "OPENDAP DATA" ).URL'
}

####################################################################
#
# get_collection_opendap_urls()
#
# Returns every granules OPeNDAP Data Access URL for the environment
# and collection specified (collection_concept_id).
#
function get_collection_opendap_urls() {
    target_ngap_env=${1};
    collection_concept_id=${2};
    
    if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    
    echo ""
    echo "================================================================================="
    echo "collection_concept_id=\"${collection_concept_id}\""
    granule_cids=`cmr_granules ${ngap_env} ${collection_concept_id}`;
    for granule_cid in ${granule_cids};
    do
        echo "   -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --"
        echo "   granule_concept_id=\"${granule_cid}\""
        opendap_url=`cmr_get_granule_opendap_link ${ngap_env} ${granule_cid}`
        echo "          opendap_url=\"${opendap_url}\""
        
    done
}


####################################################################
#
# probe_provider_opendap_granules()
#
# Returns every granules OPeNDAP Data Access URL for the environment
# and provider specified.
#
function probe_provider_opendap_granules() {
    target_ngap_env=${1};
    target_provider=${2};
    
   if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    
    export eedtest_collections=`cmr_collections ${ngap_env} ${target_provider}`
    for collection_concept_id in ${eedtest_collections};
    do 
        get_collection_opendap_urls ${target_ngap_env} ${collection_concept_id}
    done
}


####################################################################
#
# get_providers()
#
# the list of collections is populated by all collections that are tagged with tag: gov.nasa.eosdis. 
# To find a list of all providers, e.g. in PROD, 
# run curl https://cmr.earthdata.nasa.gov/ingest/providers?pretty=true
function get_providers() {
    target_ngap_env=${1};
    
    if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi

    local cmr_url="https://cmr.${ngap_env}earthdata.nasa.gov/ingest/providers?pretty=true"
    echo "# CMR query URL: ${cmr_url}" >&2
    providers_list=$(curl -s "${cmr_url}")
    echo "${providers_list}" | awk '{print "#    "$0;}' >&2
    echo ${providers_list} | jq -r '.[]."provider-id"'
}






####################################################################
#
# CMR Legacy API
#
# GET providers (aka DAACs) info:
# curl -s "https://cmr.earthdata.nasa.gov/legacy-services/rest/providers.json"
#
# Get info about a single provider.
# curl -s "https://cmr.earthdata.nasa.gov/legacy-services/rest/providers/GHRC_CLOUD"
#
#
function cmr_get_provider_info() {
    local ngap_env="${1}";
    local provider_id="${2}";

    echo "#############################################################" >&2
    echo "#" >&2
    echo "# get_provider_info()" >&2
    echo "#    ngap_env: ${ngap_env}" >&2
    echo "# provider_id: ${provider_id}" >&2

    if [ -n "${ngap_env}" ]; then  ngap_env="${ngap_env}."; else ngap_env=;  fi

    local cmr_url="https://cmr.${ngap_env}earthdata.nasa.gov/legacy-services/rest/providers"
    if test -n "${provider_id}"
    then
        cmr_url+="/${provider_id}"
    fi
    cmr_url+=".json"
    echo "# cmr_url: ${cmr_url}" >&2
    
    local providers_info=""
    providers_info=$(curl -s "${cmr_url}" | jq '.')
    echo "${providers_info}"
}

function cmr_get_providers() {
    local ngap_env=${1};

    provider_info=$(cmr_get_provider_info "${ngap_env}")
    echo "${provider_info}" | jq '.' | awk '{print "#    "$0;}' >&2
    echo "${provider_info}" | jq  -r ".[].provider.provider_id"
}


function cmr_get_provider_description() {
    local ngap_env=${1};
    local provider_id=${2};

    echo "#############################################################" >&2
    echo "#" >&2
    echo "# get_provider_description()" >&2
    echo "#" >&2

    provider_info=$(cmr_get_provider_info "${ngap_env}" "${provider_id}")
    echo "${provider_info}" | jq '.' | awk '{print "##    "$0;}' >&2
    echo "#" >&2
    echo "#--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=--=" >&2
    echo "#" >&2
    echo "# Provider Description" >&2
    if test -n "${provider_id}" 
    then
        
        echo "#   provider_id: ${provider_id}" >&2
        echo "#" >&2
        echo "${provider_info}" | jq  ".provider | [.provider_id, .description_of_holdings]"
    else
        echo "#   ALL PROVIDERS" >&2
        echo "#" >&2
        echo "${provider_info}" | jq  ".[].provider | [.provider_id, .description_of_holdings]"
    fi
}
####################################################################
#
# get_providers()
#
# the list of collections is populated by all collections that are tagged with tag: gov.nasa.eosdis. 
# To find a list of all providers, e.g. in PROD, 
# run curl https://cmr.earthdata.nasa.gov/ingest/providers?pretty=true
function get_env_opendap_urls() {
    target_ngap_env=${1};
    
    if [ -n "${target_ngap_env}" ]; then  ngap_env="${target_ngap_env}."; else ngap_env=;  fi
    for provider  in `get_providers ${target_ngap_env}`;
    do 
        echo "########################################################################################"
        echo "# provider: ${provider}"
        probe_provider_opendap_granules ${target_ngap_env} ${provider}
    done
}



