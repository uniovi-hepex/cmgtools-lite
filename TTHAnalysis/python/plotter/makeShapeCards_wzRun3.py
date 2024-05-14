''' Script to generate datacards for the WZ analysis '''

# -- Import libraries -- #
from CMGTools.TTHAnalysis.plotter.mcAnalysis import *
from CMGTools.TTHAnalysis.plotter.histoWithNuisances import _cloneNoDir
from optparse import OptionParser
import re, sys, os, os.path

# -- Define functions -- #
def log_msg(msg, msgtype = "INFO"):
  print(("[makeShapeCards_wzRun3:%s]: %s"%(msgtype, msg)))
  return

parser = OptionParser(usage="%prog [options] mc.txt cuts.txt var bins")
addMCAnalysisOptions(parser)
parser.add_option("--od", "--outdir",       dest="outdir", type="string", default="", help="output directory name")
parser.add_option("--asimov",               dest="asimov", type="string", default=None, help="Use an Asimov dataset of the specified kind: including signal ('signal','s','sig','s+b') or background-only ('background','bkg','b','b-only')")
parser.add_option("--bbb",                  dest="bbb", type="string", default=None, help="Options for bin-by-bin statistical uncertainties with the specified nuisance name")
parser.add_option("--amc", "--autoMCStats", dest="autoMCStats", action="store_true", default=False, help="use autoMCStats")
parser.add_option("--autoMCStatsThreshold", dest="autoMCStatsValue", type="int", default=10, help="threshold to put on autoMCStats")
parser.add_option("--infile",               dest="infile", action="store_true", default=False, help="Read histograms to file")
#parser.add_option("--binname",              dest="binname", type="string", default=None, help="binname")
parser.add_option("--savefile",             dest="savefile", action="store_true", default=False, help="Save histos to file")
parser.add_option("--categorize",           dest="categ", type="string", nargs=3, default=None, help="Split in categories. Requires 3 arguments: expression, binning, bin labels")
parser.add_option("--categorize-by-ranges", dest="categ_ranges", type="string", nargs=2, default=None, help="Split in categories according to the signal extraction variables. Requires 2 arguments: binning (in bin numbers), bin labels")
parser.add_option("--regularize",           dest="regularize", action="store_true", default=False, help="Regularize templates")
parser.add_option("--threshold",            dest="threshold", type=float, default=0.0, help="Minimum event yield to consider processes")
parser.add_option("--filter",               dest="filter", type="string", default=None, help="File with list of processes to be removed from the datacards")
parser.add_option("--storeAll",             dest = "storeall",       action = "store_true", default = False, help = "Store all histograms in the final rootfile, including those of normalisation uncertainties.")
parser.add_option("--notMinimumFill",       dest = "notminimumfill", action = "store_true", default = False, help = "Don't crop bins whenever they show low number of entries, or negative ones.")
parser.add_option("--notVarsChanges",       dest = "notvarschanges", action = "store_true", default = False, help = "Don't modify variations in extreme situations.")
parser.add_option("--notCropNegUncs",       dest = "cropnegativeuncs", action = "store_true", default = False, help = "Don't crop uncertainties of histograms that might go below zero.")
parser.add_option("--forceShape",           dest = "forceshape",     type = "string",       default = "",    help = "Force this list of nuisances to be of shape origin.")
parser.add_option("--minBinContent",        dest = "minbincont",     type = float,       default = 1e-5,    help = "Minimum content of any bin.")
(options, args) = parser.parse_args()
options.weight = True
options.final  = True
  
def read_histograms(mca, cuts, report, options):
  ''' To read histograms from an input file '''  
  log_msg(" >> Reading file with input histograms...")
  infile = ROOT.TFile(outdir+binname+".bare.root","read")
  
  # This fetches a list with all signal processes
  # even those that are marked with "SkipMe".
  
  processes = mca.listSignals(True) 
  processes.extend(mca.listBackgrounds(True)) # same with background processes
  processes.extend(['data'])
  
  for p in processes:
    # Now read only variated MC histograms 
    variations = mca.getProcessNuisances(p) if p != "data" else []
    h = readHistoWithNuisances(infile, "x_"+p, variations, mayBeMissing=True)
    if h: 
      report[p] = h 
  return report
  
def get_histograms(mca, cuts, report, options):
  ''' This function creates variated histograms using TTree::Draw '''
  log_msg(" >> Getting histograms for processes")
  categorize = options.categ
  if categorize:
    cexpr, cbins, _ = options.categ
    report = mca.getPlotsRaw("x", cexpr+":"+args[2], makeBinningProductString(args[3],cbins), cuts.allCuts(), nodata=options.asimov, closeTreeAfter=True)
  else:
    report = mca.getPlotsRaw("x", args[2], args[3], cuts.allCuts(), nodata=options.asimov, closeTreeAfter=True)
  return report

def apply_asimov(mca, cuts, report, options):
  ''' This function create an asimov dataset for s+b or b-only hypothesis '''
  if options.asimov in ("s","sig","signal","s+b"):
    asimovprocesses = mca.listSignals() + mca.listBackgrounds()
  elif options.asimov in ("b","bkg","background", "b-only"):
    asimovprocesses = mca.listBackgrounds()
  else: 
    raise RuntimeError("the --asimov option requires to specify signal/sig/s/s+b or background/bkg/b/b-only")
  
  # -- Iterate over asimov processes: equal to the sum of all processes considered in the asimov dataset
  tomerge = None
  for p in asimovprocesses:
    if p in report: 
      if tomerge is None:
        tomerge = report[p].raw().Clone("x_data_obs")
        tomerge.SetDirectory(ROOT.nullptr)
      else: 
        tomerge.Add(report[p].raw())
  report['data_obs'] = HistoWithNuisances(tomerge)
  return report

def apply_categorisation(mca, cuts, report, options, allreports, binname):
  ''' This function is used when categorisation in different channels is required ''' 

  catlabels = options.categ[2].split(",")
  if len(catlabels) != report["data_obs"].GetNbinsY(): 
    raise RuntimeError("Mismatch between category labels and bins")
  for icat, label in enumerate(catlabels):
    kk = {}
    for (k, h) in report.items():
      kk[k] = h.projectionX("x_%s"%k, icat+1, icat+1)
    allreports["%s_%s"%(binname, label)] = kk
  return allreports

def apply_categorisation_ranges(mca, cuts, report, options, allreports, binname):
  ''' This function categorises based on bin ranges. Useful for e.g. regions defined
      by a given MVA discriminator value. '''
  catlabels = options.categ_ranges[1].split(',')
  catbinning = eval( options.categ_ranges[0] ) 
    
  for ic,lab in enumerate(catlabels):
    kk = {} 
    for (k,h) in report.items(): 
      kk[k] = h.getHistoInRange("x_%s"%k, catbinning[ic], catbinning[ic+1])
    allreports["%s_%s"%(binname,lab)] = kk
  return allreports
  
def apply_filtering(mca, cuts, report, options):
  ''' This function filters processes '''
  toremove = []
  
  # Open filter file
  f = open(options.filter, 'r')
  lines = f.readlines()
  for l in lines:
    binname, proc = l.split(':')
    procpattern = re.compile(proc.rstrip())
    if binname in report:
      for p in allreports[binname]:
        if procpattern.match(p) and (binname, p) not in toremove:
          toremove.append( (binname, p) )
  
  # Now remove
  for binname, p in toremove:
    report[binname].pop(p)
  return report

def apply_bin_by_bin(report):
  for p,h in report.items():
    if p not in ("data", "data_obs"):
      h.addBinByBin(namePattern = "%s_%s_%s_bin{bin}" % (options.bbb, binname, p), conservativePruning = True)
  return

def find_shapes(options):
  """ 
  This function reads the variations file and finds which inputs
  must be put as shape in the datacard (otherwise everything is set to lnN when
  doing categories). This is duplicated work but it's the quickes thing to
  implement.
  """
  shapes = []
  variation_list = options.variationsFile
  f = open(variation_list, "r")
  for line in f.readlines():
    if line[0].strip() in ["#", "", "$"]: continue
    if "template" in line: shapes.append( line.split(":")[0].strip())
  f.close()
  return shapes

def get_systematics(mca, cuts, report, options, binname, shapes):
  ''' Function to process histogram and write datacard '''
  # Iterate over bin names and reports 
  
  # Check which option to use for MC stat propagation (aMC: barlow-beeston, bbb: bin-by-bin)
  if options.bbb and options.autoMCStats: 
    raise RuntimeError("Can't use --bbb together with --amc/--autoMCStats")
  elif options.bbb: 
    apply_bin_by_bin(report)
    
  # Crop all uncertainties to 100% to avoid negative variations if desired
  if not options.cropnegativeuncs:
    for p, h in report.items():
      for b in range(1, h.GetNbinsX() + 1):
        h.SetBinError(b, min(h.GetBinContent(b), h.GetBinError(b)))
        
  # List all the nuisances to be written in the cards.
  nuisances = sorted(listAllNuisances(report))
  log_msg("List of nuisances considered: %s"%(["%s"%n for n in nuisances]))
  log_msg("Shape uncertainties: %s"%(["%s"%s for s in shapes]))

  allyields = dict([(p, h.Integral()) for p, h in report.items()])
  
  procs = []
  iproc = {}
  
  signals     = mca.listSignals()
  backgrounds = mca.listBackgrounds()
  
  
  # Keep track of the position of a given process within the list of processes
  for i, p in enumerate(signals + backgrounds):
    if p not in allyields: continue
    if allyields[p] <= options.threshold:
      print(("Dropping %s due to low statistics"%p))
      continue
    procs.append(p)        
    iproc[p] = i+1
    if p in signals:
      iproc[p] -= len(signals)
    
  # Now iterate over the systematics
  systs = {}
  for name in nuisances:
    effshape = {}
    isShape = False
    
    # Iterate over processes
    for p in procs:
      h = report[p]

      # Make use of param name to filter by channel
      if "eee" in name and "eee" not in binname:  
          print(" >> Skipping %s for %s"%(name, binname))
          continue
      if "eem" in name and "eem" not in binname:
          print(" >> Skipping %s for %s"%(name, binname))
          continue
      if "mme" in name and "mme" not in binname:
          print(" >> Skipping %s for %s"%(name, binname))
          continue
      if "mmm" in name and "mmm" not in binname: 
          print(" >> Skipping %s for %s"%(name, binname))
          continue

      n0 = h.Integral()
       
      # First, check if the process has this variation
      if not h.hasVariation(name): continue
      
      # Is it a shape variation?
      isShape = name in shapes #isShape or h.isShapeVariation(name, debug = True)
      log_msg("Is %s nuisance shape? %s"%(name, isShape))
      
      
      variants = list(h.getVariation(name))  
      
      # Treatment of extreme cases: symmetrization
      for bini in range(1, h.GetNbinsX()+1):
        for d in range(2):
          # Case variant has no content: shift by a small factor
          if variants[d].GetBinContent(bini) == 0: 
            shift = max(5e-6, variants[1-d].GetBinContent(bini))
            variants[d].SetBinContent(bini, h.raw().GetBinContent(bini)**2/shift)
          # Case variant is big in comparison with nominal
          
          # --- Check for float divisions by 0
          if h.raw().GetBinContent(bini) == 0:
            log_msg("Histogram %s has 0 content in bin %d for nuisance %s"%(h.GetName(), bini, name), "WARNING")
            h.raw().SetBinContent(bini, 1e-5) 
            #sys.exit()
            
          if variants[d].GetBinContent( bini )/h.raw().GetBinContent(bini) > 10: 
            log_msg("Big shift in template for %s %s %s %s in bin %d: variation = %g"
                    %( binname, p, name, d, bini, variants[d].GetBinContent( bini )/h.raw().GetBinContent(bini)), "WARNING")
                    
            variants[d].SetBinContent( bini, 10*h.raw().GetBinContent(bini) )
          if variants[d].GetBinContent( bini )/h.raw().GetBinContent(bini) < 0.1: 
            log_msg("Big shift in template for %s %s %s %s in bin %d: variation = %g"
                    %( binname, p, name, d, bini, variants[d].GetBinContent( bini )/h.raw().GetBinContent(bini)), "WARNING")
            variants[d].SetBinContent( bini, 0.1*h.raw().GetBinContent(bini) )

      # Now save into dictionary
      effshape[p] = variants

    # Now prepare lines for data cards
    if isShape: # Shape uncertainty
      if options.regularize:
        for p in procs: report[p].regularizeVariation(name, binname = binname)
      systs[name] = ("shape", dict((p, "1" if p in effshape else "-") for p in procs), effshape)
    else:       # Normalization unc.
      effyield = dict((p, "-") for p in procs)
      isNorm = False
      for p, (hup, hdn) in effshape.items():
        i0 = allyields[p]
        kup, kdn = hup.Integral()/i0, hdn.Integral()/i0
        
        # Choose to apply (a)symm normalizations based on how much they
        # vary the nominal yield.
        
        # If the variations are small and close to 1: symmetric variation
        if abs(kup*kdn-1) < 1e-5 or abs(kdn-1) < 5e-4:
          if abs(kup-1) > 5e-4:
            effyield[p] = "%.3f"%kup
            isNorm = True
        else: # asymmetric variation
          effyield[p] = "%.3f/%.3f"%(kdn, kup) 
          isNorm = True
          
        # Create line for datacard.
        if isNorm or options.storeall:
          thedict = {}
          if options.storeall:
            thedict = effshape
          if name.endswith("_lnU"):
            systs[name] = ("lnU", effyield, thedict)
          else:
            systs[name] = ("lnN", effyield, thedict)

  return systs,allyields,procs, iproc
  
def write_datacards(mca, cuts, report, options, systs, outdir, binname, allyields, procs, iproc):
  nuisances = sorted(systs.keys())
  
  datacard = open(os.path.join(outdir, binname + ".txt"), "w")
  datacard.write("shapes *        * %s.root x_$PROCESS x_$PROCESS_$SYSTEMATIC\n" % binname)
  datacard.write('##----------------------------------\n')
  datacard.write('bin         %s\n' % binname)
  datacard.write('observation %s\n' % allyields['data_obs'])
  datacard.write('##----------------------------------\n')
  klen = max([7, len(binname)]+[len(p) for p in procs])
  kpatt = " %%%ds "  % klen
  fpatt = " %%%d.%df " % (klen,3)
  npatt = "%%-%ds " % max([len('process')]+list(map(len,nuisances)))
  datacard.write('##----------------------------------\n')
  datacard.write((npatt % 'bin    ')+(" "*6)+(" ".join([kpatt % binname  for p in procs]))+"\n")
  datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % p        for p in procs]))+"\n")
  datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % iproc[p] for p in procs]))+"\n")
  datacard.write((npatt % 'rate   ')+(" "*6)+(" ".join([fpatt % allyields[p] for p in procs]))+"\n")
  datacard.write('##----------------------------------\n')
  towrite = [ report[p].raw() for p in procs ] + [ report["data_obs"].raw() ]
  for name in nuisances:
    (kind,effmap,effshape) = systs[name]
    datacard.write(('%s %5s' % (npatt % name,kind)) + " ".join([kpatt % effmap[p]  for p in procs]) +"\n")
    for p,(hup,hdn) in effshape.items():
      towrite.append(hup.Clone("x_%s_%sUp"   % (p,name)))
      towrite.append(hdn.Clone("x_%s_%sDown" % (p,name)))
  if options.autoMCStats:
    datacard.write('* autoMCStats %d\n' % options.autoMCStatsValue)


  workspace = ROOT.TFile.Open(outdir+binname+".root", "RECREATE")
  for h in towrite:
    workspace.WriteTObject(h,h.GetName())
  workspace.Close()

  log_msg("Wrote to {0}.txt and {0}.root .".format(outdir+binname))
  return

# -- Main code -- #
if __name__ == "__main__":
#  options = add_parsing_options()

  # -- Load MCA and cut files
  mca  = MCAnalysis(args[0], options)
  cuts = CutsFile(args[1], options) 

  
  if not options.binname:
    binname = os.path.basename(args[1]).replace(".txt", "") 
  else:
    binname = options.binname
  outdir = os.path.join( options.outdir ) 
  if not os.path.exists(outdir): os.mkdir(outdir)


  # -- Preprocessing
  report = {}


  ''' 1) Read/get histograms to be written into the cards '''
  # Read the histograms that are going to be processed
  if options.infile:
    report = read_histograms(mca, cuts, report, options)
  else:
    report = get_histograms(mca, cuts, report, options)



  ''' 2) Apply criteria based on input options '''
  ## Asimov dataset for blind results
  if options.asimov:
    report = apply_asimov(mca, cuts, report, options)
  else:
    report['data_obs'] = report['data'].Clone("x_data_obs")


  ## Categorisation
  allreports = {}
  if options.categ:
    allreports = apply_categorisation(mca, cuts, report, options, allreports, binname)
  elif options.categ_ranges:
    allreports = apply_categorisation_ranges(mca, cuts, report, options, allreports, binname)
  else:
    allreports = {binname : report}
  
  ## Filtering
  if options.filter:
    allreports = apply_filtering(mca, cuts, report, allreports, options)
  
  shapes = find_shapes(options)
  for binname, report in allreports.items():
    ''' 3) Processing '''
    systs, yields, procs, iproc = get_systematics(mca, cuts, report, options, binname, shapes)
    
    
    ''' 4) Write datacards '''
    write_datacards(mca, cuts, report, options, systs, outdir, binname, yields, procs,iproc)
  
  
  
  
  
  
  
  
  
