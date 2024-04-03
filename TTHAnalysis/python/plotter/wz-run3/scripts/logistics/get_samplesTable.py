""" Script to plot a table with all sample metadata in LaTeX format """
import os,sys

sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table
from functions import color_msg
from cfgs.datasets_cfg import mcas, mcas_fr

if __name__ == "__main__":
    table_mc = {
            "Short name" : [],
            #"DAS" : [],
            "$\sigma$" : [],
            "Plotting group" : []
    }


    # Make table for MC
    color_msg(" >> Table for MC:", "green")
    caption_mc="""Background and signal MC samples used in the analysis, their associated cross 
    section times branching fraction and the plotting group in which each one is included during the different steps
    of the analysis. Each sample name has to be completed with the Run3Summer2022EE. Samples marked in \\textcolor{red}{red} are 
    listed as missing samples."""
    for mcagroup, mcaitem in mcas.items():
        if mcagroup == "data" : continue
        for group, dsets in mcaitem.get_datasets().items():
            for dset in dsets:
                dset.get_pure_nanoaod("2022PostEE")
                if dset.exists:
                    table_mc["Short name"].append(dset.dbsname.replace("_","\_"))
                    table_mc["$\sigma$"].append("%3.2f"%dset.xsec)
                    table_mc["Plotting group"].append(mcagroup)
                else:
                    table_mc["Short name"].append("\\textcolor{red}{%s}"%dset.dbsname.replace("_","\_"))
                    table_mc["$\sigma$"].append("\\textcolor{red}{%3.2f}"%dset.xsec)
                    table_mc["Plotting group"].append("\\textcolor{red}{%s}"%mcagroup)
    table = dict_to_latex_table(table_mc, caption_mc, "Samples2022EE")
    print(table)  
    color_msg(" ---------------------- ", "green")

#for biggroup, dset in datasets["mc"].items():
#    for subgroup, samples in dset.items():
#        for sample in samples:
#            table_mc["Short name"].append(sample.name.replace("_","\_"))
#            table_mc["DAS"].append("%s/"%sample.dbspath.replace("_", "\_"))#.split("/")[1])
#            #table_mc["$\sigma$"].append("%3.2f"%sample.xsec)
#            table_mc["Plotting group"].append(sample.label)

    # Rearrange plotting group to show just one cell
    
