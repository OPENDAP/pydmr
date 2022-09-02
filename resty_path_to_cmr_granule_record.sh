#!/bin/bash
#
#
# resty_path="https://opendap.uat.earthdata.nasa.gov/collections/C1241426872-NSIDC_CUAT/granules/ATL06_20181014190217_005_01.h5"
#
# resty_path="https://opendap.uat.earthdata.nasa.gov/collections/C1234714698-EEDTEST/granules/SC:ATL08.005:230469509"
#
#
####################################################################
# 
# If you've set this already then it remains the same. 
# If it's not set then it will try to use the one in my home 
# directory :) (You could change it)
#
export netrc_file=${netrc_file:-"/Users/ndp/.netrc"}

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
    local hyrax_service_endpoint="${1}";
    if test -n "${verbose}" ; then echo "# hyrax_service_endpoint: ${hyrax_service_endpoint}" >&2; fi
    
    local cookies=$(mktemp ./test_cookies.XXXXXX)
    burl="curl -s -L -c ${cookies} -b ${cookies} -n --netrc-file ${netrc_file}"
    
    local fnoc1_dds=$(${burl} ${hyrax_service_endpoint}/hyrax/data/nc/fnoc1.nc.dds)
    if test -n "${verbose}" ; then echo "#              fnoc1_dds: " >&2; fi
    if test -n "${verbose}" ; then echo "${fnoc1_dds}" | \
        awk '{print "#                                "$0;}' >&2; fi
    
    local token_type=$(${burl} ${hyrax_service_endpoint}/login | \
        grep token_type | \
        awk '{print $3}' | \
        sed -e "s/\"//g" -e "s/,//g")
        
    if test -n "${verbose}" ; then echo "#             token_type: '${token_type}'" >&2; fi
    
    local access_token=$(${burl} ${hyrax_service_endpoint}/login | \
        grep access_token | \
        awk '{print $3}' | \
        sed -e "s/\"//g" -e "s/,//g" ) 
           
    if test -n "${verbose}" ; then echo "#           access_token: '${access_token}'" >&2; fi
    
    edl_auth_header="Authorization: ${token_type} ${access_token}";
    if test -n "${verbose}" ; then echo "# EDL Athorization Header: '${edl_auth_header}'" >&2; fi
    
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
    
    if test -n "${verbose}" ; then echo "# restified_path_url=\"${restified_path_url}\"" >&2; fi
    if test -n "${verbose}" ; then echo "# authorization_header=\"${authorization_header}\"" >&2; fi
        
    local ngap_env=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{num=split($3,names,"."); if(num>4){print names[2];}}')
    if [ -n "${ngap_env}" ]; then  ngap_env="${ngap_env}."; else ngap_env="";  fi
    if test -n "${verbose}" ; then echo "# ngap_env=\"${ngap_env}\"" >&2; fi
    
    local collection=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{print $5;}')
    if test -n "${verbose}" ; then echo "# collection=\"${collection}\"" >&2; fi

    local granule_ur=$(echo "${restified_path_url}" | awk 'BEGIN{FS="/";}{print $7;}')
    if test -n "${verbose}" ; then echo "# granule_ur=\"${granule_ur}\"" >&2; fi

    local cmr_query_url="https://cmr.${ngap_env}earthdata.nasa.gov"
    cmr_query_url+="/search/granules.umm_json_v1_4"
    cmr_query_url+="?collection_concept_id=${collection}"
    cmr_query_url+="&granule_ur=${granule_ur}"
    cmr_query_url+="&pretty=true";
    if test -n "${verbose}" ; then echo "# cmr_query_url=\"${cmr_query_url}\"" >&2; fi

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

if test -n "${1}"; then
    cmr_granule_from_restified_path_url "${1}"
fi