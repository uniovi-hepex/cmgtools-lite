from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True


class puWeightProducer(Module):
    def __init__(self,
                 myfile,
                 targetfile,
                 myhist="pileup",
                 targethist="pileup",
                 name="puWeight_fix",
                 norm=True,
                 verbose=False,
                 nvtx_var="Pileup_nTrueInt",
                 doSysVar=True
     ):
        self.targeth = self.loadHisto(targetfile, targethist)
        if isinstance(doSysVar, list):
            self.targeth_plus = self.loadHisto(doSysVar[0], targethist)
            self.targeth_minus = self.loadHisto(doSysVar[1], targethist)
        self.fixLargeWeights = True  # temporary fix
        if myfile != "auto":
            self.autoPU = False
            self.myh = self.loadHisto(myfile, myhist)
        else:
            self.fixLargeWeights = False  # AR: it seems to crash with it, to be deugged
            self.autoPU = True
            ROOT.gROOT.cd()
            self.myh = self.targeth.Clone("autoPU")
            self.myh.Reset()
        self.name = name
        self.norm = norm
        self.verbose = verbose
        self.nvtxVar = nvtx_var
        self.doSysVar = doSysVar

        # Try to load module via python dictionaries
        try:
            ROOT.gSystem.Load("libPhysicsToolsNanoAODTools")
            dummy = ROOT.WeightCalculatorFromHistogram
        # Load it via ROOT ACLIC. NB: this creates the object file in the
        # CMSSW directory, causing problems if many jobs are working from the
        # same CMSSW directory
        except Exception as e:
            print(("Could not load module via python, trying via ROOT" + str(e)))
            if "/WeightCalculatorFromHistogram_cc.so" not in ROOT.gSystem.GetLibraries(
            ):
                print("Load C++ Worker")
                ROOT.gROOT.ProcessLine(
                    ".L %s/src/PhysicsTools/NanoAODTools/src/WeightCalculatorFromHistogram.cc++"
                    % os.environ['CMSSW_BASE'])
            dummy = ROOT.WeightCalculatorFromHistogram

    def loadHisto(self, filename, hname):
        tf = ROOT.TFile.Open(filename)
        hist = tf.Get(hname)
        hist.SetDirectory(0)
        tf.Close()
        return hist

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        if self.autoPU:
            self.myh.Reset()
            print("Computing PU profile for this file")
            ROOT.gROOT.cd()
            inputFile.Get("Events").Project("autoPU",
                                            self.nvtxVar)  # doitfrom inputFile
            if outputFile:
                outputFile.cd()
                self.myh.Write()
        self._worker = ROOT.WeightCalculatorFromHistogram(
            self.myh, self.targeth, self.norm, self.fixLargeWeights,
            self.verbose)
        self.out = wrappedOutputTree
        self.out.branch(self.name, "F")
        if self.doSysVar:
            self._worker_plus = ROOT.WeightCalculatorFromHistogram(
                self.myh, self.targeth_plus, self.norm, self.fixLargeWeights,
                self.verbose)
            self._worker_minus = ROOT.WeightCalculatorFromHistogram(
                self.myh, self.targeth_minus, self.norm, self.fixLargeWeights,
                self.verbose)
            self.out.branch(self.name + "_up", "F")
            self.out.branch(self.name + "_dn", "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if hasattr(event, self.nvtxVar):
            nvtx = int(getattr(event, self.nvtxVar))
            weight = self._worker.getWeight(
                nvtx) if nvtx < self.myh.GetNbinsX() else 1
            if self.doSysVar:
                weight_plus = self._worker_plus.getWeight(
                    nvtx) if nvtx < self.myh.GetNbinsX() else 1
                weight_minus = self._worker_minus.getWeight(
                    nvtx) if nvtx < self.myh.GetNbinsX() else 1
        else:
            weight = 1
        self.out.fillBranch(self.name, weight)
        if self.doSysVar:
            self.out.fillBranch(self.name + "_up", weight_plus)
            self.out.fillBranch(self.name + "_dn", weight_minus)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

# 2022EE
pufile_data2022 = "%s/src/CMGTools/TTHAnalysis/data/WZRun3/PU/2022/pileupHistogram-Cert_Collisions2022_355100_357900_eraBCD_GoldenJson-13p6TeV-69200ub-99bins.root" % os.environ['CMSSW_BASE']
sysVars = [
    pufile_data2022.replace("69200ub", "72400ub"),
    pufile_data2022.replace("69200ub", "66000ub")
]

puAutoWeight_2022 = lambda: puWeightProducer(
    "auto", 
    pufile_data2022, 
    "pu_mc", 
    "pileup", 
    doSysVar = sysVars,
    verbose=False
)

# 2022EE
pufile_data2022PostEE = "%s/src/CMGTools/TTHAnalysis/data/WZRun3/PU/2022EE/pileupHistogram-Cert_Collisions2022_359022_362760_eraEFG_GoldenJson-13p6TeV-69200ub-99bins.root" % os.environ['CMSSW_BASE']
sysVars = [
    pufile_data2022PostEE.replace("69200ub", "72400ub"),
    pufile_data2022PostEE.replace("69200ub", "66000ub")
]

puAutoWeight_2022PostEE = lambda: puWeightProducer(
    "auto", 
    pufile_data2022PostEE, 
    "pu_mc", 
    "pileup", 
    doSysVar = sysVars,
    verbose=False
)
