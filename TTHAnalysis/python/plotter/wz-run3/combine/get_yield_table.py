""" Read input cards and provide a table """
import ROOT as r
import sys, os, re
import math
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table
from optparse import OptionParser

caption="""
Expected (pre-fit) yields (by flavor channel) for the relevant processes in the signal 
region of the analysis. All analysis uncertainties but the $(\mu_r, \mu_F)$ and PDFs are included.
"""

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
    parser.add_option("--inpath", dest = "inpath", help = "Path to folder with fit diagnostics.")
    return parser

def get_maps( inpath ):
    """ Reads the combined card and matches combine channels to analysis channels  """
    card = open( os.path.join(inpath, "combinedCard.dat") )
    pattern = r"shapes \* +(\S+) +.*srwz.input(\d+)([A-Za-z]+)?_(\w+)\.root"
    
    maps = {}
    lines = card.readlines()
    for line in lines:
        match_line = re.search(pattern, line)
        if match_line:
            channel_combine, year, era, channel_name = match_line.groups()
            maps[channel_combine] = channel_name
    return maps

def get_yields( inpath, maps ):
    """ Read the fitdiagnostics and computes the yields """
    yields = {
        "eee" : {},
        "eem" : {},
        "mme" : {},
        "mmm" : {},
        "inclusive" : {}
    }

    fD = r.TFile.Open( os.path.join(inpath, "fitDiagnosticsTest.root") )
    dire = fD.Get("shapes_prefit")
    
    for ch, channel_name in maps.items():
        if channel_name == "eee": binIndex = 1    
        if channel_name == "eem": binIndex = 2
        if channel_name == "mme": binIndex = 3
        if channel_name == "mmm": binIndex = 4

        direch = dire.Get( ch )
        color_msg("Considering channel %s"%ch, "blue")
        for prockey in direch.GetListOfKeys():
            procname = prockey.GetName()
            if procname in ["data", "total", "prompt_WZ",  "prompt_WZ_nonfiducial", "total_covar"]: continue
            proch = direch.Get( procname )
            color_msg("Considering process %s"%procname, "green", 1)
            color_msg("Summing %3.2f"%proch.Integral(), indentlevel = 2)

            if procname not in yields[channel_name]:
                yields[channel_name][procname] = [proch.GetBinContent(binIndex), proch.GetBinError(binIndex)]
            else:
                yields[channel_name][procname][0] = yields[channel_name][procname][0] + proch.GetBinContent(binIndex)
                yields[channel_name][procname][1] = math.sqrt(yields[channel_name][procname][1]*yields[channel_name][procname][1] + proch.GetBinError(binIndex)*proch.GetBinError(binIndex))

            if procname not in yields["inclusive"]:
                yields["inclusive"][procname] = [proch.GetBinContent(binIndex), proch.GetBinError(binIndex)]

            else:
                yields["inclusive"][procname][0] = yields["inclusive"][procname][0] + proch.GetBinContent(binIndex)
                yields["inclusive"][procname][1] = math.sqrt(yields["inclusive"][procname][1]*yields["inclusive"][procname][1] + proch.GetBinError(binIndex)*proch.GetBinError(binIndex))


    return yields

def format_table( yields ):
    table = {
        "processes" : [],
        "eee" : [],
        "eem" : [],
        "mme" : [],
        "mmm" : [],
        "inclusive" : []
    }

    processes = yields["inclusive"].keys()

    for proc in processes:
        table["processes"].append(proc)
        for ch in yields.keys():
            if proc in yields[ch]:
                format = "3.0f" if yields[ch][proc][0] > 1 else "3.1f"
                table[ch].append( "%3.2f $\pm$ %3.2f "%(yields[ch][proc][0], yields[ch][proc][1]) )
            else:
                table[ch].append( "0 $\pm$ 0 " )

    return table

if __name__ == "__main__":
    opts, args = add_parsing_opts().parse_args()
    inpath = opts.inpath

    # 1. Map channels and processes
    maps = get_maps( inpath )

    # 2. Read the fit diagnostics and sum yields
    yields = get_yields( inpath, maps )    

    # 3. Put it in a format for latex table script
    table = format_table( yields )

    # 4. Create the latex table
    table = dict_to_latex_table(table, caption, "yields_prefit")
    print(table)

    
