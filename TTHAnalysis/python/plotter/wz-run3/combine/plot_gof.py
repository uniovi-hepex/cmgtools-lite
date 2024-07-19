""" Small macro to plot GOF """
import ROOT as r
from optparse import OptionParser
from copy import deepcopy
import os 
import re
import sys
import json 

r.gROOT.SetBatch(1)

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]",  description = "Main options for running WZ analysis fits") 

    # -- Input and outputs
    parser.add_option("--inpath", "-i", dest = "inpath",                               help = "Path to the fit results")
    parser.add_option("--region",       dest = "region", default = "srwz",             help = "Region to get the GOF from.")
    parser.add_option("--title",        dest = "title", default = "Pre-fit GOF test", help = "Title for the plot")
    return parser

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

if __name__ == "__main__":
    opts, args = add_parsing_opts().parse_args()
    inpath  = opts.inpath
    region  = opts.region
    title  = opts.title

    inFile_toys  = "higgsCombine_{region}.root".format( region = region )
    inFile_data  = "higgsCombine.Test.GoodnessOfFit.mH120.root".format( region = region )
    plot_outname = os.path.join( inpath,  "GOF_{region}".format(region = region) )

    # First of all, check if it's needed to merge output
    if not os.path.isfile( os.path.join(inpath, inFile_toys) ):
        files_to_merge = [ "%s/%s"%(inpath, ifile) for ifile in os.listdir(inpath) if "higgsCombine_{region}_gof_job".format(region = region) in ifile ]
        haddcmd = "hadd -f {inpath}/{inFile_toys} {files}".format( inpath = inpath, inFile_toys = inFile_toys, files = " ".join(files_to_merge) )

        color_msg("Merging files: " + " ".join(files_to_merge), "green")
        color_msg(haddcmd, indentlevel = 1)
        os.system(haddcmd)

    # Now make the plot
    r.gStyle.SetOptStat(0)
    inpData = r.TFile( os.path.join(inpath, inFile_data), "READ")
    inptoys = r.TFile( os.path.join(inpath, inFile_toys), "READ")
    tData = inpData.Get("limit")
    tToys = inptoys.Get("limit")

    c = r.TCanvas("c" ,"c" , 800, 600)
    valToys = []
    valData = 0.
    for ev in tData:
        valData = ev.limit

    up   = 0.
    down = 0.
    for ev in tToys:
        valToys.append(ev.limit)
        if ev.limit >= valData:
            up += 1
        else:
            down +=1

    minX = min(0., min(valToys))
    maxX = min(max(valToys), sorted(valToys)[len(valToys)/2] * 4) # To avoid skewing for exta high values

    if valData > maxX * 0.9: maxX = valData * 1.1
    hToys = r.TH1F("hToys", "hToys", 100, minX, maxX)
    for v in valToys: hToys.Fill(v)

    hToys.SetLineColor(r.kBlue)
    hToys.GetXaxis().SetTitle("Saturated test statistic (adim.)")
    hToys.GetYaxis().SetTitle("Probability")

    # Normalise
    hToys.Scale(1. / hToys.Integral("width"))
    hToys.SetTitle(" {title}".format(title = title) )
    hToys.Draw("hist")
    lineData = r.TLine(valData, 0, valData, hToys.GetMaximum() * 1.05)
    lineData.Draw("same")

    tl = r.TLegend(0.65, 0.6, 0.85, 0.85)
    tl.SetHeader("p-value = %1.4f"%(up / ((up + down)*1.)))
    tl.AddEntry(hToys,    "Saturated ({n} toys)".format(n = tToys.GetEntries()), "f")
    tl.AddEntry(lineData, "Data", "l")
    tl.Draw("same")

    c.SaveAs("%s.png"%(plot_outname))
    c.SaveAs("%s.pdf"%(plot_outname))
    c.Close(); del c

