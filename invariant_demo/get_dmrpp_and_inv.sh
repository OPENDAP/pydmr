#!/usr/bin/env bash

ccid=C2152045877-POCLOUD
granules_file=C2152045877-POCLOUD-10.txt
ask_cmr=../ask_cmr.py
get_dmrpp=../get_dmrpp.py
mk_invariant=../mk_invariant_dmrpp.py

# get the DMR++
for granule in $(cat $granules_file)
do
  echo "Getting the URL for $granule"
  g_url=$($ask_cmr -t -R $ccid:$granule | grep "https://archive.podaac.earthdata.nasa.gov" | awk '{print $2}')

  echo "Getting the DMR++"
  $get_dmrpp $g_url > $granule.dmrpp

  echo "Building the DMR++ Invariant"
  $mk_invariant $granule.dmrpp > $granule.dmrpp.inv
done
