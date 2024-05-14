'''
Based on @cericeci's postprocessor
-----------------------------------
Config file defines two things: POSTPROCESSOR and selectedComponents. 
 * selectedComponents is read by the submitter to configure the different samples. 
 * POSTPROCESSOR is read at running time, and configures the modules to run 
   using the json file produced.
-----------------------------------
'''

# -- Import libraries -- #
### Main
import re, os, sys
from copy import deepcopy
### CMGTools
from CMGTools.RootTools.samples.configTools import printSummary, mergeExtensions, doTestN, configureSplittingFromTime, cropToLumi
from CMGTools.RootTools.samples.autoAAAconfig import autoAAA
from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator

### For crab submission
from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption


def byCompName(components, regexps):
  return [ c for c in components if any(re.match(r, c.name) for r in regexps) ]


# -- Unpack submission configurations  -- #
year              = getHeppyOption("year", "2022")
analysis          = getHeppyOption("analysis", "main")    
selectComponents  = getHeppyOption('selectComponents')
justSummary       = getHeppyOption("justSummary")
test              = getHeppyOption("test")
preprocessor      = 0
quiet             = not(getHeppyOption("verboseAAA", False))
applyTriggersInMC = getHeppyOption('applyTriggersInMC')

### Prepare samples for submission 
doData = (selectComponents == "DATA")

# -- Import sample configuration files -- #

# -- From ~10 fb-1 (preEE)
if year == "2022": 
  if analysis == "main":
    from CMGTools.RootTools.samples.samples_13p6TeV_mc2022_nanoAODv12_fromLocal   import mcSamples_toImport   as mcSamples_
    from CMGTools.RootTools.samples.samples_13p6TeV_data2022_nanoAODv12_fromLocal import dataSamples_toImport as allData
  elif analysis == "fr":
    from CMGTools.RootTools.samples.samples_13p6TeV_mc_FR_2022_nanoAODv12_fromLocal   import mcSamples_toImport   as mcSamples_
    allData = []
  elif analysis == "fiducial":
    from CMGTools.RootTools.samples.samples_13p6TeV_mc2022_nanoAODv12_fromLocal_unskimWZ  import mcSamples_toImport  as mcSamples_
    allData = []
   
# -- From 20.06 fb-1 (March 2023 -- FG -- postEE)
elif year == "2022EE":
  if analysis == "main":
    from CMGTools.RootTools.samples.samples_13p6TeV_mc2022EE_nanoAODv12_fromLocal   import mcSamples_toImport   as mcSamples_
    from CMGTools.RootTools.samples.samples_13p6TeV_data2022EE_nanoAODv12_fromLocal import dataSamples_toImport as allData
  elif analysis == "fr":
    from CMGTools.RootTools.samples.samples_13p6TeV_mcFR2022EE_nanoAODv12_fromLocal  import mcSamples_toImport  as mcSamples_
    from CMGTools.RootTools.samples.samples_13p6TeV_dataFR2022EE_nanoAODv12_fromLocal  import dataSamples_toImport  as allData
  elif analysis == "fiducial":
    from CMGTools.RootTools.samples.samples_13p6TeV_mc2022EE_nanoAODv12_fromLocal_unskimWZ  import mcSamples_toImport  as mcSamples_
    allData = []
        
autoAAA(mcSamples_ + allData, 
        quiet         = quiet, 
        redirectorAAA = "xrootd-cms.infn.it",
        node          = 'T2_ES_IFCA') 
mcSamples_, _ = mergeExtensions(mcSamples_) ### autoAAA must be created before call mergeExtensions

# From now on, just use 2022 for everything
if year == "2022EE" or year == "2022": 
  yearstr = year
  year = 2022

### Set up trigger paths 
if year == 2022:
  from CMGTools.TTHAnalysis.tools.nanoAOD.triggers_13p6TeV_DATA2022 import triggerGroups_dict

DatasetsAndTriggers = {}; DatasetsAndVetos = {} 

### Double muon
DatasetsAndTriggers["DoubleMuon"] = triggerGroups_dict["triggers_mumu_iso"][year]
DatasetsAndTriggers["DoubleMuon"].extend(triggerGroups_dict["triggers_3mu"][year])

### MuonEG
DatasetsAndTriggers["MuonEG"] = triggerGroups_dict["triggers_2mu1e"][year]
DatasetsAndTriggers["MuonEG"].extend(triggerGroups_dict["triggers_mue"][year])
DatasetsAndTriggers["MuonEG"].extend(triggerGroups_dict["triggers_2e1mu"][year])
DatasetsAndTriggers["MuonEG"].extend(triggerGroups_dict["triggers_mue_noiso"][year])

### E-Gamma
DatasetsAndTriggers["EGamma"] = triggerGroups_dict["triggers_3e"][year] 
DatasetsAndTriggers["EGamma"].extend(triggerGroups_dict["triggers_ee"][year])
DatasetsAndTriggers["EGamma"].extend(triggerGroups_dict["triggers_ee_noniso"][year])
DatasetsAndTriggers["EGamma"].extend(triggerGroups_dict["triggers_1e_iso"][year])
#DatasetsAndTriggers["EGamma"].extend(deepcopy(triggerGroups_dict["triggers_etau"])

### SingleMuon
DatasetsAndTriggers["SingleMuon"] = triggerGroups_dict["triggers_1mu_iso"][year]
#DatasetsAndTriggers["SingleMuon"].extend(deepcopy(triggerGroups_dict["triggers_mutau"])

### Muon dataset = DoubleMuon + SingleMuon (from era D onwards)
DatasetsAndTriggers["Muon"] = deepcopy(DatasetsAndTriggers["DoubleMuon"])
DatasetsAndTriggers["Muon"].extend(deepcopy(DatasetsAndTriggers["SingleMuon"]))

### MET
DatasetsAndTriggers["JetMET"] = triggerGroups_dict["triggers_met"][year]
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_htmet"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_metNoMu100_mhtNoMu100"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_pfht"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_pfht1050"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_pfht800_mass50"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_pfjet500"][year])
DatasetsAndTriggers["JetMET"].extend(triggerGroups_dict["triggers_pfjet400_mass30"][year])


### TRIGGER OVERLAP REMOVAL: inherited from tt-run3 analysis
# -- Do not veto MuonEG datasets
DatasetsAndVetos["MuonEG"]     = [] 

# -- Veto DoubleMuon with MuonEG
DatasetsAndVetos["DoubleMuon"] = deepcopy(DatasetsAndTriggers["MuonEG"])

# -- Same for Muon
DatasetsAndVetos["Muon"]       = deepcopy(DatasetsAndTriggers["MuonEG"])

# -- Veto EGamma with the remaining datasets
DatasetsAndVetos["EGamma"]     = deepcopy(DatasetsAndTriggers["MuonEG"])
DatasetsAndVetos["EGamma"].extend(deepcopy(DatasetsAndTriggers["DoubleMuon"])) 
DatasetsAndVetos["EGamma"].extend(deepcopy(DatasetsAndTriggers["Muon"])) 

# -- Same for SingleMuon
DatasetsAndVetos["SingleMuon"] = deepcopy(DatasetsAndTriggers["MuonEG"])
DatasetsAndVetos["SingleMuon"].extend(deepcopy(DatasetsAndTriggers["DoubleMuon"]))
DatasetsAndVetos["SingleMuon"].extend(deepcopy(DatasetsAndTriggers["EGamma"]))

# -- Do not veto MET triggers with lepton triggers. That way we can use JetMET samples
#    to measure trigger efficiencies. 
DatasetsAndVetos["JetMET"] = []

selectedComponents = []

if doData:
  dataSamples = []
  for pd, trigs in DatasetsAndTriggers.items():
    if not trigs: continue
    for comp in byCompName(allData, [pd+"_"]):
      print("---")
      print(("Adding to %s dataset"%comp.name))
      comp.triggers = trigs[:]
      print((" >> triggers %s"%trigs[:]))
      comp.vetoTriggers = DatasetsAndVetos[pd][:]
      print((" >> vetoTriggers %s"%DatasetsAndVetos[pd][:]))
      dataSamples.append(comp)
  selectedComponents = dataSamples 
else:
  mcSamples = byCompName(mcSamples_, ["%s$"%dset for dset in [
      # ----------------- Single boson
      "WtoLNu_2Jets",
      # ----------------- Drell Yan
      "DYto2L_2Jets_MLL_50",
      "DYto2L_2Jets_MLL_50_NLO",
      "DYto2L_4Jets_MLL_50_LO",
      "DYto2L_2Jets_MLL_10to50",
      # ----------------- ttbar
      "TTto2L2Nu",
      "TTTo2J1L1Nu",
      # ----------------- single top + tW
      "TbarWplusto2L2Nu",
      "TWminusto2L2Nu",
      # ----------------- conversions
      "WZGtoLNuZG",
      "WGtoLNuG_1Jets_PTG_200",
      "WGtoLNuG_1Jets_PTG_100to200",
      "WGtoLNuG_1Jets_PTG_10to100", 
      "DYGto2LG_1Jets_MLL_4to50_PTG_10to100",
      "DYGto2LG_1Jets_MLL_4to50_PTG_100to200",
      "DYGto2LG_1Jets_MLL_4to50_PTG_200",
      "DYGto2LG_1Jets_MLL_50_PTG_10to50",
      "DYGto2LG_1Jets_MLL_50_PTG_50to100",
      "DYGto2LG_1Jets_MLL_50_PTG_100to200",
      "DYGto2LG_1Jets_MLL_50_PTG_200to400",
      "DYGto2LG_1Jets_MLL_50_PTG_400to600",
      "DYGto2LG_1Jets_MLL_50_PTG_600",
      # ----------------- ttV
      #"TTWToLNu_fxfx", 
      #"TTZToLLNuNu", 
      #"TTZToLLNuNu_m1to10",
      #'TTWToLNu', 
      #"TTWToLNu_EWK",
      # ----------------- ttH + tHq/tHW
      #"TTHnobb_pow",
      #"THQ", 
      #"THW", 
      #"TTH_ctcvcp",
      #'TTH_pow',
      # ----------------- Top + V rare processes
      "TTLL_MLL_50",
      "TTLL_MLL_4to50",
      "TTLNu_1Jets",
      "TTHtoNon2B_M_125",
      "TTG_1Jets_PTG_200",
      "TTG_1Jets_PTG_10to100",
      "TTG_1Jets_PTG_100to200",
      "TZQB_Zto2L_4FS_MLL_30",
      #"TZQToLL",
      #"tWll",
      # "TTWW","TTWW_LO",
      #'TTTT_P8M2T4','TTTT',
      #'tZq_ll_1','tZq_ll_2',
      # ----------------- Diboson
      "WZto3LNu",
      "WZto3LNu_pow",
      "WZto3LNu_amc",
      "ZZto4L",
      "ZZto2L2Nu",
      "ZZto2L2Q",
      "GluGlutoContinto2Zto4Tau",
      "GluGlutoContinto2Zto4Mu",
      "GluGlutoContinto2Zto4E",
      "GluGlutoContinto2Zto2E2Mu",
      "GluGlutoContinto2Zto2E2Tau",
      "GluGlutoContinto2Zto2Mu2Tau",
      "WWto2L2Nu",
      #"WWTo2L2Nu"
      #"WW_DPS", 
      #"WpWpJJ",
      #"WWTo2L2Nu_DPS",
      # ----------------- TRIBOSON  
      "WWW_4F",
      "WWZ_4F",
      "WZZ", 
      "ZZZ",
      "WZG",
      "VH_HtoNonbb_M_125",
      # ----------------- Other Higgs processes
      "ggHtoZZto4L",
      #"qqHZZ4L", 
      #"VHToNonbb", 
      #"VHToNonbb_ll", 
      #"ZHTobb_ll", 
      #"ZHToTauTau", 
      #"TTWH", 
      #"TTZH",
      # ------------------ For fake rate
      "TTtoLNu2Q",
      "WZto2L2Q",
      "QCD_PT.*Enriched",
      "QCD_PT.*MuEnriched.*",
      "QCD_PT.*bcToE.*",
  ]])
  # -- Apply trigger in MC -- # 
  mcTriggers = sum((trigs for (pd,trigs) in DatasetsAndTriggers.items() if trigs), [])
  if applyTriggersInMC :
      for comp in mcSamples:
          comp.triggers = mcTriggers
  selectedComponents = mcSamples 

# -- Create the submitter -- #
autoAAA(selectedComponents, 
        quiet=quiet, 
        redirectorAAA="xrootd-cms.infn.it")

### Configure for efficient processing
if not doData:
  if year==2022:
      configureSplittingFromTime(byCompName(mcSamples,['^(?!(TTJets_Single|T_|TBar_)).*']),150 if preprocessor else 10,12)
      configureSplittingFromTime(byCompName(mcSamples,['^(TTJets_Single|T_|TBar_).*']),70 if preprocessor else 10,12)
      #configureSplittingFromTime(dataSamples,50 if preprocessor else 5,12)
  else: # rerunning deepFlavor can take up to twice the time, some samples take up to 400 ms per event
      configureSplittingFromTime(byCompName(mcSamples,['^(?!(TTJets_Single|T_|TBar_)).*']),300 if preprocessor else 10,12)
      configureSplittingFromTime(byCompName(mcSamples,['^(TTJets_Single|T_|TBar_).*']),150 if preprocessor else 10,12)
      #configureSplittingFromTime(dataSamples,100 if preprocessor else 5,12)
      #configureSplittingFromTime(byCompName(dataSamples,['Single']),50 if preprocessor else 5,12)
selectedComponents, _ = mergeExtensions(selectedComponents)




# Load modules
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_data

from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_EE
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_EE_data

from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_FR
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_data_FR

from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_EE_FR
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_EE_data_FR

#Muestras quitando skim
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_EE_nS
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import lepCollector_nS



from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

# in the cut string, keep only the main cuts to have it simpler
modules = []

# ----------------------------- For 2022 preEE ANALYSIS -------------------------- #
if yearstr == "2022":
  
  # ------------- Main analysis -------------- #
  if analysis == "main":
    if doData:
      print(" >> Using lepCollector for data")
      modules = lepCollector_data
    else:
      print(" >> Using lepCollector")
      modules = lepCollector
  
  # ------------- FR analysis -------------- #
  elif analysis == "fr":
    if doData:
      print(" >> Using lepCollector_FR for data")
      modules = lepCollector_data_FR
    else:
      print(" >> Using lepCollector_FR")
      modules = lepCollector_FR

  # ------------- Fiducial analysis -------------- #
  elif analysis == "fiducial":
    if doData:
      print(" ERROR! Fiducial analysis can't run on data :)")
      sys.exit()
    else:
      print(" >> Using lepCollector_FR")
      modules = lepCollector_nS
      
# ----------------------------- For 2022 postEE ANALYSIS -------------------------- #    
elif yearstr == "2022EE":
  # ------------- Main analysis -------------- #
  if analysis == "main":
    if doData:
      print(" >> Using lepCollector_EE for data")
      modules = lepCollector_EE_data
    else:
      print(" >> Using lepCollector_EE")
      modules = lepCollector_EE
      
  # ------------- FR analysis -------------- #
  elif analysis == "fr":
    if doData:
      print(" >> Using lepCollector_EE_FR for data")
      modules = lepCollector_EE_data_FR
    else:
      print(" >> Using lepCollector_EE_FR")
      modules = lepCollector_EE_FR
 
  # ------------- Fiducial analysis -------------- #
  elif analysis == "fiducial":
    if doData:
      print(" ERROR! Fiducial analysis can't run on data :)")
      sys.exit()
    else:
      print(" >> Using lepCollector_FR")
      #modules = lepCollector_fiducial
      modules = lepCollector_EE_nS     
        
if (doData):
  from CMGTools.TTHAnalysis.tools.nanoAOD.remove_overlap import OverlapRemover
  modules.extend( [lambda : OverlapRemover()] ) 
# print summary of components to process
if justSummary: 
    printSummary(selectedComponents)
    sys.exit(0)
    
cut = "1" 
compression = "ZLIB:3" #"LZ4:4" #"LZMA:9"
branchsel_out = os.environ['CMSSW_BASE']+"/src/CMGTools/TTHAnalysis/python/tools/nanoAOD/OutputSlim_wz.txt"
branchsel_in  = os.environ['CMSSW_BASE']+"/src/CMGTools/TTHAnalysis/python/tools/nanoAOD/InputSlim_wz.txt"


# -- Finally create the postprocessor
POSTPROCESSOR = PostProcessor(None, [], modules = modules,
        cut = cut, prefetch = False, longTermCache = False,
        branchsel = branchsel_in, outputbranchsel = None, compression = compression)
