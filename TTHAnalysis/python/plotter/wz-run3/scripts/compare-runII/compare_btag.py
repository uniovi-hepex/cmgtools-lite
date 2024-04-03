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

# Turn off root gui mode
r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]", 
                                    description = "Main options for running WZ analysis")
    return parser.parse_args()

if __name__ == "__main__":

    opts, args = add_parsing_opts()

    legacy_path = f"/lustrefs/hdd_pool_dir/HeppyTrees/RA7/nanoAODv5_2018_skimWZ/"
    run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE"
    

    legacy_ntuple = ntuple_reader( 
        samplename = [ 
            #os.path.join( legacy_path, "WZTo3LNu_pow/treeProducerSusyMultilepton/tree.root/Events") 
            os.path.join( legacy_path, "TTTo2L2Nu_part0/treeProducerSusyMultilepton/tree.root/Events") 
        ],
        friends = [ 
            os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    run3_ntuple = ntuple_reader( 
        samplename = [ 
            #os.path.join( run3_path, "WZto3LNu.root/Events") 
            os.path.join( run3_path, "TTto2L2Nu_part1.root/Events") 
        ],
        friends = [ 
            os.path.join( run3_path, "leptonJetRecleaning_Elewp090/TTto2L2Nu_part1_Friend.root"),
            os.path.join( run3_path, "leptonBuilder_Elewp090/TTto2L2Nu_part1_Friend.root"),
            os.path.join( run3_path, "scalefactors_Elewp090/TTto2L2Nu_part1_Friend.root"),
            #os.path.join( run3_path, "leptonJetRecleaning_Elewp090/WZto3LNu_Friend.root"),
            #os.path.join( run3_path, "leptonBuilder_Elewp090/WZto3LNu_Friend.root"),
            #os.path.join( run3_path, "scalefactors_Elewp090/WZto3LNu_Friend.root"),
        ],
        ftreename = "Friends"
    )

    sr = [ 
      "(1)",
      "(nLepSel >= 3)",
      "(LepSel_isTight[0] && LepSel_isTight[1] && LepSel_isTight[2])",
      "(LepZ1_pt >= 25 && LepZ2_pt >= 15 && LepW_pt >= 25)",
      "(abs(LepSel_pdgId[0]) < 15 && abs(LepSel_pdgId[1]) < 15 && abs(LepSel_pdgId[2]) < 15 && nOSSF_3l >= 1)",
      "(m3L >= 100)",
      "(MET_pt_central > 35)",
      "(nLepGood < 4)",
      "(nBJetTight25_Mini == 0)",
      "(abs(mll_3l - 91.16) < 15)",
      "(minMllSFOS_Mini > 4 || minMllSFOS_Mini == -1)"
    ]
    sr_sel = " && ".join(sr)

    # Plot the distributions of btag score for different taggers in Run 2 legacy and Run 3
    hlegacy_deepcsv = legacy_ntuple.draw("bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Up", "200,-0.02,0.02", f"{sr_sel} && (bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Up) != 0", "legacy_leading_deepcsv", normToGenSum = False)
    hlegacy_deepcsv_dn = legacy_ntuple.draw("bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Dn", "200,-0.02,0.02", f"{sr_sel} && (bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Dn) != 0", "legacy_leading_deepcsv_dn", normToGenSum = False)

    #hlegacy_deepjet = legacy_ntuple.draw("Jet_btagDeepFlavB[iJSel_Mini[0]]", "50,0,1", "abs(Jet_hadronFlavour[iJSel_Mini[0]]) == 5", "legacy_leading_deepcsv", normToGenSum = False)
    hrun3           = run3_ntuple.draw("bTagWeight - bTagWeight_btag_correlatedUp", "200,-0.02, 0.02", f"{sr_sel} && (bTagWeight - bTagWeight_btag_correlatedUp) != 0", "run3_leading_deepjet", normToGenSum = False)
    hrun3_dn           = run3_ntuple.draw("bTagWeight - bTagWeight_btag_correlatedDown", "200,-0.02, 0.02", f"{sr_sel} && (bTagWeight - bTagWeight_btag_correlatedDown) != 0", "run3_leading_deepjet_dn", normToGenSum = False)


    hrun3.SetFillColor(0)
    hrun3.SetLineColor(2)
    hrun3.SetLineWidth(2)
    hrun3.GetYaxis().SetRangeUser(0, 1.0)
    hrun3.Scale( 1 / hrun3.Integral() )
    hrun3.Rebin(10)
    hrun3.SetTitle("bTagWeight variations (Run 3 -- DeepJET)")

    hrun3_dn.SetFillColor(0)
    hrun3_dn.SetLineColor(2)
    hrun3_dn.SetLineWidth(2)
    hrun3_dn.SetLineStyle(9)
    hrun3_dn.Scale( 1 / hrun3_dn.Integral() )
    hrun3_dn.Rebin(10)
    hrun3_dn.SetTitle("")

    legend_run3 = r.TLegend(0.2, 0.6, 0.8, 0.75)
    legend_run3.SetBorderSize(0)
    legend_run3.AddEntry( hrun3, "Variation up", "l" )
    legend_run3.AddEntry( hrun3_dn, "Variation down", "l" )   

    c = r.TCanvas("crun3", "", 600, 600)
    hrun3.Draw("hist")
    hrun3_dn.Draw("hist same")
    legend_run3.Draw("same")
    c.SaveAs("btag_weight_run3.png")

    c = r.TCanvas("c", "", 600, 600)
    # deepcsv up
    hlegacy_deepcsv.SetFillColor(0)
    hlegacy_deepcsv.SetLineColor(2)
    hlegacy_deepcsv.SetLineWidth(2)
    hlegacy_deepcsv.Rebin(10)
    hlegacy_deepcsv.GetYaxis().SetRangeUser(0, 1.0)
    hlegacy_deepcsv.Scale( 1 / hlegacy_deepcsv.Integral() )
    hlegacy_deepcsv.SetTitle("bTagWeight variations (Run II -- DeepCSV)")

    # deepcsv dn
    hlegacy_deepcsv_dn.SetFillColor(0)
    hlegacy_deepcsv_dn.SetLineColor(2)
    hlegacy_deepcsv_dn.SetLineWidth(2)
    hlegacy_deepcsv_dn.Rebin(10)
    hlegacy_deepcsv_dn.SetLineStyle(9)
    hlegacy_deepcsv_dn.Scale( 1 / hlegacy_deepcsv_dn.Integral() )

    legend_legacy = r.TLegend(0.2, 0.6, 0.8, 0.75)
    legend_legacy.SetBorderSize(0)
    legend_legacy.AddEntry( hlegacy_deepcsv, "Variation up", "l" )
    legend_legacy.AddEntry( hlegacy_deepcsv_dn, "Variation down", "l" )

    hlegacy_deepcsv.Draw("hist")
    hlegacy_deepcsv_dn.Draw("hist same")
    legend_legacy.Draw("same")
    c.SaveAs("btag_weight_legacy.png")
