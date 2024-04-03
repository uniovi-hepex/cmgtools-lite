# Config file with processes. Used to create MCAs mostly
import sys
import os
import re
sys.path.append( os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3/"))
from cfgs.samplepaths import samplepaths as paths
from cfgs.datasets_cfg import mcas, mcas_fr
from functions import color_msg

from optparse import OptionParser



def get_local_files(name, inpath):
    files = list(filter(lambda element: name in element, os.listdir(inpath)))
    files = [file_.replace(".root", "") for file_ in files]
    return files

def add_parsing_opts():
  """ Function with base parsing arguments used by any script """
  parser = OptionParser(usage = "python wz-run.py [options]", 
                                 description = "Main options for running WZ analysis") 
  # -- Input and outputs
  parser.add_option("--analysis", dest = "analysis", default = "main", 
              help = "Main analysis or FR")
  return parser.parse_args()


def write_mca_mainAnal(year):
    template_line = '{procname}: {files}: {norm} {cut} ;FillColor={fc}, Label="{label}", genSumWeightName="genEventSumw"\n'
    template_line_data = '{procname}: {files}; Label="data"\n'
    targetpath = os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3/mca")
    
    f_global = open( os.path.join(targetpath, "mca_wz_3l.txt"), "w" )
    color_msg("> Year %s"%year, "blue")
    for mcagroup, mcaitem in mcas.items():
        color_msg(">> Writing mca for: %s"%mcagroup, "blue")
        f_global.write("## %s\n"%mcagroup)
        f_global.write('incl_{mca} : + ; IncludeMca="wz-run3/mca/includes/mca-{mca}.txt"\n\n'.format(mca = mcagroup))
        f_mca = open( os.path.join(targetpath, "includes/mca-{mca}.txt".format(mca = mcagroup)), "w" )

        for group, dsets in mcaitem.get_datasets().items():
            color_msg("  + Adding process group: %s"%group, "yellow")

            for dset in dsets:
                dname = dset.processname
                color_msg("    o Adding process: %s"%dname, "green")
                
                inpath = os.path.join(paths["processed"], "data" if group == "data" else "mc", year )
                
                files = get_local_files( dname, inpath )
                if files == []:
                    color_msg("    o There are no files for %s"%dname, "red")
                    continue
                
                if mcagroup != "data":
                    line = template_line.format(
                        procname = group, 
                        files = "+".join(files), 
                        norm = dset.xsec, 
                        cut = "", 
                        fc = dset.fC, 
                        label = group
                    )    
                else:
                    line = template_line_data.format(
                        procname = group,
                        files = "+".join(files), 
                    )
                    
                f_mca.write("## {}\n".format(dname))
                f_mca.write("{line}\n".format(line = line))
            f_mca.write("\n\n")
            
        f_mca.close()
    f_global.close()
    
    return

    
if __name__ == "__main__":
    (opts, args) = add_parsing_opts()
    analysis = opts.analysis
    if analysis == "main":
        for year in ["2022EE"]:
            write_mca_mainAnal(year)
