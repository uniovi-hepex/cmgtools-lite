import ROOT as r
import os, re, sys
from copy import deepcopy
import json
import argparse
import numpy as np
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
import cmsstyle as CMS

r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)

reference_process = "fakes_T"

def add_parsing_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inpath', '-i', dest = "inpath", help = "Path to the folder that contains all the cards")
    return parser.parse_args()

def color_msg(msg, color = "none", indentlevel=0):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;35m"
    }

    if indentlevel == 0: indentSymbol=">> "
    if indentlevel == 1: indentSymbol="+ "
    if indentlevel == 2: indentSymbol="* "

    indent = indentlevel*" " + indentSymbol
    print("\033[%s%s%s \033[0m"%(codes[color], indent, msg))
    return

def get_variations(card):
    """ Just get a list of shape variations from a given card """
    f = r.TFile.Open( card )
    variations = [ re.match( f"x_{reference_process}(.*)Up", k.GetName()) for k in f.GetListOfKeys() if "TT" not in k.GetName()]

    # filter by those that actually matched
    variations = list( filter( lambda x : x != None, variations) )

    # Finally, just return the names
    variations = [ v.group(0).replace("Up", "") for v in variations ]
    variations = list( filter( lambda x: "non" not in x, variations) )
    f.Close()
    return variations

def get_histograms(cards, variation):
    """ Retrieve the nominal and variated histograms and fill ratios (for the uncertainties)"""
    # We build a 4 bin distribution

    nominal    = r.TH1F( f"h_{variation}_nominal", "", 4, -0.5, 3.5)
    up         = r.TH1F( f"h_{variation}_up", "", 4, -0.5, 3.5)
    down       = r.TH1F( f"h_{variation}_down", "", 4, -0.5, 3.5)
    ratio_up   = r.TH1F( f"ratio_{variation}_up", "", 4, -0.5, 3.5)
    ratio_down = r.TH1F( f"ratio_{variation}_down", "", 4, -0.5, 3.5)

    for ipoint, card in enumerate(cards):
        # Open the card
        f = r.TFile.Open( card )
        nominal_card = f.Get( f"x_{reference_process}" )
        up_card = f.Get( f"{variation}Up" )
        dn_card = f.Get( f"{variation}Down" )

        if "eee" in card: ibin = 1
        elif "eem" in card: ibin = 2
        elif "mme" in card: ibin = 3
        elif "mmm" in card: ibin = 4
        else: 
            print("Channel not nown")
            sys.exit(1)
        
        nominal_content = nominal_card.GetBinContent(ibin)
        up_content = up_card.GetBinContent(ibin)
        dn_content = dn_card.GetBinContent(ibin)

        nominal.SetBinContent(ibin, nominal_content )
        up.SetBinContent(ibin, up_content )
        down.SetBinContent(ibin, dn_content )
        ratio_up.SetBinContent(ibin, up_content / nominal_content)
        ratio_down.SetBinContent(ibin, dn_content / nominal_content)
        f.Close()

    # Style histograms
    nominal.SetLineColor(1)
    nominal.SetLineWidth(2)
    nominal.GetXaxis().SetLabelSize(0)
    nominal.GetXaxis().SetTitleSize(0)
    up.SetLineColor(r.TColor.GetColor(63,144,218))
    up.SetLineWidth(2)
    down.SetLineColor(r.TColor.GetColor(231,99,0))
    down.SetLineWidth(2)

    ratio_up.SetLineColor(r.TColor.GetColor(63,144,218))
    ratio_up.SetLineWidth(2)
    ratio_down.SetLineColor(r.TColor.GetColor(231,99,0))
    ratio_down.SetLineWidth(2)


    return nominal, up, down, ratio_up, ratio_down

def plot_variations(cards, outpath):
    """ Function to plot variations from WZ cards """
    # 0. Make sure output folder exists
    if not os.path.exists( outpath ):
        os.system( f"mkdir -p {outpath}" )
    # 1. Get the list of variation names
    variation_names = get_variations( cards[0] )


    # 2. Iterate over variations, and make a plot for each of these
    for var in variation_names:
        # 2.1. Get histograms
        nominal, up, dn, ratio_up, ratio_down = get_histograms( cards, var )


        ratio_min = min( ratio_up.GetMinimum(), ratio_down.GetMinimum()) 
        ratio_max = max( ratio_up.GetMaximum(), ratio_down.GetMaximum()) 

        # 2.2 Create the canvas using CAT tools
        CMS.SetExtraText("Preliminary")
        CMS.SetEnergy("13.6")
        CMS.SetLumi("")
        canv = CMS.cmsDiCanvas(
            canvName = var, 
            x_min = -0.5, 
            x_max = 3.5, 
            y_min = 0, 
            y_max = max( nominal.GetMaximum(), up.GetMaximum(), dn.GetMaximum() )*1.2,
            r_min = ratio_min - ratio_min*0.05 if  abs(1 - ratio_min) > 0.03 else ratio_min - ratio_min*0.01  ,
            r_max = ratio_max + ratio_max*0.05 if  abs(1 - ratio_max) > 0.03 else ratio_max + ratio_max*0.01 , 
            nameXaxis = 'Flavor', 
            nameYaxis = 'Events', 
            nameRatio = 'Ratio',
            square = CMS.kSquare, 
            extraSpace=0.01, 
            iPos=0
        )


        canv.cd(1)
        nominal.Draw("hist same")
        up.Draw("hist same")
        dn.Draw("hist same")


        # Make legend
        legend = CMS.cmsLeg(
            x1 = 0.25, 
            y1 = 0.55, 
            x2 = 0.55, 
            y2 = 0.75, 
            textSize=0.04, 
            textFont=42, 
            textColor=r.kBlack, 
            columns=None
        )

        legend.AddEntry( nominal, "Nominal", "l")
        legend.AddEntry( up, "Up", "l")
        legend.AddEntry( dn, "Down", "l")

        canv.cd(2)

        ratio_up.Draw("hist")
        ratio_down.Draw("hist same")
        legend_ratio = CMS.cmsLeg(
            x1 = 0.35, 
            y1 = 0.75, 
            x2 = 0.65, 
            y2 = 0.95, 
            textSize=0.06, 
            textFont=42, 
            textColor=r.kBlack, 
            columns=2
        )
                # Rename the x axis labels and take the format from the ratio plot
        ratio_up.GetYaxis().SetTitleOffset(0.01 + 1.0 * 600 / (600 * (1 - 0.13)))
        ratio_up.GetXaxis().SetTitleOffset(0.9)
        ratio_up.SetTitleSize(ratio_up.GetTitleSize("Y") * 600 / (600 * (1 - 0.13)), "Y")
        ratio_up.SetLabelSize(ratio_up.GetLabelSize("Y") * 600 / (600 * (1 - 0.13)), "Y")
        ratio_up.SetTitleSize(ratio_up.GetTitleSize("X") * 600 / (600 * (1 - 0.13)), "X")
        ratio_up.SetLabelSize(ratio_up.GetLabelSize("X") * 600 / (600 * (1 - 0.13)), "X")
        ratio_up.SetLabelOffset(ratio_up.GetLabelOffset("X") * 600 / (600 * (1 - 0.13)), "X")
        ratio_up.GetXaxis().SetTitle("Flavor")
        ratio_up.GetYaxis().SetTitle("Ratio")
        ratio_up.GetXaxis().SetBinLabel(1, "eee")
        ratio_up.GetXaxis().SetBinLabel(2, "eem")
        ratio_up.GetXaxis().SetBinLabel(3, "mme")
        ratio_up.GetXaxis().SetBinLabel(4, "mmm")
        #ratio_up.GetYaxis().SetRangeUser( ratio_min - ratio_min*0.05 if  abs(1 - ratio_min) > 0.05 else ratio_min - ratio_min*0.01, ratio_max + ratio_max*0.05 if  abs(1 - ratio_max) > 0.05 else ratio_max + ratio_max*0.01  )
        ratio_up.GetYaxis().SetRangeUser( 0.995, 1.005 )
        
        ratio_up.SetTickLength(ratio_up.GetTickLength("Y") * 600 / (600 * (1 - 0.13)), "Y")  # ?? ok if 1/3
        ratio_up.SetTickLength(ratio_up.GetTickLength("X") * 600 / (600 * (1 - 0.13)), "X")
        ratio_up.GetYaxis().SetNdivisions(505)

        legend_ratio.AddEntry( ratio_up, "Up", "l")
        legend_ratio.AddEntry( ratio_down, "Down", "l")




        CMS.SaveCanvas( canv, outpath + f"/{var}.png" )


if __name__ == "__main__":
    opts = add_parsing_options()
    inpath = opts.inpath

    
    # 1. Get a list of all the cards and match them by year
    files = [os.path.join(inpath, card) for card in os.listdir( inpath )]
    
    match_year = ".*2022_.*"
    files_2022   = list( filter( lambda x : re.match(".*2022_.*root", x), files) )
    files_2022EE = list( filter( lambda x : re.match(".*2022EE_.*root", x), files) )

    # Now plot them
    color_msg("Plotting for 2022 PreEE ", "green")
    plot_variations( cards = files_2022, outpath = os.path.join(inpath, "2022") )
    color_msg("Plotting for 2022 PostEE ", "green")
    plot_variations( cards = files_2022EE, outpath = os.path.join(inpath, "2022EE") )
