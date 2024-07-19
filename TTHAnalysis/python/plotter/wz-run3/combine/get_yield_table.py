""" Read input cards and provide a table """
import ROOT as r
import sys, os, re
import math
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table
from optparse import OptionParser
from collections import OrderedDict
from copy import deepcopy


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
    parser.add_option("--cc", dest = "combinedCardPath", help = "Path to combinedCard to fetch process namings.")
    parser.add_option("--fd", dest = "fitDiagnosticsPath", help = "Path to fitDiagnostics to fetch yields.")
    parser.add_option("--shapedir", dest = "shapedir", default = "postfit", help = "prefit or postfit")
    return parser

def get_maps( inpath ):
    """ Reads the combined card and matches combine channels to analysis channels  """
    card = open( inpath )
    pattern = r"shapes \* +(\S+) +.*srwz.input(\d+)([A-Za-z]+)?_(\w+)\.root"
    
    maps = {}
    lines = card.readlines()
    for line in lines:
        match_line = re.search(pattern, line)
        if match_line:
            channel_combine, year, era, channel_name = match_line.groups()
            maps[channel_combine] = channel_name
    return maps

def integrate(values_dict):
    """ Reads a dictionary and integrates histograms according to keys """
    summed = {}
    for proc, values in values_dict.items():
        # Grab the first one

        v0 = values[0][0]
        v0_unc = values[0][1] 

        # Go summing up the rest
        for v in values[1:]:
            v0 += v[0]
            v0_unc += v[1]

        summed[proc] = [v0, v0_unc]
    return summed

def get_yields( inpath, maps, shapedir = "shapes_prefit" ):
    """ Read the fitdiagnostics and computes the yields """
    yields = {
        "eee" : {},
        "eem" : {},
        "mme" : {},
        "mmm" : {},
        "inclusive" : {}
    }

    fD = r.TFile.Open( inpath )
    dire = fD.Get(shapedir)
    
    for ch, channel_name in maps.items():
        if channel_name == "eee": binIndex = 1    
        if channel_name == "eem": binIndex = 2
        if channel_name == "mme": binIndex = 3
        if channel_name == "mmm": binIndex = 4

        direch = dire.Get( ch )
        color_msg("Considering channel %s"%ch, "blue")
        for prockey in direch.GetListOfKeys():
            procname = prockey.GetName()
            if procname in ["total", "prompt_WZ",  "prompt_WZ_nonfiducial", "total_covar"]: continue
            proch = direch.Get( procname )
            color_msg("Considering process %s"%procname, "green", 1)
            color_msg("Summing %3.2f"%proch.Integral(), indentlevel = 2)

            if procname not in yields[channel_name]:
                if procname != "data":
                    yields[channel_name][procname] = [proch.GetBinContent(binIndex), proch.GetBinError(binIndex)]
                else:
                    yields[channel_name][procname] = [proch.GetY()[binIndex-1], proch.GetErrorY(binIndex-1)]
            else:
                if procname != "data":
                    yields[channel_name][procname][0] = yields[channel_name][procname][0] + proch.GetBinContent(binIndex)
                    yields[channel_name][procname][1] = math.sqrt(yields[channel_name][procname][1]*yields[channel_name][procname][1] + proch.GetBinError(binIndex)*proch.GetBinError(binIndex))
                else:
                    yields[channel_name][procname][0] = yields[channel_name][procname][0] + proch.GetY()[binIndex-1]
                    yields[channel_name][procname][1] = math.sqrt(yields[channel_name][procname][1]*yields[channel_name][procname][1] + proch.GetErrorY(binIndex-1)*proch.GetErrorY(binIndex-1))

            if procname not in yields["inclusive"]:
                if procname != "data":
                    yields["inclusive"][procname] = [proch.GetBinContent(binIndex), proch.GetBinError(binIndex)]
                else:
                    yields["inclusive"][procname] = [proch.GetY()[binIndex-1], proch.GetErrorY(binIndex-1)]

            else:
                if procname != "data":
                    yields["inclusive"][procname][0] = yields["inclusive"][procname][0] + proch.GetBinContent(binIndex)
                    yields["inclusive"][procname][1] = math.sqrt(yields["inclusive"][procname][1]*yields["inclusive"][procname][1] + proch.GetBinError(binIndex)*proch.GetBinError(binIndex))
                else:
                    yields["inclusive"][procname][0] = yields["inclusive"][procname][0] + proch.GetY()[binIndex-1]
                    yields["inclusive"][procname][1] = math.sqrt(yields["inclusive"][procname][1]*yields["inclusive"][procname][1] + proch.GetErrorY(binIndex-1)*proch.GetErrorY(binIndex-1))


    return yields

def format_table( yields ):
    table = {
        "processes" : [],
        "eee" : [],
        "eem" : [],
        "mme" : [],
        "mmm" : [],
        "inclusive" : [],
    }

    translate = OrderedDict()
    translate["fakes"] =  "Non prompt"
    translate["ZZ"] =  "\\ZZ"
    translate["convs"] =  "\\Xg"
    translate["prompt_TTX"] = "\\ttX"
    translate["prompt_VVV"] = "\\VVV"
    translate["prompt_VH"] =  "VH"
    translate["prompt_TZQ"] = "\\tZq"
    translate["total_background"] = "Background"
    translate["total_signal"] = "\\WZ"
    translate["data"] = "Data"
    processes = yields["inclusive"].keys()

    for proc in translate.keys():
        table["processes"].append(translate[proc])


        for ch in yields.keys():
            if proc in yields[ch]:
                relative_presence = yields[ch][proc][0] / (yields[ch]["total_signal"][0] + yields[ch]["total_background"][0]) * 100
                formatting = "%3.0f" if yields[ch][proc][0] > 1.0 else "%3.1f"
                line_format = "%s $\pm$ %s "%( formatting%yields[ch][proc][0], formatting%yields[ch][proc][1])

                #if float(relative_presence) < 1.0: 
                #    line_format += "%1.1f"#%( relative_presence) + "\\%)"
                #else:
                #    line_format += "%1.0f"#%( relative_presence) + "\\%)"

                if line_format == "0.0 $\pm$ 0.0 ": 
                    line_format = "$<0.1$"
                table[ch].append( line_format )
            else:
                table[ch].append( "$<0.1$" )




    return table

if __name__ == "__main__":
    opts, args = add_parsing_opts().parse_args()

    if opts.shapedir == "prefit":   
        caption="""
        Expected (pre-fit) yields (by flavor channel) for the relevant processes in the signal 
        region of the analysis. The numbers between parenthesis show the relative presence of each process in the corresponding channel; 
        computed with respect to the total yield.
        """ 
        shapedir = "shapes_prefit"

    elif opts.shapedir == "postfit":   
        caption="""
        Expected (post-fit) yields (by flavor channel) for the relevant processes in the signal 
        region of the analysis. The numbers between parenthesis show the relative presence of each process in the corresponding channel; 
        computed with respect to the total yield.
        """
        shapedir = "shapes_fit_s"

    combinedCardPath = opts.combinedCardPath
    fitDiagnosticsPath = opts.fitDiagnosticsPath

    # 1. Map channels and processes
    maps = get_maps( combinedCardPath )

    # 2. Read the fit diagnostics and sum yields
    yields = get_yields( fitDiagnosticsPath, maps, shapedir )    
    yields_for_table = deepcopy( yields )
    for ch, yields_ch in yields.items():
        
        # 2.1 Sum over some processes
        yields_for_table_ch = OrderedDict()
        yields_for_table_ch["fakes"]            = {"processes" : ["fakes"]}
        yields_for_table_ch["ZZ"]               = {"processes" : ["prompt_ZZ", "prompt_ggZZ"]}
        yields_for_table_ch["convs"]            = {"processes" : ["convs"]}
        yields_for_table_ch["prompt_TTX"]       = {"processes" : ["prompt_TTX"]}
        yields_for_table_ch["prompt_VVV"]       = {"processes" : ["prompt_VVV"]}
        yields_for_table_ch["prompt_VH"]        = {"processes" : ["prompt_VH"]}
        yields_for_table_ch["prompt_TZQ"]       = {"processes" : ["prompt_TZQ"]}
        yields_for_table_ch["total_background"] = {"processes" : ["total_background"]}
        yields_for_table_ch["total_signal"]     = {"processes" : ["total_signal"]}
        yields_for_table_ch["data"]             = {"processes" : ["data"]}
    

        for group, group_info in yields_for_table_ch.items():
            sub_dict = { group : [ yields_ch[proc] for proc in group_info["processes"] if proc in yields_ch ] }
            summed_group = integrate( sub_dict )

            # Now update the histogram dictionary
            for proc in group_info["processes"]: 
                if proc in yields_ch:
                    yields_ch.pop( proc ) 
            
            yields_ch[group] = summed_group[group]

        yields_for_table[ch] = yields_ch

    # 3. Put it in a format for latex table script
    table = format_table( yields_for_table  )

    # 4. Create the latex table
    table = dict_to_latex_table(table, caption, "yields")
    print(table)

    
