
# Script to fetch DAS entries using regexpresions
import os
import sys
import subprocess

sys.path.append( os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3/"))
from functions import color_msg
from cfgs.datasets_cfg_improved import datasets

campaigns = [
    "Run3Summer22NanoAODv12", 
    "Run3Summer22EENanoAODv12"
]

def check_exists_das(campaign, datasets):
    """ Function to check if a sample has NANOAOD in DAS """
    color_msg(">> Checking for campaign {}...".format(campaign), "blue")
    for dataset, values in datasets.items():
        dbs = values["dbs"]
        dasquery = 'dasgoclient -query="dataset={dbs}{campaign}*/NANOAODSIM"'.format(dbs = dbs, campaign = campaign)
        dasentry = subprocess.check_output(dasquery, shell=True, universal_newlines=True)
        
        if dasentry != "":
            color_msg("  + {} exists :)".format(dbs), "green")
        else:
            color_msg("  + {} does not exist :(".format(dbs), "red")
    return dasentry

if __name__ == "__main__":
    for campaign in campaigns:
        check_exists_das(campaign, datasets)
            
            
            
            
        
        
        
    


