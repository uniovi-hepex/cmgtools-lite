from .producer import producer
from utils.ftree_producer import ftree_producer
from cfgs.lumi import lumis
import os
from cfgs.friends_cfg import friends_mc, friends_data
from cfgs.datasets_cfg import mcas

from functions import color_msg


class plot_producer(producer):
  name = "plot_producer"
  basecommand = "python3 mcPlots.py"
  jobname = "CMGPlot"
  
  def add_more_options(self, parser):
    self.parser = parser
    # -- mca includes to consider -- #
    parser.add_option("--mca", dest = "mca", type="string", default = "wz-run3/mca/mca_wz_3l.txt", 
                  help = '''Input mcafile''')
    # -- CMGTools configuration files -- #
    parser.add_option("--mccfile", dest = "mccfile", type="string", default = None, 
                  help = '''Event selection requirements file''')
    parser.add_option("--plotfile", dest = "plotfile", type="string", default = "wz-run3/common/plots_wz.txt", 
                  help = '''File with plots''')
    parser.add_option("--uncfile", dest = "uncfile", type="string", default = "wz-run3/common/systs-wz.txt",
            help = "File with systematic variations")
    parser.add_option("--treename", dest = "treename", default = "NanoAOD", 
                  help = ''' Name of the tree file ''')
    
    # --- More options for customization --- #
    parser.add_option("--blind", dest = "blind", default = False, action = "store_true",
                  help = ''' Blind data flag.''')
    parser.add_option("--unc", dest = "unc", default = False, action = "store_true",
                  help = ''' Apply uncertainties (default is false).''')
    parser.add_option("--cutfile", dest = "cutfile", default = "wz-run3/common/cuts-srwz.txt",
                  help = ''' Region for cut application.''')
    parser.add_option("--normtodata", dest = "normtodata", default = False, action = "store_true",
                  help = ''' Normalize MC to data.''')
    parser.add_option("--plot-groups", dest = "plot_group", default = None,
                  help = ''' Make groups of plots.''')
    
    # --- Override main producer option for output path
    parser.add_option("--outname", dest = "outname", type="string", default = "plots/",
          help = "Output (folder) name")
    parser.add_option("--unweight", dest = "unweight", action="store_true", default = False,
      help = "Don't use corrections")
    parser.add_option("--unfriend", dest = "unfriend", action="store_true", default = False,
      help = "Don't add friend trees")

    return

  def add_friends(self, maxstep = -1):
      """ Method to add friends to command """
      friends = []
      # Iterate over modules available in this year
      list_friends_mc = [ mcfriend[0] for mcfriend in friends_mc ]
      list_friends_data = [ datafriend[0] for datafriend in friends_data ]
      
      for step, module in enumerate(list_friends_mc):
        if module not in list_friends_data:
          friends.append( "--FMCs {P}/%s"%(module) )
        else:
          friends.append( "--Fs {P}/%s"%(module) )
      return " ".join(friends)
 
  def run(self):
    # Yearly stuff 
    year      = self.year
    outname   = self.outname
    extra     = self.extra
    blind     = self.blind
    uncfile   = self.uncfile
    mccfile   = self.mccfile
    apply_unc = self.unc
    unweight  = self.unweight

    # Other plotting stuff 
    plottingStuff =  "--obj Events "
    plottingStuff += "--maxRatioRange 0.6 1.4 "
    plottingStuff += "--fixRatioRange "
    plottingStuff += "--print C,pdf,png,txt "
    plottingStuff += "--legendWidth 0.23 "
    plottingStuff += "--legendFontSize 0.036 "
    plottingStuff += "--showMCError "
    plottingStuff += "--showRatio "
#    plottingStuff += "--perBin "
    plottingStuff += "--showRatio "
    plottingStuff += "--neg "
    plottingStuff += "--noCms --lspam '#scale[1.1]{#bf{CMS}} #scale[0.9]{#it{Preliminary}}' "
    plottingStuff += "--TotalUncRatioColor 922 922 "
    plottingStuff += "--TotalUncRatioStyle 3444 0 "
    plottingStuff += "--plotgroup prompt_WZ+=prompt_WZ_nonfiducial "
    plottingStuff += "--plotgroup fakes_DY+=fakes_VV,fakes_TT,fakes_T,wjets "

    if self.year != "all":
        lumi   = lumis[year] if self.era == None else lumis[self.era]
        mcpath = os.path.join(self.mcpath, self.year)
        datapath = os.path.join(self.datapath, self.year)
    else:
        year = ",".join(["%s"%y for y in lumis if y in ["2022", "2022EE"]])
        lumi = ",".join(["%s"%lumis[y] for y in lumis if y in ["2022", "2022EE"]])
        mcpath = self.mcpath
        datapath = self.datapath
    
    
    # List with all the options given to CMGTools
    self.commandConfs = ["%s"%self.mca, 
                   "%s"%self.cutfile,
                   "%s"%self.plotfile,
                   "-l %s"%lumi,
                   "--year %s"%year if self.era == None else "--year %s"%self.era,
                   "-f --pdir %s"%outname,
                   "--tree %s "%self.treename,
                   "-P {mcpath} -P {datapath}".format(mcpath = mcpath, datapath = datapath),
                   self.add_friends() if not self.unfriend else "",
                   "-L " + " -L ".join(self.functions),
                   "-W '%s'"%("*".join(self.weights)) if not unweight else "", # Always keep PU weights
                   "%s"%plottingStuff,
                   "-j %s"%(self.ncores),
                   "--mcc %s"%mccfile if mccfile != None else "", 
                   "--unc %s"%uncfile if apply_unc else "",
                   "--xp data" if blind else "",
                   "%s"%extra]
    return


