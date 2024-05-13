""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
from optparse import OptionParser
import array
from optparse import OptionParser
import json

# Analysis libraries
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from functions import color_msg
import scripts.canvas as cv 
from scripts.ntuple_reader import ntuple_reader
from scripts.make_latex_table import dict_to_latex_table

# Specific trigger SF libraries
import scripts.triggerSFs.trigger_modes as trg

# hlt_trigger = "(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 || HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_TripleMu_12_10_5 || HLT_TripleMu_10_5_5_DZ || HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ || HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ || HLT_Ele32_WPTight_Gsf || HLT_IsoMu24)"
# reftrigger = "(HLT_PFMETNoMu110_PFMHTNoMu110_IDTight || HLT_PFMETNoMu120_PFMHTNoMu120_IDTight)"

# Turn off root gui mode
r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]", 
                                    description = "Main options for running WZ analysis")
    parser.add_option("--mode", dest = "mode", default = "inclusive",
            help = "Compute efficiencies with given criteria")
    parser.add_option("--hlt", dest = "hlt", action = "append",
            help = "HLT paths to measure efficiency over.")
    return parser.parse_args()

class trg_eff_calculator:
    """ Takes one reference trigger and one HLT trigger and computes the efficiency """
    
    def __init__(self, ntuple, hlt_trigger, reftrigger, baseline, name, filename):
        self.ntuple = ntuple
        self.baseline = baseline
        self.name = name.replace("/", "_")
        self.folder = name
        self.hlt_trigger = hlt_trigger
        self.reftrigger = reftrigger
        self.num = f"({hlt_trigger} && {reftrigger})"
        self.den = f"{reftrigger}"
        self.filename = filename
        self.compute_efficiency()
        self.compute_correlation()
        self.save_numbers()

    def compute_efficiency(self):
        """ Count how many events pass and fail the selections """
        self.hNumt = self.ntuple.draw( f"{self.num} > 0", "2, 0, 2", self.baseline, "hNumt", normToGenSum = False )
        self.hDent = self.ntuple.draw( f"{self.den} > 0", "2, 0, 2", self.baseline, "hDent", normToGenSum = False )

        self.pass_num = self.hNumt.GetBinContent(2)
        self.fail_num = self.hNumt.GetBinContent(1)
        self.pass_den = self.hDent.GetBinContent(2)
        self.fail_den = self.hDent.GetBinContent(1)        
        
        # Now properly create the efficiency object
        self.hNum = r.TH1D(self.name + "_num", "", 1, 0, 1)
        self.hDen = r.TH1D(self.name + "_den", "", 1, 0, 1)

        self.hNum.SetBinContent(1, self.pass_num)
        self.hDen.SetBinContent(1, self.pass_den)

        self.teff = r.TEfficiency(self.hNum, self.hDen)
        self.eff = self.teff.GetEfficiency(1)
        self.eff_errup = self.teff.GetEfficiencyErrorUp(1) 
        self.eff_errdn = self.teff.GetEfficiencyErrorLow(1) 

    def compute_correlation(self):
        """ Compute the correlation in the trigger SF measurement """

        if self.pass_num == 0: 
            self.correlation = -1
        else:
            self.hRef = self.ntuple.draw( f"{self.reftrigger} > 0", "2, 0, 2", self.baseline, "hNumt", normToGenSum = False)
            self.hHLT = self.ntuple.draw( f"{self.hlt_trigger} > 0", "2, 0, 2", self.baseline, "hDent", normToGenSum = False )
            self.correlation = (self.hRef.GetBinContent(2)*self.hHLT.GetBinContent(2))/(self.pass_num*(self.pass_num+self.fail_num))
    
    def save_numbers(self):
        """ Save the relevant values for the calculation """
        if not os.path.exists( self.folder ):
            os.system(f" mkdir -p {self.folder}")

        f = open(f"{self.folder}/{self.filename}", "w")
        results = {
            "pass_num" : self.pass_num,
            "pass_den" : self.pass_den,
            "fail_num" : self.fail_num,
            "fail_den" : self.fail_den,
            "corr" : self.correlation,
            "eff" : self.eff,
            "eff_errup" : self.eff_errup,
            "eff_errdn" : self.eff_errdn
        }

        f.write( json.dumps( results, indent = 4 ) )

    def summarize(self):
        """ Printout for debugging """
        print(f" + Proc: {self.name}")
        print(f"   - Pass num: {self.pass_num}")
        print(f"   - Fail num: {self.fail_num}")
        print(f"   - Pass den: {self.pass_den}")
        print(f"   - Fail den: {self.fail_den}")
        print(f"   - Correlation: {self.correlation}")
        print(f"   - Efficiency: {self.eff} +/- {self.eff_errup} +/- {self.eff_errdn}")

def recompute_efficiencies(ntuples, outpath, filename):
    """ Recompute the efficiencies merging up samples """
    # Take the first one
    hNum = deepcopy( ntuples[0].hNum )
    hDen = deepcopy( ntuples[0].hDen )

    for ntuple in ntuples[1:]:
        hNum.Add( ntuple.hNum )
        hDen.Add( ntuple.hDen )

    teff = r.TEfficiency(hNum, hDen)
    eff = teff.GetEfficiency(1)
    eff_errup = teff.GetEfficiencyErrorUp(1) 
    eff_errdn = teff.GetEfficiencyErrorLow(1)

    if not os.path.exists( outpath ):
        os.system(f" mkdir -p {outpath}")

    f = open(f"{outpath}/{filename}", "w")
    results = {
        "pass_num" : hNum.GetBinContent(1),
        "pass_den" : hDen.GetBinContent(1),
        "fail_num" : -1,
        "fail_den" : -1,
        "corr" : 1,
        "eff" : eff,
        "eff_errup" : eff_errup,
        "eff_errdn" : eff_errdn
    }

    f.write( json.dumps( results, indent = 4 ) )


def create_graph( effs, name, color ):
    """ Creates a TGraph with the efficiencies for each channel """

    gr = r.TGraphAsymmErrors(5)
    gr.SetName( name )
    gr.SetMarkerColor( color )
    gr.SetMarkerSize( 1 )
    gr.SetMarkerStyle( 20 )

    gr.SetLineWidth( 0 )

    for ipoint, eff in enumerate(effs):
        gr.SetPoint(ipoint, 2*ipoint + 1, eff.eff)
        gr.SetPointEYhigh(ipoint,  eff.eff_errup)
        gr.SetPointEYlow(ipoint, eff.eff_errup)
    
    return gr


if __name__ == "__main__":

    opts, args = add_parsing_opts()

    mcpath = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/"
    datapath = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/data/"
    ntuples = {
        "2022PreEE" : {
            "WZ" : ntuple_reader( 
              samplename = [
                  os.path.join(mcpath, "2022", "WZto3LNu.root/Events")
              ],
              friends = [ 
                  os.path.join(mcpath, "2022", "leptonJetRecleaning/WZto3LNu_Friend.root"), 
                  os.path.join(mcpath, "2022", "leptonBuilder/WZto3LNu_Friend.root"), 
              ],
              ftreename = "Friends"
            ),
            "Data_Run2022C" : ntuple_reader( 
              samplename = [
                  os.path.join(datapath, "2022", "JetMET_Run2022C.root/Events")
              ],
              friends = [ 
                  os.path.join(datapath, "2022", "leptonJetRecleaning/JetMET_Run2022C_Friend.root"), 
                  os.path.join(datapath, "2022", "leptonBuilder/JetMET_Run2022C_Friend.root"), 
              ],
              ftreename = "Friends"
            ),
            "Data_Run2022D" : ntuple_reader( 
              samplename = [
                  os.path.join(datapath, "2022", "JetMET_Run2022D.root/Events")
              ],
              friends = [ 
                  os.path.join(datapath, "2022", "leptonJetRecleaning/JetMET_Run2022D_Friend.root"), 
                  os.path.join(datapath, "2022", "leptonBuilder/JetMET_Run2022D_Friend.root"), 
              ],
              ftreename = "Friends"
            )
        },
        "2022PostEE" : {
            "WZ" : ntuple_reader( 
              samplename = [
                  os.path.join(mcpath, "2022EE", "WZto3LNu.root/Events")
              ],
              friends = [ 
                  os.path.join(mcpath, "2022EE", "leptonJetRecleaning/WZto3LNu_Friend.root"), 
                  os.path.join(mcpath, "2022EE", "leptonBuilder/WZto3LNu_Friend.root"), 
              ],
              ftreename = "Friends"
            ),
            "Data_Run2022E" : ntuple_reader( 
              samplename = [
                  os.path.join(datapath, "2022EE", "JetMET_Run2022E.root/Events"),
              ],
              friends = [ 
                  os.path.join(datapath, "2022EE", "leptonJetRecleaning/JetMET_Run2022E_Friend.root"), 
                  os.path.join(datapath, "2022EE", "leptonBuilder/JetMET_Run2022E_Friend.root"), 
              ],
              ftreename = "Friends"
            ),        
            "Data_Run2022F" : ntuple_reader( 
              samplename = [
                  os.path.join(datapath, "2022EE", "JetMET_Run2022F.root/Events"),
              ],
              friends = [ 
                  os.path.join(datapath, "2022EE", "leptonJetRecleaning/JetMET_Run2022F_Friend.root"), 
                  os.path.join(datapath, "2022EE", "leptonBuilder/JetMET_Run2022F_Friend.root"), 
              ],
              ftreename = "Friends"
            ),
            "Data_Run2022G" : ntuple_reader( 
              samplename = [
                  os.path.join(datapath, "2022EE", "JetMET_Run2022G.root/Events"),
              ],
              friends = [ 
                  os.path.join(datapath, "2022EE", "leptonJetRecleaning/JetMET_Run2022G_Friend.root"), 
                  os.path.join(datapath, "2022EE", "leptonBuilder/JetMET_Run2022G_Friend.root"), 
              ],
              ftreename = "Friends"
            )
         }
    }



    # Compute the efficiencies
    #  -- Below is the baseline selection
    baseline = [
        "nLepSel >= 3", 
        #"LepSel_isTight[0] && LepSel_isTight[1] && LepSel_isTight[2]",
        "MET_pt_central > 120",  
        "LepZ1_pt > 25", 
        "LepW_pt > 25",
    ]

    if opts.mode == "inclusive": 
        function = trg.inclusive
        title = "Inclusive phase space"
    elif opts.mode == "lowpt": 
        function = trg.lowpt
        title = r"15 < p_{T}(#ell_3) #leq 25 "
    elif opts.mode == "highpt": 
        function = trg.highpt
        title = r"p_{T}(#ell_3) > 25 "
    elif opts.mode == "barrel0": 
        function = trg.barrel0
        title = r"0 barrel leptons"
    elif opts.mode == "barrel1": 
        function = trg.barrel1
        title = r"1 barrel lepton"
    elif opts.mode == "barrel2": 
        function = trg.barrel2
        title = r"2 barrel leptons"
    elif opts.mode == "barrel3": 
        function = trg.barrel3
        title = r"3 barrel leptons"
    else:
        print(f" >> Mode {opts.mode} not available. ")

    hlt_trigger = "(" + " | ".join( opts.hlt ) + ")" 
    #reftrigger = "(HLT_PFMETNoMu110_PFMHTNoMu110_IDTight || HLT_PFMETNoMu120_PFMHTNoMu120_IDTight)"

    reftrigger = "(HLT_PFMETNoMu110_PFMHTNoMu110_IDTight || HLT_PFMETNoMu120_PFMHTNoMu120_IDTight || HLT_CaloJet500_NoJetID || HLT_AK8PFJet400_TrimMass30 || HLT_AK8PFJet500 || HLT_DiJet110_35_Mjj650_PFMET110 || HLT_PFHT800_PFMET75_PFMHT75_IDTight || HLT_PFHT700_PFMET85_PFMHT85_IDTight || HLT_PFHT500_PFMET100_PFMHT100_IDTight || HLT_PFHT1050 || HLT_PFJet500 || HLT_PFMET120_PFMHT120_IDTight || HLT_PFMETTypeOne140_PFMHT140_IDTight || HLT_TripleJet110_35_35_Mjj650_PFMET110)"

    # Get the selections
    selection_inclusive, caption_inclusive = function( selection = baseline, flav_cut = "1" )
    selection_eee, caption_eee = function( selection = deepcopy(baseline), flav_cut = "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2 == 0" )
    selection_eem, caption_eem = function( selection = deepcopy(baseline), flav_cut = "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2 == 1" )
    selection_mme, caption_mme = function( selection = deepcopy(baseline), flav_cut = "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2 == 2" )
    selection_mmm, caption_mmm = function( selection = deepcopy(baseline), flav_cut = "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2 == 3" )
    
    # Gather all the efficiencies
    # :: eee
    eff_data_Run2022C_eee  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022C"],  hlt_trigger, reftrigger, selection_eee, f"results/PreEE/2022C/eee/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022D_eee  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022D"],  hlt_trigger, reftrigger, selection_eee, f"results/PreEE/2022D/eee/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022E_eee  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022E"],  hlt_trigger, reftrigger, selection_eee, f"results/PostEE/2022E/eee/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022F_eee  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022F"],  hlt_trigger, reftrigger, selection_eee, f"results/PostEE/2022F/eee/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022G_eee  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022G"],  hlt_trigger, reftrigger, selection_eee, f"results/PostEE/2022G/eee/{opts.mode}", filename = "data_results.json" )
    
    eff_data_2022_eee = recompute_efficiencies(
        ntuples = [eff_data_Run2022C_eee, eff_data_Run2022D_eee], 
        outpath = f"results/PreEE/2022CD/eee/{opts.mode}",
        filename = "data_results.json"
    )
    eff_data_2022EE_eee = recompute_efficiencies(
        ntuples = [eff_data_Run2022E_eee, eff_data_Run2022F_eee, eff_data_Run2022G_eee], 
        outpath = f"results/PostEE/2022EFG/eee/{opts.mode}",
        filename = "data_results.json"
    )

    eff_mc_2022_eee        = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_eee, f"results/PreEE/2022CD/eee/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_eee      = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_eee, f"results/PostEE/2022EFG/eee/{opts.mode}", filename = "mc_results.json" )
    

    # :: eem
    eff_data_Run2022C_eem  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022C"],  hlt_trigger, reftrigger, selection_eem, f"results/PreEE/2022C/eem/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022D_eem  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022D"],  hlt_trigger, reftrigger, selection_eem, f"results/PreEE/2022D/eem/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022E_eem  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022E"],  hlt_trigger, reftrigger, selection_eem, f"results/PostEE/2022E/eem/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022F_eem  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022F"],  hlt_trigger, reftrigger, selection_eem, f"results/PostEE/2022F/eem/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022G_eem  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022G"],  hlt_trigger, reftrigger, selection_eem, f"results/PostEE/2022G/eem/{opts.mode}", filename = "data_results.json" )

    eff_data_2022_eem = recompute_efficiencies(
        ntuples = [eff_data_Run2022C_eem, eff_data_Run2022D_eem], 
        outpath = f"results/PreEE/2022CD/eem/{opts.mode}",
        filename = "data_results.json"
    )
    eff_data_2022EE_eem = recompute_efficiencies(
        ntuples = [eff_data_Run2022E_eem, eff_data_Run2022F_eem, eff_data_Run2022G_eem], 
        outpath = f"results/PostEE/2022EFG/eem/{opts.mode}",
        filename = "data_results.json"
    )

    eff_mc_2022_eem     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_eem, f"results/PreEE/2022CD/eem/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_eem   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_eem, f"results/PostEE/2022EFG/eem/{opts.mode}", filename = "mc_results.json" )
    

    # :: mme
    eff_data_Run2022C_mme  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022C"],  hlt_trigger, reftrigger, selection_mme, f"results/PreEE/2022C/mme/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022D_mme  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022D"],  hlt_trigger, reftrigger, selection_mme, f"results/PreEE/2022D/mme/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022E_mme  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022E"],  hlt_trigger, reftrigger, selection_mme, f"results/PostEE/2022E/mme/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022F_mme  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022F"],  hlt_trigger, reftrigger, selection_mme, f"results/PostEE/2022F/mme/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022G_mme  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022G"],  hlt_trigger, reftrigger, selection_mme, f"results/PostEE/2022G/mme/{opts.mode}", filename = "data_results.json" )


    eff_data_2022_mme = recompute_efficiencies(
        ntuples = [eff_data_Run2022C_mme, eff_data_Run2022D_mme], 
        outpath = f"results/PreEE/2022CD/mme/{opts.mode}",
        filename = "data_results.json"
    )
    eff_data_2022EE_eem = recompute_efficiencies(
        ntuples = [eff_data_Run2022E_mme, eff_data_Run2022F_mme, eff_data_Run2022G_mme], 
        outpath = f"results/PostEE/2022EFG/mme/{opts.mode}",
        filename = "data_results.json"
    )
    eff_mc_2022_mme     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_mme, f"results/PreEE/2022CD/mme/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_mme   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_mme, f"results/PostEE/2022EFG/mme/{opts.mode}", filename = "mc_results.json" )
    


    # :: mmm
    eff_data_Run2022C_mmm  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022C"],  hlt_trigger, reftrigger, selection_mmm, f"results/PreEE/2022C/mmm/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022D_mmm  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022D"],  hlt_trigger, reftrigger, selection_mmm, f"results/PreEE/2022D/mmm/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022E_mmm  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022E"],  hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/2022E/mmm/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022F_mmm  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022F"],  hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/2022F/mmm/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022G_mmm  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022G"],  hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/2022G/mmm/{opts.mode}", filename = "data_results.json" )

    eff_data_2022_mmm = recompute_efficiencies(
        ntuples = [eff_data_Run2022C_mmm, eff_data_Run2022D_mmm], 
        outpath = f"results/PreEE/2022CD/mmm/{opts.mode}",
        filename = "data_results.json"
    )
    eff_data_2022EE_mmm = recompute_efficiencies(
        ntuples = [eff_data_Run2022E_mmm, eff_data_Run2022F_mmm, eff_data_Run2022G_mmm], 
        outpath = f"results/PostEE/2022EFG/mmm/{opts.mode}",
        filename = "data_results.json"
    )

    eff_mc_2022_mmm     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_mmm, f"results/PreEE/2022CD/mmm/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_mmm   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/2022EFG/mmm/{opts.mode}", filename = "mc_results.json" )
    

    # :: Inclusive
    eff_data_Run2022C  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022C"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PreEE/2022C/inclusive/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022D  = trg_eff_calculator( ntuples["2022PreEE"]["Data_Run2022D"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PreEE/2022D/inclusive/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022E  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022E"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/2022E/inclusive/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022F  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022F"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/2022F/inclusive/{opts.mode}", filename = "data_results.json" )
    eff_data_Run2022G  = trg_eff_calculator( ntuples["2022PostEE"]["Data_Run2022G"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/2022G/inclusive/{opts.mode}", filename = "data_results.json" )


    eff_data_2022_mmm = recompute_efficiencies(
        ntuples = [eff_data_Run2022C, eff_data_Run2022D], 
        outpath = f"results/PreEE/2022CD/inclusive/{opts.mode}",
        filename = "data_results.json"
    )

    eff_data_2022EE_mmm = recompute_efficiencies(
        ntuples = [eff_data_Run2022E, eff_data_Run2022F, eff_data_Run2022G], 
        outpath = f"results/PostEE/2022EFG/inclusive/{opts.mode}",
        filename = "data_results.json"
    )

    eff_mc_2022     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_inclusive, f"results/PreEE/2022CD/inclusive/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/2022EFG/inclusive/{opts.mode}", filename = "mc_results.json" )
    




