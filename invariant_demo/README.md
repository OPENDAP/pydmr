Demo scratch:
Use this collection since we have new DMR++ doc s for it: C2152045877-POCLOUD. I got the collection concept Id from
Phoebe Sham's spreadsheet.

Use ask_cmr.py for all the granules (used later): 
`./ask_cmr.py -c C2152045877-POCLOUD -g -t > C2152045877-POCLOUD_granules.txt`

There are 17564 granules in this dataset. 

We have the new DMR++ for four granules:
SWOT_L2_LR_SSH_Expert_001_001_20111113T000000_20111113T005105_DG10_01
SWOT_L2_LR_SSH_Expert_001_001_20111113T000000_20111113T005126_DG10_01
SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01
SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125126_DG10_01

The last two are part of two different CCIDs: C2152045877-POCLOUD and C2152046451-POCLOUD

Build the DMR++ invariant files and for the old and the new DMR++ and look for differences.
The command looks like ./mk_invariant_dmrpp SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01.nc.dmrpp
In this directory, `bash make_inv.sh old_and_new_dmrpp.txt` will do this for the two sets of 
old and new DMR++ files. Use `diff` to examine the differences between the two. Note that for
these two sets of files there are differences. Differences that can be seen: the new DMR++
has support for fill values, string arrays and also lacks three variables. It's clear that 
for these data, the new DMR++ builder produces something with significant differences.

What about differences within a collection - will there be false positives (i.e., datasets
that look different but are not)?

Use `bash get_dmrpp_and_inv.sh` which read from `C2152045877-POCLOUD-10.txt` to get granule 
names to sample a 17,000 granule collection, getting the DMR++ and building its invariant.
Use diff to examine them.

NB: I have moved the old and new DMR++ files along with their invariants to the directory
'old_and_new_files' and the ten DMR++ and associated invariant files to 'single_ccid_files'
to reduce clutter here.

-----------------------------

We can also look at the version information and see they were clearly built by different DMR++ builders:
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01.nc.dmrpp
DMR++ Builder Version: 3.20.13
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01.nc.dmrpp.old
DMR++ Builder Version: None
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125126_DG10_01.nc.dmrpp    
DMR++ Builder Version: 3.20.13
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125126_DG10_01.nc.dmrpp.old
DMR++ Builder Version: None


