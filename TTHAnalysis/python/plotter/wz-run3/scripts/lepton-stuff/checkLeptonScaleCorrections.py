""" Macro to see effect of electron energy corrections on the signal """
import ROOT as r
import os
from copy import deepcopy

treespath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE/"
process = "WZto3LNu"

if __name__ == "__main__":
    # Open root file and friend
    f = r.TFile.Open( os.path.join(treespath, process + ".root") )
    t = f.Get("Events")
    t.AddFriend( "Friends", os.path.join(treespath, "leptonEnergyCorrections", process + "_Friend.root") )
    
    # ---- Electrons
    selection=" && ".join([
        "LepGood_pt > 15",
        "abs(LepGood_eta) < 2.5",
        "abs(LepGood_dxy)<0.05",
        "abs(LepGood_dz)<0.1",
        "LepGood_sip3d < 8",
        "LepGood_miniPFRelIso_all < 0.4",
        "abs(LepGood_pdgId) == 11",
        #"LepGood_mvaTTH_run3 > 0.97",
    ])
    
    t.Draw("LepGood_correctedpt >> histo_correctedpt(20, 0, 200)", selection, "h")
    t.Draw("LepGood_correctedptSmearUp >> histo_correctedpt_SmearUp(20, 0, 200)", selection, "h_SmearUp")
    t.Draw("LepGood_correctedptSmearUp >> histo_correctedpt_SmearDown(20, 0, 200)", selection, "h_SmearDown")
    t.Draw("LepGood_correctedptScaleUp >> histo_correctedpt_ScaleUp(20, 0, 200)", selection, "h_ScaleUp")
    t.Draw("LepGood_correctedptScaleUp >> histo_correctedpt_ScaleDown(20, 0, 200)", selection, "h_ScaleDown")
    t.Draw("LepGood_pt >> histo_pt(20, 0, 200)", selection, "h")

    histo_correctedpt = r.gDirectory.Get("histo_correctedpt")
    histo_correctedpt_SmearUp = r.gDirectory.Get("histo_correctedpt_SmearUp")
    histo_correctedpt_SmearDown = r.gDirectory.Get("histo_correctedpt_SmearDown")
    histo_correctedpt_ScaleUp = r.gDirectory.Get("histo_correctedpt_ScaleUp")
    histo_correctedpt_ScaleDown = r.gDirectory.Get("histo_correctedpt_ScaleDown")
    histo_pt = r.gDirectory.Get("histo_pt")

    # Make ratios
    ratio_smearUp   = deepcopy(histo_correctedpt)
    ratio_smearUp.Divide(histo_correctedpt_SmearUp)
    ratio_smearDown = deepcopy(histo_correctedpt)
    ratio_smearDown.Divide(histo_correctedpt_SmearDown)
    ratio_scaleUp   = deepcopy(histo_correctedpt)
    ratio_scaleUp.Divide(histo_correctedpt_ScaleUp)
    ratio_scaleDown = deepcopy(histo_correctedpt)
    ratio_scaleDown.Divide(histo_correctedpt_ScaleDown)
    ratio_pt = deepcopy(histo_correctedpt)
    ratio_pt.Divide(histo_pt)

    l = r.TLegend(.7, .25, .79, .8)
    l.SetFillColor(0)
    l.SetShadowColor(0)
    l.SetTextFont(42)
    l.SetTextSize( 0.027)
    l.SetNColumns(1)
    l.SetBorderSize(0)
    
    c = r.TCanvas("c_vetomaps","", 800,600)
    topSpamSize=1.2
    plotformat = (600,600)
    height = plotformat[1]+150
    c.Divide(1, 2)
    p1 = r.TPad("pad1","pad1",0,0.30,1,1)
    p1.SetTopMargin(p1.GetTopMargin()*topSpamSize)
    p1.SetBottomMargin(0)
    p1.Draw()
    p1.SetLogy()
    p2 = r.TPad("pad2","pad2",0,0,1,0.30)
    p2.SetTopMargin(0)
    p2.SetBottomMargin(0.3)
    p2.SetFillStyle(0)
    p2.Draw()
    p1.cd()

    histo_correctedpt.SetTitle(r"Electron p_{T} corrections")
    histo_correctedpt.SetStats(False)

    histo_correctedpt.GetXaxis().SetTitleSize(0)
    histo_correctedpt.GetYaxis().SetTitle("Events")
    r.gStyle.SetPaintTextFormat("4.3f")
    
    histo_correctedpt.SetLineColor(1)
    histo_correctedpt.SetLineWidth(3)
    
    histo_correctedpt_SmearUp.SetLineColor(2)
    histo_correctedpt_SmearUp.SetLineWidth(3)
    ratio_smearUp.SetLineColor(2)
    ratio_smearUp.SetLineWidth(3)
    
    histo_correctedpt_SmearDown.SetLineColor(3)
    histo_correctedpt_SmearDown.SetLineWidth(3)
    ratio_smearDown.SetLineColor(3)
    ratio_smearDown.SetLineWidth(3)
    
    histo_correctedpt_ScaleUp.SetLineColor(4)
    histo_correctedpt_ScaleUp.SetLineWidth(3)
    ratio_scaleUp.SetLineColor(4)
    ratio_scaleUp.SetLineWidth(3)
    
    histo_correctedpt_ScaleDown.SetLineColor(5)
    histo_correctedpt_ScaleDown.SetLineWidth(3)
    ratio_scaleDown.SetLineColor(5)
    ratio_scaleDown.SetLineWidth(3)
    
    histo_pt.SetLineColor(6)
    histo_pt.SetLineWidth(3)
    ratio_pt.SetLineColor(6)
    ratio_pt.SetLineWidth(3)
    
    histo_correctedpt.Draw("hist")
    histo_correctedpt_SmearUp.Draw("hist same")
    histo_correctedpt_SmearDown.Draw("hist same")
    histo_correctedpt_ScaleUp.Draw("hist same")
    histo_correctedpt_ScaleDown.Draw("hist same")
    histo_pt.Draw("hist same")

    l.AddEntry(histo_correctedpt, "Corrected. p_{T}",  "l")
    l.AddEntry(histo_correctedpt_SmearUp, "Corrected. p_{T} (smear up)", "l")
    l.AddEntry(histo_correctedpt_SmearDown, "Corrected. p_{T} (smear down)", "l")
    l.AddEntry(histo_correctedpt_ScaleUp,"Corrected. p_{T} (scale up)", "l")
    l.AddEntry(histo_correctedpt_ScaleDown, "Corrected. p_{T} (scale down)", "l")
    l.AddEntry(histo_pt,  "Uncorr. p_{T}", "l")

    l.Draw("same")
    p2.cd()
    ratio_smearUp.SetStats(False)
    ratio_smearUp.Draw("e1")
    ratio_smearUp.GetYaxis().SetRangeUser(0.9, 1.1)
    ratio_smearUp.GetYaxis().SetLabelSize(0.08)
    ratio_smearUp.GetXaxis().SetLabelSize(0.1)

    ratio_smearUp.GetYaxis().SetNdivisions(505)

    ratio_smearUp.SetTitle("")
    ratio_smearUp.GetYaxis().SetTitleSize(0.2)
    ratio_smearUp.GetYaxis().SetTitle("Ratio")
    ratio_smearUp.GetXaxis().SetTitle(r"Electron p_{T}")
    ratio_smearUp.GetXaxis().SetTitleSize(0.1)


    ratio_smearDown.Draw("e1 same")
    ratio_scaleUp.Draw("e1 same")
    ratio_scaleDown.Draw("e1 same")
    ratio_pt.Draw("e1 same")
    
    c.SaveAs("electron_lepEnergyCorrections_2022EE.pdf")
    c.SaveAs("electron_lepEnergyCorrections_2022EE.png")
    c.SaveAs("electron_lepEnergyCorrections_2022EE.root")
