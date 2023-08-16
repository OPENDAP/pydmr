#! /bin/sh
#Add the python executable to the path
export PATH=/home/centos/pydmr/:$PATH

#Run the tests and move them into a folder generated for today's date
opendap_providers.py -e PROD -T
file_mover.py

