#!/usr/bin/env bash
#
# Process all the granules in C2152045877-POCLOUD-10.txt.
# For example, bash get_dmrpp_and_inv.sh < C2152045877-POCLOUD-10.txt

granules_file=C2152045877-POCLOUD-10.txt

ccid=$1   # C2152045877-POCLOUD
ask_cmr=../ask_cmr.py
get_dmrpp=../get_dmrpp.py
get_dataurl=../get_data_url.py
mk_invariant=../mk_invariant_dmrpp.py
mk_inv_option=-d

besstandalone=$prefix/bin/besstandalone


# get the DMR++
# cat $granules_file | while IFS= read -r
# OR while IFS= read -r AND redirect 'C2152045877-POCLOUD-10.txt' in
# for granule in $(cat $granules_file)
while IFS= read -r granule
do
  echo "Getting the URL for $granule"
  g_url=$($ask_cmr -t -R "$ccid":"$granule" | grep "https://archive.podaac.earthdata.nasa.gov" | awk '{print $2}')

  echo "Getting the DMR++"
  $get_dmrpp "$g_url" > "$granule".dmrpp

  echo "Building the DMR++ Invariant"
  $mk_invariant $mk_inv_option "$granule".dmrpp > "$granule".dmrpp.inv

  echo "Create a builddmrpp BESCMD XML document"
  $ask_cmr -b "$ccid":"$granule"

  echo "Use besstandalone to create new DMRPP"
  $besstandalone -c $prefix/etc/bes/bes.conf -i "$granule".bescmd > "$granule".builddmrpp

  echo "Building the DMR++ Invariant"
  $mk_invariant $mk_inv_option "$granule".builddmrpp > "$granule".builddmrpp.inv
done
