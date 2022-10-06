"""
May not be needed. Adding functions to cmr.py to handle the building of the regression
testing files/format.

Will use ask_cmr.py and cmr.py for the time being.
"""

import time
import cmr

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Query CMR and get information about Collections and Granules, "
                                                 "especially as that information relates to OPeNDAP. EDC credentials "
                                                 "stored in ~/.netrc are needed. See the requests package for details.")