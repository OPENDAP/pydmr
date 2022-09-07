#!/usr/bin/env bash

dmrpp_files=$1
mk_invariant=../mk_invariant_dmrpp.py

for f in $(cat $dmrpp_files)
do
  $mk_invariant $f > ${f}.inv
done
