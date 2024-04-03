from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import declareOutput, writeOutput
from CMGTools.TTHAnalysis.tools.nanoAOD.leptonJetRecleanerWZSM import passMllTLVeto, passTripleMllVeto
import itertools
import ROOT, copy, os
import array, math

""" Define some useful functions """
def deltaPhi( p1, p2):
    '''Computes delta phi, handling periodic limit conditions.'''
    res = p1 - p2
    while res > math.pi:
        res -= 2*math.pi
    while res < -math.pi:
        res += 2*math.pi
    return res


def deltaR2( e1, p1, e2=None, p2=None):
    """Take either 4 arguments (eta,phi, eta,phi) or two objects that have 'eta', 'phi' attributes)"""
    if (e2 == None and p2 == None):
        return deltaR2(e1.eta,e1.phi, p1.eta, p1.phi)
    de = e1 - e2
    dp = deltaPhi(p1, p2)
    return de*de + dp*dp


def deltaR( *args ):
    return math.sqrt( deltaR2(*args) )

class leptonMatcher(Module):
    def __init__(self, inputlabel):
        self.isData = False
        self.inputlabel = inputlabel
        self.listBranches()        
        return

    def analyze(self, event):
        self.isData = not(hasattr(event, "genWeight"))
        self.resetMemory()
        self.collectObjects(event)
        self.analyzeTopology()
        
        writeOutput(self, self.ret)
        return True

    def analyzeTopology(self):
        self.getGenMatch()

    def collectObjects(self, event):
        ## light leptons
        self.lepSelFO = [l for l  in Collection(event, "LepGood", "nLepGood")  ]
        if not self.isData:
            self.gendressleps = [l for l  in Collection(event, "GenDressedLepton", "nGenDressedLepton")  ]
            self.genparts = [p for p  in Collection(event, "GenPart", "nGenPart")  ]        

    def listBranches(self):
        self.branches = [
            ("nLepGood_forMemory", "I"),
            ("LepGood_mcUCSX_v2", "I", 8, "nLepGood_forMemory"), 
            ("LepGood_motherId", "I", 8, "nLepGood_forMemory"), 
            ("LepGood_motherIdx","I", 8, "nLepGood_forMemory"), 
            ("LepGood_grandmotherId","I", 8, "nLepGood_forMemory"), 
            ("LepGood_grandmotherIdx","I",8, "nLepGood_forMemory")
        ]
        return self.branches
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        declareOutput(self, wrappedOutputTree, self.branches)
        return
    
    def getGenMatch(self):
      #We need to rebuild a la UCSX to match 2016 analysis like inHeppy/python/analyzers/objects/LeptonAnalyzer.py
      if not self.isData:
          for i in range(len(self.lepSelFO)):

              self.lepSelFO[i].isMatched      = False
              self.lepSelFO[i].genpt          = 0
              self.lepSelFO[i].geneta         = 0
              self.lepSelFO[i].genphi         = 0
              self.lepSelFO[i].genmass        = 0
              self.lepSelFO[i].isMatchingWZ   = False

              if self.lepSelFO[i].genPartIdx < 0 or self.lepSelFO[i].genPartIdx > len(self.genparts)-1: 
                  self.lepSelFO[i].isMatched      = False
                  self.lepSelFO[i].genpt          = 0
                  self.lepSelFO[i].geneta         = 0
                  self.lepSelFO[i].genphi         = 0
                  self.lepSelFO[i].genmass        = 0
                  self.lepSelFO[i].isMatchingWZ   = False
                  self.lepSelFO[i].mcUCSX         = -1

              else:
                  match  = self.genparts[self.lepSelFO[i].genPartIdx]
                  isPrompt = (match.statusFlags & 1) or (match.statusFlags & 32) or (match.statusFlags & 128)
                  isFlip   = (match.pdgId*self.lepSelFO[i].pdgId > 0)
                  self.lepSelFO[i].isMatched      = True
                  self.lepSelFO[i].genpt          = match.pt
                  self.lepSelFO[i].geneta         = match.eta
                  self.lepSelFO[i].genphi         = match.phi
                  self.lepSelFO[i].genmass        = match.mass

                  #Find heaviest mother
                  mother = match
                  idx = self.lepSelFO[i].genPartIdx
                  sumTau = 0
                  nParents = 0
                  while nParents < 1000:
                      if self.ret["LepGood_grandmotherId"][i] == -999 and self.ret["LepGood_motherId"][i] != -999: 
                          self.ret["LepGood_grandmotherId"][i]  = mother.pdgId
                          self.ret["LepGood_grandmotherIdx"][i] = idx

                      if self.ret["LepGood_motherId"][i] == -999: 
                          self.ret["LepGood_motherId"][i] = mother.pdgId
                          self.ret["LepGood_motherIdx"][i] = idx


                      if mother.pdgId == 22:
                          self.lepSelFO[i].mcUCSX = 4 + sumTau
                          break
                      if mother.pdgId == 24 or mother.pdgId == -24 or mother.pdgId == 23 or mother.pdgId == 25:
                          self.lepSelFO[i].mcUCSX =  sumTau if isFlip else  1 + sumTau                       
                          if not (mother.pdgId ==25): self.lepSelFO[i].isMatchingWZ = True
                          break
                      if abs(mother.pdgId) == 5 or abs(mother.pdgId) == 4:
                          self.lepSelFO[i].mcUCSX = 3  + sumTau
                          break
                      if abs(mother.pdgId) == 1 or abs(mother.pdgId) == 2 or abs(mother.pdgId) == 3:
                          self.lepSelFO[i].mcUCSX = 2 + sumTau
                          break
                      if abs(mother.pdgId) == 15:
                          sumTau = 10
                          mother = self.genparts[mother.genPartIdxMother]
                          idx = mother.genPartIdxMother
                      else:            
                          if not(mother.genPartIdxMother) >= 0:
                              self.lepSelFO[i].mcUCSX = 5 + sumTau
                              break
                          else:
                              mother = self.genparts[mother.genPartIdxMother]
                              idx = mother.genPartIdxMother
                      self.lepSelFO[i].mcUCSX = sumTau
                      if self.ret["LepGood_grandmotherId"][i] == -999 and self.ret["LepGood_motherId"][i] != -999: 
                          self.ret["LepGood_grandmotherId"][i]  = mother.pdgId
                          self.ret["LepGood_grandmotherIdx"][i] = idx

                      if self.ret["LepGood_motherId"][i] == -999: 
                          self.ret["LepGood_motherId"][i] = mother.pdgId
                          self.ret["LepGood_motherIdx"][i] = idx


                      nParents += 1
              self.ret["LepGood_mcUCSX_v2"][i] = self.lepSelFO[i].mcUCSX

    def resetMemory(self):
        self.ret = {}
        self.ret["nLepGood_forMemory"] = 0
        self.ret["LepGood_mcUCSX_v2"] = [0]*20
        self.ret["LepGood_motherId"]  = [-999]*20
        self.ret["LepGood_grandmotherId"]  = [-999]*20
        self.ret["LepGood_motherIdx"]  = [-999]*20
        self.ret["LepGood_grandmotherIdx"]  = [-999]*20
        return
    
if __name__ == '__main__':
    """ Debug the module """
    from sys import argv
    from copy import deepcopy
    from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import eventLoop
    from PhysicsTools.NanoAODTools.postprocessing.framework.output import FriendOutput, FullOutput
    from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import InputTree
    
    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc_unskim_march2024/2022EE/"
    process = "WZto3LNu_pow_part4"
#    process = "TTTo2L2Nu_part17"
    
    friends = [
      "leptonJetRecleaning_Elewp090",
      "leptonBuilder_Elewp090"
    ]
    nentries = int(argv[1])
    ### Open the main file
    file_ = ROOT.TFile( os.path.join(mainpath, process+".root") )
    tree = file_.Get("Events")
    for friend in friends:
      print(os.path.join(mainpath, friend, process+"_Friend.root"))
      friendfile = ROOT.TFile( os.path.join(mainpath, friend, process+"_Friend.root") ) 
      tree.AddFriend("Friends", friendfile)
    
    ### Replicate the eventLoop
    tree = InputTree(tree)
    outFile = ROOT.TFile.Open("test_%s.root"%process, "RECREATE")
    outTree = FriendOutput(file_, tree, outFile)
    
    module_test =  leptonMatcher(
        "Mini"
    )
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()


