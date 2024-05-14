import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TLorentzVector

import os
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

def conept_TTH(lep, pt):
    if (abs(lep.pdgId)!=11 and abs(lep.pdgId)!=13): 
        return pt 
    if (abs(lep.pdgId)==13 and lep.mediumId>0 and lep.mvaTTH > 0.64): 
        return pt
    if (abs(lep.pdgId)==11  and lep.mvaTTH > 0.90): 
        return pt
    else: return 0.90 * pt * (1+lep.jetRelIso)
    
_rootLeafType2rootBranchType = {'UChar_t': 'b', 
                                'Char_t' : 'B', 
                                'UInt_t' : 'i', 
                                'Int_t'  : 'I', 
                                'Float_t' : 'F', 
                                'Double_t':'D', 
                                'ULong64_t':'l', 
                                'Long64_t':'L', 
                                'Bool_t':'O',
                                'Short_t' : 'S'}


class addTnpTree(Module):
    def __init__(self, year, flavor):
        self.flavor = flavor
        if self.flavor == "Electron":
            #self.probeSel = lambda x : x.pt > 7 and abs(x.eta) < 2.5 and x.mvaFall17V2noIso_WPL
            self.probeSel = lambda x : x.pt > 5 and abs(x.eta) < 2.5 
            self.tagSel = lambda x : x.pt > 30 and x.cutBased > 3 and abs(x.eta) < 2.5
            self.kMaxMass = 140
            self.kMinMass = 60

        if self.flavor == "Muon":
            #self.probeSel = lambda x : x.pt > 5 and x.looseId and abs(x.eta) < 2.4
            self.probeSel = lambda x : x.pt > 5 and abs(x.eta) < 2.4
            self.tagSel = lambda x : x.pt > 30 and x.tightId and abs(x.eta) < 2.4
            self.kMaxMass = 140
            self.kMinMass = 60
        
        self.year = year
        self.i = 0


    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        self.out = wrappedOutputTree
        ## Dump electron / muon variables
        _brlist_in = inputTree.GetListOfBranches()
        branches_in = [( _brlist_in.At(i).GetName(), _brlist_in.At(i).FindLeaf(_brlist_in.At(i).GetName()).GetTypeName()) for i in range(_brlist_in.GetEntries())]

        _brlist_out = wrappedOutputTree._tree.GetListOfBranches()
        branches_out = set(
            [(_brlist_out.At(i).GetName(), _brlist_out.At(i).FindLeaf( _brlist_out.At(i).GetName()).GetTypeName()) for i in range(_brlist_out.GetEntries())])
        branches_out = [
            x for x in branches_out
            if wrappedOutputTree._tree.GetBranchStatus(x[0])
        ]
        branches=branches_in+branches_out
        
        self.lepBranches = []
        for brname, brtype in branches:
            if brname.startswith(self.flavor + "_"):
                if brname == "Electron_seediEtaOriX": 
                    brtype = "Int_t" 
                self.lepBranches.append( (brname.replace("%s_"%self.flavor,""), brtype) )

        for branch in self.lepBranches:
            self.out.branch('Tag_%s'%branch[0], _rootLeafType2rootBranchType[branch[1]])
            self.out.branch('Probe_%s'%branch[0], _rootLeafType2rootBranchType[branch[1]])

        ## Additional variables  added by hand 
        self.out.branch("Tag_isGenMatched", "I")
        self.out.branch('Tag_jetBTagDeepFlavB' ,'F')
        self.out.branch('Tag_smoothBDeepFlavB' ,'F')

        self.out.branch('Tag_conept' ,'F')
        self.out.branch('Tag_mvaTTHRun3' ,'F')
        self.out.branch("Probe_isGenMatched",     "I")
        self.out.branch('Probe_jetBTagDeepFlavB' ,'F')
        self.out.branch('Probe_smoothBDeepFlavB' ,'F')

        self.out.branch('Probe_conept' ,'F')
        self.out.branch('Probe_mvaTTHRun3' ,'F')

        self.out.branch("TnP_mass", "F")
        self.out.branch("TnP_ht",   "F")
        self.out.branch("TnP_met",  "F")
        self.out.branch("TnP_trigger", "I")
        self.out.branch("TnP_npairs",  "I")

        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def IsMatched(self, lep, trigObjCollection):
      dRmin = 0.1
      match = False
      for trigObj in trigObjCollection:
          trigObj.mass = 0 # :) 
          dR = lep.p4().DeltaR(trigObj.p4())
          if dR < dRmin: match = True
      return match

    
    def matchesPrompt(self, lep, genparts):
        return (lep.genPartFlav == 1 and genparts[lep.genPartIdx].statusFlags & 1) or  (lep.genPartFlav == 15 and genparts[lep.genPartIdx].statusFlags & (1 << 5))

    def analyze(self, event):
        # Get Jet and Ele collections
        jet      = Collection(event, 'Jet')
        lepton   = Collection(event, 'LepGood')
        trigObj  = Collection(event, 'TrigObj')

        #print ("*******************************************")
        #print ("************Analyze Event ********************")
        #print ("Flavor %s" %self.flavor)
        #print ("--Run number %d" %event.run)
        #print ("----Event number %d" %event.event)
        #print ("------Jet length %s" %event.nJet)
        #print ("------- number of Leptons %i" %len(lepton))
        #print ("---------  number of Muons %i" %event.nMuon)
        #print ("-------------  number of Electrons %i" %event.nElectron)

        #### Construct the trigger object collection containing electrons triggering a single iso electron trigger
        selTrigObj = []
        for tr in trigObj:
            if self.flavor == "Electron":
                if not abs(tr.id) == 11: continue
                if not (tr.filterBits & 2): continue
            if self.flavor == "Muon":
                if not abs(tr.id) == 13: continue
                if not ((tr.filterBits & 2) or (tr.filterBits & 8)): continue
            selTrigObj.append(tr)

        # Calculate event-per-event variables

        # Trigger requirement... IsoEle
        if self.flavor == "Electron":
            if   self.year == 2017:
                passTrigger = event.HLT_Ele27_WPTight_Gsf or event.HLT_Ele35_WPTight_Gsf
            elif self.year == 2016:
                passTrigger = event.HLT_Ele27_WPTight_Gsf
            elif self.year == 2015:
                passTrigger = event.HLT_Ele27_WPTight_Gsf
            elif self.year == 2018:
                passTrigger = event.HLT_Ele27_WPTight_Gsf or event.HLT_Ele35_WPTight_Gsf
            elif self.year == 2022:
                passTrigger = event.HLT_Ele32_WPTight_Gsf
        if self.flavor == "Muon":
            if   self.year == 2017:
                passTrigger = event.HLT_IsoMu24 or event.HLT_IsoMu27
            elif self.year == 2016:
                passTrigger = event.HLT_IsoMu24 or event.HLT_IsoMu27
            elif self.year == 2015:
                passTrigger = event.HLT_IsoMu24 or event.HLT_IsoMu27
            elif self.year == 2018:
                passTrigger = event.HLT_IsoMu24 or event.HLT_IsoMu27
            elif self.year == 2022:
                passTrigger = event.HLT_IsoMu24

        # Compute HT and MET
        ht = 0; met = event.METFixEE2017_pt if self.year == 17 else event.MET_pt
        jetId = 1 if self.year == 2016 else 2 
        for j in jet: 
            ht += j.pt if j.pt > 30 and abs(j.eta)  < 2.4 and j.jetId&(1<<jetId) else 0

        #isdata = 0 if hasattr(event, 'Electron_genPartFlav') else 1
        try:
            getattr(event, 'Electron_genPartFlav') 
            isdata=0
        except:
            isdata=1
        if not isdata: genparts = Collection(event, 'GenPart')

        #### Selection of tag and probe electrons
        # Tag: pT, eta, tightId, iso
        # Probe: pT, eta
        tags = []; probes = []; pair = []
        index = 0
        #print("*** Run number %d" %event.run)
        #print("*** number of Leptons %i" %len(lepton))
        #print("*** number of Muons %i" %event.nMuon)
        #for checklep in lepton:            
            #print("****** check lepton pt %f" %checklep.pt)
            #print("****** check lepton eta %f" %checklep.eta)
        
        for tag in lepton:
            if not self.tagSel(tag): continue
            if not self.IsMatched(tag, selTrigObj): continue
            probes = [] 
            for probe in lepton: 
                if not self.probeSel(probe): continue
                mass = (probe.p4()+tag.p4()).M()
                if mass > self.kMaxMass or mass < self.kMinMass: continue    
                if probe.charge*tag.charge > 0: continue
                #print("*** tag pt %i" %tag.pt)
                #print("*** probe pt %i" %probe.pt)
                probes.append(probe)
            if len(probes) == 1: pair.append( (tag, probes[0]) )

        #print("---------------number of pair %d" % len(pair))
        # Check that we have at least one pair... calculate the mass of the pair
        if len(pair) == 0: return False # events with 1 or 2 pairs!


        self.i += 1

        # Set variables for tag, probe and event
        for thisPair in pair:
            tag, probe = thisPair
            mass = (probe.p4()+tag.p4()).M()

            for branch in self.lepBranches:
                branchName = branch[0]
                if branchName != "seediEtaOriX":
                    self.out.fillBranch("Tag_%s"%branchName, getattr(tag,branchName))
                    self.out.fillBranch("Probe_%s"%branchName, getattr(probe,branchName))
                else:
                    self.out.fillBranch("Tag_%s"%branchName, int(getattr(tag,branchName)))
                    self.out.fillBranch("Probe_%s"%branchName, int(getattr(probe,branchName)))
                
            #print ("tag jetidx %s" %tag.jetIdx)
            tagMatch = 1 if isdata else self.matchesPrompt(tag,genparts)
            self.out.fillBranch("Tag_isGenMatched", tagMatch)
            self.out.fillBranch('Tag_jetBTagDeepFlavB', 0 if tag.jetIdx < 0 else jet[tag.jetIdx].btagDeepFlavB)

            self.out.fillBranch('Tag_conept',       conept_TTH(tag))
            self.out.fillBranch('Tag_conept_corrected', conept_TTH(tag, tag.correctedpt))
            self.out.fillBranch('Tag_mvaTTHRun3',   tag.mvaTTH_run3)

            #print ("probe jetidx %d" %probe.jetIdx)
            probeMatch = 1 if isdata else  self.matchesPrompt(probe, genparts)
            self.out.fillBranch("Probe_isGenMatched", probeMatch)
            self.out.fillBranch('Probe_jetBTagDeepFlavB', 0 if probe.jetIdx < 0 else jet[probe.jetIdx].btagDeepFlavB) 
            self.out.fillBranch('Probe_conept',       conept_TTH(probe, probe.pt))
            self.out.fillBranch('Probe_conept_corrected',       conept_TTH(probe, probe.correctedpt))
            self.out.fillBranch('Probe_mvaTTHRun3',   probe.mvaTTH_run3)

            # TnP variables
            self.out.fillBranch("TnP_mass",     mass)
            self.out.fillBranch("TnP_trigger",  passTrigger) 
            self.out.fillBranch("TnP_npairs",   len(pair))
            self.out.fillBranch("TnP_met",      met)
            self.out.fillBranch("TnP_ht",       ht)
            self.out.fill()
        
        #print ("************ End Event ********************")
        #print ("*******************************************")
                  
        return False

