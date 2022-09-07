#!/usr/bin/env bash

dmrpp_files=$1

for f in $(cat dmrpp_files)
do
  $mk_invariant $f > ${f}.inv
done
