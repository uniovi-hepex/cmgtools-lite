from .producer import producer
from utils.ftree_producer import ftree_producer
from cfgs.lumi import lumis
import os
from cfgs.friends_cfg import friends_mc, friends_data
from cfgs.datasets_cfg import mcas

from functions import color_msg


class dump_producer(producer):
  name = "dump_producer"
  basecommand = "python3 mcDump.py"
  jobname = "CMGDump"
  
  def add_more_options(self, parser):
    self.parser = parser
    # -- mca includes to consider -- #
    parser.add_option("--mca", dest = "mca", type="string", default = "wz-run3/mca/mca_wz_3l.txt", 
                  help = '''Input mcafile''')
    # -- CMGTools configuration files -- #
    parser.add_option("--mccfile", dest = "mccfile", type="string", default = None, 
                  help = '''Event selection requirements file''')
    parser.add_option("--treename", dest = "treename", default = "NanoAOD", 
                  help = ''' Name of the tree file ''')
    
    # --- More options for customization --- #
    parser.add_option("--cutfile", dest = "cutfile", default = "wz-run3/common/cuts-srwz.txt",
                  help = ''' Region for cut application.''')
    parser.add_option("--expression", dest = "expression", default = "{event|luminosityBlock}",
                  help = ''' Expression to dump.''')

    # --- Override main producer option for output path
    parser.add_option("--outname", dest = "outname", type="string", default = "dumps/",
          help = "Output (folder) name")
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
    mccfile   = self.mccfile

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
                   "-l %s"%lumi,
                   "--year %s"%year,
                   "-f ",
                   "--tree %s "%self.treename,
                   "-P {mcpath} -P {datapath}".format(mcpath = mcpath, datapath = datapath),
                   self.add_friends() if not self.unfriend else "",
                   "-L " + " -L ".join(self.functions),
                   "-j %s"%(self.ncores),
                   "--mcc %s"%mccfile if mccfile != None else "", 
                   "'%s'"%self.expression,
                   "--dumpFile %s/out.log"%(outname),
                   "%s"%extra]
    return


