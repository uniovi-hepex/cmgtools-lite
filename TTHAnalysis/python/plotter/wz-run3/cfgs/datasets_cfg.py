import os, re, sys
from copy import deepcopy
import ROOT 
# Add some other functions useful for debugging
sys.path.append( os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3/"))
from utils.datasets import dataset_mc, dataset_data, dataset_fr, dataset_fr_data, mca
from cfgs.samples_dbspaths_cfg import dbs_mc, dbs_data
from functions import color_msg

mcas = {
    # ---- Specials
    "data" : mca("data", ["data"]),
    "signal" : mca("signal", ["WZ"]),
    # ---- Backgrounds
    "prompts" : mca("prompts", ["ZZ", "ttX", "TZQ", "Others", "VVV", "VH"]),
    "mcfakes" : mca("mcfakes", ["Fakes_TT", "Fakes_ST", "Fakes_DY", "Fakes_VV", "Wjets"]),
    "convs" : mca("convs", ["convs"])
}

mcas_fr = {
    "data" : mca("data", ["data"]),
    "qcd" : mca("qcd", ["qcd"]),
    "ewk" : mca("ewk", ["ewk"]),
    "top" : mca("top", ["top"])
}

# Add datasets to the MCA objects
# ======================== For the main analysis ========================== #
# ---- data
# 2022
# + Era C
mcas["data"].add_dataset( dataset_data(dbs_data["Muon_Run2022C"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["EGamma_Run2022C"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["MuonEG_Run2022C"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["JetMET_Run2022C"]), "data" )
# + Era D
mcas["data"].add_dataset( dataset_data(dbs_data["Muon_Run2022D"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["EGamma_Run2022D"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["MuonEG_Run2022D"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["JetMET_Run2022D"]), "data" )
# + Era E
mcas["data"].add_dataset( dataset_data(dbs_data["Muon_Run2022E"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["EGamma_Run2022E"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["MuonEG_Run2022E"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["JetMET_Run2022E"]), "data" )
# + Era F
mcas["data"].add_dataset( dataset_data(dbs_data["Muon_Run2022F"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["EGamma_Run2022F"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["MuonEG_Run2022F"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["JetMET_Run2022F"]), "data" )
# + Era G
mcas["data"].add_dataset( dataset_data(dbs_data["Muon_Run2022G"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["EGamma_Run2022G"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["MuonEG_Run2022G"]), "data" )
mcas["data"].add_dataset( dataset_data(dbs_data["JetMET_Run2022G"]), "data" )

# ---- Signal
mcas["signal"].add_dataset( dataset_mc(dbs_mc["WZto3LNu"], "ROOT.kOrange"), "WZ" )


# ---- Prompts
# + ZZ
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["ZZto4L"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGlutoContinto2Zto2E2Mu"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGluToContinto2Zto2E2Tau"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGluToContinto2Zto2Mu2Tau"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGlutoContinto2Zto4E"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGlutoContinto2Zto4Mu"], "ROOT.kGreen+1"), "ZZ")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["GluGlutoContinto2Zto4Tau"], "ROOT.kGreen+1"), "ZZ")

# + TZQ
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TZQB"], "ROOT.kCyan"), "TZQ")

# + TTX
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTG_1Jets_PTG_10to100"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTG_1Jets_PTG_100to200"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTG_1Jets_PTG_200"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTHtoNon2B"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTLNu_1Jets"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTLL_MLL_50"], "ROOT.kViolet-3"), "ttX")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTLL_MLL_4to50"], "ROOT.kViolet-3"), "ttX")

# + Others
#mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTWW"], "ROOT.kSpring+2 "), "Others")
#mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTTT"], "ROOT.kSpring+2 "), "Others")
#mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTHH"], "ROOT.kSpring+2 "), "Others")
#mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTWZ"], "ROOT.kSpring+2 "), "Others")
#mcas["prompts"].add_dataset( dataset_mc(dbs_mc["TTWH"], "ROOT.kSpring+2 "), "Others")

# + Tribosons
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["WWW_4F"], "ROOT.kRed+1"), "VVV")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["WWZ_4F"], "ROOT.kRed+1"), "VVV")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["WZZ"], "ROOT.kRed+1"), "VVV")
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["ZZZ"], "ROOT.kRed+1"), "VVV")

# + VH
mcas["prompts"].add_dataset( dataset_mc(dbs_mc["VH_HtoNonbb"], "ROOT.kRed-1"), "VH")


# ---- MC fakes
# + EWK fakes
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["ZZto2L2Q"], "ROOT.kGray+1"), "Fakes_VV")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["ZZto2L2Nu"], "ROOT.kGray+1"), "Fakes_VV")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["WWto2L2Nu"], "ROOT.kGray+1"), "Fakes_VV")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["DYto2L_2Jets_MLL_50"], "ROOT.kGray+9"), "Fakes_DY")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["DYto2L_2Jets_MLL_10to50"], "ROOT.kGray+9"), "Fakes_DY")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["WtoLNu_2Jets"], "ROOT.kViolet+7"), "Wjets")

# + TOP fakes
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["TTtoLNu2Q"], "ROOT.kGray+2 "), "Fakes_TT")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["TTto2L2Nu"], "ROOT.kGray+2 "), "Fakes_TT")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["TWminusto2L2Nu"], "ROOT.kGray+3 "), "Fakes_ST")
mcas["mcfakes"].add_dataset( dataset_mc(dbs_mc["TbarWplusto2L2Nu"], "ROOT.kGray+3 "), "Fakes_ST")

# ---- Convs
mcas["convs"].add_dataset( dataset_mc(dbs_mc["WGtoLNuG_PTG_10to100"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["WGtoLNuG_PTG_100to200"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["WGtoLNuG_PTG_200"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["WZGtoLNuZG"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-4to50_PTG-10to100"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-4to50_PTG-100to200"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-4to50_PTG-200"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-100to200"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-10to50"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-50to100"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-200to400"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-400to600"], "ROOT.kOrange-3"), "convs")
mcas["convs"].add_dataset( dataset_mc(dbs_mc["DYGto2LG_MLL-50_PTG-600"], "ROOT.kOrange-3"), "convs")

# ======================== For the FR analysis ========================== #
# Data
mcas_fr["data"].add_dataset( dataset_fr_data(dbs_data["Muon_Run2022F"]), "data" )
#mcas_fr["data"].add_dataset( dataset_fr_data(dbs_data["Muon_Run2022G"]), "data" )

# EWK
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["ZZto2L2Q"], "ROOT.kGray+9"), "ewk")
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["ZZto2L2Nu"], "ROOT.kGray+9"), "ewk")
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["WWto2L2Nu"], "ROOT.kGray+9"), "ewk")
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["DYto2L_2Jets_MLL_50"], "ROOT.kGray+9"), "ewk")
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["DYto2L_2Jets_MLL_10to50"], "ROOT.kGray+9"), "ewk")
mcas_fr["ewk"].add_dataset( dataset_fr(dbs_mc["WtoLNu_2Jets"], "ROOT.kGray+9"), "ewk")

# TOP
mcas_fr["top"].add_dataset( dataset_fr(dbs_mc["TTtoLNu2Q"], "ROOT.kGray+2 "), "top")

# QCD
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_10to30_EMEnriched'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_30to50_EMEnriched'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_50to80_EMEnriched'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_80to120_EMEnriched'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_120to170_EMEnriched'], "ROOT.kPink+1"), "qcd")
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-170to300_EMEnriched'], "ROOT.kPink+1"), "qcd")
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT_300_EMEnriched'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-15to20_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")     
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-20to30_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")     
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-30to50_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")     
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-50to80_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")     
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-80to120_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")    
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-120to170_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")   
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-170to300_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")   
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-300to470_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")   
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-470to600_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")   
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-600to800_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")   
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-800to1000_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")  
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc["QCD_PT-1000_MuEnrichedPt5"], "ROOT.kPink+1"), "qcd")       
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-20to30_bcToE'], "ROOT.kPink+1"), "qcd") 
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-30to80_bcToE'], "ROOT.kPink+1"), "qcd")
mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-80to170_bcToE'], "ROOT.kPink+1"), "qcd")
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-170to250_bcToE'], "ROOT.kPink+1"), "qcd") 
#mcas_fr["qcd"].add_dataset( dataset_fr(dbs_mc['QCD_PT-250_bcToE'], "ROOT.kPink+1"), "qcd")

if __name__ == "__main__":
    # Print out a summary
    for mcagroup, mcaitem in mcas.items():
        color_msg(" >> MCA: {}".format(mcagroup), "blue")
        for group, dsets in mcaitem.get_datasets().items():
            color_msg("   + Group: {}".format(group), "yellow")
            for dset in dsets:
                color_msg("     o Dataset: {}".format(dset.processname), "green")
                color_msg("     o NanoAOD 2022: {}".format(dset.get_pure_nanoaod("2022")))
                color_msg("     o NanoAOD 2022EE: {}".format(dset.get_pure_nanoaod("2022PostEE")))

    for mcagroup, mcaitem in mcas_fr.items():
        color_msg(" >> MCA: {}".format(mcagroup), "blue")
        for group, dsets in mcaitem.get_datasets().items():
            color_msg("   + Group: {}".format(group), "yellow")
            for dset in dsets:
                color_msg("     o Dataset: {}".format(dset.processname), "green")
                color_msg("     o NanoAOD 2022: {}".format(dset.get_pure_nanoaod("2022")))
                color_msg("     o NanoAOD 2022EE: {}".format(dset.get_pure_nanoaod("2022PostEE")))
            
