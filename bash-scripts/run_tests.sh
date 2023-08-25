#!/bin/sh
#Add the python executable to the path
export PATH=/home/centos/pydmr/:$PATH

#Run the tests and move them into a folder generated for today's date
python3 opendap_providers.py -e PROD -T
#python3 file_mover.py

