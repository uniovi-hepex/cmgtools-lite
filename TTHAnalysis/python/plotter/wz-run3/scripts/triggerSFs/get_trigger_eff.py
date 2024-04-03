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
        self.hNumt = self.ntuple.draw( f"{self.num} > 0", "2, 0, 2", self.baseline, "hNumt" )
        self.hDent = self.ntuple.draw( f"{self.den} > 0", "2, 0, 2", self.baseline, "hDent" )

        self.pass_num = self.hNumt.GetBinContent(2)
        self.fail_num = self.hNumt.GetBinContent(1)
        self.pass_den = self.hDent.GetBinContent(2)
        self.fail_den = self.hDent.GetBinContent(1)        
        
        # Now properly create the efficiency object
        hNum = r.TH1D(self.name + "_num", "", 1, 0, 1)
        hDen = r.TH1D(self.name + "_den", "", 1, 0, 1)

        hNum.SetBinContent(1, self.pass_num)
        hDen.SetBinContent(1, self.pass_den)

        self.teff = r.TEfficiency(hNum, hDen)
        self.eff = self.teff.GetEfficiency(1)
        self.eff_errup = self.teff.GetEfficiencyErrorUp(1) 
        self.eff_errdn = self.teff.GetEfficiencyErrorLow(1) 

    def compute_correlation(self):
        """ Compute the correlation in the trigger SF measurement """

        if self.pass_num == 0: 
            self.correlation = -1
        else:
            self.hRef = self.ntuple.draw( f"{self.reftrigger} > 0", "2, 0, 2", self.baseline, "hNumt" )
            self.hHLT = self.ntuple.draw( f"{self.hlt_trigger} > 0", "2, 0, 2", self.baseline, "hDent" )
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
            "WZ" : ntuple_reader( os.path.join(mcpath, "2022"), "WZto3LNu" ),
            "Data" : ntuple_reader( os.path.join(datapath, "2022"), ["JetMET_Run2022D", "JetMET_Run2022C"] ),
            #"JetMET_Run2022C" : ntuple_reader( os.path.join(datapath, "2022"), "JetMET_Run2022C" ),
            #"JetMET_Run2022D" : ntuple_reader( os.path.join(datapath, "2022"), "JetMET_Run2022D" )
        },
        "2022PostEE" : {
            "WZ" : ntuple_reader( os.path.join(mcpath, "2022EE"), "WZto3LNu" ),
            "Data" : ntuple_reader( os.path.join(datapath, "2022EE"), ["JetMET_Run2022E", "JetMET_Run2022F", "JetMET_Run2022G"] ),
            #"JetMET_Run2022E" : ntuple_reader( os.path.join(datapath, "2022EE), "JetMET_Run2022E" ),
            #"JetMET_Run2022F" : ntuple_reader( os.path.join(datapath, "2022EE), "JetMET_Run2022F" ),
            #"JetMET_Run2022G" : ntuple_reader( os.path.join(datapath, "2022EE), "JetMET_Run2022G" )
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
    eff_mc_2022_eee     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_eee, f"results/PreEE/eee/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_eee   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_eee, f"results/PostEE/eee/{opts.mode}", filename = "mc_results.json" )
    eff_data_2022_eee   = trg_eff_calculator( ntuples["2022PreEE"]["Data"],  hlt_trigger, reftrigger, selection_eee, f"results/PreEE/eee/{opts.mode}", filename = "data_results.json" )
    eff_data_2022EE_eee = trg_eff_calculator( ntuples["2022PostEE"]["Data"], hlt_trigger, reftrigger, selection_eee, f"results/PostEE/eee/{opts.mode}", filename = "data_results.json" )

    # :: eem
    eff_mc_2022_eem     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_eem, f"results/PreEE/eem/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_eem   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_eem, f"results/PostEE/eem/{opts.mode}", filename = "mc_results.json" )
    eff_data_2022_eem   = trg_eff_calculator( ntuples["2022PreEE"]["Data"],  hlt_trigger, reftrigger, selection_eem, f"results/PreEE/eem/{opts.mode}", filename = "data_results.json" )
    eff_data_2022EE_eem = trg_eff_calculator( ntuples["2022PostEE"]["Data"], hlt_trigger, reftrigger, selection_eem, f"results/PostEE/eem/{opts.mode}", filename = "data_results.json" )

    # :: mme
    eff_mc_2022_mme     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_mme, f"results/PreEE/mme/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_mme   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_mme, f"results/PostEE/mme/{opts.mode}", filename = "mc_results.json" )
    eff_data_2022_mme   = trg_eff_calculator( ntuples["2022PreEE"]["Data"],  hlt_trigger, reftrigger, selection_mme, f"results/PreEE/mme/{opts.mode}", filename = "data_results.json" )
    eff_data_2022EE_mme = trg_eff_calculator( ntuples["2022PostEE"]["Data"], hlt_trigger, reftrigger, selection_mme, f"results/PostEE/mme/{opts.mode}", filename = "data_results.json" )


    # :: mmm
    eff_mc_2022_mmm     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_mmm, f"results/PreEE/mmm/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE_mmm   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/mmm/{opts.mode}", filename = "mc_results.json" )
    eff_data_2022_mmm   = trg_eff_calculator( ntuples["2022PreEE"]["Data"],  hlt_trigger, reftrigger, selection_mmm, f"results/PreEE/mmm/{opts.mode}", filename = "data_results.json" )
    eff_data_2022EE_mmm = trg_eff_calculator( ntuples["2022PostEE"]["Data"], hlt_trigger, reftrigger, selection_mmm, f"results/PostEE/mmm/{opts.mode}", filename = "data_results.json" )

    # :: Inclusive
    eff_mc_2022     = trg_eff_calculator( ntuples["2022PreEE"]["WZ"],    hlt_trigger, reftrigger, selection_inclusive, f"results/PreEE/inclusive/{opts.mode}", filename = "mc_results.json" )
    eff_mc_2022EE   = trg_eff_calculator( ntuples["2022PostEE"]["WZ"],   hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/inclusive/{opts.mode}", filename = "mc_results.json" )
    eff_data_2022   = trg_eff_calculator( ntuples["2022PreEE"]["Data"],  hlt_trigger, reftrigger, selection_inclusive, f"results/PreEE/inclusive/{opts.mode}", filename = "data_results.json" )
    eff_data_2022EE = trg_eff_calculator( ntuples["2022PostEE"]["Data"], hlt_trigger, reftrigger, selection_inclusive, f"results/PostEE/inclusive/{opts.mode}", filename = "data_results.json" )


    # Make a plot    
#    make_plot( 
#        [eff_mc_2022_eee, eff_mc_2022_eem, eff_mc_2022_mme, eff_mc_2022_mmm, eff_mc_2022], 
#        [eff_data_2022_eee, eff_data_2022_eem, eff_data_2022_mme, eff_data_2022_mmm, eff_data_2022], 
#        #[eff_mc_2022], 
#        #[eff_data_2022], 
#        f"{opts.mode}_2022PreEE", 
#        title
#    )
#    
#
#    make_plot( 
#        [eff_mc_2022EE_eee, eff_mc_2022EE_eem, eff_mc_2022EE_mme, eff_mc_2022EE_mmm, eff_mc_2022EE], 
#        [eff_data_2022EE_eee, eff_data_2022EE_eem, eff_data_2022EE_mme, eff_data_2022EE_mmm, eff_data_2022EE], 
#        #[eff_mc_2022EE], 
#        #[eff_data_2022EE], 
#        f"{opts.mode}_2022PostEE", 
#        title
#    )
    



        





    
    
    
    
    
    



