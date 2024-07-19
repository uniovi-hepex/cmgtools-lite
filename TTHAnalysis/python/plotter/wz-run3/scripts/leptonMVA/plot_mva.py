""" Script to plot MVA performance plots """
import ROOT as r
from copy import deepcopy
import os,sys
from optparse import OptionParser
import array as ar
import numpy as np
from array import array

r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from functions import color_msg
import scripts.canvas as cv 

class histo(object):
    def __init__(self, file, legend = ""):
        self.file = file
        self.name = file.split("/")[-1].split("_mva")[0] 
        if "mvaISO" in self.file: self.name += "_mvaISO"
        print(self.name)
        
        self.legend = legend
        self.histos = {}
        self.open_file()
        
        self.yields_fake = self.get_yields( self.histos["bkg"] )
        self.yields_sig = self.get_yields( self.histos["signal"] )

        self.roc = self.get_roc( self.histos["signal"], self.histos["bkg"] )
        self.significance = self.get_significance(self.histos["signal"], self.histos["bkg"])
        return
    
    def open_file(self):
        f = r.TFile.Open(self.file)
        nametofetch = self.name.replace("_ttH", "") 
        self.histos["signal"] = deepcopy(f.Get("h_signal_%s"%nametofetch))
        self.histos["signal_total"] = deepcopy(f.Get("h_signal_%s_total"%nametofetch))
        self.histos["bkg"] = deepcopy(f.Get("h_bkg_%s"%nametofetch))
        self.histos["bkg_total"] = deepcopy(f.Get("h_bkg_%s_total"%nametofetch))
        print(self.histos) 
        f.Close()
        return
    
    def get_yields(self, h):
        """ Returns the number of anything per MVA score in a TGraph. """
        gr = r.TGraph()
        nbins = h.GetNbinsX() 
        for bini in range(1, 1+nbins):
            x_point = h.GetBinLowEdge(bini)
            yields = h.Integral(bini, 1+nbins)
            eff = yields/h.Integral()
            gr.SetPoint(bini-1, x_point, eff)
        gr.SetName(self.name)
        return gr
    
    def get_roc(self, sig, bkg):
        """ Returns a ROC curve: 
        That is the integral for a given range of bins (WP)
        of signal over background 
        """
        integral_sig = sig.Integral()
        integral_bkg = bkg.Integral()

        eff_s = 0
        eff_b = 0
        
        roc = r.TGraph()
        nbins = sig.GetNbinsX()
        for b in range(1, 1+nbins):
            S = sig.Integral(b, nbins+1)
            B = bkg.Integral(b, nbins+1)
            eff_sig = S / integral_sig
            eff_bkg = B / integral_bkg
            roc.SetPoint(b-1, eff_bkg, eff_sig)
    
        roc.SetName(self.name)
        return roc
    
    def get_significance(self, h_sig, h_bkg, kind = 2):
        """ Function to get a significant curve of different kinds:
            kind=1: S/B
            kind=2: S/sqrt(B)
            kind=3: S/sqrt(S+B)
        """

        gr = r.TGraph()
        nbins = h_sig.GetNbinsX() 
        for i in range(1, 1+nbins):
            S = h_sig.Integral(i, nbins+1)
            B = h_bkg.Integral(i, nbins+1)

            #x = -1 + i*0.002
            x = h_sig.GetBinCenter(i)
            if B != 0:
                if kind == 0:
                    gr.SetPoint(i-1, x, S/B)
                elif kind == 1:
                    gr.SetPoint(i-1, x, S/np.sqrt(B))
                elif kind == 2:
                    gr.SetPoint(i-1, x, S/np.sqrt(S+B))
                else:
                    color_msg("Wrong kind of significance. Choose 0, 1 or 2.", "red")
                    sys.exist()
            else:
                gr.SetPoint(i-1, x, 0)
        gr.SetName(self.name)
        return gr
    
    def get_wp_forFR(self, fr = 0.2):
        return self.cut_on_graph(self.yields_fake, fr)
    
    def get_fr_forWp(self, wp = 0.8):
        return self.yields_fake.Eval(wp)
    
    def get_signalEff_ForWp(self, wp = 0.8):
        return self.yields_sig.Eval(wp)
    
    def get_eff(self, wp):
        """ Function to integrate and get overall efficiencies """
        # The working point is the cut on discriminant in the X axis.
        # But the integral has to be done using the bin number
        h = self.histos["signal"]
        bini = h.FindBin(wp)
        nbins = h.GetNbinsX()
        eff = h.Integral(bini, nbins+1) / h.Integral()
        return eff
    
    def get_bkgeff(self, wp):
        """ Function to integrate and get overall efficiencies """
        # The working point is the cut on discriminant in the X axis.
        # But the integral has to be done using the bin number
        h = self.histos["bkg"]
        bini = h.FindBin(wp)
        nbins = h.GetNbinsX()
        eff = h.Integral(bini, nbins+1) / h.Integral()
        return eff
    
    def cut_on_graph(self, gr, thr):
        """ 
            This function returns the GRAPH POINT above which the associated value 
            (point content) is below a given threshold
        """
        npoints = gr.GetN() 
        correct_WP = 0
        for i in range(npoints):
            # Get the value for this point
            current_value = gr.GetPointY(i)

            # Find the point at which the value you obtain
            # is <= the threshold you set.
            if (current_value  <= thr):
                x_value = gr.GetPointX(i)
                y_value = gr.GetPointY(i)
                return (i, x_value, y_value) 
    
    def cut_on_hist(self, h, thr):
        """ 
            This function returns the HIST BIN above which the INTEGRAL value 
            is below a given threshold
        """
        nbins = h.GetNbinsX()
        for bini in range(1, nbins+1):
            current_val = h.Integral(bini, nbins+1)/h.Integral()
            if current_val <= thr:
                return (bini, h.GetBinLowEdge(bini))
        
def plot_roc(histos, outpath, name, fr = None, plot = "roc", setLogy = False, setLogx = False):
    
    text = "#bf{CMS} Simulation"
    cmsprel = cv.add_text("#bf{CMS} Simulation", (.08, .91, .5, .97))
    c = cv.new_canvas(nPads = 1, name = "roc_%s"%(name))
    
    legend = cv.new_legend((0.15, 0.65, 0.35, 0.85))
    if plot == "significance":
        legend = cv.new_legend((0.15, 0.25, 0.45, 0.45))

    if setLogx: c.SetLogx()
    if setLogy: c.SetLogy()
    
    # ---- Plot stuff
    toDraw0 = getattr(histos[0], plot)
    
    
    if plot == "roc":
        toDraw0.GetYaxis().SetTitle("Signal efficiency")
        toDraw0.GetXaxis().SetTitle("Background efficiency")
        legend = cv.new_legend((0.25, 0.15, 0.45, 0.35))
        legend.SetTextSize(legend.GetTextSize()*2)
        toDraw0.GetXaxis().SetRangeUser(0.0015, 1)
        toDraw0.GetYaxis().SetRangeUser(0.0, 1)
        
    
    elif plot == "significance":
        toDraw0.GetXaxis().SetTitle("BDT score")
        toDraw0.GetYaxis().SetTitle("Significance S/sqrt(S+B)")
        toDraw0.GetYaxis().SetLabelSize(0.02)
        legend = cv.new_legend((0.15, 0.15, 0.35, 0.35))
        legend.SetTextSize(legend.GetTextSize()*2)
        toDraw0.GetXaxis().SetRangeUser(0.0015, 1)
    elif plot == "yields_fake":
        toDraw0.GetXaxis().SetTitle("BDT score")
        toDraw0.GetYaxis().SetTitle("Fake rate")
        legend = cv.new_legend((0.25, 0.35, 0.45, 0.55))
        legend.SetTextSize(legend.GetTextSize()*2)
        toDraw0.GetXaxis().SetRangeUser(-1, 1)
                    
    toDraw0.Draw("aL")
    
    if fr != None:
        # Get the WP for a given FR
        _, wp_sameFR, _ = histos[0].get_wp_forFR( fr )
        signal_eff = histos[0].get_eff(wp_sameFR)
        histos[0].legend = "%s (WP: %3.2f, #epsilon=%3.2f)"%(histos[0].legend, wp_sameFR,  signal_eff)
        
    legend.AddEntry(toDraw0, histos[0].legend)

    color = 2
    refpoint = r.TGraph(1)
    toprint = []
    for ih, h in enumerate(histos[1:]):
        href = deepcopy(h)
        toDraw = getattr(histos[1:][ih], plot)
        toDraw.SetLineColor(ih+color)
        toDraw.Draw("L same")
        if fr != None:
            # Get the WP for a given FR
            _, wp_sameFR, _ = histos[1:][ih].get_wp_forFR( fr )
            signal_eff = histos[1:][ih].get_eff(wp_sameFR)
            bkg_eff = histos[1:][ih].get_fr_forWp(wp_sameFR)


            if histos[1:][ih].legend == "Run3" : wp_sameFR = 0.97
            histos[1:][ih].legend = "%s (WP: %3.2f, #epsilon=%3.2f)"%(href.legend, wp_sameFR,  signal_eff)
            if plot == "roc":
                point = deepcopy(refpoint)
                point.SetPoint(1, bkg_eff, signal_eff)
                point.SetMarkerColor(ih+color)
                point.SetMarkerSize(2)
                point.SetMarkerStyle(20)
                toprint.append(point)
        legend.AddEntry(toDraw, histos[1:][ih].legend)
    
    for pi in toprint:
        pi.Draw("p same")
    # ---- Draw legend
    legend.Draw("same")
    cmsprel.Draw("same")
    c.SaveAs( os.path.join( outpath, "%s_%s.png"%(plot, name)) )
    c.SaveAs( os.path.join( outpath, "%s_%s.pdf"%(plot, name)) )
    return

if __name__ == "__main__":
    inpath = "lepmva_results"
    year = sys.argv[1]
    
    inpath = os.path.join(inpath, year)

    def compare_btag(ofWhat = "muon"):
        h_pnet = histo( os.path.join(inpath, "%s_pnet_mvaEvaluate.root"%ofWhat), "ParticleNet")
        h_df = histo( os.path.join(inpath, "%s_df_mvaEvaluate.root"%ofWhat), "DeepJET")
        #h_pnet_tth = histo( os.path.join(inpath, "%s_pnet_ttH_mvaEvaluate.root"%ofWhat), "ParticleNet (ttH-like)")
        #h_df_tth = histo( os.path.join(inpath, "%s_df_ttH_mvaEvaluate.root"%ofWhat), "DF (ttH-like)")
        
        # Compare ROC curves
        plot_roc([h_pnet, h_df], inpath, "compare_btag_%s"%ofWhat, setLogx = True)
        plot_roc([h_pnet, h_df], inpath, "compare_btag_%s"%ofWhat, plot = "yields_fake") 
        plot_roc([h_pnet, h_df], inpath, "compare_btag_%s"%ofWhat, plot = "significance")
        return
    
    def compare_legacy(ofWhat = "muon"):
        h_legacy = histo( os.path.join(inpath, "%s_legacy_mvaEvaluate.root"%ofWhat), "Legacy mvaTTH")

        # Get legacy FR
        legacy_fr = h_legacy.get_fr_forWp(0.8)
        #h_df = histo( os.path.join(inpath, "%s_df_wIso_mvaEvaluate.root"%ofWhat), "Run3 ")
        #print(os.path.join(inpath, "%s_mvaISO_mvaEvaluate.root"%ofWhat))
        #h_df_ttw = histo( os.path.join(inpath, "%s_mvaISO_mvaEvaluate.root"%ofWhat), "mvaISO ")
        h_df_tth = histo( os.path.join(inpath, "%s_df_ttH_mvaEvaluate.root"%ofWhat), "Run3 ttH presel")

#        electron_fr = h_df.get_fr_forWp(0.9)
        histos = [h_legacy, h_df_tth]
#        if ofWhat == "electron":
#            #h_df_wNoIso = histo( os.path.join(inpath, "%s_df_wNoIso_mvaEvaluate.root"%ofWhat), "Run3 (mvaNoIso) ")
#            #h_df_wNoIso_tth = histo( os.path.join(inpath, "%s_pnet_wNoIso_ttH_mvaEvaluate.root"%ofWhat), "Run3 ttH presel (with noIso)")
#            #h_df_wIso_tth = histo( os.path.join(inpath, "%s_pnet_wIso_ttH_mvaEvaluate.root"%ofWhat), "Run3 ttH presel (with Iso)")
#            h_df_wIso = histo( os.path.join(inpath, "%s_df_wIso_mvaEvaluate.root"%ofWhat), "Run3")
#            histos.extend([h_df_wIso])
#            #histos.append(h_df_wNoIso_tth)
#            #histos.append(h_df_wIso)
#            #histos.append(h_df_wIso_tth)
        
        # Compare ROC curves
        plot_roc(histos, inpath, "compare_legacy_%s"%ofWhat, legacy_fr, setLogx = True)
        plot_roc(histos, inpath, "compare_legacy_%s"%ofWhat, None, plot = "yields_fake")
        plot_roc(histos, inpath, "compare_legacy_%s"%ofWhat, None, plot = "significance")
        return
    
    #compare_btag("muon")
    compare_legacy("muon")
