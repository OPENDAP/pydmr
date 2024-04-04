#!/bin/sh
#Add the python executable to the path
export PATH=/home/centos/pydmr/:$PATH

#Add python3 path to the path, needed for pydmr.o.o
#export PATH=/home/rocky/anaconda3/bin/:$PATH

#Run the tests and move them into a folder generated for today's date
python3 opendap_providers.py -e PROD -T -d
python3 file_mover.py

