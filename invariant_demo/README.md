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

We can look at the version information and see they were clearly built by different DMR++ builders:
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01.nc.dmrpp
DMR++ Builder Version: 3.20.13
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125105_DG10_01.nc.dmrpp.old
DMR++ Builder Version: None
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125126_DG10_01.nc.dmrpp    
DMR++ Builder Version: 3.20.13
pydmr/invariant_demo % ../mk_invariant_dmrpp.py -v SWOT_L2_LR_SSH_Expert_001_001_20140412T120000_20140412T125126_DG10_01.nc.dmrpp.old
DMR++ Builder Version: None


