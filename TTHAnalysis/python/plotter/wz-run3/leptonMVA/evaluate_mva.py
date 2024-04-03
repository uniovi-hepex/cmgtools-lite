""" Script to evaluate MVA trainings """

import ROOT as r
from copy import deepcopy
import os,sys
from optparse import OptionParser
import array as ar
import numpy as np
from copy import deepcopy
import mva_configs as mvacfgs
import numpy as np

sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from functions import color_msg

sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/PhysicsTools/NanoAODTools/python/postprocessing/framework/"))
from datamodel import Collection as Collection

r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)
    
def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python plot_triggerSF.py [options]", 
                                    description = "Main options for running WZ trigger SF")
    parser.add_option("--inpath", dest = "inpath", default = None,
                help = "Path to the folder with the files used to evaluate performance")
    parser.add_option("--nfiles", dest = "nfiles", type = int, default = -1,
            help = "Number of files to be iterated over.")
    parser.add_option("--mode", dest = "mode", default = "muon",
        help = "Produce results for muons or electrons.")
    parser.add_option("--year", dest = "year", default = "year",
        help = "Year")
    return parser.parse_args()

def create_rootfiles(mode, inpath, files, mva, outpath):
    """ Evaluate MVA """
    if mva.useBranch == None:
        mva.open_model()
    
    chain = r.TChain("Events", "chain")
    for file in files:
        chain.AddFile(os.path.join(inpath, file))
    color_msg(" >> Evaluating Muon MVA", "green")
    color_msg("    * Number of events: %d "%chain.GetEntries())
    
    presel = lambda lep: 1
    collection = None
    if mode == "muon":
        collection = "Muon"
        presel = lambda lep: (lep.pt > 5 and
                            abs(lep.eta) < 2.4 and
                            #(lep.isGlobal == 1 or lep.isTracker == 1) and
                            #lep.isPFcand and
                            lep.looseId == 1)
    elif mode == "electron":
        collection = "Electron"
        presel = lambda lep: (lep.pt > 5 and
                          abs(lep.eta) < 2.5 and
                          lep.lostHits < 2)
        
    for ievent, event in enumerate(chain):
        jets = Collection(event, "Jet", "nJet")
        leps = Collection(event, collection,"n%s"%collection)
        for ilep, lep in enumerate(leps):
            # Fill the histograms
            if (lep.jetIdx > 40): continue # Sometimes the branch appears not to be filled and it crashes 
            
            # Update the values of the variables
            mva.set_vars(lep, jets)
            
            if mva.useBranch == None:
                score = mva.evaluate(lep)
            else:
                score = getattr(lep, mva.useBranch)
            
            genPartFlav = lep.genPartFlav
            
            if (genPartFlav == 1 or genPartFlav == 15):
                mva.fill("signal_total", score)
            elif (genPartFlav != 1 or genPartFlav != 15):
                mva.fill("bkg_total", score)

            # -- Now fill the selected histograms
            ## Baseline selection
            if (lep.miniPFRelIso_all > 0.4): continue
            if (lep.sip3d > 8): continue
            if (abs(lep.dxy) > 0.05): continue
            if (abs(lep.dz) > 0.1): continue
            if not presel (lep): continue #new
            
            if (genPartFlav == 1 or genPartFlav == 15):
                mva.fill("signal", score)
            elif (genPartFlav != 1 or genPartFlav != 15):
                mva.fill("bkg", score)
    
    print(" ---------------------------------------------------------------- ")        
    print("    * Finished iterating over events. Results:")
    print(" ---------------------------------------------------------------- ")
    mva.summarize()
    mva.write(outpath)
              
if __name__ == "__main__":
    opts, _ = add_parsing_opts()
    mode = opts.mode
    inpath = opts.inpath
    if not inpath: color_msg("Wrong path: %s"%inpath, "red")
    nfiles = opts.nfiles
    mode = opts.mode
    year = opts.year
    
    outpath = os.path.join("lepmva_results", year) 
    if not os.path.exists(outpath): 
        os.system("mkdir -p %s"%outpath)
    if "muon_legacy" in mode:
        function = mvacfgs.muon_legacy
    if "muon_df_train_pt5_tth" in mode:
        function = mvacfgs.muon_df_train_pt5_tth
    elif "muon_df_train_pt5_ttw" in mode:
        function = mvacfgs.muon_df_train_pt5_ttw
    elif "muon_pnet_train_pt5_tth" in mode:
        function = mvacfgs.muon_pnet_train_pt5_tth
    elif "muon_pnet_train_pt5_ttw" in mode:
        function = mvacfgs.muon_pnet_train_pt5_ttw
    
    elif "electron_legacy" in mode:
        function = mvacfgs.electron_legacy
    elif "electron_mvaISO" in mode:
        function = mvacfgs.electron_mvaISO
    elif "electron_mvaNOISO" in mode: 
        function = mvacfgs.electron_mvaNOISO
    elif "electron_pnet_wIso" in mode:
        function = mvacfgs.electron_pnet_wIso
    elif "electron_df_wIso" in mode:
        function = mvacfgs.electron_df_wIso
    elif "electron_pnet" in mode: 
        function = mvacfgs.electron_pnet
    elif "electron_df" in mode:   
        function = mvacfgs.electron_df
        
    # Get files for input
    mode_to_function = "electron" if "electron" in mode else "muon"
    files = os.listdir(inpath)[:nfiles]
    create_rootfiles(mode_to_function, inpath, files, function(year), outpath)
