""" Macro to see effect of electron veto maps in 2022EE """

import ROOT as r
import os

treespath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE/"
process = "WZto3LNu"

if __name__ == "__main__":
    # Open root file and friend
    f = r.TFile.Open( os.path.join(treespath, process + ".root") )
    t = f.Get("Events")
    #t.AddFriend( "Friends", os.path.join(treespath, "lepmva", process + "_Friend.root") )

    variable="int(LepGood_seediEtaOriX):LepGood_seediPhiOriY >> phieta(100,0,100,100,0,100)"
    
    selection=" && ".join([
        "LepGood_pt > 15",
        "(LepGood_eta + LepGood_deltaEtaSC) > 1.44",
        "abs(LepGood_dxy)<0.05",
        "abs(LepGood_dz)<0.1",
        "LepGood_sip3d < 8",
        "LepGood_miniPFRelIso_all < 0.4",
        "abs(LepGood_pdgId) == 11",
        #"LepGood_mvaTTH_run3 > 0.97",
    ])
    
    t.Draw(variable, selection, "COLZ")
    h = r.gDirectory.Get("phieta")
    
    c = r.TCanvas("c_vetomaps","", 800,600)

    h.SetTitle("Electron seed i#phi vs i#eta (Electron #eta > 1.44)")
    h.SetStats(False)

    h.GetYaxis().SetTitle("i#eta")
    h.GetXaxis().SetTitle("i#phi")
    r.gStyle.SetPaintTextFormat("4.3f")
    h.Draw("colz")
    c.SaveAs("electron_vetomaps_2022EE.pdf")
    c.SaveAs("electron_vetomaps_2022EE.png")
    c.SaveAs("electron_vetomaps_2022EE.root")
