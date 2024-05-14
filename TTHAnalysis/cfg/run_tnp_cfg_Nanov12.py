import re, os, sys
from copy import deepcopy
from CMGTools.RootTools.samples.configTools import printSummary, mergeExtensions, doTestN, configureSplittingFromTime, cropToLumi
from CMGTools.RootTools.samples.autoAAAconfig import autoAAA
from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator
from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption

#kreator = ComponentCreator()
def byCompName(components, regexps):
    return [ c for c in components if any(re.match(r, c.name) for r in regexps) ]

year              = getHeppyOption("year", "2022")
analysis          = getHeppyOption("analysis", "main")
selectComponents  = getHeppyOption('selectComponents')
flavor            = getHeppyOption("flavor")
analysis          = getHeppyOption("analysis")
quiet             = not(getHeppyOption("verboseAAA", False))
justSummary       = getHeppyOption("justSummary")
applyTriggersInMC = getHeppyOption('applyTriggersInMC')
### Prepare samples for submission 
doData = (selectComponents == "DATA")

#samples NanoAODv11
if year == "2022":
    if analysis == "nominal":
        from CMGTools.RootTools.samples.samples_13p6TeV_2022_TnP_NanoAODv12 import mcSamples_toImport as mcSamples_
    elif analysis == "alternative":
        print(" Importing alternative sample")
        from CMGTools.RootTools.samples.samples_13p6TeV_2022_TnP_NanoAODv12_ALT  import mcSamples_toImport  as mcSamples_
    else:
        print( "Wrong analysis. Choose between nominal and alternative. ")
        sys.exit(0)
    from CMGTools.RootTools.samples.samples_13p6TeV_2022_TnP_NanoAODv12_DATA  import dataSamples_toImport  as allData
elif year == "2022EE":
    if analysis == "nominal":
        from CMGTools.RootTools.samples.samples_13p6TeV_2022EE_TnP_NanoAODv12 import mcSamples_toImport as mcSamples_
    elif analysis == "alternative":
        print(" Importing alternative sample")
        from CMGTools.RootTools.samples.samples_13p6TeV_2022EE_TnP_NanoAODv12_ALT  import mcSamples_toImport  as mcSamples_
    else:
        print( "Wrong analysis. Choose between nominal and alternative. ")
        sys.exit(0)
    from CMGTools.RootTools.samples.samples_13p6TeV_2022EE_TnP_NanoAODv12_DATA  import dataSamples_toImport  as allData
else:
    print("%%%%%%%% Wrong year sampDatasetsAndVetosles %%%%%%%%%%%%%%")

autoAAA(mcSamples_ + allData, 
        quiet         = quiet, 
        redirectorAAA = "xrootd-cms.infn.it",
        node          = 'T2_ES_IFCA') 

mcSamples_, _ = mergeExtensions(mcSamples_) ### autoAAA must be created before call mergeExtensions

if year == "2022EE" or year == "2022": 
  yearstr = year
  year = 2022

if year == 2022:
    from CMGTools.TTHAnalysis.tools.nanoAOD.triggers_13p6TeV_DATA2022  import triggerGroups_dict
else:
    print("%%%%%%%% Wrong year dataset%%%%%%%%%%%")



DatasetsAndTriggers = {}
DatasetsAndVetos    = {}
#triggers
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

# -- We do not use MET samples
DatasetsAndVetos["MET"]        = []

#old
#if flavor == "Muon":
#    DatasetsAndTriggers.append( ("Muon", triggers["1mu_iso"]) )
#elif flavor == "Electron":
#    DatasetsAndTriggers.append( ("EGamma", triggers["1e_iso"]) )

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
    ##processes
    mcSamples = byCompName(mcSamples_, ["DYJetsToLL_M_50"])
        
    
    # make MC
    mcTriggers = sum((trigs for (pd,trigs) in DatasetsAndTriggers.items() if trigs), [])
    if applyTriggersInMC :
        for comp in mcSamples:
            comp.triggers = mcTriggers

    selectedComponents = mcSamples 

# -- Create the submitter -- #
autoAAA(selectedComponents, 
        quiet=quiet, 
        redirectorAAA="xrootd-cms.infn.it")


# Lep MERGE
from PhysicsTools.NanoAODTools.postprocessing.modules.common.collectionMerger import collectionMerger


if yearstr == "2022EE":
    etaLeak = 1.56
    remove_ecalDeadZones = lambda l: not( (l.eta+l.deltaEtaSC) > etaLeak and int(l.seediEtaOriX) < 45 and l.seediPhiOriY > 72)
    lepMerge = collectionMerger(
        input = ["Electron", "Muon"], 
        output = "LepGood",
        selector = dict(Muon = lambda l: 1, Electron = lambda l: 1 )
    )
elif yearstr == "2022":
    lepMerge = collectionMerger(
        input = ["Electron", "Muon"], 
        output = "LepGood",
        selector = dict(Muon = lambda l: 1, Electron = lambda l: 1 )
    
    )

from CMGTools.TTHAnalysis.tools.nanoAOD.addTnpTree import addTnpTree
import CMGTools.TTHAnalysis.tools.nanoAOD.mvaTTH_vars_run3 as mvatth_cfg
from CMGTools.TTHAnalysis.tools.nanoAOD.lepJetBTagAdder import lepJetBTagAdder
from CMGTools.TTHAnalysis.tools.nanoAOD.lepMVAWZ_run3 import lepMVAWZ_run3


weightspath_2022EE = os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/data/WZRun3/")
lepmva = lambda : lepMVAWZ_run3(
        weightspath_2022EE, 
        elxmlpath = "EGM/Electron-mvaTTH.2022EE.weights_mvaISO.xml", 
        muxmlpath = "MUO/Muon-mvaTTH.2022EE.weights.xml", 
        suffix = "_run3",
        inputVars = {"muons":  mvatth_cfg.muon_df("2022"), "electrons" : mvatth_cfg.electron_df_wIso("2022")}
)
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor


# in the cut string, keep only the main cuts to have it simpler
from CMGTools.TTHAnalysis.tools.nanoAOD.puWeightProducer_run3 import puAutoWeight_2022PostEE, puAutoWeight_2022

#modules = [ autoPuWeight, addTnpTree(year,flavor), LepMVAFriend(era, False)] 
#modules = [ autoPuWeight, lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), LepMVAFriend(flavor), addTnpTree(year,flavor)] 
#modules = [lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), addTnpTree(year,flavor)] 
#modules = [lepMerge, addTnpTree(year,flavor)] 
#modules = [lepMerge]

from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import  lepEnergyCorrection_2022, lepEnergyCorrection_2022_data, lepEnergyCorrection_2022EE, lepEnergyCorrection_2022EE_data
if not doData:
    if yearstr == "2022EE":
        print(" Using modules for 2022EE")
        modules = [lepEnergyCorrection_2022EE[0], lepMerge, puAutoWeight_2022PostEE, lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), lepmva, addTnpTree(year,flavor)] 
    elif yearstr == "2022":
        print(" Using modules for 2022")
        modules = [lepEnergyCorrection_2022[0], lepMerge, puAutoWeight_2022, lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), lepmva, addTnpTree(year,flavor)] 
else:
    from CMGTools.TTHAnalysis.tools.nanoAOD.remove_overlap import OverlapRemover
    remove_overlap = lambda : OverlapRemover() 

    if yearstr == "2022EE":
        print("Using modules for %s (data)"%yearstr)
        modules = [lepEnergyCorrection_2022EE_data[0], remove_overlap, lepMerge, lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), lepmva, addTnpTree(year,flavor)] 
    elif yearstr == "2022":
        print("Using modules for %s (data)"%yearstr)
        modules = [lepEnergyCorrection_2022_data[0], remove_overlap, lepMerge, lepJetBTagAdder("btagDeepFlavB", "jetBTagDeepFlav"), lepmva, addTnpTree(year,flavor)] 

cut = 'n%s > 1'%flavor
#cut = None

branchsel_out = os.environ['CMSSW_BASE']+"/src/CMGTools/TTHAnalysis/python/tools/nanoAOD/OutputSlim_wz.txt"
branchsel_in  = os.environ['CMSSW_BASE']+"/src/CMGTools/TTHAnalysis/python/tools/nanoAOD/InputSlim_wz.txt"
compression = "ZLIB:3" #"LZ4:4" #"LZMA:9"

# print summary of components to process
if justSummary: 
    printSummary(selectedComponents)
    sys.exit(0)



POSTPROCESSOR = PostProcessor(None, [], modules = modules,
        cut = cut, prefetch = True, longTermCache = True,
        branchsel = branchsel_in, outputbranchsel = branchsel_out, compression = compression)


