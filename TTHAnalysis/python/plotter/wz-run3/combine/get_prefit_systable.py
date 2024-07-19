""" Read input cards and provide a table """
import ROOT as r
import sys, os, re
import math
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table
from optparse import OptionParser
from copy import deepcopy 


caption="""
Summary of input relative uncertainties for the \WZ measurement. Numbers are presented in percentages over the total yields of the associated process they have an effect on.
The parametrization of uncertainty (shape/global normalization), as well as the per Era correlation scheme, are also included.  """

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

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]", 
                        description = "Main options for running WZ analysis")  
    parser.add_option("--inpath", dest = "inpath", help = "Path to folder with cards.")
    return parser

def open_rfiles(inpath, card_list):
    retlist = []
    for card in card_list:
        # open file
        rfile = r.TFile.Open( os.path.join(inpath, card) )
        rfile.ls()
        retlist.append( deepcopy(rfile) )
        if len(retlist) > 0: print(retlist[-1].ls())
        #rfile.Close()

    return retlist

def get_from_rfile(inpath, cards, variations):
    mini = 0
    maxi = 0

    for card in cards:
        rfile = r.TFile.Open( os.path.join(inpath, card) )

        for variation in variations:

            nom = rfile.Get("x_prompt_WZ")


            hup = rfile.Get("x_prompt_WZ_%sUp"%variation)
            hdn = rfile.Get("x_prompt_WZ_%sDown"%variation)


            if type(hup) != r.TObject:
                # Compute the deviation with respect to the nominal
                rel_unc = max( abs(hup.GetMaximum() - nom.GetMaximum()) / nom.GetMaximum(), abs(hdn.GetMaximum() - nom.GetMaximum()) / nom.GetMaximum()) * 100
                
                if rel_unc > maxi: 
                    maxi = rel_unc 
            else:
                continue
            if "btag" in variation:
                print(variation, maxi)

        rfile.Close()
            
    return maxi

if __name__ == "__main__":
    channels = ["eee", "eem", "mme", "mmm"]
    years = ["2022", "2022EE"]

    opts, args = add_parsing_opts().parse_args()
    inpath = opts.inpath

    cards_2022 = [ card for card in os.listdir( inpath ) if ".root" in card and "2022EE" not in card ]
    cards_2022EE = [ card for card in os.listdir( inpath ) if ".root" in card and "2022EE" in card ]



    info = {
        "Integrated luminosity" : {
            "2022"   : "1.4",
            "2022EE"   : "1.4",
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "Normalization"
        },
        "Trigger efficiencies" : {
            "2022"   : "-1.6/1.6",
            "2022EE"   : "-1.0/1.0",
            "Correlation" : "Uncorrelated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "b tagging (heavy)" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["btag_HF_Corr", "btagging_HF_2022"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["btag_HF_Corr", "btagging_HF_2022PostEE"] ),
            "Correlation" : "Partially correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "b tagging (light)" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["btag_LF_Corr", "btagging_LF_2022"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["btag_LF_Corr", "btagging_LF_2022PostEE"] ),
            "Correlation" : "Partially correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "Pileup" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["pileup"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["pileup"] ),
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "Jet energy scale" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["jer_2022PreEE", "jestotal_2022PreEE"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["jer_2022PostEE", "jestotal_2022PostEE"] ),
            "Correlation" : "Partially correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "Electron ID efficiencies" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["elecidsf"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["elecidsf"] ),
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape" 
        },
        "Electron reconstruction" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["elecrecosf"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["elecrecosf"] ),
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "Electron energy scale" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["elec_smear_2022PreEE", "elec_scale_2022PreEE"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["elec_smear_2022PostEE", "elec_scale_2022PostEE"] ),
            "Correlation" : "Uncorrelated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },
        "Muon efficiencies" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["muonidsf_ID"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["muonidsf_ID"] ),
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "shape"
        },


        "Nonprompt normalization" : {
            "2022"   : "30",
            "2022EE"   : "30",
            "Correlation" : "Correlated",
            "Processes" : "Nonprompt",
            "Paramatrization" : "Normalization"
        },
        "\\VVV normalization" : {
            "2022"   : "50",
            "2022EE"   : "50",
            "Correlation" : "Correlated",
            "Processes" : "\\VVV",
            "Paramatrization" : "Normalization"
        },
        "\\tZq normalization" : {
            "2022"   : "15",
            "2022EE"   : "15",
            "Correlation" : "Correlated",
            "Processes" : "\\tZq",
            "Paramatrization" : "Normalization"
        },
        "\\ZZ normalization" : {
            "2022"   : "Free",
            "2022EE"   : "Free",
            "Correlation" : "Correlated",
            "Processes" : "\\ZZ",
            "Paramatrization" : "Normalization"
        },
        "\\VH normalization" : {
            "2022"   : "25",
            "2022EE"   : "25",
            "Correlation" : "Correlated",
            "Processes" : "\\VH",
            "Paramatrization" : "Normalization"
        },
        "\\Xg normalization" : {
            "2022"   : "Free",
            "2022EE"   : "Free",
            "Correlation" : "Correlated",
            "Processes" : "\\Xg",
            "Paramatrization" : "Normalization"
        },
        "\\ttZ normalization" : {
            "2022"   : "Free",
            "2022EE"   : "Free",
            "Correlation" : "Correlated",
            "Processes" : "\\ttZ",
            "Paramatrization" : "Normalization"
        },
        "ISR" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["ISR"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["ISR"] ),
            "Correlation" : "Correlated",
            "Processes" : "\\WZ",
            "Paramatrization" : "Normalization"
        },
        "FSR" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["FSR"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["FSR"] ),
            "Correlation" : "Correlated",
            "Processes" : "All MC",
            "Paramatrization" : "Normalization"
        },
        "WZ theo ($\mu_R$, $\mu_F$, PDF)" : {
            "2022"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022, ["wz_muF", "wz_muR", "pdf_wz"] ),
            "2022EE"   : "0-%1.1f"%get_from_rfile(inpath, cards_2022EE, ["wz_muF", "wz_muR", "pdf_wz"] ),
            "Correlation" : "Correlated",
            "Processes" : "\\WZ",
            "Paramatrization" : "Normalization"
        },
        "MC Statistical uncertainty" : {
            "2022"   : "By bin",
            "2022EE"   : "By bin",
            "Correlation" : "Decorrelated",
            "Processes" : "All MC",
            "Paramatrization" : "Barlow-Beeston"
        },
    }

    table = {
        "Source" : list(info.keys()),
        #"2022PreEE" : [ info[source]["2022"] for source in list(info.keys())],
        "Range (\\%)" : [ info[source]["2022EE"] for source in list(info.keys())],
        #"Correlation" : [ info[source]["Correlation"] for source in list(info.keys())],
        "Processes" : [ info[source]["Processes"] for source in list(info.keys())],
        "Paramatrization" : [ info[source]["Paramatrization"] for source in list(info.keys())],

    }
    # Create the latex table
    table = dict_to_latex_table(table, caption, "tab:systsCorr")
    print(table)
        

