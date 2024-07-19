from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import declareOutput, writeOutput
from CMGTools.TTHAnalysis.tools.nanoAOD.leptonJetRecleanerWZSM import passMllTLVeto, passTripleMllVeto
from ROOT import TFile,TH1F
import ROOT, copy, os
import array, math

## OSpair
class OSpair:
    def __init__(self, l1, l2, genparts):
        self.l1   = l1
        self.l2   = l2
        self.genparts = genparts
        self.load()
        

        
    def debug(self):
        add = "SF" if self.isSF else "OF"
        return "OSpair (%s, %3.1f) made up of (%3.1f, %d) and (%3.1f, %d)" % (add, self.mll, self.l1.pt, self.l1.pdgId, self.l2.pt, self.l2.pdgId)

    def load(self):

        self.isSF = False
        self.isZ = False
        self.wTau = False

        if     self.l1.pdgId  ==          -self.l2.pdgId       : self.isSF = True
        if abs(self.l1.pdgId) == 15 or abs(self.l2.pdgId) == 15: self.wTau = True

        if   self.isSF                                           : self.target = 91.1876
        else                                                     : self.target = 50
  
        self.mll  = (self.l1.p4()               + self.l2.p4()              ).M()
        self.diff = abs(self.target - self.mll)
        if self.l1.motherpdgId == 23 and self.l2.motherpdgId == 23 : self.diff = 0
       
    def test(self, leps):
        if len(leps) > 3: return False
        ll = [self.l1, self.l2, self.l3]
        return all([l in ll for l in leps])
            
class lepgenVarsWZSM_nondressed_withtaus(Module):

    def __init__(self, inputlabel, verbosity = 0):

        self.mt2maker = None
        self.verbosity = verbosity
        self.inputlabel = '_' + inputlabel

        self.systsJEC = {0: ""}
        self.listBranches()
        return

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        declareOutput(self, wrappedOutputTree, self.branches)
        return
    
    def analyze(self, event):
        #print(f" >> Event {event.event}")
        self.resetMemory()
        self.collectObjects(event)
        self.analyzeTopology()
        self.writeLepSel()
        
        writeOutput(self, self.ret)
        return True
        
    def analyzeTopology(self):

        #self.passCleverPtCut()
        #if not self.passPtAndMll(): return
        if len(self.genleps)>=3: self.ret["is_3l_gen"] = 1
        if len(self.genleps)>=4: self.ret["is_4l_gen"] = 1
        if len(self.genleps)>=5: self.ret["is_5l_gen"] = 1

        self.collectOSpairs(3, False)
        self.makeMass(3)
        self.makeMt2(3)
        self.findBestOSpair(3)
        self.makeMassMET(3)

    def filterGenPart(self, p):
       #print "Analyze GenPart:", p.pdgId, p.status
       if not(abs(p.pdgId)==11 or abs(p.pdgId)==13 or abs(p.pdgId)==15): return False
       #print "Pass pdgId"
       if not(p.status==23 or p.status==1 or (abs(p.pdgId) == 15 and p.status == 2)): return False
       #print "Pass status"
       if p.genPartIdxMother < 0: return False
       #print "Has mother"
       #Now go back and try to get ancesters
       motherIdx = p.genPartIdxMother
       while motherIdx > 0:
           newpart = self.genparts[motherIdx]
           if  abs(newpart.pdgId) == 23 or abs(newpart.pdgId) == 24:
               setattr(p, "motherpdgId", self.genparts[p.genPartIdxMother].pdgId)
               break
           elif newpart.pdgId == p.pdgId:
               motherIdx = newpart.genPartIdxMother
           else: #Decay from tau, jet or photon
               return False
       setattr(p, "motherIDX", motherIdx)
       #print "Has mother index: ", motherIdx
       if not( abs(self.genparts[p.genPartIdxMother].pdgId) == 23 or abs(self.genparts[p.genPartIdxMother].pdgId) == 24): return False
       #print "Mother is W/Z"
       return True
    
    def collectObjects(self, event):

        ## gen leptons
        self.genparts    = [l             for l  in Collection(event, "GenPart", "nGenPart")  ]
        self.genleps = list(filter(lambda x: self.filterGenPart(x), self.genparts))
        #Lightlepton cleanup
        self.genleps.sort(key = lambda x: x.pt, reverse=True)
        finalleps = []
        for lep in self.genleps:
            test = min([10] + [deltaR(lep.eta, lep.phi, l.eta, l.phi)  for l in finalleps])
            if test < 0.02: continue
            else: finalleps.append(lep)
        self.genleps = finalleps
        self.metgen        = {}
        self.metgen[0]     = event.GenMET_pt if not False else event.MET_pt

        self.metgenphi     = {}
        self.metgenphi[0]  = event.GenMET_phi if not False else event.MET_phi
        
        self.OS = []
            
    def collectOSpairs(self, max, useBuffer = False):

        self.OS = []
        for i in range(min(max, len(self.genleps))):
            for j in range(i+1,min(max, len(self.genleps))):
                if useBuffer and abs(self.genleps[i].pdgId) != abs(self.genleps[j].pdgId): continue # if buffer then SF
                if self.genleps[i].pdgId * self.genleps[j].pdgId < 0: 
                    self.OS.append(OSpair(self.genleps[i], self.genleps[j], self.genparts))

        ## loop over all pairs, only keep the best OSSF ones, and make sure that they do not overlap
        if useBuffer:
            self.OS.sort(key=lambda x: x.diff)
            buffer = self.OS
            self.OS = []
            used = []
            for os in buffer:
                if not os.l1 in used and not os.l2 in used:
                    self.OS.append(os)
                    used.append(os.l1); used.append(os.l2)

        self.ret["nOSSF_" + str(max) + "l_gen"] = self.countOSSF(max)
        self.ret["nOSTF_" + str(max) + "l_gen"] = self.countOSTF(max)
        self.ret["nOSLF_" + str(max) + "l_gen"] = self.countOSLF(max)

    def countOSLF(self, max):
        return sum(1 if not os.wTau else 0 for os in self.OS)

    def countOSSF(self, max):
        return sum(1 if os.isSF else 0 for os in self.OS)

    def countOSTF(self, max):
        return sum(1 if os.wTau else 0 for os in self.OS)

    def makeMass(self, max):
       
        if len(self.genleps) < 3: return 
        sum = self.genleps[0].p4()
        for i in range(1,min(max,len(self.genleps))):
            sum += self.genleps[i].p4(self.genleps[i].pt)
        self.ret["m" + str(max) + "L_gen"] = sum.M()

        minMllAFAS = 10000
        minMllSFOS = 10000

        for i in range(len(self.genleps)):
          for j in range(i,len(self.genleps)):
            if i==j: continue
            testMass = (self.genleps[i].p4() + self.genleps[j].p4()).M()
            #if testMass <  5: print testMass, i, j
            if testMass < minMllAFAS:
              minMllAFAS = testMass
            if testMass < minMllSFOS and (self.genleps[i].pdgId + self.genleps[j].pdgId) == 0:
              minMllSFOS = testMass
        self.ret["minmllAFAS_gen"] = minMllAFAS
        self.ret["minmllSFOS_gen"] = minMllSFOS
      
    def makeMassMET(self, max):
           
        if len(self.genleps) < 3: return 
        sumlep = self.genleps[0].p4()
        metp4 = ROOT.TLorentzVector()
        for i in range(1,min(max,len(self.genleps))):
            sumlep += self.genleps[i].p4(self.genleps[i].pt) 
        for var in self.systsJEC:
            metp4.SetPtEtaPhiM(self.metgen[var],0,self.metgenphi[var],0)
            sumtot = sumlep + metp4
            self.ret["m" + str(max) + "Lmet" + self.systsJEC[var] + "_gen"] = sumtot.M()

    def makeMt2(self, max):
        ## building two sets of MT2
        ## mT2L = two light flavor leptons from the OS pair (category C, D)
        ## mT2T = hardest light lepton and one tau (category E, F)

        if not self.mt2maker: return False
        #if self.mt2maker: print "I have mT2maker\n"
        anyPairs = []
        for i in range(min(max, len(self.genleps))):
            for j in range(i+1,min(max, len(self.genleps))):
                if abs(self.genleps[i].pdgId) == 15 or abs(self.genleps[j].pdgId) == 15:
                    anyPairs.append(OSpair(self.genleps[i], self.genleps[j], self.genparts))

        mt2t = []
        mt2l = []

        mt2t.sort(reverse=True) # we want the hardest leptons here! 
        mt2l.sort(reverse=True) # we want the hardest leptons here! 
        #if len(mt2l)>0: print "I have os pair for mt2l\n"
        for var in self.systsJEC:
            if len(mt2t)>0: 
                self.ret["mT2T_" + str(max) + "l" + self.systsJEC[var] + "_gen"] = self.mt2(mt2t[0][1].l1, mt2t[0][1].l2, var)
            if len(mt2l)>0: 
                self.ret["mT2L_" + str(max) + "l" + self.systsJEC[var] + "_gen"] = self.mt2(mt2l[0][1].l1, mt2l[0][1].l2, var)
        #if len(mt2l)>0: print self.ret["mT2L_" + str(max) + "l"]

    def mt(self, pt1, pt2, phi1, phi2):
        return math.sqrt(2*pt1*pt2*(1-math.cos(phi1-phi2)))

    def mt2(self, obj1, obj2, var, useGenMet = False):
            
        vector_met     = array.array('d', [0, self.metgen[var]*math.cos(self.metgenphi[var]), self.metgen[var]*math.sin(self.metgenphi[var])])
        vector_obj1    = array.array('d', [obj1.mass, obj1.p4(obj1.pt).Px(), obj1.p4(obj1.pt).Py()])
        vector_obj2    = array.array('d', [obj2.mass, obj2.p4(obj2.pt).Px(), obj2.p4(obj2.pt).Py()])

        if useGenMet:
            vector_met = array.array('d', [0, self.metgen[var]*math.cos(self.metgenphi[var]), self.metgen[var]*math.sin(self.metgenphi[var])])

        self.mt2maker.set_momenta(vector_obj1, vector_obj2, vector_met)
        self.mt2maker.set_mn(0)

        return self.mt2maker.get_mt2()
    

    def mtW(self, lep, var, useGenMet = False):
        if useGenMet: return self.mt(lep.pt, self.metgen[var], lep.phi, self.metgenphi[var])
        return self.mt(lep.pt, self.metgen[var], lep.phi, self.metgenphi[var])

    def findBestOSpair(self, max):

        self.bestOSPair = None

        all = []
        #all2 = []
        for os in self.OS:
            all.append((0 if os.isZ else 1, 0 if os.isSF else 1, os.diff, os)) # priority to SF, then difference to target
            #all2.append((0 if os.isZ else 1, 0 if os.isSF else 1, os.diff, os)) # priority to SF, then difference to target

        if all:
            #all.sort( key = lambda el: el[0] )
            all.sort() 
            #all2.sort()
            #print("        ", all)
            #print("        ", "-")
            #print("        ", all2)
            self.bestOSPair = all[0][3]
            self.ret["mll_" + str(max) + "l_gen"] = self.bestOSPair.mll
            used = [self.bestOSPair.l1, self.bestOSPair.l2] if self.bestOSPair else []
            
            for var in ["pt", "eta", "phi", "mass"]:
                self.ret["genLepZ1_" + var] = getattr(self.bestOSPair.l1, var, 0)
                self.ret["genLepZ2_" + var] = getattr(self.bestOSPair.l2, var, 0)
            for var in ["pdgId"]:
                self.ret["genLepZ1_" + var] = int(getattr(self.bestOSPair.l1, var, 0))
                self.ret["genLepZ2_" + var] = int(getattr(self.bestOSPair.l2, var, 0))


            for i in range(min(max,len(self.genleps))):
                if self.genleps[i] in used : continue
                for var in ["pt", "eta", "phi", "mass"]:
                    self.ret["genLepW_" + var] = getattr(self.genleps[i], var, 0)
                for var in ["pdgId"]:
                    self.ret["genLepW_" + var] = int(getattr(self.genleps[i], var, 0))
                #for var in ["pt", "pt"]:
                #    self.ret["wzBalance_" + var] = getattr(self.bestOSPair.l1.p4()+self.bestOSPair.l2.p4()-self.genleps[i].p4(), var, 0)
                balance = self.bestOSPair.l1.p4()
                balance += self.bestOSPair.l2.p4()
                self.ret["deltaR_WZ_gen"] = deltaR(balance.Eta(), balance.Phi(), self.genleps[i].p4().Eta(), self.genleps[i].p4().Phi())
                balance += self.genleps[i].p4()
                metmom = ROOT.TLorentzVector()
                metmom.SetPtEtaPhiM(self.metgen[0],0,self.metgenphi[0],0)
                balance += metmom
                # Later do it with standalone function like makeMassMET
                self.ret["wzBalance_pt_gen"] = balance.Pt()
                balance = self.bestOSPair.l1.p4(self.bestOSPair.l1.pt)
                balance += self.bestOSPair.l2.p4(self.bestOSPair.l2.pt)
                balance += self.genleps[i].p4(self.genleps[i].pt)
                balance += metmom
                self.ret["wzBalance_pt_gen"] = balance.Pt()
            return

        self.ret["mll_" + str(max) + "l_gen"] = -1

    def listBranches(self):

        self.branches = [
            ("is_3l_gen"            , "I"),
            ("is_4l_gen"            , "I"),
            ("is_5l_gen"            , "I"),
            ("nOSSF_3l_gen"         , "I"),
            ("nOSLF_3l_gen"         , "I"),
            ("nOSTF_3l_gen"         , "I"),
            ("mll_3l_gen"           , "F"),
            ("m3L_gen"              , "F"),
            ("nOSSF_4l_gen"         , "I"),
            ("nOSLF_4l_gen"         , "I"),
            ("nOSTF_4l_gen"         , "I"),
            ("mll_4l_gen"           , "F"),
            ("m4L_gen"              , "F"),
            ("minDeltaR_3l_gen"     , "F"),
            ("minDeltaR_4l_gen"     , "F"),
            ("minDeltaR_3l_mumu_gen", "F"),
            ("minDeltaR_4l_mumu_gen", "F"),
            ("minmllAFAS_gen"       , "F"),
            ("minmllSFOS_gen"       , "F")]
            
        self.branches.append(("nOS_gen"   , "I"))
        #biglist.append(("mll_gen"   , "F", 20, "nOS"))
        #biglist.append(("mll_i1_gen", "I", 20, "nOS"))
        #biglist.append(("mll_i2_gen", "I", 20, "nOS"))
        self.branches.append(("deltaR_WZ_gen", "F"))

        self.branches.append(("nLepGen_forMemory"   , "I"))
        self.branches.append(("nLepGen_gen"   , "I"))
        
        for var in ["pt", "eta", "phi", "mass"]:
            self.branches.append(("LepGen_" + var, "F", 20, "nLepGen_forMemory"))
            self.branches.append(("genLepZ1_"  + var, "F"))
            self.branches.append(("genLepZ2_"  + var, "F"))
            self.branches.append(("genLepW_"   + var, "F"))
        for var in ["pdgId"]:
            self.branches.append(("LepGen_" + var, "I", 20, "nLepGen_forMemory"))
            self.branches.append(("genLepZ1_"  + var, "I"))
            self.branches.append(("genLepZ2_"  + var, "I"))
            self.branches.append(("genLepW_"   + var, "I"))

        for var in ["pt"]:
            self.branches.append(("wzBalance_" + var + "_gen", "F"))
  
        for var in self.systsJEC:
            self.branches.append(("mT_3l"       + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("mT2L_3l"     + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("mT2T_3l"     + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("mT_4l"       + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("mT2L_4l"     + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("mT2T_4l"     + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("m3Lmet"      + self.systsJEC[var] + "_gen", "F"))
            self.branches.append(("m4Lmet"      + self.systsJEC[var] + "_gen", "F"))
        return self.branches


    ## resetMemory
    ## _______________________________________________________________
    def resetMemory(self):

        self.ret = {}

        self.ret["is_3l_gen"                ] = 0
        self.ret["is_4l_gen"                ] = 0
        self.ret["is_5l_gen"                ] = 0
        self.ret["nOSSF_3l_gen"             ] = 0
        self.ret["nOSLF_3l_gen"             ] = 0
        self.ret["nOSTF_3l_gen"             ] = 0
        self.ret["mll_3l_gen"               ] = 0
        self.ret["m3L_gen"                  ] = 0
        self.ret["nOSSF_4l_gen"             ] = 0
        self.ret["nOSLF_4l_gen"             ] = 0
        self.ret["nOSTF_4l_gen"             ] = 0
        self.ret["mll_4l_gen"               ] = 0
        self.ret["m4L_gen"                  ] = 0
        self.ret["minDeltaR_3l_gen"         ] = -1
        self.ret["minDeltaR_4l_gen"         ] = -1
        self.ret["minDeltaR_3l_mumu_gen"    ] = -1
        self.ret["minDeltaR_4l_mumu_gen"    ] = -1
        self.ret["deltaR_WZ_gen"            ] = 0

        self.ret["nOS_gen"   ] = 0
        #self.ret["mll_gen"   ] = [0.]*20
        #self.ret["mll_i1_gen"] = [-1]*20
        #self.ret["mll_i2_gen"] = [-1]*20

        self.ret["nLepGen_gen"] = 0
        self.ret["nLepGen_forMemory"] = 0

        for var in ["pt", "eta", "phi", "mass"]:
            self.ret["LepGen_" + var] = [0.]*20
            self.ret["genLepZ1_"  + var] = 0.
            self.ret["genLepZ2_"  + var] = 0.
            self.ret["genLepW_"   + var] = 0.
        for var in ["pdgId"]:
            self.ret["LepGen_" + var] = [0]*20
            self.ret["genLepZ1_"  + var] = 0
            self.ret["genLepZ2_"  + var] = 0
            self.ret["genLepW_"   + var] = 0

        for var in ["pt", "pt"]:
            self.ret["wzBalance_" + var + "_gen"] = 0

        for var in self.systsJEC:
            self.ret["mT_3l"       + self.systsJEC[var] + "_gen"] = 0.
            self.ret["mT2L_3l"     + self.systsJEC[var] + "_gen"] = 0.  
            self.ret["mT2T_3l"     + self.systsJEC[var] + "_gen"] = 0. 
            self.ret["mT_4l"       + self.systsJEC[var] + "_gen"] = 0.
            self.ret["mT2L_4l"     + self.systsJEC[var] + "_gen"] = 0.  
            self.ret["mT2T_4l"     + self.systsJEC[var] + "_gen"] = 0. 
            self.ret["m3Lmet"      + self.systsJEC[var] + "_gen"] = 0. 
            self.ret["m4Lmet"      + self.systsJEC[var] + "_gen"] = 0. 
    
    def writeLepSel(self):

        self.ret["nLepGen_gen"] = len(self.genleps)
        for i, l in enumerate(self.genleps):
            if i == 4: break # only keep the first 4 entries
            for var in ["pt", "eta", "phi", "mass"]:
                self.ret["LepGen_" + var][i] = getattr(l, var, 0)
            for var in ["pdgId"]:
                self.ret["LepGen_" + var][i] = int(getattr(l, var, 0))


        all = []
        #all2 = []
        for os in self.OS:
            all.append((0 if os.isSF else 1, 1 if os.wTau else 0, os.diff, os)) # priority to SF, then light, then difference to target
        #    all2.append((0 if os.isSF else 1, 1 if os.wTau else 0, os.diff, os)) # priority to SF, then light, then difference to target
        if all:
            #all.sort( key = lambda el: el[0] )
            all.sort()
            #print("        ", all)
            #print("        ", "-")
            #print("        ", all2)
            self.ret["nOS_gen"] = len(all)
            #for i,os in enumerate(all):
            #    self.ret["mll_gen"][i] = os[3].mll
            #    self.ret["mll_i1_gen"][i] = self.genleps.index(os[3].l1)
            #    self.ret["mll_i2_gen"][i] = self.genleps.index(os[3].l2)

def deltaPhi(phi1, phi2):
    res = phi1 - phi2
    while res >   math.pi: res -= 2*math.pi
    while res <= -math.pi: res += 2*math.pi
    return res

def deltaR(eta1, phi1, eta2, phi2):
    dEta = abs(eta1-eta2)
    dPhi = deltaPhi(phi1, phi2)
    return math.sqrt(dEta*dEta + dPhi*dPhi)


if __name__ == '__main__':
    """ Debug the module """
    from sys import argv
    from copy import deepcopy
    from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import eventLoop
    from PhysicsTools.NanoAODTools.postprocessing.framework.output import FriendOutput, FullOutput
    from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import InputTree
    
    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE/"
    process = "WZto3LNu"
#    process = "TTTo2L2Nu_part17"
    
    friends = [
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
    
    module_test =  lepgenVarsWZSM_nondressed_withtaus(
        "Mini", 
        verbosity = 2
    )
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()



